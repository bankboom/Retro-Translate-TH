import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import project_manager as pm

class TestProjectManager(unittest.TestCase):
    def test_create_and_status_without_rom(self):
        with tempfile.TemporaryDirectory() as d:
            code=pm.main(['init','--game','Sample Adventure','--platform','NDS',
                          '--slug','sample-adventure','--output-root',d])
            self.assertEqual(code,0)
            project=Path(d)/'sample-adventure'
            self.assertTrue((project/'AGENTS.md').exists())
            self.assertFalse(list(project.rglob('*.nds')))
            profile=json.loads((project/'project_profile.json').read_text(encoding='utf-8'))
            self.assertIsNone(profile['source_rom']['expected_clean_sha256'])
            rep=pm.status_project(type('Args',(),{'project':str(project),'output':None})())
            self.assertTrue(all(x=='PENDING' for x in rep['gate_statuses'].values()))
    def test_refuses_overwriting_project(self):
        with tempfile.TemporaryDirectory() as d:
            args=['init','--game','Test','--platform','GBA','--output-root',d]
            self.assertEqual(pm.main(args),0)
            self.assertEqual(pm.main(args),2)
    def test_slug_rejects_traversal_and_empty(self):
        for bad in ('../escape','', '../', 'ชื่อเกม', '/abs/path'):
            with self.assertRaises(ValueError):pm.slugify(bad)
    def test_invalid_platform(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(pm.main(['init','--game','ABC','--platform','NOTREAL','--output-root',d]),2)
            self.assertFalse((Path(d)/'abc').exists())

if __name__=='__main__':unittest.main()
