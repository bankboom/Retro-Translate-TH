import importlib.util
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
S = HERE / 'tools' / 'portable_code_probe.py'
spec = importlib.util.spec_from_file_location('probe', S)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

class PortableCodeProbeTests(unittest.TestCase):
    def test_arm_branch_bl(self):
        v = struct.pack('<II', 0xEB000001, 0xEAFFFFFD)
        a = probe.scan(v, mode='arm', base=0x02000000, start=0, end=8)
        self.assertEqual([r['candidate_kind'] for r in a], ['bl','b'])
        self.assertEqual(a[0]['candidate_target'], '0x0200000C')
        self.assertEqual(a[1]['candidate_target'], '0x02000000')

    def test_arm_literal(self):
        v = struct.pack('<III', 0xE59F0000, 0xE1A00000, 0x02345678)
        a = probe.scan(v, mode='arm', base=0x02000000, start=0, end=4)
        self.assertEqual(a[0]['candidate_kind'], 'ldr_pc_literal')
        self.assertEqual(a[0]['candidate_target'], '0x02345678')
        self.assertEqual(len(probe.scan(v, mode='arm', base=0x02000000,
                                        start=0, end=4, match_address=0x777)), 0)

    def test_thumb_bl_b_ldr(self):
        b = struct.pack('<HHHHI', 0xF000,0xF802,0xE7FD,0x4800,0x02345678)
        a = probe.scan(b, mode='thumb', base=0x02000000, start=0, end=8)
        self.assertEqual([r['candidate_kind'] for r in a], ['bl','b','ldr_pc_literal'])
        self.assertEqual(a[0]['candidate_target'], '0x02000008')
        self.assertEqual(a[2]['candidate_target'], '0x02345678')

    def test_adr_and_conditional_branch(self):
        arm = struct.pack('<I', 0xE28F0004)
        a = probe.scan(arm, mode='arm', base=0x02000000, start=0, end=4)
        self.assertEqual(a[0]['candidate_kind'], 'adr_pc')
        self.assertEqual(a[0]['candidate_target'], '0x0200000C')
        thumb = struct.pack('<H', 0xD0FE)
        t = probe.scan(thumb, mode='thumb', base=0x02000000, start=0, end=2)
        self.assertEqual(t[0]['candidate_kind'], 'b_cond')
        self.assertEqual(t[0]['candidate_target'], '0x02000000')

    def test_truncated_thumb_bl_not_overread_code_region(self):
        blob = struct.pack('<HH', 0xF000, 0xF802)
        self.assertEqual([], probe.scan(blob, mode='thumb', base=0, start=0, end=2))

    def test_reject_unsafe_ranges(self):
        cases=[dict(mode='arm',base=0,start=1,end=4),dict(mode='arm',base=0,start=0,end=6),
               dict(mode='thumb',base=0,start=0,end=50),dict(mode='mips',base=0,start=0,end=4),
               dict(mode='arm',base=0xFFFFFFFF,start=0,end=4)]
        for opts in cases:
            with self.subTest(opts=opts), self.assertRaises(ValueError):
                probe.scan(b'\0'*8,**opts)

    def test_no_external_package_cli_and_readonly(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'code.bin'; content=struct.pack('<II',0xEAFFFFFE,0)
            p.write_bytes(content)
            r=subprocess.run([sys.executable,str(S),'scan','--input',str(p),'--mode','arm',
                              '--base','0x2000000','--start','0','--end','4'],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(json.loads(r.stdout)['evidence_status'],'CANDIDATE_ONLY')
            self.assertEqual(p.read_bytes(),content)

if __name__=='__main__':
    unittest.main()
