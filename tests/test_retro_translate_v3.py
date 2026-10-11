"""Offline unittest suite for BPS parser and safe QA gates."""
import importlib.util
from pathlib import Path
import os
import tempfile
import unittest
import zlib
import struct

spec=importlib.util.spec_from_file_location('rtv3',str(Path(__file__).resolve().parents[1] / 'tools' / 'retro_translate_v3.py'))
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def vlq(v):
    out=bytearray()
    while True:
        x=v & 127
        v >>=7
        if v==0:
            out.append(x|128)
            return bytes(out)
        out.append(x)
        v-=1


def patch(source,target,commands):
    data=bytearray(b'BPS1'+vlq(len(source))+vlq(len(target))+vlq(0)+commands)
    data.extend(struct.pack('<II',zlib.crc32(source),zlib.crc32(target)))
    data.extend(struct.pack('<I',zlib.crc32(data)))
    return bytes(data)


class TestRetroTranslateV3(unittest.TestCase):
    def test_target_read_patch(self):
        src=b'ABCDE'
        tgt=b'THAI!'
        action=vlq(((len(tgt)-1)<<2)|1) + tgt
        result,info=m.apply_bps(src,patch(src,tgt,action))
        self.assertEqual(result,tgt)
        self.assertTrue(info['target_crc_valid'])
    def test_source_read_and_overlapping_targetcopy(self):
        src=b'ABCxyz'
        tgt=b'ABCABCABC'
        action=vlq(((3-1)<<2)|0)+vlq(((6-1)<<2)|3)+vlq(0)
        result,_=m.apply_bps(src,patch(src,tgt,action))
        self.assertEqual(result,tgt)
    def test_source_copy(self):
        src=b'ABCDE'
        tgt=b'BCD'
        # source copy rel +1 -> signed delta 2
        action=vlq(((3-1)<<2)|2)+vlq(2)
        result,_=m.apply_bps(src,patch(src,tgt,action))
        self.assertEqual(result,tgt)
    def test_crc_corruption_detected(self):
        src=b'123'
        tgt=b'xyz'
        good=patch(src,tgt,vlq(9)+tgt)
        bad=bytearray(good);bad[-5]^=0x40
        with self.assertRaises(m.BpsError):m.apply_bps(src,bytes(bad))
    def test_wrong_clean_rom_rejected(self):
        good=patch(b'123',b'abc',vlq(9)+b'abc')
        with self.assertRaises(m.BpsError):m.apply_bps(b'321',good)
    def test_gba_header_checksum(self):
        src=bytearray(256);src[0xA0:0xAC]=b'SAMPLE\x00\x00\x00\x00\x00\x00'
        src[0xAC:0xB0]=b'ABCD'
        src[0xBD]=(-sum(src[0xA0:0xBD])-0x19)&255
        x=m.rom_info(bytes(src),'test.gba')
        self.assertEqual(x['platform'],'GBA')
        self.assertTrue(x['gba_header_checksum_pass'])
    def test_comparison(self):
        x=m.compare_roms(b'abcxy',b'abzxx')
        self.assertEqual(x['changed_byte_count'],2)
    def test_csv_blanks_duplicates_tokens(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.csv'
            p.write_text('Bank,ID,English,Thai,TranslationStatus\nUI,1,Hello {NAME},สวัสดี {NAME},DRAFT\nUI,2,OK,,UNTRANSLATED\nUI,1,Press {KEY},กดปุ่ม,DRAFT\n',encoding='utf-8')
            x=m.audit_csv(p)
            self.assertEqual(x['count'],3)
            self.assertEqual(x['thai_blank'],1)
            self.assertEqual(x['duplicate_bank_ids'],1)
            self.assertEqual(x['token_mismatches_heuristic'],1)

if __name__=='__main__':unittest.main(verbosity=2)
