import hashlib
import struct
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mpds_adapter.nds import NDSFormatError, parse_header, parse_nitrofs, parse_overlay_tables


def make_minimal_rom():
    rom = bytearray(0x405)
    rom[0:12] = b"TESTGAME1234"
    rom[0x0C:0x10] = b"TST1"
    rom[0x10:0x12] = b"01"
    struct.pack_into("<I", rom, 0x20, 0x200)  # ARM9 offset
    struct.pack_into("<I", rom, 0x2C, 0x10)  # ARM9 size
    struct.pack_into("<I", rom, 0x30, 0x210)  # ARM7 offset
    struct.pack_into("<I", rom, 0x3C, 0x10)  # ARM7 size
    struct.pack_into("<II", rom, 0x40, 0x300, 0x10)  # FNT
    struct.pack_into("<II", rom, 0x48, 0x380, 8)  # FAT
    struct.pack_into("<II", rom, 0x50, 0x220, 32)  # ARM9 overlay table
    struct.pack_into("<8I", rom, 0x220, 7, 0x02345678, 0x100, 0, 0, 0, 0, 0)
    rom[0x200:0x210] = bytes(range(16))
    rom[0x210:0x220] = bytes(range(16, 32))
    # Root directory record: entry list at +8, first file id 0, one directory.
    struct.pack_into("<IHH", rom, 0x300, 8, 0, 1)
    rom[0x308:0x310] = bytes((5,)) + b"a.bin" + b"\x00\x00"
    struct.pack_into("<II", rom, 0x380, 0x400, 0x405)
    rom[0x400:0x405] = b"hello"
    return bytes(rom)


class NDSReaderTests(unittest.TestCase):
    def test_reads_header_identity_and_sections(self):
        data = make_minimal_rom()
        header = parse_header(data)
        self.assertEqual(header.title, "TESTGAME1234")
        self.assertEqual(header.game_code, "TST1")
        self.assertEqual(header.maker_code, "01")
        self.assertEqual(header.sections["fnt"], (0x300, 0x10))
        self.assertEqual(header.sections["arm9"], (0x200, 0x10))

    def test_lists_named_nitrofs_file_with_hash(self):
        files = parse_nitrofs(make_minimal_rom())
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].path, "a.bin")
        self.assertEqual(files[0].file_id, 0)
        self.assertEqual((files[0].start, files[0].end), (0x400, 0x405))
        self.assertEqual(files[0].sha256, hashlib.sha256(b"hello").hexdigest())

    def test_maps_arm9_overlay_descriptor_to_fat_id(self):
        overlays = parse_overlay_tables(make_minimal_rom())
        self.assertEqual(len(overlays), 1)
        self.assertEqual(overlays[0].cpu, "arm9")
        self.assertEqual(overlays[0].overlay_id, 7)
        self.assertEqual(overlays[0].file_id, 0)
        self.assertFalse(overlays[0].compressed)

    def test_rejects_malformed_overlay_table_or_file_id(self):
        data = bytearray(make_minimal_rom())
        struct.pack_into("<II", data, 0x50, 0x220, 31)
        with self.assertRaises(NDSFormatError):
            parse_overlay_tables(bytes(data))
        data = bytearray(make_minimal_rom())
        struct.pack_into("<I", data, 0x220 + 24, 1)
        with self.assertRaises(NDSFormatError):
            parse_overlay_tables(bytes(data))

    def test_rejects_out_of_bounds_sections_and_fat_entries(self):
        data = bytearray(make_minimal_rom())
        struct.pack_into("<II", data, 0x40, len(data) - 4, 0x20)
        with self.assertRaises(NDSFormatError):
            parse_header(bytes(data))
        data = bytearray(make_minimal_rom())
        struct.pack_into("<II", data, 0x380, 0x404, 0x410)
        with self.assertRaises(NDSFormatError):
            parse_nitrofs(bytes(data))

    def test_rejects_bad_directory_table(self):
        data = bytearray(make_minimal_rom())
        struct.pack_into("<IHH", data, 0x300, 0xFFFF, 0, 1)
        with self.assertRaises(NDSFormatError):
            parse_nitrofs(bytes(data))


if __name__ == "__main__":
    unittest.main()
