import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from thai_text_lint import lint_pair,audit

class ThaiLintTests(unittest.TestCase):
    def test_natural_thai_not_flagged(self):
        self.assertEqual(lint_pair('Thank you, {name}!', 'ขอบคุณนะ {name}!'), [])
        self.assertEqual(lint_pair('Water', 'น้ำ'), [])
        self.assertEqual(lint_pair('Skills', 'เก่ง'), [])

    def test_orphan_mark_and_double_tone(self):
        self.assertIn('ORPHAN_COMBINING_MARK',lint_pair('X','้มา'))
        self.assertIn('CONSECUTIVE_TONE_MARKS',lint_pair('X','ก้่'))

    def test_control_token_regression(self):
        self.assertIn('POSSIBLE_CONTROL_TOKEN_CHANGE',lint_pair('Attack {hp} %d', 'โจมตี {hp}'))
        self.assertEqual(lint_pair('Attack {hp} %d', 'โจมตี {hp} %d'),[])

    def test_audit_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'master.csv'
            with p.open('w',encoding='utf-8',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['ID','English','Thai']);w.writeheader()
                w.writerow({'ID':'1','English':'Hello {name}','Thai':'สวัสดี {name}'})
                w.writerow({'ID':'2','English':'Next','Thai':'้ถัดไป'})
            result=audit(p)
            self.assertEqual(result['checked_translated_entries'],2)
            self.assertEqual(result['issue_counts']['ORPHAN_COMBINING_MARK'],1)

if __name__=='__main__':unittest.main()
