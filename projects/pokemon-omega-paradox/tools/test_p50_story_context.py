#!/usr/bin/env python3
"""P5.0 static translation QA on 47 actual Omega-custom strings.

These checks are NOT a binary injection, semantic approval, font width
verification or gameplay certification.
"""
from __future__ import annotations
import csv
import unittest
from pathlib import Path
from omega_control_tokens import tokens, max_visible_segment
from p47_full_scope_merge import ROOT, DRAFT_FILES, audit_drafts_only

FILE=ROOT/"translation"/"P5_0_CASTELIA_NIMBASA_CONTEXT_DRAFTS.csv"

class P50ContextDraftQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with FILE.open(encoding="utf-8-sig",newline="") as fh:
            cls.rows=list(csv.DictReader(fh))
        cls.by_id={(r["archive"],r["file_id"],r["message_id"]):r for r in cls.rows}

    def test_unique_messages(self):
        self.assertEqual(len(self.rows),47)
        self.assertEqual(len(self.by_id),47)
        self.assertIn(("story","61","16"),self.by_id)
        self.assertIn(("story","67","27"),self.by_id)

    def test_original_control_token_order_never_changes(self):
        for r in self.rows:
            with self.subTest(message=(r["archive"],r["file_id"],r["message_id"])):
                self.assertEqual(tokens(r["original_english"]),tokens(r["draft_thai"]))
                self.assertEqual(int(r["token_count"]),len(tokens(r["original_english"])))
                self.assertEqual(r["ordered_control_codes"],"PASS")

    def test_35_codepoint_static_line_limit(self):
        for r in self.rows:
            with self.subTest(message=r["message_id"]):
                n=max_visible_segment(r["draft_thai"])
                self.assertLessEqual(n,35)
                self.assertEqual(n,int(r["longest_codepoint_segment"]))
                self.assertEqual(r["width_review"],"PIXEL_WIDTH_PENDING")

    def test_context_must_not_be_falsely_approved(self):
        for r in self.rows:
            self.assertEqual(r["status"],"DRAFT_NEEDS_CONTEXT")
            self.assertNotIn("EMULATOR_VERIFIED",r["status"])
            self.assertIn("not native PUA or ROM injected",r["comment"])

    def test_tokenized_player_name_preserved(self):
        for fid, mids in {"61":["34","35"],"67":["9","10","13","14","17","20","32"]}.items():
            for mid in mids:
                row=self.by_id[("story",fid,mid)]
                self.assertEqual(row["draft_thai"].count(r"\xF000Ā\x0001\x0000"),1)

    def test_cynthia_title_context_is_not_claimed_resolved(self):
        for mid in ("27","34"):
            self.assertIn("STORY_CONTINUITY_REVIEW",self.by_id[("story","67",mid)]["comment"])
        self.assertIn("สูญเสียตำแหน่งแชมเปียน",
            self.by_id[("story","67","27")]["draft_thai"])

    def test_cynthia_speaks_to_gible_in_first_person(self):
        row=self.by_id[("story","61","16")]
        self.assertIn("Gible ฉันดีใจ",row["draft_thai"])

    def test_all_unique_draft_ids_cumulative(self):
        sources=[ROOT/"translation"/x for x in DRAFT_FILES]
        results=audit_drafts_only(sources)
        self.assertEqual(results["draft_rows"],196)
        self.assertEqual(results["unique_message_ids"],196)
        self.assertEqual(results["counts"].get("CONTROL_MISMATCH",0),0)
        self.assertEqual(results["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT",0),0)

if __name__=="__main__":
    unittest.main()
