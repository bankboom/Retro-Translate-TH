import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "portable_code_probe.py"
spec = importlib.util.spec_from_file_location("portable_code_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class TestOfflineCodeProbe(unittest.TestCase):
    def test_arm_branch(self):
        b = struct.pack("<II", 0xEB000001, 0xEAFFFFFD)
        result = probe.scan(b, mode="arm", base=0x02000000, start=0, end=8)
        self.assertEqual([v["candidate_kind"] for v in result], ["bl", "b"])
        self.assertEqual(result[0]["candidate_target"], "0x0200000C")
        self.assertEqual(result[1]["candidate_target"], "0x02000000")

    def test_arm_literal_adr(self):
        b = struct.pack("<III", 0xE59F0000, 0xE28F0004, 0x02345678)
        result = probe.scan(b, mode="arm", base=0x02000000, start=0, end=8)
        self.assertEqual(result[0]["candidate_target"], "0x02345678")
        self.assertEqual(result[1]["candidate_kind"], "adr_pc")

    def test_thumb(self):
        b = struct.pack("<HHHHI", 0xF000, 0xF802, 0xE7FD, 0x4800, 0x02345678)
        result = probe.scan(b, mode="thumb", base=0x02000000, start=0, end=8)
        self.assertEqual([r["candidate_kind"] for r in result], ["bl", "b", "ldr_pc_literal"])
        self.assertEqual(result[-1]["candidate_target"], "0x02345678")

    def test_reject_invalid(self):
        for mode, base, start, end in [("arm", 0, 1, 4), ("arm", 0, 0, 6),
                                      ("thumb", 0, 0, 100), ("mips", 0, 0, 4),
                                      ("arm", 0xFFFFFFFF, 0, 4)]:
            with self.subTest(mode=mode, start=start), self.assertRaises(ValueError):
                probe.scan(bytes(8), mode=mode, base=base, start=start, end=end)

    def test_cli_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "sample.bin"
            original = struct.pack("<II", 0xEAFFFFFE, 0)
            p.write_bytes(original)
            process = subprocess.run([sys.executable, str(SCRIPT), "scan", "--input", str(p),
                                     "--mode", "arm", "--base", "0x02000000",
                                     "--start", "0", "--end", "4"],
                                     capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(process.stdout)["evidence_status"], "CANDIDATE_ONLY")
            self.assertEqual(p.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
