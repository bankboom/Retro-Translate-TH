import csv
import hashlib
import zlib
import struct
import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from regression_guard import audit, ranges_from, evaluate
from quality_queue import make_queue, inspect
from font_review_plan import choose
from release_audit import audit_project


class GuardTests(unittest.TestCase):
    def test_no_change_passes(self):
        r=audit(b'hello',b'hello')
        self.assertEqual(r['scope_status'],'PASS')
        self.assertEqual(r['visual_qa'],'PENDING')
    def test_without_policy_requires_approval(self):
        r=audit(b'abcde',b'abzde')
        self.assertEqual(r['scope_status'],'PENDING')
        self.assertEqual(r['changed_bytes'],1)
    def test_in_scope_only(self):
        r=audit(b'abcde',b'abzde',{'allowed_changes':[{'start':'0x2','end_exclusive':'0x3','reason':'approved glyph trial'}]})
        self.assertEqual(r['scope_status'],'PASS')
        self.assertEqual(r['changed_regions'],1)
    def test_outside_scope_fails(self):
        p={'allowed_changes':[{'start':0,'end_exclusive':1,'reason':'small header'}]}
        self.assertEqual(audit(b'abc',b'abx',p)['scope_status'],'FAIL')
    def test_protected_overrides_allow(self):
        p={'allowed_changes':[{'start':1,'end_exclusive':3,'reason':'approved'}],
           'protected_ranges':[{'start':2,'end_exclusive':3}]}
        self.assertEqual(audit(b'abc',b'abX',p)['reason'],'PROTECTED_RANGE_CHANGED')
    def test_size_or_hash_fail(self):
        self.assertEqual(audit(b'a',b'aa')['scope_status'],'FAIL')
        self.assertEqual(audit(b'a',b'b',{'expected_baseline_sha256':'wrong'})['scope_status'],'FAIL')
    def test_bad_ranges_fail(self):
        with self.assertRaises(ValueError): audit(b'abc',b'axc',{'allowed_changes':[{'start':2,'end_exclusive':1,'reason':'bad'}]})
        with self.assertRaises(ValueError): audit(b'abc',b'axc',{'allowed_changes':[{'start':1,'end_exclusive':2}]})


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def make(self,name,rows):
        p=self.root/name
        with p.open('w',newline='',encoding='utf8') as f:
            w=csv.DictWriter(f,fieldnames=['Bank','ID','English','Thai','TranslationStatus','Context_Key'])
            w.writeheader();w.writerows(rows)
        return p
    def test_deltas_only_and_bounded(self):
        earlier=self.make('old.csv',[{'Bank':'main','ID':'1','English':'OK','Thai':'ตกลง','TranslationStatus':'REVIEWED'},
                                     {'Bank':'main','ID':'2','English':'Charge','Thai':'','TranslationStatus':'DRAFT'}])
        now=self.make('new.csv',[{'Bank':'main','ID':'1','English':'OK','Thai':'ตกลง','TranslationStatus':'REVIEWED'},
                                 {'Bank':'main','ID':'2','English':'Charge','Thai':'ชาร์จ','TranslationStatus':'DRAFT'},
                                 {'Bank':'main','ID':'3','English':'HP {name}: 50','Thai':'HP: 40','TranslationStatus':'DRAFT'}])
        q,s=make_queue(now,earlier,1)
        self.assertEqual(s['unchanged_skipped'],1)
        self.assertEqual(s['delta_rows'],2)
        self.assertEqual(s['returned_rows'],1)
        self.assertEqual(s['remaining_risk_rows'],1)
        self.assertEqual(q[0]['Priority'],'HIGH')
    def test_reviewed_good_not_queued(self):
        f=self.make('t.csv',[{'ID':'1','English':'Hello','Thai':'สวัสดี','TranslationStatus':'REVIEWED'}])
        q,_=make_queue(f)
        self.assertEqual(q,[])
    def test_duplicate_ids_rejected(self):
        f=self.make('duplicate.csv',[{'ID':'1'},{'ID':'1'}])
        with self.assertRaises(ValueError):make_queue(f)
    def test_numeric_difference_flagged(self):
        self.assertIn('NUMERIC_DIFFERENCE_REVIEW',inspect({'English':'HP 40','Thai':'พลังชีวิต 50','TranslationStatus':'REVIEWED'})['Issues'])

class FontTests(unittest.TestCase):
    def test_plan_only(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'master.csv'
            f.write_text('ID,Thai,Scene\n1,น้ำ,Menu\n2,เก่ง,Talk\n3,ตุ๊กตา,Menu\n',encoding='utf8')
            rows,s=choose(f)
            self.assertGreater(len(rows),0)
            self.assertTrue(all(r['Visual_Result']=='PENDING' for r in rows))
            self.assertEqual(s['status'],'PENDING_VISUAL')

class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'qa').mkdir();(self.root/'patches').mkdir()
        source=b'abc';target=b'xyz'
        self.valid_bps=(b'BPS1'+bytes([0x83,0x83,0x80,0x89])+target)
        self.valid_bps+=struct.pack('<II',zlib.crc32(source),zlib.crc32(target))
        self.valid_bps+=struct.pack('<I',zlib.crc32(self.valid_bps))
        (self.root/'patches/a.bps').write_bytes(self.valid_bps)
    def tearDown(self):self.tmp.cleanup()
    def write(self,entry):
        (self.root/'qa/gates.json').write_text(json.dumps({'gates':entry}),encoding='utf8')
    def test_empty_blocked(self):
        self.write({})
        r=audit_project(self.root)
        self.assertEqual(r['decision'],'BLOCKED')
        self.assertEqual(r['g5'],'PENDING')
    def test_ready_is_not_pass(self):
        (self.root/'qa/real_scene.png').write_bytes(b'file-for-test-only')
        self.write({g:{'status':'PASS','reviewer':'someone','evidence':['qa/real_scene.png']} for g in ['G0','G1','G2','G3','G4']})
        (self.root/'qa/release_manifest.json').write_text(json.dumps({
            'build_id':'test','clean_rom_sha256':'a'*64,'patch_sha256':hashlib.sha256(self.valid_bps).hexdigest(),
            'patch_path':'patches/a.bps','patch_format':'BPS','rollback':'previous stable'}),encoding='utf8')
        r=audit_project(self.root)
        self.assertEqual(r['decision'],'READY_FOR_MANUAL_RELEASE_REVIEW')
        self.assertEqual(r['g5'],'PENDING')
        self.assertTrue(r['manifest']['bps_patch_crc_valid'])
    def test_invalid_bps_rejected_even_with_matching_hash(self):
        path=self.root/'patches/a.bps';path.write_bytes(b'fake-test')
        (self.root/'qa/release_manifest.json').write_text(json.dumps({
            'build_id':'bad', 'clean_rom_sha256':'a'*64,
            'patch_sha256':hashlib.sha256(b'fake-test').hexdigest(),
            'patch_path':'patches/a.bps','patch_format':'BPS','rollback':'stable'}))
        self.write({g:{'status':'PASS','reviewer':'human','evidence':['patches/a.bps']} for g in ['G0','G1','G2','G3','G4']})
        self.assertIn('INVALID_BPS_FILE',audit_project(self.root)['blockers'])
    def test_escape_evidence_rejected(self):
        self.write({'G0':{'status':'PASS','reviewer':'x','evidence':['../../outside']}})
        self.assertIn('G0: EVIDENCE_OUTSIDE_PROJECT',audit_project(self.root)['blockers'])

if __name__=='__main__':unittest.main()
