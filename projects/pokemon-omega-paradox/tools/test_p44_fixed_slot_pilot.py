"""Synthetic fixed-slot smoke tests. Not ROM/emulator test evidence."""
import unittest
from p44_fixed_slot_pilot import UnsafePilot, prepare_fixed_slot, _parts, _len_native
from omega_control_tokens import tokens


def case(source="She is flighty,\\xFFFEbut works hard.\\xF000븁\\x0000",
         native="\\xE801\\xE802\\xFFFE\\xE803\\xE804\\xF000븁\\x0000"):
    return dict(archive="system", file_id="44", message_id="24",
        original_english=source, native_reference=native,
        renderer="system_44_dialogue",
        reference_rom_sha256="a"*64, reference_archive="system",
        reference_file_id="44", reference_message_id="24",
        evidence_state="REFERENCE_EXTRACTED")


class FixedSlotTests(unittest.TestCase):
    def test_smoke_prepares_fixed_capacity_without_rom(self):
        row = case()
        result = prepare_fixed_slot(row)
        self.assertEqual(result["capacities_in_codeunits"],[14,15,0])
        self.assertEqual(result["native_used_codeunits"],[2,2,0])
        self.assertEqual(tokens(result["escaped_fixed_slot_message"]),
                         tokens(row["original_english"]))
        self.assertFalse(result["bps_created"])

    def test_control_operand_mutation_rejected(self):
        row=case(native="\\xE801\\xFFFE\\xE802\\xF000븀\\x0000")
        with self.assertRaisesRegex(UnsafePilot,"CONTROL_OPCODE"):
            prepare_fixed_slot(row)

    def test_native_too_long_for_fixed_segment_rejected(self):
        row=case(source="A\\xFFFEGo!\\xF000븁\\x0000",
                 native="\\xE801\\xE802\\xFFFE\\xE803\\xF000븁\\x0000")
        with self.assertRaisesRegex(UnsafePilot,"EXCEEDS"):
            prepare_fixed_slot(row)

    def test_literal_unicode_thai_never_injected(self):
        with self.assertRaisesRegex(UnsafePilot,"INVALID_OR_UNPROVEN"):
            prepare_fixed_slot(case(native="เธอ\\xFFFE\\xE801\\xF000븁\\x0000"))

    def test_literal_unknown_escape_never_injected(self):
        with self.assertRaisesRegex(UnsafePilot,"INVALID_OR_UNPROVEN"):
            prepare_fixed_slot(case(native="\\xE012\\xFFFE\\xE801\\xF000븁\\x0000"))

    def test_source_non_ascii_requires_real_decoder(self):
        with self.assertRaisesRegex(UnsafePilot,"SOURCE_NON_ASCII"):
            prepare_fixed_slot(case(source="Pokémon\\xFFFEGood!\\xF000븁\\x0000"))

    def test_evidence_placeholder_is_not_accepted(self):
        with self.assertRaisesRegex(UnsafePilot,"REFERENCE_NOT_EXTRACTED"):
            prepare_fixed_slot(case() | dict(evidence_state="DRAFT"))

    def test_cross_renderer_and_cross_bank_rejected(self):
        with self.assertRaisesRegex(UnsafePilot,"WRONG_RENDERER"):
            prepare_fixed_slot(case() | dict(renderer="battle_font"))
        with self.assertRaisesRegex(UnsafePilot,"REFERENCE_BANK"):
            prepare_fixed_slot(case() | dict(reference_file_id="54"))

    def test_nonzero_operand_preserved(self):
        original="MM: \\xF000븉\\x0001\\x0001Hello\\xFFFEGo.\\xF000븉\\x0001\\x0000"
        native="MM: \\xF000븉\\x0001\\x0001\\xE801\\xFFFE\\xE802\\xF000븉\\x0001\\x0000"
        out=prepare_fixed_slot(case(source=original,native=native))
        self.assertEqual(tokens(out["escaped_fixed_slot_message"]),tokens(original))

    def test_missing_reference_provenance_rejected(self):
        with self.assertRaisesRegex(UnsafePilot,"MISSING_REFERENCE"):
            prepare_fixed_slot(case() | dict(reference_rom_sha256=""))

    def test_no_e8_glyph_rejected(self):
        with self.assertRaisesRegex(UnsafePilot,"NO_NATIVE_E8"):
            prepare_fixed_slot(case(native="Hello\\xFFFEWorld!\\xF000븁\\x0000"))

    def test_control_token_positions_same_in_codeunits(self):
        r=prepare_fixed_slot(case())
        source_parts,_=_parts(case()["original_english"])
        out_parts,_=_parts(r["escaped_fixed_slot_message"])
        self.assertEqual([len(x) for x in source_parts],
                         [_len_native(x) for x in out_parts])


if __name__=="__main__":
    unittest.main()
