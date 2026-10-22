#!/usr/bin/env python3
"""Non-ROM synthetic tests for P4.0 cross-ID matching."""
import csv
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from p40_cross_id_review import candidates

def save(path, header, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=header)
        wr.writeheader()
        wr.writerows(rows)

INV = ["archive","file_id","message_id","status","omega_custom",
       "source_english_or_original","current_p35_message","white_thai_master",
       "reuse_master_available","control_safe_master"]
TM = ["archive","file_id","message_id","white_english","white_thai_pua_text"]

def source_row(message_id="5", source=r"Hello\xFFFEWorld", custom="0",
               status="PENDING"):
    return dict(archive="story", file_id="44", message_id=message_id,
                status=status, omega_custom=custom,
                source_english_or_original=source,
                current_p35_message=source, white_thai_master="",
                reuse_master_available="0", control_safe_master="0")

def memory_row(fid="2", mid="1", source=r"Hello\xFFFEWorld",
               thai=r"\xE801\xFFFE\xE802"):
    return dict(archive="story",file_id=fid,message_id=mid,
                white_english=source, white_thai_pua_text=thai)

class CrossIDTest(unittest.TestCase):
    def run_case(self, inv, tm, expected=None):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            save(root/"inv.csv", INV, inv)
            save(root/"tm.csv", TM, tm)
            out=root/"output.csv"
            report=candidates(root/"inv.csv",root/"tm.csv",out,
                              expected_count=len(inv) if expected is None else expected)
            with out.open(encoding="utf-8",newline="") as f:
                rows=list(csv.DictReader(f))
            return report,rows

    def test_cross_id_exact_source_suggests_but_not_approved(self):
        report, rows = self.run_case([source_row()], [memory_row()])
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["status"], "STATIC_CROSS_ID_CONTEXT_PENDING")
        self.assertEqual(rows[0]["master_file_id"],"2")
        self.assertFalse(report["bps_created"])

    def test_custom_never_overwritten(self):
        report,rows=self.run_case([source_row(custom="1")],[memory_row()])
        self.assertEqual(rows,[])
        self.assertEqual(report["counts"]["OMEGA_CUSTOM_HELD"],1)

    def test_same_id_routes_to_primary_audit(self):
        inv=[source_row()]
        mem=[memory_row(fid="44",mid="5")]
        report,rows=self.run_case(inv,mem)
        self.assertEqual(rows,[])
        self.assertEqual(report["counts"]["SAME_ID_USE_PRIMARY_AUDIT"],1)

    def test_ambiguous_thai_variant_is_held(self):
        report,rows=self.run_case([source_row()],
            [memory_row(),memory_row(fid="3",mid="2",thai=r"\xE888\xFFFE\xE802")])
        self.assertEqual(rows,[])
        self.assertEqual(report["counts"]["CONTEXT_COLLISION_HELD"],1)

    def test_control_token_operand_changes_are_rejected(self):
        s=r"Hi\xF000븁\x0000"
        t=r"\xE801\xF000븀\x0000"
        report,rows=self.run_case([source_row(source=s)],
                                  [memory_row(source=s,thai=t)])
        self.assertEqual(rows,[])

    def test_truncated_inventory_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected 56700"):
            self.run_case([source_row()],[memory_row()],expected=56700)

    def test_snapshot_thai_not_assumed_ready_for_p37b(self):
        report,rows=self.run_case([source_row(status="THAI_IN_ROM")],[memory_row()])
        self.assertEqual(rows,[])
        self.assertEqual(report["counts"]["P35_THAI_SNAPSHOT_HELD"],1)

if __name__=="__main__":
    unittest.main()
