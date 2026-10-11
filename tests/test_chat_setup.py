import contextlib
from io import StringIO
import importlib.util
import json
import tempfile
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import install_once as install
import chat_project

class TestChatSetup(unittest.TestCase):
    def test_global_rules_preserve_existing_and_idempotent(self):
        with tempfile.TemporaryDirectory() as t:
            home=Path(t)
            codex=home/'.codex';codex.mkdir()
            (codex/'AGENTS.md').write_text('User independent rule.\n',encoding='utf8')
            install.install(home)
            once=(codex/'AGENTS.md').read_text(encoding='utf8')
            self.assertIn('User independent rule.',once)
            self.assertEqual(once.count(install.BEGIN),1)
            sf=home/'.agents/skills/retro-game-th-v3-1/SKILL.md'
            self.assertTrue(sf.exists())
            self.assertTrue(sf.read_text(encoding='utf8').startswith('---\n'))
            self.assertTrue((home/'RetroThaiProjects/projects').is_dir())
            install.install(home)
            twice=(codex/'AGENTS.md').read_text(encoding='utf8')
            self.assertEqual(once,twice)
            self.assertEqual(twice.count(install.BEGIN),1)
            install.uninstall(home)
            self.assertEqual((codex/'AGENTS.md').read_text(encoding='utf8'),'User independent rule.\n')
            self.assertTrue((home/'RetroThaiProjects').exists())
            self.assertFalse((home/'.agents/skills/retro-game-th-v3-1').exists())
    def test_skill_conflict_fails_without_editing_global(self):
        with tempfile.TemporaryDirectory() as t:
            home=Path(t);skill=home/'.agents/skills/retro-game-th-v3-1'
            skill.mkdir(parents=True)
            (skill/'SKILL.md').write_text('Independent skill')
            with self.assertRaises(ValueError): install.install(home)
            self.assertFalse((home/'.codex/AGENTS.md').exists())
    def test_invalid_markers(self):
        with self.assertRaises(ValueError):install.replace_managed('test '+install.BEGIN,'rule')
    def test_new_project_and_resume(self):
        with tempfile.TemporaryDirectory() as t:
            state,p=chat_project.create_or_resume(game='Thai Wizard Game',platform='NDS',output_root=t)
            self.assertEqual(state,'CREATED')
            self.assertTrue((p/'project_profile.json').is_file())
            state2,p2=chat_project.create_or_resume(game='Thai Wizard Game',platform='NDS',output_root=t)
            self.assertEqual((state2,p2),('EXISTING',p))
            self.assertEqual(chat_project.find_game('Thai Wizard',t),p)
    def test_changed_rom_same_path_is_new_project(self):
        with tempfile.TemporaryDirectory() as t:
            rom=Path(t)/'Same (USA).gba'
            rom.write_bytes(bytes(256))
            a,p=chat_project.create_or_resume(rom=rom,output_root=Path(t)/'projects')
            rom.write_bytes(bytes([9])+bytes(255))
            b,q=chat_project.create_or_resume(rom=rom,output_root=Path(t)/'projects')
            self.assertEqual((a,b),('CREATED','CREATED'))
            self.assertNotEqual(p,q)
    def test_global_extra_text_after_block_is_preserved(self):
        src='First rule\n\n'+install.BEGIN+'\nmanaged\n'+install.END+'\nOther rule\n'
        output=install.replace_managed(src,None)
        self.assertIn('First rule',output)
        self.assertIn('Other rule',output)
    def test_safe_unicode_slug(self):
        self.assertRegex(chat_project.safe_slug('เกมทดสอบ','GBA'),r'^gba-[0-9a-f]{10}$')
        self.assertTrue(chat_project.safe_slug('Final Fight One (USA)','GBA').startswith('final-fight'))
    def test_ambiguous_platform_requires_explicit_flag(self):
        with tempfile.TemporaryDirectory() as t:
            rom=Path(t)/'disc.iso';rom.write_bytes(b'1234')
            with self.assertRaisesRegex(ValueError,'Platform is ambiguous'):
                chat_project.create_or_resume(rom=rom,output_root=Path(t)/'projects')
            self.assertFalse((Path(t)/'projects').exists())
    def test_gba_rom_creates_no_rom_copy(self):
        with tempfile.TemporaryDirectory() as t:
            rom=Path(t)/'Sample (USA).gba';rom.write_bytes(bytes(256))
            before=rom.read_bytes()
            state,p=chat_project.create_or_resume(rom=rom,output_root=Path(t)/'projects')
            self.assertEqual(state,'CREATED')
            self.assertFalse(list(p.rglob('*.gba')))
            self.assertEqual(rom.read_bytes(),before)
            state2,p2=chat_project.create_or_resume(rom=rom,output_root=Path(t)/'projects')
            self.assertEqual((state2,p2),('EXISTING',p))

if __name__=='__main__':unittest.main()
