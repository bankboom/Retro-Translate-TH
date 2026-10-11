from contextlib import redirect_stderr
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from mpds_adapter.cli import _bank_for_path, _write_new_json, main


class CLISafetyTests(unittest.TestCase):
    def test_existing_master_bank_mapping_is_preserved(self):
        self.assertEqual(_bank_for_path("data/US/mpd_010_main_manu_LZ.bin"), "US_MAIN_MENU")

    def test_inventory_refuses_wrong_game_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rom = bytearray(0x200)
            rom[0:12] = b"NOTMARIO1234"
            rom[0x0C:0x10] = b"NOPE"
            rom[0x10:0x12] = b"01"
            rom_bytes = bytes(rom)
            rom_path = root / "wrong.nds"
            rom_path.write_bytes(rom_bytes)
            profile = {
                "source_rom": {
                    "size_bytes": len(rom_bytes),
                    "observed_sha256": hashlib.sha256(rom_bytes).hexdigest(),
                    "expected_clean_sha1": hashlib.sha1(rom_bytes).hexdigest(),
                    "expected_clean_crc32": f"{zlib.crc32(rom_bytes) & 0xFFFFFFFF:08X}",
                }
            }
            profile_path = root / "profile.json"
            profile_path.write_text(json.dumps(profile), encoding="utf-8")
            output = root / "inventory.json"
            with redirect_stderr(io.StringIO()):
                result = main(["inventory", str(rom_path), "--output", str(output), "--profile", str(profile_path)])
            self.assertEqual(result, 2)
            self.assertFalse(output.exists())

    def test_report_writer_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "report.json"
            target.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                _write_new_json(target, {"new": True})
            self.assertEqual(target.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
