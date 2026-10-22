#!/usr/bin/env python3
"""Read-only cross-ID reuse finder for Pokemon Omega Paradox TH.

Finds exact-source matches to native White TH strings even if text moved to
another message ID. NEVER encodes or injects a ROM. A match is always a
CONTEXT_PENDING suggestion, never REVIEWED or EMULATOR_VERIFIED.
"""
from __future__ import annotations
import argparse
import csv
import json
from collections import defaultdict, Counter
from pathlib import Path

from p40_reuse_audit import CTRL, PUA, INV_FIELDS, TM_FIELDS, key, read_csv, control_signature

COLUMNS = [
    "archive", "file_id", "message_id", "master_file_id",
    "master_message_id", "source_text", "master_thai_pua",
    "control_signature", "status", "reason",
]


def candidates(inventory: Path, master: Path, output: Path,
               expected_count: int = 56700) -> dict:
    # Fail closed: a paginated Files preview is never a full inventory.
    count = sum(1 for _ in read_csv(inventory, INV_FIELDS))
    if count != expected_count:
        raise ValueError(f"inventory has {count} records, expected {expected_count}")

    # Index only sources that already carry native Thai PUA from the master.
    by_source = defaultdict(list)
    for row in read_csv(master, TM_FIELDS):
        source, thai = row["white_english"], row["white_thai_pua_text"]
        if not source.strip() or not thai or not PUA.search(thai):
            continue
        if control_signature(source) != control_signature(thai):
            continue
        by_source[(row["archive"], source, control_signature(source))].append(row)

    # Distinct native Thai bytecode per source is ambiguous, even if exact
    # English matches. Distinct locations for ONE Thai rendering are okay.
    ambiguous = set()
    for k, variants in by_source.items():
        if len({v["white_thai_pua_text"] for v in variants}) != 1:
            ambiguous.add(k)

    output.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    suggestions = 0
    seen = set()
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in read_csv(inventory, INV_FIELDS):
            k = key(row)
            if k in seen:
                raise ValueError(f"duplicate Omega message key {k}")
            seen.add(k)
            if str(row["omega_custom"]).strip().lower() in {"1", "true", "yes"}:
                counts["OMEGA_CUSTOM_HELD"] += 1
                continue
            if row["status"] == "THAI_IN_ROM":
                # P3.5 snapshot only; MUST check against current P3.7B target
                # before claiming that a message is already translated.
                counts["P35_THAI_SNAPSHOT_HELD"] += 1
                continue
            source = row["source_english_or_original"]
            if not source.strip():
                counts["EMPTY_HELD"] += 1
                continue
            signature = control_signature(source)
            idx = (row["archive"], source, signature)
            matches = by_source.get(idx)
            if not matches:
                counts["NO_EXACT_MASTER_PHRASE"] += 1
                continue
            if idx in ambiguous:
                counts["CONTEXT_COLLISION_HELD"] += 1
                continue
            src = sorted(matches, key=lambda r: (int(r["file_id"]), int(r["message_id"])))[0]
            if (src["archive"], src["file_id"], src["message_id"]) == k:
                counts["SAME_ID_USE_PRIMARY_AUDIT"] += 1
                continue
            thai = src["white_thai_pua_text"]
            if row["current_p35_message"] == thai:
                counts["ALREADY_IDENTICAL_SNAPSHOT_HELD"] += 1
                continue
            if row["white_thai_master"] and row["white_thai_master"] != thai:
                counts["MASTER_CONFLICT_HELD"] += 1
                continue
            writer.writerow({
                "archive": row["archive"], "file_id": row["file_id"],
                "message_id": row["message_id"],
                "master_file_id": src["file_id"],
                "master_message_id": src["message_id"],
                "source_text": source, "master_thai_pua": thai,
                "control_signature": "|".join(signature),
                "status": "STATIC_CROSS_ID_CONTEXT_PENDING",
                "reason": "Exact source, unique Thai variant; requires scene, bank, pixel and baseline check",
            })
            suggestions += 1
            counts["STATIC_CROSS_ID_CONTEXT_PENDING"] += 1

    report = {
        "scope": "Static exact-source cross-message-ID proposals only",
        "inventory_checked": count,
        "master_exact_source_keys": len(by_source),
        "master_ambiguous_source_keys": len(ambiguous),
        "suggestions_not_approved": suggestions,
        "counts": dict(sorted(counts.items())),
        "rom_modified": False,
        "bps_created": False,
        "emulator_tested": False,
        "note": "P3.5 is a snapshot and not the P3.7B build state; verify every candidate against target bank and build.",
    }
    report_path = output.with_suffix(".json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", type=Path, required=True)
    p.add_argument("--memory", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected-count", type=int, default=56700)
    a = p.parse_args()
    print(json.dumps(candidates(a.inventory, a.memory, a.out, a.expected_count),
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
