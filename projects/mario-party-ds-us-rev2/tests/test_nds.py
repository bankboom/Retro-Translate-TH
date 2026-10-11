import hashlib
import struct
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mpds_adapter.nds import NDSFormatError, parse_header, parse_nitrofs, parse_overlay_tables
from mpds_adapter.rebuild import RebuildError, _crc16_header, replace_nitro_file

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from retro_translate_v3 import apply_bps


def bps_target_read(source, target):
    """Build a simple valid BPS patch used only by synthetic tests."""
    import zlib

    def varint(value):
        out = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value == 0:
                out.append(byte | 0x80)
                return bytes(out)
            out.append(byte)
            value -= 1

    commands = varint(((len(target) - 1) << 2) | 1) + target
    body = b"BPS1" + varint(len(source)) + varint(len(target)) + varint(0) + commands
    trailer = struct.pack("<II", zlib.crc32(source), zlib.crc32(target))
    return body + trailer + struct.pack("<I", zlib.crc32(body + trailer))


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


def make_two_file_rom():
    rom = bytearray(0x40B)
    base = make_minimal_rom()
    rom[: len(base)] = base
    struct.pack_into("<II", rom, 0x40, 0x300, 0x18)  # FNT with two root files
    struct.pack_into("<II", rom, 0x48, 0x380, 16)  # FAT with two entries
    struct.pack_into("<IHH", rom, 0x300, 8, 0, 1)
    rom[0x308:0x315] = bytes((5,)) + b"a.bin" + bytes((5,)) + b"b.bin" + b"\x00"
    struct.pack_into("<IIII", rom, 0x380, 0x400, 0x405, 0x408, 0x40B)
    rom[0x405:0x408] = b"\xAA\xBB\xCC"
    rom[0x408:0x40B] = b"xyz"
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

    def test_size_changing_file_rebuild_updates_fat_without_mutating_source(self):
        source = make_two_file_rom()
        original_prefix = source[:0x80] + source[0x84:0x15E] + source[0x160:0x380]
        rebuilt = replace_nitro_file(source, 0, b"1234567890123456")

        files = parse_nitrofs(rebuilt)
        self.assertEqual(
            rebuilt[:0x80] + rebuilt[0x84:0x15E] + rebuilt[0x160:0x380],
            original_prefix,
        )
        self.assertEqual(rebuilt[files[0].start : files[0].end], b"1234567890123456")
        self.assertEqual((files[0].start, files[0].end), (0x400, 0x410))
        self.assertEqual((files[1].start, files[1].end), (0x414, 0x417))
        self.assertEqual(rebuilt[files[1].start : files[1].end], b"xyz")
        self.assertEqual(struct.unpack_from("<I", rebuilt, 0x80)[0], len(rebuilt))
        self.assertEqual(source, make_two_file_rom())
        self.assertEqual(struct.unpack_from("<H", rebuilt, 0x15E)[0], _nds_header_crc(rebuilt[:0x15E]))

    def test_nds_header_crc_uses_crc16_ibm_known_vector(self):
        self.assertEqual(_crc16_header(b"123456789"), 0x4B37)

    def test_synthetic_bps_apply_and_reverse_restore_exact_rebuild_baseline(self):
        clean = make_two_file_rom()
        rebuilt = replace_nitro_file(clean, 0, b"expanded payload")
        forward, _ = apply_bps(clean, bps_target_read(clean, rebuilt))
        rollback, _ = apply_bps(forward, bps_target_read(rebuilt, clean))
        self.assertEqual(forward, rebuilt)
        self.assertEqual(rollback, clean)

    def test_rebuild_rejects_unknown_id_and_metadata_overlapping_files(self):
        source = make_minimal_rom()
        with self.assertRaises(RebuildError):
            replace_nitro_file(source, 4, b"nope")
        overlapping = bytearray(source)
        struct.pack_into("<II", overlapping, 0x20, 0x400, 1)
        with self.assertRaises(RebuildError):
            replace_nitro_file(bytes(overlapping), 0, b"unsafe")
        dsi = bytearray(source)
        dsi[0x12] = 2
        with self.assertRaises(RebuildError):
            replace_nitro_file(bytes(dsi), 0, b"unsafe")


def _nds_header_crc(header):
    crc = 0xFFFF
    for byte in header:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc & 0xFFFF


if __name__ == "__main__":
    unittest.main()
