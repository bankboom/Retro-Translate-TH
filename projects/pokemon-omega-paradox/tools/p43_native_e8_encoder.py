#!/usr/bin/env python3
"""Fail-closed Thai -> NDS native dialogue code-unit encoder preflight.

A verified map is required, per renderer.  This script NEVER writes a ROM.
The output is an escaped logical text stream, not NARC ciphertext/ROM bytes.
Do not feed U+0E Thai to the game's serializer or invent E8xx glyph indices.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from pathlib import Path

from omega_control_tokens import CODE

# A mapping row MUST have reproducible emulator evidence, not an assumed shape.
FIELDS = {"renderer", "thai", "native_units", "evidence_build", "evidence_scene",
          "review_state"}
NATIVE = re.compile(r"(?:\\xE8[0-9A-Fa-f]{2})+")
THAI = re.compile(r"[\u0E00-\u0E7F]")
ESCAPED = re.compile(r"\\x[0-9A-Fa-f]{4}")


class MappingRequired(ValueError):
    pass


def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def load_verified_map(path: Path, renderer: str) -> dict[str, str]:
    """Never use font mappings from a different renderer without evidence."""
    mappings = {}
    reverse = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = FIELDS - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"Mapping CSV missing columns: {sorted(missing)}")
        for row in reader:
            if row["renderer"] != renderer:
                continue
            thai = _norm(row["thai"])
            units = row["native_units"]
            if (row["review_state"] != "IN_GAME_VERIFIED"
                    or not row["evidence_build"].strip()
                    or not row["evidence_scene"].strip()):
                # DRAFT row is never a glyph authority, even when E8 exists.
                continue
            if not thai or not THAI.search(thai):
                raise ValueError("verified mapping needs a Thai substring")
            if not NATIVE.fullmatch(units):
                raise ValueError(f"invalid native E8xx code sequence for {thai!r}")
            if thai in mappings and mappings[thai] != units:
                raise ValueError(f"conflicting Thai code units for {thai!r}")
            if units in reverse and reverse[units] != thai:
                raise ValueError(f"ambiguous reverse mapping for {units!r}")
            mappings[thai] = units
            reverse[units] = thai
    return mappings


def encode_visible(text: str, mappings: dict[str, str]) -> str:
    """Encode Thai by longest verified sequence; no unknown Thai fallback."""
    text = _norm(text)
    keys = sorted(mappings, key=lambda s: (-len(s), s))
    out = []
    i = 0
    while i < len(text):
        hit = next((k for k in keys if text.startswith(k, i)), None)
        if hit:
            out.append(mappings[hit])
            i += len(hit)
            continue
        ch = text[i]
        if ord(ch) < 128 and ch != "\\":
            out.append(ch)
            i += 1
            continue
        # Native E8 escapes should never be stuffed as literal user prose.
        raise MappingRequired(f"NO_VERIFIED_NATIVE_MAPPING at codepoint {i}: {ch!r}")
    return "".join(out)


def encode_message(message: str, mappings: dict[str, str]) -> str:
    """Keep all F000/FFFE/FFFF command bytes in exactly the original order."""
    result = []
    cursor = 0
    for match in CODE.finditer(message or ""):
        visible = message[cursor:match.start()]
        result.append(encode_visible(visible, mappings))
        result.append(match.group(0))
        cursor = match.end()
    result.append(encode_visible(message[cursor:], mappings))
    return "".join(result)


def decode_visible(native: str, mappings: dict[str, str]) -> str:
    """Roundtrip the logical native escaped stream, not ROM binary packing."""
    reverse = {v: k for k, v in mappings.items()}
    units = sorted(reverse, key=lambda s: (-len(s), s))
    out = []
    i = 0
    while i < len(native):
        hit = next((t for t in units if native.startswith(t, i)), None)
        if hit:
            out.append(reverse[hit])
            i += len(hit)
            continue
        ch = native[i]
        if ord(ch) < 128 and ch != "\\":
            out.append(ch)
            i += 1
            continue
        raise MappingRequired(f"UNEXPECTED_NATIVE_CODE at {i}: {native[i:i+12]!r}")
    return "".join(out)


def preflight_csv(drafts: Path, map_path: Path, renderer: str,
                  output: Path) -> dict:
    # This report is a gate check only. No binary injection or BPS creation.
    mappings = load_verified_map(map_path, renderer)
    result = {"rows_checked": 0, "encoding_ready": 0, "blocked": 0,
              "block_reasons": {}, "renderer": renderer,
              "rom_modified": False, "bps_created": False}
    reasons = {}
    with drafts.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for required in ("archive", "file_id", "message_id",
                         "draft_thai", "original_english"):
            if required not in (reader.fieldnames or ()):
                raise ValueError(f"draft file missing {required!r}")
        for row in reader:
            result["rows_checked"] += 1
            rid = "/".join(row[x] for x in ("archive", "file_id", "message_id"))
            if not rid.startswith("system/44/") and renderer == "system_44_dialogue":
                # Cross-bank reuse requires independent authority.
                reason = "WRONG_RENDERER_BANK"
            elif row.get("status") not in ("REVIEWED", "IN_GAME_VERIFIED"):
                reason = "CONTEXT_NOT_REVIEWED"
            else:
                try:
                    from omega_control_tokens import equal_tokens
                    if not equal_tokens(row["original_english"], row["draft_thai"]):
                        reason = "CONTROL_TOKEN_MISMATCH"
                    else:
                        native = encode_message(row["draft_thai"], mappings)
                        # Roundtrip visible segments only.
                        decoded = "".join(
                            decode_visible(x, mappings) if i % 2 == 0 else x
                            for i, x in enumerate(
                                re.split(f"({CODE.pattern})", native)
                            )
                        )
                        if decoded != _norm(row["draft_thai"]):
                            reason = "ENCODE_ROUNDTRIP_MISMATCH"
                        else:
                            reason = ""
                except MappingRequired:
                    reason = "MISSING_VERIFIED_GLYPH"
            if reason:
                result["blocked"] += 1
                reasons[reason] = reasons.get(reason, 0) + 1
            else:
                result["encoding_ready"] += 1
    result["block_reasons"] = dict(sorted(reasons.items()))
    assert result["rows_checked"] == result["encoding_ready"] + result["blocked"]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--drafts", type=Path, required=True)
    ap.add_argument("--mapping", type=Path, required=True)
    ap.add_argument("--renderer", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    print(json.dumps(preflight_csv(args.drafts, args.mapping,
                                   args.renderer, args.out),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
