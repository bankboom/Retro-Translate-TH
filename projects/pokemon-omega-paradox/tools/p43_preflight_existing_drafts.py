#!/usr/bin/env python3
"""Fail-closed P4.1/P4.2 draft-to-glyph readiness report (no ROM writes)."""
from __future__ import annotations
import csv
import json
from collections import Counter
from pathlib import Path

from p43_native_e8_encoder import load_verified_map, MappingRequired, encode_message
from omega_control_tokens import equal_tokens

PROJECT = Path(__file__).resolve().parents[1]
DRAFT_FILES = [
    PROJECT / "translation/P4_1_OMEGA_STORY_EARLY_DRAFTS.csv",
    PROJECT / "translation/P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv",
    PROJECT / "translation/P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv",
]


def audit_files(paths, glyph_map, renderer="story_dialogue"):
    glyphs = load_verified_map(glyph_map, renderer)
    results = []
    seen = set()
    counts = Counter()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                key = (row["archive"], row["file_id"], row["message_id"])
                if key in seen:
                    raise ValueError("Duplicate message ID " + repr(key))
                seen.add(key)
                source = row["original_english"]
                thai = row["draft_thai"]
                if not equal_tokens(source, thai):
                    reason = "CONTROL_TOKEN_MISMATCH"
                elif row["status"] != "REVIEWED":
                    reason = "CONTEXT_NOT_REVIEWED"
                else:
                    try:
                        encode_message(thai, glyphs)
                        reason = "ENCODER_STATIC_READY_NOT_ROM_VERIFIED"
                    except MappingRequired:
                        reason = "NO_VERIFIED_NATIVE_GLYPH"
                counts[reason] += 1
                results.append(dict(archive=key[0],file_id=key[1],
                                    message_id=key[2],source_file=path.name,
                                    decision=reason))
    return {
        "total_draft_rows": len(results),
        "distinct_ids": len(seen),
        "counts": dict(sorted(counts.items())),
        "map_verified_fragments": len(glyphs),
        "code_injected": False, "bps_created": False,
        "emulator_verified": False,
        "rows": results,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map", type=Path,
        default=PROJECT/"glyph_maps/P4_3_NATIVE_E8_PENDING.csv")
    ap.add_argument("--out", type=Path)
    args=ap.parse_args()
    result=audit_files(DRAFT_FILES,args.map)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                            encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
