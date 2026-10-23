#!/usr/bin/env python3
"""Static provenance, control and story distinction tests for 18 P5.1 drafts.

These tests cannot certify emulator rendering, localization semantics, or ROM completeness.
"""
import csv
import unittest
from omega_control_tokens import tokens,max_visible_segment
from p47_full_scope_merge import ROOT,DRAFT_FILES,audit_drafts_only

PATH=ROOT/"translation"/"P5_1_LEGENDS_AND_MASKED_MAN_DRAFTS.csv"

class LoreContextChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PATH.open(encoding="utf-8-sig",newline="") as f:
            cls.rows=list(csv.DictReader(f))
        cls.index={(r["archive"],r["file_id"],r["message_id"]):r for r in cls.rows}

    def test_18_unique_message_ids(self):
        self.assertEqual(len(self.rows),18)
        self.assertEqual(len(self.index),18)

    def test_all_control_ops_exact(self):
        for r in self.rows:
            with self.subTest(id=(r["file_id"],r["message_id"])):
                self.assertEqual(tokens(r["original_english"]),tokens(r["draft_thai"]))
                self.assertEqual(int(r["token_count"]),len(tokens(r["draft_thai"])))

    def test_35_character_limit(self):
        for r in self.rows:
            with self.subTest(id=r["message_id"]):
                n=max_visible_segment(r["draft_thai"])
                self.assertLessEqual(n,35)
                self.assertEqual(n,int(r["longest_codepoint_segment"]))

    def test_truth_and_ideals_are_not_conflated(self):
        self.assertIn("ความจริง",self.index[("story","61","6")]["draft_thai"])
        self.assertIn("อุดมคติ",self.index[("story","61","7")]["draft_thai"])

    def test_masked_man_switch_preserves_native_special_codes(self):
        for msg in ("0","1","4","7"):
            r=self.index[("story","69",msg)]
            self.assertIn(r"\xF000븉\x0001\x0001",r["draft_thai"])

    def test_context_remains_pending_for_all(self):
        for r in self.rows:
            self.assertEqual(r["status"],"DRAFT_NEEDS_CONTEXT")
            self.assertEqual(r["width_review"],"PIXEL_WIDTH_PENDING")

    def test_cumulative_merger_has_no_variants(self):
        result=audit_drafts_only([ROOT/"translation"/p for p in DRAFT_FILES])
        self.assertGreaterEqual(result["draft_rows"],214)
        self.assertEqual(result["unique_message_ids"],result["draft_rows"])
        self.assertEqual(result["counts"].get("CONTROL_MISMATCH",0),0)
        self.assertEqual(result["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT",0),0)

if __name__=="__main__":
    unittest.main()
