#!/usr/bin/env python3
"""P4.8 real-draft static integrity QA. No ROM writing or emulator claim."""
import csv
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from omega_control_tokens import tokens, max_visible_segment
from p47_full_scope_merge import ROOT, DRAFT_FILES, audit_drafts_only

PATH = ROOT / "translation" / "P4_8_OMEGA_PRIORITY_FULL_MESSAGE_DRAFTS.csv"

class P48FullMessages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PATH.open(encoding="utf-8-sig", newline="") as file:
            cls.rows = list(csv.DictReader(file))

    def test_23_new_message_ids(self):
        self.assertEqual(len(self.rows), 23)
        keys = {(r["archive"], r["file_id"], r["message_id"]) for r in self.rows}
        self.assertEqual(len(keys), 23)
        self.assertIn(("system", "44", "26"), keys)
        self.assertIn(("story", "36", "18"), keys)

    def test_every_message_keeps_the_complete_control_sequence(self):
        for row in self.rows:
            with self.subTest(key=(row["archive"], row["file_id"], row["message_id"])):
                self.assertEqual(tokens(row["original_english"]), tokens(row["draft_thai"]))
                self.assertEqual(row["ordered_control_codes"], "PASS")
                self.assertEqual(int(row["token_count"]), len(tokens(row["original_english"])))

    def test_no_segment_over_35_codepoints(self):
        for row in self.rows:
            with self.subTest(key=(row["archive"], row["file_id"], row["message_id"])):
                self.assertLessEqual(max_visible_segment(row["draft_thai"]), 35)
                self.assertEqual(int(row["longest_codepoint_segment"]),
                                 max_visible_segment(row["draft_thai"]))

    def test_drafts_are_not_misrepresented_as_reviewed(self):
        for row in self.rows:
            self.assertEqual(row["status"], "DRAFT_NEEDS_CONTEXT")
            self.assertEqual(row["width_review"], "PIXEL_WIDTH_PENDING")

    def test_merge_all_196_without_duplicate_or_variant(self):
        files = [ROOT / "translation" / x for x in DRAFT_FILES]
        result = audit_drafts_only(files)
        self.assertEqual(result["draft_rows"], 196)
        self.assertEqual(result["unique_message_ids"], 196)
        self.assertEqual(result["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT", 0), 0)
        self.assertEqual(result["counts"].get("CONTROL_MISMATCH", 0), 0)

    def test_variable_name_token_is_preserved(self):
        # Validate only new P4.8 messages; earlier story/21 drafts already
        # have their own regression coverage.
        for archive, fid, mid in (
            ("system", "44", "26"),
            ("story", "36", "12"),
            ("story", "36", "13"),
        ):
            rows = [r for r in self.rows if r["archive"] == archive
                    and r["file_id"] == fid and r["message_id"] == mid]
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["draft_thai"].count(r"\xF000Ā\x0001\x0000"), 1)

if __name__ == "__main__":
    unittest.main()
