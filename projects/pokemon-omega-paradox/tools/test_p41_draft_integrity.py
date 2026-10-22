#!/usr/bin/env python3
"""Real 40-row Omega early-story draft integrity QA.

This checks source-vs-draft control codes and 35-codepoint segment limit.
It DOES NOT encode native E8xx glyphs, rebuild the ROM, or run an emulator.
"""
import csv
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "translation" / "P4_1_OMEGA_STORY_EARLY_DRAFTS.csv"
TOK = re.compile(r"\\xF000(?:(?!\\xF000|\\xFFFE|\\xFFFF).)*?\\x0000|\\x(?:FFFE|FFFF)", re.S)


def rows():
    with CSV.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


class P41DraftIntegrityTests(unittest.TestCase):
    def test_rows_unique_and_40_in_scope(self):
        data = list(rows())
        self.assertEqual(len(data), 40)
        ids = [(r["archive"], r["file_id"], r["message_id"]) for r in data]
        self.assertEqual(len(set(ids)), 40)
        self.assertTrue(all(r["archive"] == "story" for r in data))

    def test_control_codes_and_operands_preserved_in_order(self):
        for r in rows():
            with self.subTest(file_id=r["file_id"], message_id=r["message_id"]):
                self.assertEqual(
                    TOK.findall(r["original_english"]),
                    TOK.findall(r["draft_thai"]),
                )

    def test_all_thai_segments_max_35_codepoints(self):
        for r in rows():
            with self.subTest(file_id=r["file_id"], message_id=r["message_id"]):
                chunks = TOK.split(r["draft_thai"])
                max_codepoints = max(map(len, chunks), default=0)
                self.assertLessEqual(max_codepoints, 35)
                self.assertEqual(int(r["longest_codepoint_segment"]), max_codepoints)
                self.assertEqual(r["width_review"], "PIXEL_WIDTH_PENDING")

    def test_remain_drafts_not_fake_gameplay_approval(self):
        for r in rows():
            self.assertEqual(r["status"], "DRAFT_NEEDS_CONTEXT")
            self.assertEqual(r["ordered_control_codes"], "PASS")


if __name__ == "__main__":
    unittest.main()
