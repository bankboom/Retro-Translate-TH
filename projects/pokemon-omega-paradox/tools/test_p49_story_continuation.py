#!/usr/bin/env python3
"""Omega P4.9 real whole-message draft structure QA. NOT a ROM/emulator test."""
import csv
import unittest
from pathlib import Path
from omega_control_tokens import tokens, max_visible_segment
from p47_full_scope_merge import ROOT, DRAFT_FILES, audit_drafts_only

PATH = ROOT / "translation" / "P4_9_OMEGA_STORY_CONTINUATION_DRAFTS.csv"

class P49StoryContinuationQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PATH.open("r", encoding="utf-8-sig", newline="") as f:
            cls.data = list(csv.DictReader(f))

    def test_28_distinct_full_messages(self):
        keys = [(r["archive"], r["file_id"], r["message_id"]) for r in self.data]
        self.assertEqual(len(keys), 28)
        self.assertEqual(len(set(keys)), 28)
        self.assertIn(("story", "43", "2"), keys)
        self.assertIn(("story", "43", "18"), keys)
        self.assertIn(("story", "56", "4"), keys)

    def test_all_28_preserve_control_tokens_with_parameters(self):
        for r in self.data:
            with self.subTest(message=(r["archive"],r["file_id"],r["message_id"])):
                self.assertEqual(tokens(r["original_english"]), tokens(r["draft_thai"]))
                self.assertEqual(r["ordered_control_codes"], "PASS")
                self.assertEqual(int(r["token_count"]), len(tokens(r["original_english"])))

    def test_visible_segments_at_most_35_codepoints(self):
        for r in self.data:
            with self.subTest(message=r["message_id"]):
                width = max_visible_segment(r["draft_thai"])
                self.assertLessEqual(width, 35)
                self.assertEqual(width, int(r["longest_codepoint_segment"]))
                self.assertEqual(r["width_review"], "PIXEL_WIDTH_PENDING")

    def test_context_review_is_not_in_game_certification(self):
        for r in self.data:
            self.assertEqual(r["status"], "DRAFT_NEEDS_CONTEXT")
            self.assertTrue(r["original_english"].strip())
            self.assertTrue(r["draft_thai"].strip())

    def test_dialogue_name_control_retained(self):
        by_id = {(r["file_id"],r["message_id"]):r for r in self.data}
        for key in (("43","2"),("43","12"),("43","13"),("56","0"),("56","1")):
            r=by_id[key]
            self.assertEqual(r["draft_thai"].count(r"\xF000Ā\x0001\x0000"),1)

    def test_cynthia_story_discrepancy_not_silently_corrected(self):
        by_id = {(r["file_id"],r["message_id"]):r for r in self.data}
        for key in (("43","18"),("56","4")):
            self.assertIn("STORY CONTINUITY FLAG",by_id[key]["comment"])

    def test_214_cumulative_drafts_no_conflicts(self):
        files=[ROOT/"translation"/name for name in DRAFT_FILES]
        report=audit_drafts_only(files)
        self.assertGreaterEqual(report["draft_rows"],214)
        self.assertEqual(report["unique_message_ids"],report["draft_rows"])
        self.assertEqual(report["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT",0),0)
        self.assertEqual(report["counts"].get("CONTROL_MISMATCH",0),0)

if __name__ == "__main__":
    unittest.main()
