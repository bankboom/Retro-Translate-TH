#!/usr/bin/env python3
"""Actual synthetic BPS build-and-APPLY checks; no copyrighted ROM in CI."""
import tempfile
import unittest
import zlib
from pathlib import Path

from p55_bps_verified_io import (
    BPSError, apply_patch, create_patch, inspect_patch,
    number_encode, number_decode, read_header,
)

class BPSVerifiedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.clean = self.root/"clean.nds"
        self.target = self.root/"rebuilt.nds"
        self.patch = self.root/"pilot.bps"
        self.applied = self.root/"applied.nds"

    def tearDown(self):
        self.temp.cleanup()

    def make(self, source: bytes, target: bytes):
        self.clean.write_bytes(source)
        self.target.write_bytes(target)
        return create_patch(self.clean, self.target, self.patch)

    def test_bps_varints_roundtrip_and_monotonic(self):
        for n in (0,1,2,126,127,128,129,254,255,256,
                  16382,16383,16384,1234567,2**32,2**40):
            encoded = number_encode(n)
            self.assertEqual(number_decode(encoded, 0, len(encoded)),
                             (n, len(encoded)))
        with self.assertRaises(BPSError):
            number_encode(-1)

    def test_unchanged_source_target_bps(self):
        src = b"HEADER00" + b"\x00"*1000 + b"TAIL12345"
        r = self.make(src,src)
        self.assertTrue(r["actual_apply_verified"])
        self.assertEqual(r["action_counts"]["TargetRead"], 0)
        apply = apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),src)
        self.assertTrue(apply["target_checksum_verified"])

    def test_single_small_ciphertext_delta_and_append(self):
        old=b"NDS-HEADER"+b"\x01"*400+b"THISISNARC"+b"\x03"*400
        new=old[:200]+b"\xaa\xbb\xcc\xdd"+old[204:]+b"extra"
        self.make(old,new)
        result=apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),new)
        self.assertEqual(result["commands_per_action"]["SourceRead"],2)
        self.assertGreaterEqual(result["commands_per_action"]["TargetRead"],2)

    def test_shorter_target_rom_is_valid_bps(self):
        self.make(b"abcdef123456789",b"abc")
        apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),b"abc")

    def test_large_changed_block_streamed(self):
        old=b"ABCD"+b"\x00"*200000+b"EFGH"
        new=b"ABCD"+b"\x08"*200000+b"EFGH"
        self.make(old,new)
        apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),new)

    def test_source_and_target_copy_actions_with_overlap(self):
        # target = AB (SourceRead) + ABAB (TargetCopy, overlapping)
        #          + XY (TargetRead) + DE (SourceCopy)
        original=b"ABCDEFGHIJ"
        patched=b"ABABABXYDE"
        self.clean.write_bytes(original)
        body=bytearray(b"BPS1")
        body+=number_encode(len(original))+number_encode(len(patched))
        body+=number_encode(0)  # empty metadata
        body+=number_encode((2-1)*4+0)
        body+=number_encode((4-1)*4+3)
        body+=number_encode(0)   # TargetCopy relative offset 0
        body+=number_encode((2-1)*4+1)+b"XY"
        body+=number_encode((2-1)*4+2)
        body+=number_encode(6)   # SourceCopy signed +3
        body+=zlib.crc32(original).to_bytes(4,"little")
        body+=zlib.crc32(patched).to_bytes(4,"little")
        body+=zlib.crc32(body).to_bytes(4,"little")
        self.patch.write_bytes(body)
        res=apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),patched)
        self.assertEqual(res["commands_per_action"]["TargetCopy"],1)
        self.assertEqual(res["commands_per_action"]["SourceCopy"],1)

    def test_detect_patch_crc_corruption_before_writing(self):
        self.make(b"0123456789",b"01234___89")
        patched=bytearray(self.patch.read_bytes())
        patched[-1]^=1
        self.patch.write_bytes(patched)
        with self.assertRaisesRegex(BPSError,"PATCH_CRC"):
            apply_patch(self.clean,self.patch,self.applied)
        self.assertFalse(self.applied.exists())

    def test_detect_wrong_original_crc_before_writing(self):
        self.make(b"0123456789",b"01234___89")
        self.clean.write_bytes(b"012345678?")
        with self.assertRaisesRegex(BPSError,"SOURCE_CRC"):
            apply_patch(self.clean,self.patch,self.applied)
        self.assertFalse(self.applied.exists())

    def test_detect_wrong_expected_sha_without_publishing(self):
        self.make(b"0123456789",b"01234___89")
        with self.assertRaisesRegex(BPSError,"TARGET_SHA256"):
            apply_patch(self.clean,self.patch,self.applied,expected_sha="0"*64)
        self.assertFalse(self.applied.exists())

    def test_clean_rom_full_sha_guard_even_when_crc_matches(self):
        self.make(b"0123456789",b"01234___89")
        with self.assertRaisesRegex(BPSError,"CLEAN_ROM_SHA256_MISMATCH"):
            apply_patch(self.clean,self.patch,self.applied,
                        expected_clean_sha="0"*64)
        self.assertFalse(self.applied.exists())

    def test_cannot_overwrite_original_source(self):
        self.make(b"0123456789",b"01234___89")
        with self.assertRaisesRegex(BPSError,"OUTPUT_MUST_NOT_OVERWRITE"):
            apply_patch(self.clean,self.patch,self.clean)
        self.assertEqual(self.clean.read_bytes(),b"0123456789")

    def test_cannot_overwrite_existing_output(self):
        self.make(b"0123456789",b"01234___89")
        self.applied.write_bytes(b"keep")
        with self.assertRaisesRegex(BPSError,"OUTPUT_ALREADY_EXISTS"):
            apply_patch(self.clean,self.patch,self.applied)
        self.assertEqual(self.applied.read_bytes(),b"keep")

    def test_created_source_sha_guard(self):
        self.clean.write_bytes(b"ABC")
        self.target.write_bytes(b"ABD")
        with self.assertRaisesRegex(BPSError,"CLEAN_SHA256"):
            create_patch(self.clean,self.target,self.patch,
                         expected_clean_sha="0"*64)
        self.assertFalse(self.patch.exists())

    def test_bps_inspection_not_claiming_target_verified(self):
        self.make(b"12345678",b"xx345678")
        d=inspect_patch(self.patch,self.clean)
        self.assertTrue(d["patch_crc_valid"])
        self.assertFalse(d["target_crc_verified_by_apply"])
        self.assertEqual(d["source_bytes"],8)

    def test_truncated_bps_detected(self):
        with self.assertRaises(BPSError):
            read_header(b"BPS1")
        with self.assertRaises(BPSError):
            number_decode(b"",0,0)

if __name__=="__main__":
    unittest.main()
