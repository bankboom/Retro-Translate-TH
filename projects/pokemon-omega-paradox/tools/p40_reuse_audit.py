#!/usr/bin/env python3
"""Conservative Pokemon White TH -> Omega Paradox translation reuse audit.

This tool NEVER changes a ROM, creates an NDS, or claims gameplay QA.
Only byte/source matching, context review, a game-specific encoder and a
verified ROM builder can promote candidates to a release.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

# Captures control operations with their operands (not just the \xF000 marker).
# Native Thai PUA glyphs (\\xE0xx/\\xE8xx) are TEXT, not control codes.
CTRL = re.compile(r"\\xF000(?:(?!\\xF000|\\xFFFE|\\xFFFF).)*?\\x0000|\\x(?:FFFE|FFFF)", re.S)
PUA = re.compile(r"\\xE[0-9A-Fa-f]{3}|[\ue000-\uf8ff]")

INV_FIELDS = {
    "archive", "file_id", "message_id", "status", "omega_custom",
    "source_english_or_original", "current_p35_message",
    "white_thai_master", "reuse_master_available", "control_safe_master",
}
TM_FIELDS = {"archive", "file_id", "message_id", "white_english", "white_thai_pua_text"}


def control_signature(text: str) -> tuple[str, ...]:
    return tuple(m.group(0).upper().replace("X", "x") for m in CTRL.finditer(text or ""))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def flag(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes"}


def key(row: dict) -> tuple[str, str, str]:
    return (row["archive"].strip(), row["file_id"].strip(), row["message_id"].strip())


def read_csv(path: Path, required: set[str]):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        missing = required.difference(rdr.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {sorted(missing)}")
        for row in rdr:
            yield row


def writer(path: Path, columns: list[str]):
    f = path.open("w", encoding="utf-8", newline="")
    obj = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
    obj.writeheader()
    return f, obj


def prepare(inv_path: Path, tm_path: Path, out_dir: Path,
            expected: int = 56700, approvals: Path | None = None) -> dict:
    # Validate completeness before creating any candidate files. A Files preview
    # may contain only a small excerpt of the actual 56,700-row CSV.
    if expected is not None:
        counted = sum(1 for _ in read_csv(inv_path, INV_FIELDS))
        if counted != expected:
            raise ValueError(
                f"Inventory count {counted} != expected {expected}; refusing partial export"
            )
    out_dir.mkdir(parents=True, exist_ok=True)
    memory = {}
    for row in read_csv(tm_path, TM_FIELDS):
        k = key(row)
        if k in memory:
            prev = memory[k]
            if prev["white_english"] != row["white_english"] or prev["white_thai_pua_text"] != row["white_thai_pua_text"]:
                raise ValueError(f"Conflicting translation memory key: {k!r}")
        memory[k] = row

    # Same English source can map to different Thai depending on context.
    # Freeze those variants instead of auto-selecting the first translation.
    source_variants = {}
    for mem in memory.values():
        source_key = (mem["archive"], mem["white_english"],
                      control_signature(mem["white_english"]))
        source_variants.setdefault(source_key, set()).add(mem["white_thai_pua_text"])
    memory_collision_count = sum(len(x) > 1 for x in source_variants.values())

    approved = {}
    if approvals:
        need = {"archive", "file_id", "message_id", "source_sha256",
                "qa_status", "scene_id", "reviewer"}
        for row in read_csv(approvals, need):
            k = key(row)
            if k in approved:
                raise ValueError(f"Duplicate approval key: {k!r}")
            approved[k] = row

    columns = ["archive", "file_id", "message_id", "source_sha256",
               "source_text", "master_thai_pua", "status", "control_signature",
               "scene_id", "reviewer", "notes"]
    reject_cols = columns + ["reason"]
    cand_file, cand = writer(out_dir / "p40_static_candidates.csv", columns)
    hold_file, hold = writer(out_dir / "p40_held_entries.csv", reject_cols)
    app_file, app = writer(out_dir / "p40_reviewed_reuse_manifest.csv", columns)
    stats = Counter()
    source_to_thai = {}
    count = 0
    seen = set()
    try:
        for row in read_csv(inv_path, INV_FIELDS):
            count += 1
            k = key(row)
            if k in seen:
                raise ValueError(f"Duplicate inventory key: {k!r}")
            seen.add(k)
            original = row["source_english_or_original"]
            current = row["current_p35_message"]
            sha = sha256_text(original)
            tm = memory.get(k)
            tha = tm["white_thai_pua_text"] if tm else ""
            base = {
                "archive": k[0], "file_id": k[1], "message_id": k[2],
                "source_sha256": sha, "source_text": original,
                "master_thai_pua": tha,
                "control_signature": "|".join(control_signature(original)),
                "status": "PENDING", "scene_id": "", "reviewer": "",
                "notes": "No ROM injection or emulator evidence provided",
            }
            reason = ""
            if flag(row["omega_custom"]):
                reason = "OMEGA_CUSTOM_DO_NOT_OVERWRITE"
            elif row["status"] == "THAI_IN_ROM":
                reason = "THAI_ALREADY_IN_P35_SNAPSHOT_RETEST_PER_BUILD"
            elif not original.strip():
                reason = "EMPTY"
            elif not tm:
                reason = "NO_WHITE_TH_MEMORY_AT_SAME_ID"
            elif original != tm["white_english"]:
                reason = "SOURCE_MISMATCH_EXACT_TEXT"
            elif not tha or not PUA.search(tha):
                reason = "NO_NATIVE_PUA_MASTER_TEXT"
            elif row["white_thai_master"] and row["white_thai_master"] != tha:
                reason = "INVENTORY_AND_MASTER_THAI_CONFLICT"
            elif control_signature(original) != control_signature(tha):
                reason = "CONTROL_SIGNATURE_MISMATCH"
            elif len(source_variants.get((k[0], original,
                                          control_signature(original)), set())) > 1:
                reason = "AMBIGUOUS_SAME_SOURCE_DIFFERENT_THAI"
            elif not flag(row["reuse_master_available"]) or not flag(row["control_safe_master"]):
                reason = "PREVIOUS_AUDIT_FLAG_NOT_SAFE"
            elif current == tha:
                reason = "MASTER_ALREADY_PRESENT"
            else:
                # Do not call a row reviewed based on an exact English match.
                base["status"] = "STATIC_MATCH_CONTEXT_PENDING"
                cand.writerow(base)
                stats["STATIC_MATCH_CONTEXT_PENDING"] += 1
                # A candidate might also have manually confirmed context.
                review = approved.get(k)
                if review:
                    if (review["qa_status"] == "REVIEWED"
                        and review["source_sha256"] == sha
                        and review["scene_id"].strip()
                        and review["reviewer"].strip()):
                        review_base = dict(base, status="REVIEWED_NOT_INJECTED",
                                           scene_id=review["scene_id"],
                                           reviewer=review["reviewer"])
                        app.writerow(review_base)
                        stats["REVIEWED_NOT_INJECTED"] += 1
                    else:
                        stats["APPROVAL_REJECTED"] += 1
                # Detect context-dependent source with conflicting translations.
                signature = (k[0], original, control_signature(original))
                source_to_thai.setdefault(signature, set()).add(tha)
                continue
            hold.writerow(dict(base, status="HELD", reason=reason))
            stats[reason] += 1
    finally:
        cand_file.close()
        hold_file.close()
        app_file.close()

    if expected is not None and count != expected:
        raise ValueError(
            f"Inventory count {count} != expected {expected}. "
            "CSV may be truncated: outputs MUST NOT be used."
        )
    conflicts = sum(1 for values in source_to_thai.values() if len(values) > 1)
    # A source string may have multiple context-sensitive translations;
    # do not silently promote collisions.
    result = {
        "target": "Pokemon Omega Paradox TH P4.0",
        "input_inventory": str(inv_path),
        "input_translation_memory": str(tm_path),
        "inventory_entries_checked": count,
        "memory_keys": len(memory),
        "counts": dict(sorted(stats.items())),
        "source_to_thai_collisions_require_manual_review": memory_collision_count,
        "candidate_collision_count_after_conservative_filter": conflicts,
        "created_nds": False,
        "created_bps": False,
        "full_game_reviewed": False,
        "emulator_verified": False,
        "binary_status": "NOT_BUILT",
        "note": "Static match does not imply matching renderer, gameplay context, pixel width, or release QA.",
    }
    (out_dir / "p40_reuse_audit.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inventory", type=Path, required=True)
    ap.add_argument("--memory", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--approved-context", type=Path)
    ap.add_argument("--expected-count", type=int, default=56700)
    args = ap.parse_args()
    stats = prepare(args.inventory, args.memory, args.out,
                    args.expected_count, args.approved_context)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
