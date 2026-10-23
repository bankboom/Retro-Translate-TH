#!/usr/bin/env python3
"""Full inventory translation-scope merge for Pokemon Omega Paradox TH.

Read-only relative to ROM. Requires the ORIGINAL 56,700-row P3.5 CSV and
four repo-maintained, full-message Thai draft CSVs. Every inventory row gets
one auditable state; exact source and ordered control-token identity prevent
silently injecting wrong-game or wrong-message text.

This does NOT translate the backlog, encode E8xx, or build BPS. Only evidence
from a ROM build and emulator can promote rows to IN_GAME_VERIFIED.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from omega_control_tokens import tokens

ROOT = Path(__file__).resolve().parents[1]
DRAFT_FILES = [
    "P3_9_OMEGA_CUSTOM_CONTEXT_DRAFTS.csv",
    "P4_1_OMEGA_STORY_EARLY_DRAFTS.csv",
    "P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv",
    "P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv",
    "P4_8_OMEGA_PRIORITY_FULL_MESSAGE_DRAFTS.csv",
    "P4_9_OMEGA_STORY_CONTINUATION_DRAFTS.csv",
    "P5_0_CASTELIA_NIMBASA_CONTEXT_DRAFTS.csv",
    "P5_1_LEGENDS_AND_MASKED_MAN_DRAFTS.csv",
]
INV_REQUIRED = {
    "archive", "file_id", "message_id", "status", "omega_custom",
    "source_english_or_original", "current_p35_message", "needs_translation_review",
}
COLUMNS = [
    "archive", "file_id", "message_id", "p35_status", "omega_custom",
    "needs_translation_review", "source_sha256", "source_original",
    "current_p35_message", "draft_thai", "draft_source_file",
    "draft_stage", "source_match", "control_match", "audit_stage",
    "qa_notes",
]
P46_MESSAGE = ("system", "44", "24")
P46_BPS_SHA256 = "48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6"

def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def rid(row: dict) -> tuple[str, str, str]:
    return tuple(str(row[k]).strip() for k in ("archive", "file_id", "message_id"))

def read_csv(path: Path, required: set[str]):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        missing = required - set(r.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name}: missing fields {sorted(missing)}")
        yield from r

def load_drafts(paths: list[Path]):
    """Return unique-source draft candidates, freeze conflicting message IDs."""
    table: dict[tuple[str,str,str], list[dict]] = defaultdict(list)
    total = 0
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            fields = set(reader.fieldnames or [])
            if not {"archive","file_id","message_id"} <= fields:
                raise ValueError(f"{path.name}: missing archive/member/message ID")
            if {"original_english","draft_thai"} <= fields:
                source_key, thai_key, stage_key = "original_english", "draft_thai", "status"
            elif {"source_original","thai_draft"} <= fields:
                source_key, thai_key, stage_key = "source_original", "thai_draft", "stage"
            else:
                raise ValueError(f"{path.name}: missing full-message original and Thai draft")
            for row in reader:
                total += 1
                k = rid(row)
                orig, thai = row[source_key], row[thai_key]
                if not orig or not thai:
                    raise ValueError(f"blank original/draft for {k} in {path.name}")
                table[k].append({
                    "source":orig, "thai":thai,"file":path.name,
                    "stage":row.get(stage_key,"DRAFT"),
                })
    return table,total

def audit_drafts_only(paths: list[Path]) -> dict:
    d, total = load_drafts(paths)
    counts = Counter()
    for k, variants in d.items():
        unique = {(x["source"], x["thai"]) for x in variants}
        if len(unique) > 1:
            counts["MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT"] += 1
        else:
            x = variants[0]
            if tokens(x["source"]) != tokens(x["thai"]):
                counts["CONTROL_MISMATCH"] += 1
            else:
                counts["DRAFT_CONTROL_MATCH_CONTEXT_PENDING"] += 1
    return {"draft_rows":total,"unique_message_ids":len(d),"counts":dict(sorted(counts.items()))}

def merge(inventory: Path, drafts: list[Path], output: Path,
          expected_count: int=56700) -> dict:
    draft_map, draft_count = load_drafts(drafts)
    # Validate complete original input BEFORE opening any deliverable.
    n = 0
    seen = set()
    for row in read_csv(inventory, INV_REQUIRED):
        k = rid(row)
        if k in seen:
            raise ValueError(f"duplicate inventory ID: {k}")
        seen.add(k); n += 1
    if n != expected_count:
        raise ValueError(f"refusing truncated dataset: {n} instead of {expected_count}")
    output.mkdir(parents=True,exist_ok=True)

    stats = Counter()
    review_stats = Counter()
    matched_drafts = set()
    with (output/"p47_all_inventory_states.csv").open("w", encoding="utf-8", newline="") as out, \
         (output/"p47_context_draft_queue.csv").open("w", encoding="utf-8", newline="") as queue, \
         (output/"p47_blockers.csv").open("w", encoding="utf-8", newline="") as blocked:
        w = csv.DictWriter(out,fieldnames=COLUMNS);w.writeheader()
        q = csv.DictWriter(queue,fieldnames=COLUMNS);q.writeheader()
        b = csv.DictWriter(blocked,fieldnames=COLUMNS);b.writeheader()
        for row in read_csv(inventory,INV_REQUIRED):
            k=rid(row)
            source=row["source_english_or_original"]
            variants=draft_map.get(k,[])
            is_p46=k==P46_MESSAGE
            note=""
            source_match=""
            control_match=""
            dsrc=""
            stage=""
            thai=""
            if variants:
                matched_drafts.add(k)
                versions = {(x["source"],x["thai"]) for x in variants}
                x=variants[0]
                dsrc=";".join(sorted({v["file"] for v in variants}))
                stage=";".join(sorted({v["stage"] for v in variants}))
                thai=x["thai"]
                source_match = int(x["source"]==source)
                control_match = int(tokens(x["source"])==tokens(x["thai"]))
                if len(versions)>1:
                    state="DRAFT_VARIANTS_CONFLICT"
                    note="Cannot choose among distinct drafts at same ID"
                elif not source_match:
                    state="DRAFT_SOURCE_MISMATCH"
                    note="Draft original differs from complete P3.5 source"
                elif not control_match:
                    state="DRAFT_CONTROL_MISMATCH"
                    note="F000 operand, FFFE, or FFFF token sequence differs"
                elif is_p46:
                    state="P46_USER_TESTED_SCOPED_NOT_GLOBAL"
                    note="P4.6 test of two Cynthia clauses, not this Unicode draft injection"
                else:
                    state="DRAFT_CONTEXT_PENDING"
                    note="No verified Unicode->native E8xx mapping or emulator QA for this draft"
            elif is_p46:
                state="P46_USER_TESTED_SCOPED_NOT_GLOBAL"
                note="User tested P4.6 Cynthia clauses, dialogue advance, Save/Load"
            elif row["status"]=="THAI_IN_ROM":
                state="P35_THAI_PUA_SNAPSHOT_NOT_FULL_QA"
                note="P3.5 Thai snapshot; not an independent scene QA certification"
            elif str(row["needs_translation_review"]).strip()=="1":
                state="BACKLOG_CONTEXT_TRANSLATION_REQUIRED"
                note="No full-message Thai draft known at this ID"
            elif row["omega_custom"]=="1":
                state="OMEGA_CUSTOM_OTHER_CLASSIFICATION_REVIEW"
                note="Never blindly import White TH for Omega-exclusive source"
            else:
                state="NONLINGUISTIC_OR_OTHER_AUDIT"
                note="Keep original bytes unless independently reviewed"
            rec={
                "archive":k[0],"file_id":k[1],"message_id":k[2],
                "p35_status":row["status"],"omega_custom":row["omega_custom"],
                "needs_translation_review":row["needs_translation_review"],
                "source_sha256":sha(source),
                "source_original":source,
                "current_p35_message":row["current_p35_message"],
                "draft_thai":thai,
                "draft_source_file":dsrc,
                "draft_stage":stage,
                "source_match":source_match,
                "control_match":control_match,
                "audit_stage":state,
                "qa_notes":note
            }
            stats[state]+=1
            if row["needs_translation_review"]=="1":
                review_stats["review_flagged_total"]+=1
                if variants:
                    review_stats["review_flagged_with_draft"]+=1
            w.writerow(rec)
            if variants:q.writerow(rec)
            if state in {"DRAFT_SOURCE_MISMATCH","DRAFT_VARIANTS_CONFLICT","DRAFT_CONTROL_MISMATCH"}:
                b.writerow(rec)
    missing=sorted(set(draft_map)-matched_drafts)
    with (output/"p47_missing_draft_ids.csv").open("w",encoding="utf-8",newline="") as f:
        keys=["archive","file_id","message_id","source_files"]
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader()
        for k in missing:
            wr.writerow(dict(zip(keys,(*k,";".join(x["file"] for x in draft_map[k])))))
    result={
        "audit":"P4.7 56,700-message scope consolidation",
        "inventory_rows":n,
        "inventory_unique_ids":len(seen),
        "draft_rows":draft_count,
        "draft_unique_ids":len(draft_map),
        "draft_ids_matched_inventory":len(matched_drafts),
        "draft_ids_missing_inventory":len(missing),
        "all_row_states":dict(sorted(stats.items())),
        "review_flags":dict(review_stats),
        "baseline_p46_bps_sha256":P46_BPS_SHA256,
        "no_rom_writes":True,"no_new_bps":True,"emulator_new_build_verified":False,
        "note":"Draft, existing-PUA and user-tested P4.6 scoped evidence MUST NOT be confused with 100% approved or newly injected."
    }
    (output/"p47_summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory",type=Path)
    ap.add_argument("--draft",type=Path,action="append")
    ap.add_argument("--out",type=Path)
    ap.add_argument("--expected-count",type=int,default=56700)
    ap.add_argument("--check-drafts-only",action="store_true")
    args=ap.parse_args()
    paths=args.draft or [ROOT/"translation"/n for n in DRAFT_FILES]
    if args.check_drafts_only:
        result=audit_drafts_only(paths)
    else:
        if not args.inventory or not args.out:
            ap.error("--inventory and --out required unless --check-drafts-only")
        result=merge(args.inventory,paths,args.out,args.expected_count)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__":
    main()
