from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from mpds_adapter.mpds_lz import LZFormatError, compress, decompress


class MPDSLZTests(unittest.TestCase):
    def test_known_literal_and_back_reference_vector(self):
        # Header byte is opaque; flags are read most-significant bit first.
        source = bytes((0x10, 8, 0, 0, 0x20, ord("A"), ord("B"), 0x30, 0x01))
        self.assertEqual(decompress(source), b"ABABABAB")

    def test_roundtrip_preserves_unknown_header_byte(self):
        raw = (b"ABRACADABRA " * 30) + bytes(range(64))
        encoded = compress(raw, header_byte=0x77)
        self.assertEqual(encoded[0], 0x77)
        self.assertEqual(decompress(encoded), raw)

    def test_repeated_data_uses_back_references_within_flag_group(self):
        raw = b"A" * 96
        encoded = compress(raw)
        self.assertLess(len(encoded), 32)
        self.assertEqual(decompress(encoded), raw)

    def test_empty_payload_roundtrip(self):
        encoded = compress(b"", header_byte=0xA5)
        self.assertEqual(encoded, bytes((0xA5, 0, 0, 0)))
        self.assertEqual(decompress(encoded), b"")

    def test_rejects_reference_before_output(self):
        encoded = bytes((0x10, 3, 0, 0, 0x80, 0x00, 0x00))
        with self.assertRaises(LZFormatError):
            decompress(encoded)

    def test_rejects_truncated_literal_and_reference(self):
        with self.assertRaises(LZFormatError):
            decompress(bytes((0x10, 1, 0, 0, 0x00)))
        with self.assertRaises(LZFormatError):
            decompress(bytes((0x10, 3, 0, 0, 0x80, 0x00)))

    def test_enforces_output_limit_before_allocation(self):
        with self.assertRaises(LZFormatError):
            decompress(bytes((0x10, 0, 0, 1)), max_output_size=1024)


if __name__ == "__main__":
    unittest.main()
