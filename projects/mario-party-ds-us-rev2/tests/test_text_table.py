import struct
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mpds_adapter.text_table import TableFormatError, parse_table, serialize_table


def make_table(strings):
    count = len(strings)
    offset = 4 + count * 4
    offsets = []
    payload = bytearray()
    for value in strings:
        offsets.append(offset + len(payload))
        payload.extend(value.encode("utf-16le"))
        payload.extend(b"\x00\x00")
    return struct.pack("<I", count) + struct.pack(f"<{count}I", *offsets) + payload


class TextTableTests(unittest.TestCase):
    def test_parse_and_exact_no_change_roundtrip(self):
        raw = make_table(["Touch to start!", "เลือกไฟล์บันทึก", "A\nB"])
        table = parse_table(raw)
        self.assertEqual(table.strings, ("Touch to start!", "เลือกไฟล์บันทึก", "A\nB"))
        self.assertEqual(serialize_table(table), raw)

    def test_changed_rows_reserialize_and_parse(self):
        table = parse_table(make_table(["Start", "Exit"]))
        updated = ("เริ่ม", "Quit")
        rebuilt = serialize_table(table, updated)
        self.assertEqual(parse_table(rebuilt).strings, updated)

    def test_empty_table(self):
        raw = struct.pack("<I", 0)
        self.assertEqual(parse_table(raw).strings, ())
        self.assertEqual(serialize_table(parse_table(raw)), raw)

    def test_rejects_header_overlap_odd_and_out_of_bounds_offsets(self):
        with self.assertRaises(TableFormatError):
            parse_table(struct.pack("<II", 1, 4) + b"\x00\x00")
        with self.assertRaises(TableFormatError):
            parse_table(struct.pack("<II", 1, 9) + b"\x00\x00\x00\x00\x00\x00")
        with self.assertRaises(TableFormatError):
            parse_table(struct.pack("<II", 1, 12))

    def test_rejects_unterminated_or_invalid_utf16(self):
        unterminated = struct.pack("<II", 1, 8) + "A".encode("utf-16le")
        malformed = struct.pack("<II", 1, 8) + b"\x00\xD8\x00\x00"
        with self.assertRaises(TableFormatError):
            parse_table(unterminated)
        with self.assertRaises(TableFormatError):
            parse_table(malformed)

    def test_rejects_embedded_nul_when_rebuilding(self):
        table = parse_table(make_table(["OK"]))
        with self.assertRaises(TableFormatError):
            serialize_table(table, ("bad\x00text",))


if __name__ == "__main__":
    unittest.main()
