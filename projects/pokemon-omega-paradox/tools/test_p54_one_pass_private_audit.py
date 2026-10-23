#!/usr/bin/env python3
"""Offline integration tests of the one-pass 56700/25976/270 audit pipeline.

Fixture row counts are deliberately small; a passing test does not certify
the owner's complete datasets or any game patch.
"""
import csv
import tempfile
import unittest
import zlib
from pathlib import Path

from p54_one_pass_private_audit import (
    bps_header_audit, enforce_digest, fingerprint, run
)


def csvfile(path, headers, values):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        w.writerows(values)


INV = ["archive","file_id","message_id","status","omega_custom",
       "source_english_or_original","current_p35_message",
       "needs_translation_review"]
DRAFT = ["archive","file_id","message_id","original_english",
         "draft_thai","status"]
MASTER = ["archive","file_id","message_id","white_english",
          "white_thai_pua_text"]


class OnePassOwnerOnlyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.inv = self.root / "original_2.csv"
        self.drafts = self.root / "thai_1.csv"
        self.memory = self.root / "white_1.csv"
        csvfile(self.inv, INV, [
            dict(archive="story",file_id="1",message_id="3",
                 status="ENGLISH_OR_NAME_PENDING_REVIEW",omega_custom="1",
                 source_english_or_original="Hello",
                 current_p35_message="Hello",needs_translation_review="1"),
            dict(archive="system",file_id="1",message_id="4",
                 status="NONLINGUISTIC_NUMERIC",omega_custom="0",
                 source_english_or_original="99",
                 current_p35_message="99",needs_translation_review="0"),
        ])
        csvfile(self.drafts,DRAFT,[
            dict(archive="story",file_id="1",message_id="3",
                 original_english="Hello",draft_thai="สวัสดี",
                 status="DRAFT_NEEDS_CONTEXT"),
        ])
        csvfile(self.memory, MASTER, [
            dict(archive="story",file_id="1",message_id="8",
                 white_english="Hello",white_thai_pua_text=r"\xE800"),
        ])

    def tearDown(self):
        self.temp.cleanup()

    def invoke(self):
        return run(
            inventory=self.inv, master=self.memory,
            out=self.root / "private",
            draft_paths=[self.drafts],
            expected_inventory=2,
            expected_master=1,
            expected_drafts=1,
            required_hashes={},
        )

    def test_small_complete_fixture_queues_are_real_and_owner_only(self):
        report=self.invoke()
        self.assertEqual(report["inventory_rows_verified"],2)
        self.assertEqual(report["white_master_rows_verified"],1)
        self.assertEqual(report["draft_rows_verified"],1)
        self.assertEqual(report["p47_inventory_audit"]["inventory_unique_ids"],2)
        self.assertEqual(report["p53_native_donor_audit"][
            "native_donor_segments_for_review"],1)
        self.assertFalse(report["release_100_percent_approved"])
        self.assertFalse(report["rom_changed"])
        self.assertTrue((self.root/"private"/"native_donor_review.csv").is_file())
        self.assertTrue((self.root/"private"/"inventory"/
                         "p47_context_draft_queue.csv").is_file())

    def test_incomplete_inventory_fails_before_output(self):
        with self.assertRaisesRegex(ValueError, "INVENTORY_TRUNCATED"):
            run(inventory=self.inv,master=self.memory,
                out=self.root/"blocked",draft_paths=[self.drafts],
                expected_inventory=3,expected_master=1,expected_drafts=1)
        self.assertFalse((self.root/"blocked").exists())

    def test_wrong_sha_blocks_before_output(self):
        with self.assertRaisesRegex(ValueError,"INPUT_SHA256_MISMATCH"):
            run(inventory=self.inv,master=self.memory,
                out=self.root/"blocked",draft_paths=[self.drafts],
                expected_inventory=2,expected_master=1,expected_drafts=1,
                required_hashes={"master_sha256":"0"*64})
        self.assertFalse((self.root/"blocked").exists())

    def test_duplicate_draft_ids_fail_before_output(self):
        with self.drafts.open("a",encoding="utf-8") as f:
            f.write("story,1,3,Hello,สวัสดี,DRAFT_NEEDS_CONTEXT\n")
        with self.assertRaisesRegex(ValueError,"UNSAFE_DRAFT_SET"):
            self.invoke()

    def test_bps_patch_trailer_crc_integrity_only(self):
        p=self.root/"smoke.bps"
        prefix=b"BPS1"+b"\x80"
        # CRC values for source/target are placeholders; the audit should never
        # claim target is rebuilt from these fields.
        data=prefix+(123).to_bytes(4,"little")+(456).to_bytes(4,"little")
        data+=zlib.crc32(data).to_bytes(4,"little")
        p.write_bytes(data)
        r=bps_header_audit(p)
        self.assertTrue(r["patch_crc_valid"])
        self.assertFalse(r["target_crc_verified"])
        self.assertFalse(r["applied_target_sha_verified"])
        with p.open("r+b") as f:
            f.seek(4)
            f.write(b"\x81")
        with self.assertRaisesRegex(ValueError,"BPS_PATCH_CRC_MISMATCH"):
            bps_header_audit(p)

    def test_fingerprint_is_streaming_sha_and_crc(self):
        p=self.root/"test.bin"
        p.write_bytes(b"abc"*1000)
        fp=fingerprint(p)
        self.assertEqual(fp["bytes"],3000)
        self.assertEqual(fp["crc32"],f"{zlib.crc32(p.read_bytes()):08x}")
        self.assertEqual(enforce_digest(p,fp["sha256"]),fp)


if __name__ == "__main__":
    unittest.main()
