import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from argparse import Namespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from token_saver import pack, suggest


def write_csv(path, header, values):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w=csv.DictWriter(f, fieldnames=header)
        w.writeheader();w.writerows(values)


class TokenSaverTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.p=Path(self.temp.name)/'project'
        (self.p/'translations').mkdir(parents=True)
        (self.p/'project_profile.json').write_text(json.dumps({'game_title':'Sample', 'platform':'NDS'}), encoding='utf-8')
        self.master=self.p/'translations/master.csv'
        write_csv(self.master, ['ID','Bank','English','Thai','TranslationStatus','Context_Key','Control_Tokens','Max_Width_Px'], [
            {'ID':'1','Bank':'main','English':'Start Game','Context_Key':'ui:new-game'},
            {'ID':'2','Bank':'main','English':'Thank you','Thai':'ขอบคุณ','TranslationStatus':'REVIEWED', 'Context_Key':'scene:abc'},
            {'ID':'3','Bank':'main','English':'Start Game','Context_Key':'ui:other'},
            {'ID':'4','Bank':'main','English':'A very long piece '+('x'*700),'Context_Key':'scene:huge'},
        ])
        write_csv(self.p/'translations/glossary.csv', ['Source_Term','Thai_Term','Approved'], [
            {'Source_Term':'Game','Thai_Term':'เกม','Approved':'Yes'},
            {'Source_Term':'Start','Thai_Term':'เริ่ม','Approved':'No'}])
        self.out=Path(self.temp.name)/'packet.md'

    def test_bounded_packet_skips_translated_and_filters_glossary(self):
        report=pack(Namespace(project=str(self.p),mode='missing',bank=None,limit=5,max_chars=500,output=str(self.out)))
        content=self.out.read_text(encoding='utf-8')
        self.assertLessEqual(len(content),500)
        self.assertNotIn('Thank you',content)
        self.assertIn('Start Game',content)
        self.assertIn('Game => เกม',content)
        self.assertNotIn('Start => เริ่ม',content)
        self.assertGreaterEqual(len(report['oversized_ids']),1)

    def test_review_excludes_approved(self):
        report=pack(Namespace(project=str(self.p),mode='review',bank=None,limit=5,max_chars=500,output=str(self.out)))
        self.assertEqual(report['rows_in_packet'],0)

    def test_only_same_context_approved_suggested_without_replacing(self):
        tm=Path(self.temp.name)/'tm.csv'
        write_csv(tm,['Platform','Game','Context_Key','Source_Text','Thai_Text','Reviewed'],[
            {'Platform':'NDS','Game':'*','Context_Key':'ui:new-game','Source_Text':'Start Game','Thai_Text':'เริ่มเกม','Reviewed':'YES'},
            {'Platform':'NDS','Game':'*','Context_Key':'ui:other','Source_Text':'Start Game','Thai_Text':'เล่นใหม่','Reviewed':'NO'},
            {'Platform':'GBA','Game':'*','Context_Key':'ui:other','Source_Text':'Start Game','Thai_Text':'เริ่ม','Reviewed':'YES'},
        ])
        original=self.master.read_bytes()
        output=Path(self.temp.name)/'suggest.csv'
        report=suggest(Namespace(project=str(self.p),tm=str(tm),output=str(output)))
        with output.open('r',encoding='utf-8-sig',newline='') as f:
            suggestions=list(csv.DictReader(f))
        self.assertEqual(report['suggestion_count'],1)
        self.assertEqual(suggestions[0]['ID'],'1')
        self.assertEqual(suggestions[0]['Suggested_Thai'],'เริ่มเกม')
        self.assertEqual(original,self.master.read_bytes())

    def test_missing_context_no_cross_game_reuse(self):
        tm=Path(self.temp.name)/'tm.csv'
        write_csv(tm,['Platform','Game','Context_Key','Source_Text','Thai_Text','Reviewed'],[
            {'Platform':'NDS','Game':'Other','Context_Key':'ui:new-game','Source_Text':'Start Game','Thai_Text':'เริ่มเกม','Reviewed':'YES'}
        ])
        output=Path(self.temp.name)/'suggest.csv'
        self.assertEqual(suggest(Namespace(project=str(self.p),tm=str(tm),output=str(output)))['suggestion_count'],0)

if __name__ == '__main__': unittest.main()
