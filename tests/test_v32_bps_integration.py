import csv
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from regression_guard import evaluate


def v(value):
    arr=[]
    while True:
        b=value & 127;value >>= 7
        if not value:return bytes(arr+[b|128])
        arr.append(b);value-=1


def make_patch(src,target):
    command=v(((len(target)-1)<<2)|1)+target
    data=bytearray(b'BPS1'+v(len(src))+v(len(target))+v(0)+command)
    data.extend(struct.pack('<II',zlib.crc32(src),zlib.crc32(target)))
    data.extend(struct.pack('<I',zlib.crc32(data)))
    return bytes(data)

class BPSGuardIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.dir=Path(self.tmp.name)
        self.clean=self.dir/'clean.nds';self.clean.write_bytes(b'12345')
        self.stable=self.dir/'stable.bps';self.stable.write_bytes(make_patch(b'12345',b'aBCDE'))
        self.candidate=self.dir/'candidate.bps';self.candidate.write_bytes(make_patch(b'12345',b'aBzDE'))
        self.policy=self.dir/'scope.json';self.policy.write_text(json.dumps({'allowed_changes':[{'start':2,'end_exclusive':3,'reason':'test glyph'}]}))
    def tearDown(self):self.tmp.cleanup()
    def test_bps_source_target_integrity_and_scope(self):
        d=evaluate(None,None,self.clean,self.stable,self.candidate,self.policy)
        self.assertEqual(d['scope_status'],'PASS')
        self.assertTrue(d['candidate_patch_crc_valid'])
        self.assertEqual(d['changed_bytes'],1)
    def test_mismatched_clean_rom_fails(self):
        self.clean.write_bytes(b'54321')
        with self.assertRaises(ValueError):evaluate(None,None,self.clean,self.stable,self.candidate,self.policy)
    def test_cli_smoke(self):
        dest=self.dir/'report.json'
        cmd=[sys.executable,str(ROOT/'tools/regression_guard.py'),'--clean-rom',str(self.clean),
             '--baseline-patch',str(self.stable),'--candidate-patch',str(self.candidate),
             '--policy',str(self.policy),'--output',str(dest)]
        p=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(dest.read_text())['changed_bytes'],1)
        p2=subprocess.run(cmd,capture_output=True,text=True)
        self.assertEqual(p2.returncode,2)
    def test_quality_queue_cli(self):
        master=self.dir/'master.csv'
        with master.open('w',encoding='utf8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['Bank','ID','English','Thai','TranslationStatus'])
            w.writeheader();w.writerow(dict(Bank='main',ID='1',English='Hello {name}',Thai='สวัสดี',TranslationStatus='DRAFT'))
        p=subprocess.run([sys.executable,str(ROOT/'tools/quality_queue.py'), '--csv',str(master),
                          '--output',str(self.dir/'q.csv'), '--limit','5'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['high_risk'],1)

if __name__=='__main__':unittest.main()
