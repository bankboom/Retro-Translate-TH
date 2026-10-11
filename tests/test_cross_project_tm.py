import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from cross_project_tm import make_db, suggestions, term_suggestions, read_csv

FIELDS = ['ID','Bank','English','Thai','TranslationStatus','Context_Key','Scene','Speaker']


def make_project(base, slug, platform, series, rows, glossary=None, publisher=None):
    p = base / slug
    (p / 'translations').mkdir(parents=True)
    (p / 'project_profile.json').write_text(json.dumps({'project_slug': slug,'game_title': slug,
        'platform': platform, 'series_id': series, 'publisher': publisher}), encoding='utf8')
    with (p / 'translations' / 'master.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    if glossary:
        with (p / 'translations' / 'glossary.csv').open('w', newline='', encoding='utf8') as f:
            w=csv.DictWriter(f, ['Source_Term','Thai_Term','Approved'])
            w.writeheader(); w.writerows(glossary)
    return p


class CrossProjectTMTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.projects = self.root/'projects'
        self.projects.mkdir()
        self.a = make_project(self.projects, 'older-gba', 'GBA', 'same-series', [
            {'ID':'1','Bank':'story','English':'Potion','Thai':'ยาฟื้นพลัง','TranslationStatus':'REVIEWED','Context_Key':'item'},
            {'ID':'2','Bank':'story','English':'Charge','Thai':'ชาร์จ','TranslationStatus':'DRAFT','Context_Key':'battle'},
            {'ID':'3','Bank':'story','English':'Hello {name}','Thai':'สวัสดี','TranslationStatus':'REVIEWED','Context_Key':'talk'},
            {'ID':'4','Bank':'story','English':'The ancient gate is open','Thai':'ประตูโบราณเปิดแล้ว','TranslationStatus':'APPROVED','Context_Key':'main'},
        ], [{'Source_Term':'Potion','Thai_Term':'ยาฟื้นพลัง','Approved':'TRUE'},
            {'Source_Term':'Attack','Thai_Term':'โจมตี','Approved':'FALSE'}], publisher='company-a')
        self.b = make_project(self.projects, 'newer-nds', 'NDS', 'same-series', [
            {'ID':'10','Bank':'items','English':'Potion','Thai':'','TranslationStatus':'MISSING','Context_Key':'item'},
            {'ID':'11','Bank':'battle','English':'Charge','Thai':'','TranslationStatus':'MISSING','Context_Key':'battle'},
            {'ID':'12','Bank':'talk','English':'Hello {name}','Thai':'','TranslationStatus':'MISSING','Context_Key':'talk'},
            {'ID':'13','Bank':'story','English':'The ancient gate was open','Thai':'','TranslationStatus':'MISSING','Context_Key':'main'},
            {'ID':'14','Bank':'items','English':'Potion','Thai':'ยา','TranslationStatus':'DRAFT','Context_Key':'item'},
        ], publisher='company-b')
        self.db = self.root/'tm.sqlite'

    def tearDown(self):
        self.tmp.cleanup()

    def test_indexes_only_reviewed_and_token_safe(self):
        stats = make_db(self.db, self.projects)
        self.assertEqual(stats['approved_rows'], 2)
        self.assertEqual(stats['rejected_unreviewed'], 2) # draft Charge and target existing draft are excluded
        self.assertEqual(stats['rejected_unsafe_tokens'], 1)
        self.assertEqual(stats['glossary_terms'], 1)

    def test_cross_platform_and_fuzzy_suggestions_are_review_only(self):
        make_db(self.db, self.projects)
        output = self.root / 'suggest.csv'
        result = suggestions(self.b, self.db, output)
        by_id = {r['ID']: r for r in read_csv(output)}
        self.assertEqual(by_id['10']['Suggested_Thai'], 'ยาฟื้นพลัง')
        self.assertEqual(by_id['10']['Source_Platform'], 'GBA')
        self.assertEqual(by_id['10']['Review_Status'], 'REVIEW_REQUIRED')
        self.assertEqual(by_id['10']['Context_Match'], 'YES')
        self.assertNotIn('11', by_id) # unreviewed original excluded
        self.assertNotIn('12', by_id) # unbalanced {name} from old source excluded
        self.assertEqual(by_id['13']['Match_Type'], 'FUZZY')
        self.assertNotIn('14', by_id) # existing target translation preserved
        self.assertGreater(result['rows_with_suggestions'], 0)
        self.assertEqual(read_csv(self.b/'translations'/'master.csv')[0]['Thai'], '')
        with self.assertRaises(FileExistsError):
            suggestions(self.b, self.db, output)

    def test_glossary_reuse_and_nonapproval(self):
        make_db(self.db, self.projects)
        output = self.root/'terms.csv'
        result = term_suggestions(self.b, self.db, output)
        rows = read_csv(output)
        self.assertEqual(result['term_suggestions'], 1)
        self.assertEqual(rows[0]['Term'], 'Potion')
        self.assertEqual(rows[0]['Series_Match'], 'YES')
        self.assertIn('REVIEW_REQUIRED', rows[0]['Review_Status'])

    def test_same_english_different_thai_is_conflict(self):
        make_project(self.projects, 'older-alt', 'GB', 'same-series', [
            {'ID':'42','Bank':'items','English':'Potion','Thai':'ยารักษา','TranslationStatus':'VERIFIED','Context_Key':'item'}])
        make_db(self.db, self.projects)
        output = self.root/'conflicts.csv'
        suggestions(self.b, self.db, output)
        found = [r for r in read_csv(output) if r['ID'] == '10']
        self.assertEqual(len(found), 2)
        self.assertEqual({r['Suggested_Thai'] for r in found}, {'ยาฟื้นพลัง','ยารักษา'})
        self.assertTrue(all(r['Review_Status'] == 'CONFLICT_REVIEW_REQUIRED' for r in found))

    def test_no_fuzzy_from_unrelated_series(self):
        self.b_profile = self.b/'project_profile.json'
        p = json.loads(self.b_profile.read_text(encoding='utf8'))
        p['series_id'] = 'unrelated-series'
        self.b_profile.write_text(json.dumps(p),encoding='utf8')
        make_db(self.db, self.projects)
        result = suggestions(self.b,self.db,self.root/'unrelated.csv')
        self.assertEqual(result['fuzzy'], 0)
        self.assertEqual(result['exact'], 1) # same 'Potion' across any games as review-required


if __name__ == '__main__':
    unittest.main()
