#!/usr/bin/env python3
"""Synthetic guard tests for exact source/PUA donor reuse, never actual ROM QA."""
import unittest
from p53_white_native_segment_reuse import make_index, audit, native_len, english_len

def donor(src, thai, *, archive="story", file_id="1", message_id="2"):
    return dict(archive=archive,file_id=file_id,message_id=message_id,
                white_english=src,white_thai_pua_text=thai)

def draft(src, *, archive="story", file_id="1", message_id="3"):
    return dict(archive=archive,file_id=file_id,message_id=message_id,
                original_english=src,draft_thai=src)

class NativeWhitePhraseReuseTests(unittest.TestCase):
    def test_native_unit_count(self):
        self.assertEqual(native_len(r"\xE800\xE801 hi"), 5)
        self.assertIsNone(native_len(r"\x0E01"))   # raw Unicode Thai not PUA
        self.assertIsNone(native_len("ไทย"))
        self.assertIsNone(native_len(r"\xF000"))   # not a visible glyph
        self.assertEqual(english_len("Hello"),5)
        self.assertIsNone(english_len("Pokémon"))

    def test_1_exact_same_bank_within_capacity_stays_review_only(self):
        result,summary=audit([donor("Hello",r"\xE800\xE801")],
                             [draft("Hello")])
        self.assertEqual(result[0]["donor_review_segments"],1)
        self.assertEqual(result[0]["full_message_status"],
                         "ALL_EXACT_DONORS_HOLD_FOR_CONTEXT_AND_PIXEL")
        self.assertFalse(result[0]["rom_injected"])
        self.assertFalse(result[0]["emulator_verified"])
        self.assertEqual(summary["all_segments_have_donor_pending_context"],1)

    def test_cross_bank_cannot_supply_glyph(self):
        result,_=audit([donor("Hello",r"\xE800")],
                       [draft("Hello",file_id="44")])
        self.assertEqual(result[0]["donor_review_segments"],0)
        self.assertIn("NO_EXACT_SAME_BANK_DONOR",result[0]["segments"])

    def test_same_bank_different_message_id_allowed_for_review(self):
        result,_=audit([donor("Hello",r"\xE800")],
                       [draft("Hello",message_id="100")])
        self.assertEqual(result[0]["donor_review_segments"],1)

    def test_conflicting_native_variants_get_held(self):
        a=donor("Hello",r"\xE800")
        b=donor("Hello",r"\xE801",message_id="5")
        result,summary=audit([a,b],[draft("Hello")])
        self.assertIn("AMBIGUOUS_NATIVE_VARIANTS",result[0]["segments"])
        self.assertEqual(summary["ambiguous_bank_phrase_keys"],1)
        self.assertEqual(result[0]["donor_review_segments"],0)

    def test_control_sequence_change_in_master_is_rejected(self):
        src=r"Hello\xFFFEfriend"
        bad=r"\xE800\xF000븁\x0000\xE801"
        index,stats=make_index([donor(src,bad)])
        self.assertFalse(index)
        self.assertEqual(stats["rejected_control"],1)

    def test_segmentation_with_commands_tracks_each_visible_part(self):
        src=r"Hello\xFFFEfriend\xF000븁\x0000"
        tgt=r"\xE800\xFFFE\xE801\xF000븁\x0000"
        result,summary=audit([donor(src,tgt)],[draft(src)])
        self.assertEqual(summary["omega_visible_segments"],2)
        self.assertEqual(result[0]["donor_review_segments"],2)

    def test_native_phrase_longer_than_original_slot_gets_held(self):
        result,_=audit([donor("Hi",r"\xE800\xE801\xE802")],[draft("Hi")])
        self.assertIn("NATIVE_EXCEEDS_FIXED_SLOT",result[0]["segments"])

    def test_reject_duplicate_target_id(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            audit([],[draft("Hello"),draft("Hello")])

    def test_reject_inconsistent_draft_control(self):
        x=draft(r"Hello\xFFFEfriend")
        x["draft_thai"]="สวัสดี"
        with self.assertRaisesRegex(ValueError,"control change"):
            audit([],[x])

    def test_incomplete_coverage_never_marked_ready(self):
        src=r"Hello\xFFFEunknown"
        result,_=audit([donor("Hello",r"\xE800")],[draft(src)])
        self.assertEqual(result[0]["donor_review_segments"],1)
        self.assertEqual(result[0]["full_message_status"],
                         "INCOMPLETE_EXACT_DONOR_COVERAGE")

if __name__=="__main__":
    unittest.main()
