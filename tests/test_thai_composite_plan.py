import tempfile
import unittest
from pathlib import Path
from tools.thai_composite_plan import build_report, scan, main


class ThaiCompositePlanTests(unittest.TestCase):
    def test_required_sara_am_and_marks(self):
        counts, errors, _ = scan("น้ำ กิ่ กุ้ง ปี้")
        self.assertEqual(errors, [])
        self.assertEqual(counts["นํ้"], 1)
        self.assertEqual(counts["กิ่"], 1)
        self.assertEqual(counts["กุ้"], 1)
        self.assertEqual(counts["ปี้"], 1)

    def test_canonical_mark_order(self):
        combos, errors, _ = scan("ก้ิ กิ้")
        self.assertEqual(errors, [])
        self.assertEqual(combos["กิ้"], 2)

    def test_reject_unsupported_stack_and_orphan_mark(self):
        _, errors, _ = scan("กุิ ้")
        self.assertEqual({e["code"] for e in errors},
                         {"UNSUPPORTED_MARK_COMBINATION", "UNATTACHED_MARK"})

    def test_protected_token_and_leading(self):
        combos, errors, specials = scan("เก่ง {0} <color=red>กิ้</color> \\n")
        self.assertEqual(errors, [])
        self.assertEqual(combos["ก่"], 1)
        self.assertEqual(combos["กิ้"], 1)
        self.assertIn("เ", specials)

    def test_bank_aware_counts_and_capacity(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "master.csv"
            path.write_text("Bank,ID,Thai\nmenu,1,กิ่\nscript,1,กิ่\nmenu,2,น้ำ\n", encoding="utf-8")
            result = build_report(path, max_slots=1)
            self.assertEqual(result["unique_composite_candidates"], 2)
            self.assertEqual(result["budget_status"], "OVER_BUDGET")
            self.assertEqual(result["glyphs"][0]["text_ids"], 2)

    def test_bom_tsv_and_empty(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "master.tsv"
            path.write_text("id\tthai\n1\tกิ่\n2\t\n", encoding="utf-8-sig")
            result = build_report(path, thai_column="thai", id_column="id")
            self.assertEqual(result["nonempty_thai_rows"], 1)
            self.assertEqual(result["budget_status"], "UNMEASURED")

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "master.csv"
            output = Path(folder) / "report.json"
            path.write_text("ID,Thai\n1,กิ่\n", encoding="utf-8")
            output.write_text("leave me alone", encoding="utf-8")
            self.assertEqual(main([str(path), "--output", str(output)]), 2)
            self.assertEqual(output.read_text(), "leave me alone")
            self.assertEqual(main([str(path), "--output", str(path)]), 2)


if __name__ == "__main__":
    unittest.main()
