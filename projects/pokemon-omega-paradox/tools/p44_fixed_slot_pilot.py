#!/usr/bin/env python3
"""Conservative, fixed-size logical message pilot for Omega NDS.

Takes NATIVE, previously extracted E8xx dialogue units. No UTF-8 Thai
encoding, no guessed glyphs, no ROM mutation. This is a fixed-length
message preparation step, NOT a BPS/NARC packer or emulator verification.

Use a single archive/member/message ID from the P3.7B verified renderer.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

from omega_control_tokens import CODE, tokens

NATIVE_GLYPH = re.compile(r"\\xE8[0-9A-Fa-f]{2}")
CONTROL_SPLIT = re.compile("(" + CODE.pattern + ")", re.S)
HEX_ESCAPE = re.compile(r"\\x[0-9A-Fa-f]{4}")
ASCII = frozenset(chr(i) for i in range(0x20, 0x7F))


class UnsafePilot(ValueError):
    pass


def _parts(message: str):
    """Split into visible segments and exact ordered control token payloads."""
    parts = CONTROL_SPLIT.split(message)
    return parts[::2], parts[1::2]


def _len_source(segment: str) -> int:
    """Only plain printable ASCII is supported for an IN_PLACE smoke pilot.

    Anything else needs the game's actual encoder and code-unit accounting.
    """
    if any(c not in ASCII for c in segment):
        raise UnsafePilot("SOURCE_NON_ASCII_REQUIRES_ROM_CODEUNIT_DECODER")
    return len(segment)


def _len_native(segment: str) -> int:
    """Count a proven E8 escape as one native 16-bit code unit."""
    i = 0
    total = 0
    while i < len(segment):
        match = NATIVE_GLYPH.match(segment, i)
        if match:
            total += 1
            i = match.end()
        elif segment[i] in ASCII and segment[i] != "\\":
            total += 1
            i += 1
        else:
            raise UnsafePilot(f"INVALID_OR_UNPROVEN_NATIVE_UNIT_AT_{i}")
    return total


def _provenance(record: dict) -> None:
    """Source-traceable reference only; user asserts extracted bytes.

    This cannot cryptographically prove that the units occur at the claimed
    ROM location. The BPS builder MUST re-extract and compare bytes.
    """
    required = (
        "archive", "file_id", "message_id", "original_english",
        "native_reference", "renderer", "reference_rom_sha256",
        "reference_archive", "reference_file_id",
        "reference_message_id", "evidence_state",
    )
    if any(not (record.get(k) or "").strip() for k in required):
        raise UnsafePilot("MISSING_REFERENCE_PROVENANCE")
    if record["renderer"] != "system_44_dialogue":
        raise UnsafePilot("WRONG_RENDERER_BANK")
    if record["archive"] != "system" or record["file_id"] != "44":
        raise UnsafePilot("PILOT_SCOPE_ONLY_SYSTEM_44")
    if not re.fullmatch(r"[0-9a-fA-F]{64}", record["reference_rom_sha256"]):
        raise UnsafePilot("INVALID_REFERENCE_ROM_SHA256")
    if record["evidence_state"] not in ("REFERENCE_EXTRACTED", "IN_GAME_VERIFIED"):
        raise UnsafePilot("REFERENCE_NOT_EXTRACTED")
    if record["reference_archive"] != "system" or record["reference_file_id"] != "44":
        raise UnsafePilot("REFERENCE_BANK_MISMATCH")


def prepare_fixed_slot(record: dict) -> dict:
    """Build fixed-capacity escaped logical text without shifting controls.

    Risk note: equal codeunit count != equal rendered width, correctness,
    dialog progression, pointer integrity, or safety of a real ROM patch.
    """
    _provenance(record)
    source = record["original_english"]
    native = record["native_reference"]
    s_segments, s_controls = _parts(source)
    n_segments, n_controls = _parts(native)
    if s_controls != n_controls or tokens(source) != tokens(native):
        raise UnsafePilot("CONTROL_OPCODE_OR_OPERAND_MISMATCH")
    if len(s_segments) != len(n_segments):
        raise UnsafePilot("DIFFERENT_VISIBLE_SEGMENT_COUNT")
    capacities = [_len_source(x) for x in s_segments]
    used = [_len_native(x) for x in n_segments]
    if any(u > cap for u, cap in zip(used, capacities)):
        raise UnsafePilot("NATIVE_SEGMENT_EXCEEDS_FIXED_SLOT")
    if not any(NATIVE_GLYPH.search(x) for x in n_segments):
        raise UnsafePilot("NO_NATIVE_E8_THAI_REFERENCE")
    pad = [cap - u for cap, u in zip(capacities, used)]
    output = []
    for i, seg in enumerate(n_segments):
        output.append(seg + (" " * pad[i]))
        if i < len(n_controls):
            output.append(n_controls[i])
    escaped = "".join(output)
    out_segments, out_tokens = _parts(escaped)
    assert out_tokens == s_controls
    assert [_len_native(s) for s in out_segments] == capacities
    return {
        "archive": record["archive"], "file_id": record["file_id"],
        "message_id": record["message_id"], "renderer": record["renderer"],
        "reference_archive": record["reference_archive"],
        "reference_file_id": record["reference_file_id"],
        "reference_message_id": record["reference_message_id"],
        "reference_rom_sha256": record["reference_rom_sha256"].lower(),
        "evidence_state": record["evidence_state"],
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "native_source_sha256": hashlib.sha256(native.encode("utf-8")).hexdigest(),
        "capacities_in_codeunits": capacities,
        "native_used_codeunits": used,
        "padding_codeunits": pad,
        "escaped_fixed_slot_message": escaped,
        "control_signature_preserved": True,
        "source_codeunit_positions_preserved_in_logical_stream": True,
        "actual_reference_bytes_verified_against_rom": False,
        "context_approved": False,
        "bps_created": False,
        "emulator_verified": False,
        "status": "SMOKE_PREPARED_REFERENCE_PROVENANCE_PENDING_BINARY_QA",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    with args.input_csv.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 1:
        raise UnsafePilot("EXACTLY_ONE_MESSAGE_PER_SMOKE_PILOT")
    result = prepare_fixed_slot(rows[0])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "escaped_fixed_slot_message"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
