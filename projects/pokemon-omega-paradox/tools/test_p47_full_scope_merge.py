#!/usr/bin/env python3
"""Synthetic coverage/integrity tests; they do not certify any ROM/Emulator."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from p47_full_scope_merge import ROOT,DRAFT_FILES,audit_drafts_only,merge

INV_COLS=["archive","file_id","message_id","status","omega_custom",
          "source_english_or_original","current_p35_message","needs_translation_review"]
DR_COLS=["archive","file_id","message_id","original_english","draft_thai","status"]
DR39=["archive","file_id","message_id","source_original","thai_draft","stage"]

def put(path,cols,rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def ir(fid="3",mid="4",s=r"Hello\xF000븁\x0000",status="ENGLISH_OR_NAME_PENDING_REVIEW",flag="1"):
    return dict(archive="story",file_id=fid,message_id=mid,status=status,
                omega_custom="0",source_english_or_original=s,
                current_p35_message=s,needs_translation_review=flag)

def dr(fid="3",mid="4",s=r"Hello\xF000븁\x0000",
       th=r"สวัสดี\xF000븁\x0000"):
    return dict(archive="story",file_id=fid,message_id=mid,
                original_english=s,draft_thai=th,status="DRAFT_NEEDS_CONTEXT")

class FullScopeMergeTests(unittest.TestCase):
    def audit(self,inventory,drafts,expected=None,extra_39=None):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            put(p/"inv.csv",INV_COLS,inventory)
            put(p/"draft.csv",DR_COLS,drafts)
            paths=[p/"draft.csv"]
            if extra_39 is not None:
                put(p/"draft39.csv",DR39,extra_39)
                paths.append(p/"draft39.csv")
            result=merge(p/"inv.csv",paths,p/"out",len(inventory) if expected is None else expected)
            with (p/"out"/"p47_context_draft_queue.csv").open(encoding="utf-8",newline="") as f:
                drafts=list(csv.DictReader(f))
            with (p/"out"/"p47_blockers.csv").open(encoding="utf-8",newline="") as f:
                blockers=list(csv.DictReader(f))
            return result,drafts,blockers

    def test_perfect_source_with_thai_stays_draft(self):
        a,d,b=self.audit([ir()],[dr()])
        self.assertEqual(a["all_row_states"]["DRAFT_CONTEXT_PENDING"],1)
        self.assertEqual(len(d),1)
        self.assertEqual(len(b),0)
        self.assertTrue(a["no_new_bps"])

    def test_control_opcode_mismatch_held(self):
        a,d,b=self.audit([ir()],[dr(th=r"สวัสดี\xF000븀\x0000")])
        self.assertEqual(a["all_row_states"]["DRAFT_CONTROL_MISMATCH"],1)
        self.assertEqual(len(b),1)

    def test_stale_draft_source_held(self):
        a,d,b=self.audit([ir(s="Hello")],[dr()])
        self.assertEqual(a["all_row_states"]["DRAFT_SOURCE_MISMATCH"],1)
        self.assertEqual(len(b),1)

    def test_dual_variant_same_id_held(self):
        a,d,b=self.audit([ir()],[dr(),dr(th=r"หวัดดี\xF000븁\x0000")])
        self.assertEqual(a["draft_unique_ids"],1)
        self.assertEqual(a["all_row_states"]["DRAFT_VARIANTS_CONFLICT"],1)

    def test_legacy_p39_column_layout(self):
        legacy=dict(archive="story",file_id="3",message_id="4",
                    source_original=r"Hello\xF000븁\x0000",
                    thai_draft=r"สวัสดี\xF000븁\x0000",stage="DRAFT_CONTEXT_REVIEW")
        a,d,b=self.audit([ir()],[],extra_39=[legacy])
        self.assertEqual(a["all_row_states"]["DRAFT_CONTEXT_PENDING"],1)

    def test_p46_scoped_not_global_pass(self):
        x=ir(fid="44",mid="24",s="This young woman is Cynthia.")
        x["archive"]="system"
        a,d,b=self.audit([x],[])
        self.assertEqual(a["all_row_states"]["P46_USER_TESTED_SCOPED_NOT_GLOBAL"],1)
        self.assertFalse(a["emulator_new_build_verified"])

    def test_incomplete_inventory_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"refusing truncated"):
            self.audit([ir()],[],expected=56700)

    def test_p35_native_thai_does_not_count_as_qa(self):
        a,d,b=self.audit([ir(status="THAI_IN_ROM",flag="0")],[])
        self.assertEqual(a["all_row_states"]["P35_THAI_PUA_SNAPSHOT_NOT_FULL_QA"],1)

    def test_existing_repository_drafts_are_130_unique(self):
        sources=[ROOT/"translation"/x for x in DRAFT_FILES]
        report=audit_drafts_only(sources)
        self.assertEqual(report["draft_rows"],130)
        self.assertEqual(report["unique_message_ids"],130)
        self.assertEqual(report["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT",0),0)

if __name__=="__main__":unittest.main()
