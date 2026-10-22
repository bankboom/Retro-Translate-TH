#!/usr/bin/env python3
"""Static QA for P4.2B, including previously missed non-zero F000 operands."""
import csv
import unittest
from pathlib import Path
from omega_control_tokens import tokens, max_visible_segment, visible_segments

ROOT=Path(__file__).resolve().parents[1] / "translation"
SOURCES=[
    ("P4_1_OMEGA_STORY_EARLY_DRAFTS.csv",40),
    ("P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv",19),
    ("P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv",8),
]


def read(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class P42BSafeControlQA(unittest.TestCase):
    def test_nonzero_operand_not_omitted(self):
        literal = r"MM: \xF000븉\x0001\x0001Hello\xF000븁\x0000\xFFFE"
        self.assertEqual(tokens(literal),
            (r"\xF000븉\x0001\x0001",r"\xF000븁\x0000",r"\xFFFE"))
        self.assertEqual(visible_segments(literal),["MM: ","Hello","",""])

    def test_no_f000_token_swallowing(self):
        literal = r"\xF000븉\x0001\x0000\xF000븁\x0000\xFFFF"
        self.assertEqual(tokens(literal),
            (r"\xF000븉\x0001\x0000",r"\xF000븁\x0000",r"\xFFFF"))

    def test_all_67_translation_drafts_keep_control_tokens(self):
        keys=set()
        for name,n in SOURCES:
            data=read(ROOT/name)
            self.assertEqual(len(data),n)
            for r in data:
                k=r["archive"],r["file_id"],r["message_id"]
                with self.subTest(name=name,key=k):
                    self.assertNotIn(k,keys)
                    keys.add(k)
                    self.assertEqual(tokens(r["original_english"]),tokens(r["draft_thai"]))
                    self.assertLessEqual(max_visible_segment(r["draft_thai"]),35)
                    self.assertEqual(int(r["longest_codepoint_segment"]),
                                     max_visible_segment(r["draft_thai"]))
                    self.assertEqual(r["status"],"DRAFT_NEEDS_CONTEXT")
        self.assertEqual(len(keys),67)

    def test_p42b_preserves_special_message_control(self):
        data=read(ROOT/SOURCES[-1][0])
        keys={(r["file_id"],r["message_id"]):r for r in data}
        for n in ("3","4","5","6","7"):
            x=keys[("21",n)]
            self.assertIn(r"\xF000븉\x0001\x0001",tokens(x["draft_thai"]))
            self.assertIn(r"\xF000븉\x0001\x0000",tokens(x["draft_thai"]))

if __name__ == "__main__":
    unittest.main()
