#!/usr/bin/env python3
"""P5.2 270-ID context QA carry-forward matrix. Static data provenance only."""
import csv
import unittest
from p47_full_scope_merge import ROOT
from omega_control_tokens import tokens, max_visible_segment

P = ROOT / "translation"
MATRIX = P / "P5_2_CONTEXT_QA_270_MESSAGE_MATRIX.csv"
PRIOR = P / "P5_1_CONTEXT_QA_214_MESSAGE_MATRIX.csv"
ADDED = P / "P5_2_DRIFTVEIL_MISTRALTON_DRAGONSPIRAL_DRAFTS.csv"

def rows(p):
    with p.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def key(r):
    return (r["archive"],r["file_id"],r["message_id"])

class P52ContextMatrixChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = rows(MATRIX)
        cls.previous = rows(PRIOR)
        cls.new_drafts = rows(ADDED)
        cls.lookup={key(r):r for r in cls.matrix}

    def test_270_unique_rows(self):
        self.assertEqual(len(self.matrix),270)
        self.assertEqual(len(self.lookup),270)

    def test_214_previous_reviews_preserved_exactly(self):
        self.assertEqual(len(self.previous),214)
        for old in self.previous:
            self.assertEqual(self.lookup[key(old)],old)

    def test_56_new_rows_not_misreported_as_verified(self):
        self.assertEqual(len(self.new_drafts),56)
        for src in self.new_drafts:
            with self.subTest(k=key(src)):
                q = self.lookup[key(src)]
                self.assertEqual(q["static_token_qa"],"PASS")
                self.assertEqual(q["max_visible_codepoints"],
                                 str(max_visible_segment(src["draft_thai"])))
                self.assertEqual(tokens(src["original_english"]),
                                 tokens(src["draft_thai"]))
                self.assertEqual(q["native_pua_encoding"],"NOT_DONE")
                self.assertEqual(q["emulator_injection"],"NOT_DONE")
                self.assertNotEqual(q["automated_release_decision"],"RELEASE")

    def test_special_context_holds(self):
        for key_tuple in (("story","112","6"), ("story","118","16"),
                          ("story","118","21"), ("story","118","22"),
                          ("story","118","26"), ("story","101","28")):
            self.assertEqual(self.lookup[key_tuple]["semantic_context_status"],
                             "SCENE_DETAIL_HOLD")

    def test_old_width_flags_are_still_not_closed(self):
        flagged=[r for r in self.matrix
                 if r["static_line_qa"]=="WIDTH_FLAG_OVER_35_CODEPOINTS"]
        self.assertEqual(len(flagged),11)

if __name__ == "__main__":
    unittest.main()
