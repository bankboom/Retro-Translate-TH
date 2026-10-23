#!/usr/bin/env python3
"""Per-ID P5.1 context QA matrix correctness tests.

This deliberately tests data-state consistency, NOT semantic completeness
or in-game verification.
"""
import csv
import unittest
from p47_full_scope_merge import ROOT

FILE=ROOT/"translation"/"P5_1_CONTEXT_QA_214_MESSAGE_MATRIX.csv"

class TranslationContextMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FILE.open(encoding="utf-8-sig",newline="") as f:
            cls.rows=list(csv.DictReader(f))

    def test_214_unique_ids_with_sources(self):
        self.assertEqual(len(self.rows),214)
        self.assertEqual(len(set((r["archive"],r["file_id"],r["message_id"]) for r in self.rows)),214)
        self.assertTrue(all(r["source_csv"] for r in self.rows))

    def test_all_control_sequences_pass_static_qa(self):
        self.assertTrue(all(r["static_token_qa"]=="PASS" for r in self.rows))

    def test_11_known_width_flags_are_preserved_not_auto_approved(self):
        wide=[r for r in self.rows if r["static_line_qa"]=="WIDTH_FLAG_OVER_35_CODEPOINTS"]
        self.assertEqual(len(wide),11)
        self.assertTrue(all(int(r["max_visible_codepoints"])>35 for r in wide))

    def test_no_draft_claims_injected_or_reviewed_globally(self):
        for row in self.rows:
            self.assertEqual(row["native_pua_encoding"],"NOT_DONE")
            self.assertEqual(row["emulator_injection"],"NOT_DONE")
            self.assertNotEqual(row["automated_release_decision"],"RELEASE")

    def test_cynthia_conflicting_chronology_stays_flagged(self):
        index={(r["archive"],r["file_id"],r["message_id"]):r for r in self.rows}
        for key in (("story","43","18"),("story","56","4"),("story","67","27")):
            self.assertEqual(index[key]["semantic_context_status"],"STORY_CONTINUITY_HOLD")

if __name__=="__main__":
    unittest.main()
