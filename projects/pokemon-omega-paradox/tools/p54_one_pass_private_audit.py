#!/usr/bin/env python3
"""One-pass private Omega full-data audit, using owner's existing CSVs.

Runs exact 56,700-inventory / 25,976-White TH memory / 270-draft reconciliation
and native donor review in ONE command. Does not edit ROM, invent glyph maps,
claim semantic QA, create BPS, or publish raw text to GitHub.

Fail-closed on missing/truncated data and unexpected source fingerprints.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zlib
from pathlib import Path

from p47_full_scope_merge import DRAFT_FILES, ROOT, audit_drafts_only, merge
from p53_white_native_segment_reuse import audit as audit_native, read_csv

EXPECTED = {
    "inventory_sha256": "d5a680554e1130eb63b99f515b410937179acfb7f943c2420a4e7f4010f65e34",
    "master_sha256": "c352a547d9b44dfc881eafddb1e146e9f1fd4b5a2ec49678e99debcd4b688557",
    "clean_omega_sha256": "29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b",
    "p46_bps_sha256": "48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6",
}


def fingerprint(path: Path) -> dict:
    """Stream hashing: don't load 202-MB original ROM into memory."""
    h = hashlib.sha256()
    crc = 0
    size = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
            crc = zlib.crc32(chunk, crc)
            size += len(chunk)
    return {"sha256": h.hexdigest(), "crc32": f"{crc & 0xffffffff:08x}",
            "bytes": size}


def enforce_digest(path: Path, expected: str | None) -> dict:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    details = fingerprint(path)
    if expected and details["sha256"] != expected:
        raise ValueError(f"INPUT_SHA256_MISMATCH for {path.name}: "
                         f"{details['sha256']} != {expected}")
    return details


def bps_header_audit(bps: Path, clean_rom: Path | None = None) -> dict:
    """Verify BPS trailer and patch CRC, optionally original ROM source CRC.

    The target ROM's CRC is merely DECLARED in BPS until the patch is applied.
    This routine intentionally does not claim to verify the target checksum.
    """
    if bps.stat().st_size < 16:
        raise ValueError("BPS_TRUNCATED")
    with bps.open("rb") as f:
        if f.read(4) != b"BPS1":
            raise ValueError("NOT_A_BPS_PATCH")
        f.seek(-12, 2)
        tail = f.read(12)
    source = int.from_bytes(tail[0:4], "little")
    target = int.from_bytes(tail[4:8], "little")
    recorded_patch = int.from_bytes(tail[8:12], "little")
    crc = 0
    remaining = bps.stat().st_size - 4
    with bps.open("rb") as f:
        while remaining:
            chunk = f.read(min(1024 * 1024, remaining))
            if not chunk:
                raise ValueError("TRUNCATED_PATCH_CRC_STREAM")
            crc = zlib.crc32(chunk, crc)
            remaining -= len(chunk)
    if (crc & 0xffffffff) != recorded_patch:
        raise ValueError("BPS_PATCH_CRC_MISMATCH")
    result = {
        "bps_signature": "BPS1",
        "patch_crc_valid": True,
        "claimed_source_crc32": f"{source:08x}",
        "claimed_target_crc32": f"{target:08x}",
        "target_crc_verified": False,
        "applied_target_sha_verified": False,
    }
    if clean_rom is not None:
        original = fingerprint(clean_rom)
        result["clean_omega_source_crc_matches"] = (
            int(original["crc32"], 16) == source)
        if not result["clean_omega_source_crc_matches"]:
            raise ValueError("BPS_SOURCE_CRC_NOT_CLEAN_OMEGA")
    return result


