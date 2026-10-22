#!/usr/bin/env python3
"""P4.2 Thai draft checks; *not* a ROM, native E8xx, or emulator test."""
import csv
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "translation"
P41 = BASE / "P4_1_OMEGA_STORY_EARLY_DRAFTS.csv"
P42 = BASE / "P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv"
TOK = re.compile(r"\\xF000(?:(?!\\xF000|\\xFFFE|\\xFFFF).)*?\\x0000|\\x(?:FFFE|FFFF)",re.S)


def load(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def entry_key(r):
    return (r["archive"],r["file_id"],r["message_id"])


class P42RealDraftIntegrity(unittest.TestCase):
    def test_count_and_nonoverlap(self):
        old,new=load(P41),load(P42)
        self.assertEqual(len(old),40)
        self.assertEqual(len(new),19)
        newids=[entry_key(row) for row in new]
        self.assertEqual(len(set(newids)),19)
        self.assertFalse(set(newids)&set(entry_key(row) for row in old))
        self.assertEqual({r["archive"] for r in new},{"story"})

    def test_full_control_code_and_operand_preservation(self):
        for row in load(P42):
            with self.subTest(id=entry_key(row)):
                self.assertEqual(TOK.findall(row["original_english"]),TOK.findall(row["draft_thai"]))
                self.assertEqual(row["ordered_control_codes"],"PASS")
                self.assertEqual(int(row["token_count"]),len(TOK.findall(row["draft_thai"])))

    def test_textbox_segments_within_codepoint_35(self):
        for row in load(P42):
            with self.subTest(id=entry_key(row)):
                segments=TOK.split(row["draft_thai"])
                self.assertLessEqual(max(map(len,segments),default=0),35)
                self.assertEqual(int(row["longest_codepoint_segment"]),max(map(len,segments),default=0))
                self.assertEqual(row["width_review"],"PIXEL_WIDTH_PENDING")

    def test_draft_status_avoids_release_promotion(self):
        for row in load(P42):
            with self.subTest(id=entry_key(row)):
                self.assertEqual(row["status"],"DRAFT_NEEDS_CONTEXT")
                self.assertNotIn("\u200b",row["draft_thai"])
                self.assertNotIn("\n",row["draft_thai"])
                self.assertTrue(row["original_english"].strip())
                self.assertTrue(row["draft_thai"].strip())


if __name__ == "__main__":
    unittest.main()
