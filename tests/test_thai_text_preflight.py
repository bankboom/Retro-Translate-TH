import tempfile
import unittest
from pathlib import Path
from tools.thai_text_preflight import analyze

class PreflightTests(unittest.TestCase):
    def sample(self, contents, **kw):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sample.tsv'
            p.write_text(contents,encoding='utf-8')
            return analyze(p,**kw)

    def test_clean(self):
        r=self.sample('id\tsource\tthai\n1\tSave {0}\\nNext\tบันทึก {0}\\nต่อไป\n')
        self.assertEqual(r['issues'],[])

    def test_tokens(self):
        r=self.sample('id\tsource\tthai\n1\tHP {0} <b>\tพลังชีวิต {1} <b>\n')
        self.assertIn('CONTROL_TOKEN_MISMATCH',[i['code'] for i in r['issues']])

    def test_duplicate(self):
        r=self.sample('id\tsource\tthai\n1\tSave\tบันทึก\n1\tLoad\tโหลด\n')
        self.assertIn('MISSING_OR_DUPLICATE_ID',[i['code'] for i in r['issues']])

    def test_unknown_pixels(self):
        r=self.sample('id\tsource\tthai\n1\tStart\tเริ่ม\n',max_pixels=50)
        self.assertEqual(r['unmeasured_lines'],1)

    def test_pixel_estimate(self):
        r=self.sample('id\tsource\tthai\n1\tStart\tกก\n',advances={'ก':10},max_pixels=15)
        self.assertIn('PIXEL_ADVANCE_ESTIMATE_EXCEEDED',[i['code'] for i in r['issues']])

if __name__=='__main__':
    unittest.main()
