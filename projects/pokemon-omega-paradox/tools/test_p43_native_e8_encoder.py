#!/usr/bin/env python3
"""Synthetic tests only — no source ROM, screenshot or emulator exercised."""
import csv
import tempfile
import unittest
from pathlib import Path

from p43_native_e8_encoder import (
    MappingRequired, load_verified_map, encode_visible, encode_message,
    decode_visible, preflight_csv
)
from omega_control_tokens import tokens


def csv_write(path, header, records):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(records)


FIELDS = ["renderer", "thai", "native_units", "evidence_build",
          "evidence_scene", "review_state"]
GOOD = {
    "renderer": "system_44_dialogue", "thai": "สวัสดี",
    "native_units": r"\xE801\xE802", "evidence_build": "TEST_PROVEN",
    "evidence_scene": "TEST_SCREEN", "review_state": "IN_GAME_VERIFIED"
}


class NativeE8EncoderTests(unittest.TestCase):
    def test_blocks_arbitrary_unicode_thai(self):
        with self.assertRaises(MappingRequired):
            encode_visible("สวัสดี", {})

    def test_only_verified_map_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            fn=Path(d)/"map.csv"
            csv_write(fn,FIELDS,[dict(GOOD,review_state="DRAFT")])
            self.assertEqual(load_verified_map(fn,"system_44_dialogue"),{})

    def test_other_renderer_mapping_is_not_reused(self):
        with tempfile.TemporaryDirectory() as d:
            fn=Path(d)/"map.csv"
            csv_write(fn,FIELDS,[dict(GOOD,renderer="battle_font")])
            self.assertEqual(load_verified_map(fn,"system_44_dialogue"),{})

    def test_roundtrip_verified_sequence_and_ascii(self):
        text="สวัสดี Drake."
        native=encode_visible(text, {"สวัสดี": r"\xE801\xE802"})
        self.assertEqual(native, r"\xE801\xE802 Drake.")
        self.assertEqual(decode_visible(native,{"สวัสดี":r"\xE801\xE802"}),text)

    def test_controls_not_modified(self):
        source=r"สวัสดี\xF000븉\x0001\x0001 Drake.\xFFFEสวัสดี\xF000븁\x0000"
        native=encode_message(source,{"สวัสดี":r"\xE801\xE802"})
        self.assertEqual(tokens(source),tokens(native))
        self.assertEqual(native,
                         r"\xE801\xE802\xF000븉\x0001\x0001 Drake.\xFFFE\xE801\xE802\xF000븁\x0000")

    def test_conflicting_map_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fn=Path(d)/"map.csv"
            csv_write(fn,FIELDS,[GOOD,dict(GOOD,native_units=r"\xE812")])
            with self.assertRaisesRegex(ValueError, "conflicting"):
                load_verified_map(fn,"system_44_dialogue")

    def test_invalid_e8_code_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            fn=Path(d)/"map.csv"
            csv_write(fn,FIELDS,[dict(GOOD,native_units=r"\xE012")])
            with self.assertRaisesRegex(ValueError, "invalid native"):
                load_verified_map(fn,"system_44_dialogue")

    def test_preflight_keeps_drafts_pending(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            m=p/"mapping.csv"
            source=p/"drafts.csv"
            csv_write(m,FIELDS,[GOOD])
            csv_write(source,["archive","file_id","message_id",
                              "original_english","draft_thai","status"],[
                dict(archive="system",file_id="44",message_id="6",
                     original_english=r"Hello!\xF000븁\x0000",
                     draft_thai=r"สวัสดี\xF000븁\x0000",
                     status="DRAFT_NEEDS_CONTEXT"),
            ])
            result=preflight_csv(source,m,"system_44_dialogue",p/"audit.json")
            self.assertEqual(result["rows_checked"],1)
            self.assertEqual(result["encoding_ready"],0)
            self.assertEqual(result["block_reasons"],{"CONTEXT_NOT_REVIEWED":1})
            self.assertFalse(result["bps_created"])

    def test_approved_draft_with_verified_map_clears_static_gate_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            m=p/"mapping.csv"
            source=p/"drafts.csv"
            csv_write(m,FIELDS,[GOOD])
            csv_write(source,["archive","file_id","message_id",
                              "original_english","draft_thai","status"],[
                dict(archive="system",file_id="44",message_id="6",
                     original_english=r"Hello!\xF000븁\x0000",
                     draft_thai=r"สวัสดี\xF000븁\x0000",status="REVIEWED")
            ])
            result=preflight_csv(source,m,"system_44_dialogue",p/"audit.json")
            self.assertEqual(result["encoding_ready"],1)
            self.assertFalse(result["rom_modified"])

    def test_unknown_glyph_fails_even_when_reviewed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);m=p/"mapping.csv";source=p/"drafts.csv"
            csv_write(m,FIELDS,[GOOD])
            csv_write(source,["archive","file_id","message_id",
                              "original_english","draft_thai","status"],[
                dict(archive="system",file_id="44",message_id="6",
                     original_english="Hello",draft_thai="สวัสดีค่ะ",
                     status="REVIEWED")
            ])
            result=preflight_csv(source,m,"system_44_dialogue",p/"audit.json")
            self.assertEqual(result["block_reasons"],{"MISSING_VERIFIED_GLYPH":1})


if __name__ == "__main__":
    unittest.main()