def run(
    *,
    inventory: Path,
    master: Path,
    out: Path,
    draft_paths: list[Path],
    clean_rom: Path | None = None,
    p46_bps: Path | None = None,
    expected_inventory: int = 56700,
    expected_master: int = 25976,
    expected_drafts: int = 270,
    required_hashes: dict[str, str] | None = None,
) -> dict:
    """Generate private actionable queues only after complete input validation."""
    fingerprints = required_hashes or {}
    inv_fp = enforce_digest(inventory, fingerprints.get("inventory_sha256"))
    master_fp = enforce_digest(master, fingerprints.get("master_sha256"))
    clean_fp = (enforce_digest(clean_rom, fingerprints.get("clean_omega_sha256"))
                if clean_rom else None)
    bps_fp = (enforce_digest(p46_bps, fingerprints.get("p46_bps_sha256"))
              if p46_bps else None)

    draft_report = audit_drafts_only(draft_paths)
    if (draft_report["draft_rows"] != expected_drafts
            or draft_report["unique_message_ids"] != expected_drafts
            or draft_report["counts"].get("MULTIPLE_TRANSLATION_VARIANTS_NEED_CONTEXT")
            or draft_report["counts"].get("CONTROL_MISMATCH")):
        raise ValueError(f"UNSAFE_DRAFT_SET: {draft_report}")
    # Reuse White master / project draft content without uploading the raw
    # datasets to public GitHub or another third-party service.
    master_rows = list(read_csv(master))
    draft_rows = [r for p in draft_paths for r in read_csv(p)]
    if len(master_rows) != expected_master or len(draft_rows) != expected_drafts:
        raise ValueError(f"INPUT_TRUNCATED master={len(master_rows)} "
                         f"drafts={len(draft_rows)}")
    # Validate 56,700 unique original inventory rows before emitting any files.
    n = 0
    seen = set()
    with inventory.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"archive", "file_id", "message_id",
                    "source_english_or_original", "current_p35_message",
                    "needs_translation_review", "omega_custom", "status"}
        if not required.issubset(set(reader.fieldnames or ())):
            raise ValueError("INVENTORY_MISSING_COLUMNS")
        for row in reader:
            key = (row["archive"], row["file_id"], row["message_id"])
            if key in seen:
                raise ValueError(f"INVENTORY_DUPLICATE_ID {key}")
            seen.add(key)
            n += 1
    if n != expected_inventory:
        raise ValueError(f"INVENTORY_TRUNCATED {n} != {expected_inventory}")
    if p46_bps:
        bps_checks = bps_header_audit(p46_bps, clean_rom)
    else:
        bps_checks = None
    # Existing audit already validates complete inventory and all 270
    # original->draft exact-ID source/control pairs. Use it instead of
    # maintaining a second competing inventory state machine.
    out.mkdir(parents=True, exist_ok=True)
    row_review = merge(inventory, draft_paths, out / "inventory", expected_inventory)
    donor_rows, donor_report = audit_native(master_rows, draft_rows)

    with (out / "native_donor_review.csv").open(
            "w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(donor_rows[0]))
        writer.writeheader()
        writer.writerows(donor_rows)

    # Flag rows that MUST NOT be auto-imported even if donor English matches.
    summary = {
        "project": "Pokemon Omega Paradox TH",
        "input_inventory": inv_fp,
        "input_white_thai_master": master_fp,
        "input_clean_rom": clean_fp,
        "input_p46_bps": bps_fp,
        "p46_bps_checks": bps_checks,
        "inventory_rows_verified": n,
        "white_master_rows_verified": len(master_rows),
        "draft_rows_verified": len(draft_rows),
        "draft_qa": draft_report,
        "p47_inventory_audit": row_review,
        "p53_native_donor_audit": donor_report,
        "rom_changed": False,
        "new_bps_created": False,
        "context_qa_complete": False,
        "full_game_emulator_verified": False,
        "release_100_percent_approved": False,
        "limitation": ("Read-only reconciliation. Donor hits and P3.5 Thai "
                       "snapshots do not establish Unicode->PUA mapping, "
                       "correct scene semantics, text pixel width or "
                       "a fully translated ROM."),
    }
    (out / "private_full_audit_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    # Quick-copy index without copyrighted dialogue. Leave full CSV audit in
    # owner's local private workspace; never auto-push it into GitHub.
    (out / "README_RESULTS_TH.txt").write_text(
        "ผลการตรวจฉบับเต็มแบบส่วนตัว\n"
        "private_full_audit_summary.json: สถานะรายส่วนและจำนวนรายการที่ตรวจจริง\n"
        "inventory/p47_all_inventory_states.csv: ตรวจ 56,700 รายการ\n"
        "inventory/p47_context_draft_queue.csv: ข้อความที่มีร่างคำแปล\n"
        "inventory/p47_blockers.csv: รายการควบคุม/ต้นฉบับไม่ตรง\n"
        "native_donor_review.csv: ผลค้นหา Native Thai แบบตรงต้นฉบับ\n"
        "ไม่มีการเปลี่ยน ROM หรือสร้าง BPS ใหม่\n",
        encoding="utf-8")
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", required=True, type=Path)
    p.add_argument("--white-memory", required=True, type=Path)
    p.add_argument("--clean-rom", type=Path)
    p.add_argument("--p46-bps", type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    result = run(
        inventory=args.inventory,
        master=args.white_memory,
        out=args.out,
        draft_paths=[ROOT / "translation" / name for name in DRAFT_FILES],
        clean_rom=args.clean_rom,
        p46_bps=args.p46_bps,
        required_hashes=EXPECTED,
    )
    print(json.dumps({
        "inventory_rows": result["inventory_rows_verified"],
        "white_thai_master_rows": result["white_master_rows_verified"],
        "unique_draft_ids": result["draft_rows_verified"],
        "native_donor_hits": result["p53_native_donor_audit"].get(
            "native_donor_segments_for_review", 0),
        "new_bps_created": False,
        "release_100_percent_approved": False,
        "private_output": str(args.out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
