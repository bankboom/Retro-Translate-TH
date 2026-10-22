#!/usr/bin/env python3
"""Synthetic safety tests. These are not real-ROM nor emulator tests."""
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p40_reuse_audit", HERE / "p40_reuse_audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

INVENTORY_FIELDS = [
    "archive", "file_id", "message_id", "status", "omega_custom",
    "source_english_or_original", "current_p35_message",
    "white_thai_master", "reuse_master_available", "control_safe_master",
]
MEM_FIELDS = ["archive", "file_id", "message_id", "white_english", "white_thai_pua_text"]


def put(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def inv(msg_id="1", source="Hello\\xFFFEWorld\\xF000븁\\x0000", custom="0", status="PENDING"):
    return dict(archive="system", file_id="44", message_id=msg_id,
                status=status, omega_custom=custom,
                source_english_or_original=source,
                current_p35_message=source,
                white_thai_master="\\xE801\\xFFFE\\xE802\\xF000븁\\x0000",
                reuse_master_available="1", control_safe_master="1")


def tm(msg_id="1", original="Hello\\xFFFEWorld\\xF000븁\\x0000",
       thai="\\xE801\\xFFFE\\xE802\\xF000븁\\x0000"):
    return dict(archive="system", file_id="44", message_id=msg_id,
                white_english=original, white_thai_pua_text=thai)


class P40Tests(unittest.TestCase):
    def audit(self, inventory, memory, approved=None, expected=None):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            put(p / "inventory.csv", INVENTORY_FIELDS, inventory)
            put(p / "tm.csv", MEM_FIELDS, memory)
            app_path = None
            if approved is not None:
                app_path = p / "approval.csv"
                put(app_path, ["archive", "file_id", "message_id", "source_sha256",
                               "qa_status", "scene_id", "reviewer"], approved)
            result = audit.prepare(p / "inventory.csv", p / "tm.csv",
                                   p / "output", len(inventory) if expected is None else expected,
                                   app_path)
            with (p / "output" / "p40_static_candidates.csv").open(newline="", encoding="utf-8") as f:
                candidates = list(csv.DictReader(f))
            with (p / "output" / "p40_reviewed_reuse_manifest.csv").open(newline="", encoding="utf-8") as f:
                accepted = list(csv.DictReader(f))
            return result, candidates, accepted

    def test_control_payload_is_preserved(self):
        self.assertNotEqual(
            audit.control_signature(r"X\xF000븀\x0000"),
            audit.control_signature(r"X\xF000븁\x0000"))
        self.assertEqual(
            audit.control_signature(r"\xE801\xFFFE\xF000븁\x0000"),
            ("\\xE801", "\\xFFFE", "\\xF000븁\\x0000"))

    def test_exact_match_is_only_candidate(self):
        res, cand, accepted = self.audit([inv()], [tm()])
        self.assertEqual(len(cand), 1)
        self.assertEqual(len(accepted), 0)
        self.assertFalse(res["created_bps"])

    def test_custom_omega_is_held(self):
        res, cand, _ = self.audit([inv(custom="1")], [tm()])
        self.assertEqual(len(cand), 0)
        self.assertEqual(res["counts"]["OMEGA_CUSTOM_DO_NOT_OVERWRITE"], 1)

    def test_source_mismatch_is_held(self):
        res, cand, _ = self.audit([inv(source="New Omega line")], [tm()])
        self.assertEqual(len(cand), 0)
        self.assertEqual(res["counts"]["SOURCE_MISMATCH_EXACT_TEXT"], 1)

    def test_control_payload_change_is_held(self):
        wrong = tm(thai="\\xE801\\xFFFE\\xE802\\xF000븀\\x0000")
        r, cand, _ = self.audit([inv()], [wrong])
        self.assertEqual(len(cand), 0)
        self.assertEqual(r["counts"]["INVENTORY_AND_MASTER_THAI_CONFLICT"], 1)

    def test_previous_thai_is_never_reimported(self):
        r, cand, _ = self.audit([inv(status="THAI_IN_ROM")], [tm()])
        self.assertEqual(len(cand), 0)
        self.assertEqual(r["counts"]["THAI_ALREADY_IN_P35_SNAPSHOT_RETEST_PER_BUILD"], 1)

    def test_review_requires_exact_source_sha_and_human_evidence(self):
        a = {"archive": "system", "file_id": "44", "message_id": "1",
             "source_sha256": audit.sha256_text(inv()["source_english_or_original"]),
             "qa_status": "REVIEWED", "scene_id": "intro", "reviewer": "reviewer"}
        r, c, approved = self.audit([inv()], [tm()], [a])
        self.assertEqual(len(c), 1)
        self.assertEqual(len(approved), 1)
        self.assertEqual(approved[0]["status"], "REVIEWED_NOT_INJECTED")

    def test_missing_records_fail_expected_inventory(self):
        with self.assertRaisesRegex(ValueError, "Inventory count"):
            self.audit([inv()], [tm()], expected=56700)

    def test_duplicate_memory_conflict_fails(self):
        with self.assertRaisesRegex(ValueError, "Conflicting translation memory key"):
            self.audit([inv()], [tm(), tm(thai="\\xE999")])


if __name__ == "__main__":
    unittest.main()
