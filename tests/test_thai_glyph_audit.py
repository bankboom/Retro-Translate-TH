import tempfile
import unittest
from pathlib import Path
from tools.thai_glyph_audit import audit, inspect_text


class ThaiGlyphAuditTests(unittest.TestCase):
    def test_valid_samples(self):
        for sample in ('น้ำ', 'กุ้ง', 'กิ่', 'ภาษาไทย', 'ก๋า', 'ปี้'):
            self.assertEqual(inspect_text(sample), [])

    def test_orphan(self):
        self.assertTrue(inspect_text('่'))
        self.assertTrue(inspect_text('เ่'))

    def test_consecutive_tones(self):
        self.assertTrue(any(x['kind'] == 'consecutive_tone_marks' for x in inspect_text('ก้่')))

    def test_tsv(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.tsv'
            path.write_text('id\tthai\n1\tน้ำ\n2\tกุ้ง\n', encoding='utf-8')
            report = audit(path)
            self.assertEqual(report['rows'], 2)
            self.assertFalse(report['cmap_checked'])
            self.assertEqual(report['warnings'], [])


if __name__ == '__main__':
    unittest.main()
