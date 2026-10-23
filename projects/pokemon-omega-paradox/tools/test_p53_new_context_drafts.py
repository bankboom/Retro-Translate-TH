#!/usr/bin/env python3
"""P5.2 source-aligned 56 whole-message drafts; static only, not ROM/gameplay QA."""
import csv
import unittest
from p47_full_scope_merge import ROOT, DRAFT_FILES, audit_drafts_only
from omega_control_tokens import tokens, max_visible_segment

CSV = ROOT / "translation" / "P5_2_DRIFTVEIL_MISTRALTON_DRAGONSPIRAL_DRAFTS.csv"

class P52TranslationExpansionQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with CSV.open(encoding="utf-8-sig", newline="") as stream:
            cls.rows = list(csv.DictReader(stream))

    def test_56_unique_omega_message_ids(self):
        self.assertEqual(len(self.rows), 56)
        keys = {(r["archive"], r["file_id"], r["message_id"]) for r in self.rows}
        self.assertEqual(len(keys), 56)
        self.assertIn(("story", "118", "16"), keys)
        self.assertIn(("story", "101", "20"), keys)
        self.assertIn(("story", "112", "6"), keys)

    def test_native_control_order_and_operands_unchanged(self):
        for row in self.rows:
            with self.subTest(key=(row["archive"], row["file_id"], row["message_id"])):
                src, tgt = row["original_english"], row["draft_thai"]
                self.assertEqual(tokens(src), tokens(tgt))
                self.assertEqual(int(row["token_count"]), len(tokens(src)))
                self.assertEqual(row["ordered_control_codes"], "PASS")

    def test_visible_codepoints_at_most_35_not_pixel_certified(self):
        for row in self.rows:
            with self.subTest(key=(row["archive"], row["file_id"], row["message_id"])):
                n = max_visible_segment(row["draft_thai"])
                self.assertLessEqual(n, 35)
                self.assertEqual(int(row["longest_codepoint_segment"]), n)
                self.assertEqual(row["width_review"], "PIXEL_WIDTH_PENDING")

    def test_source_dynamic_name_tokens_preserved(self):
        for row in self.rows:
            self.assertEqual(
                row["original_english"].count(r"\xF000Ā\x0001\x0000"),
                row["draft_thai"].count(r"\xF000Ā\x0001\x0000"),
            )

    def test_older_214_drafts_unmodified_no_conflict(self):
        result = audit_drafts_only([ROOT/"translation"/p for p in DRAFT_FILES])
        self.assertEqual(result["draft_rows"], 270)
        self.assertEqual(result["unique_message_ids"], 270)
        self.assertEqual(result["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT",0), 0)
        self.assertEqual(result["counts"].get("CONTROL_MISMATCH",0), 0)

    def test_unreviewed_are_not_claimed_rom_approved(self):
        for row in self.rows:
            self.assertEqual(row["status"], "DRAFT_NEEDS_CONTEXT")
            self.assertIn("PIXEL", row["width_review"])
            self.assertNotIn("PASS_EMULATOR", row["comment"])

if __name__ == "__main__":
    unittest.main()
