#!/usr/bin/env python3
"""Plan Thai composite-glyph demand from translation tables, without modifying game assets.

Inspired by ThaiPUA's cluster-based workflow; does NOT implement ThaiPUA's PUA
mapping, Nintendo glyph encoding, font generation, shaping, ROM writes, or QA gates.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# 42 modern consonants supported by ThaiPUA's current cluster model.
CONSONANTS = frozenset("กขคฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")
BELOW = frozenset("ุู")
ABOVE = frozenset("ัิีึื็ํ")
TONE = frozenset("่้๊๋์")
MARKS = BELOW | ABOVE | TONE
LEADING = frozenset("เแโใไ")
THAI_RANGE = range(0x0E00, 0x0E80)
# Only known generic placeholders. Per-game control-code auditing remains separate.
PROTECTED = re.compile(r"\{[^{}]*\}|<[^<>]*>|\\[nt]")
SARA_AM_TONE = {"่ำ": "ํ่า", "้ำ": "ํ้า", "๊ำ": "ํ๊า", "๋ำ": "ํ๋า"}


def planning_normalize(text: str) -> str:
    """Normalize Sara Am for planning only; never rewrite the source file."""
    for before, after in SARA_AM_TONE.items():
        text = text.replace(before, after)
    return text.replace("ำ", "ํา")


def classify_cluster(consonant: str, following: str) -> tuple[str | None, str | None]:
    """Return canonical consonant/mark cluster or diagnostic for malformed stacking."""
    roles = [[ch for ch in following if ch in group] for group in (BELOW, ABOVE, TONE)]
    if any(len(group) > 1 for group in roles) or (roles[0] and roles[1]):
        return None, "UNSUPPORTED_MARK_COMBINATION"
    return consonant + "".join(group[0] for group in roles if group), None


def scan(text: str) -> tuple[Counter[str], list[dict], set[str]]:
    """Find planned precomposed mark clusters; preserve input and skip common tokens."""
    combos: Counter[str] = Counter()
    issues: list[dict] = []
    specials: set[str] = set()
    cursor = 0
    for match in PROTECTED.finditer(text):
        if match.start() > cursor:
            _scan_plain(planning_normalize(text[cursor:match.start()]), combos, issues, specials)
        cursor = match.end()
    if cursor < len(text):
        _scan_plain(planning_normalize(text[cursor:]), combos, issues, specials)
    return combos, issues, specials


def _scan_plain(text: str, combos: Counter[str], issues: list[dict], specials: set[str]) -> None:
    i = 0
    while i < len(text):
        ch = text[i]
        if ch in CONSONANTS:
            j = i + 1
            while j < len(text) and text[j] in MARKS:
                j += 1
            suffix = text[i + 1:j]
            if suffix:
                canonical, error = classify_cluster(ch, suffix)
                if error:
                    issues.append({"code": error, "offset": i, "text": text[i:j]})
                elif canonical:
                    combos[canonical] += 1
            i = j
            continue
        if ch in MARKS:
            issues.append({"code": "UNATTACHED_MARK", "offset": i, "text": ch})
        elif ch in LEADING:
            specials.add(ch)  # leading vowel requires renderer/bearing validation
        elif ord(ch) in THAI_RANGE and ch not in CONSONANTS and ch not in frozenset("าะๆฯๅ๐๑๒๓๔๕๖๗๘๙., "):
            specials.add(ch)  # standalone/unsupported Thai remains renderer-specific
        i += 1


def build_report(path: Path, thai_column: str = "Thai", id_column: str = "ID",
                 bank_column: str = "Bank", max_slots: int | None = None) -> dict:
    if max_slots is not None and max_slots < 0:
        raise ValueError("max_slots must be nonnegative")
    counts: Counter[str] = Counter()
    uses: dict[str, set[tuple[str, str]]] = defaultdict(set)
    issues: list[dict] = []
    specials: set[str] = set()
    row_count = nonempty = 0
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source, delimiter="\t" if path.suffix.lower() == ".tsv" else ",")
        headers = set(reader.fieldnames or [])
        if not {thai_column, id_column}.issubset(headers):
            raise ValueError(f"Missing columns: {sorted({thai_column, id_column} - headers)}")
        for row_count, row in enumerate(reader, start=1):
            thai_text = row.get(thai_column) or ""
            if not thai_text:
                continue
            nonempty += 1
            bank, rid = (row.get(bank_column) or ""), (row.get(id_column) or "")
            combos, row_issues, special_chars = scan(thai_text)
            counts.update(combos)
            specials.update(special_chars)
            for combo in combos:
                uses[combo].add((bank, rid))
            for issue in row_issues:
                issues.append({"row": row_count, "bank": bank, "id": rid, **issue})
    slots = len(counts)
    glyphs = [{"key": "+".join(f"U+{ord(c):04X}" for c in combo),
               "sample": combo, "uses": counts[combo], "text_ids": len(uses[combo])}
              for combo in sorted(counts, key=lambda k: (-counts[k], tuple(ord(c) for c in k)))]
    return {"kind": "THAI_COMPOSITE_GLYPH_PLAN", "status": "PLAN_ONLY",
            "input": str(path), "rows": row_count, "nonempty_thai_rows": nonempty,
            "unique_composite_candidates": slots, "max_slots_supplied": max_slots,
            "budget_status": "UNMEASURED" if max_slots is None else (
                "OVER_BUDGET" if slots > max_slots else "WITHIN_DECLARED_LIMIT_ONLY"),
            "glyphs": glyphs, "diagnostics": issues,
            "requires_renderer_check": [f"U+{ord(c):04X}" for c in sorted(specials)],
            "limitations": ["no glyph bitmap/font built", "no game encoding or PUA mapping assumed",
                            "not a full Thai shaping engine", "protected tokens require per-game verification",
                            "real emulator evidence needed for G3/G4"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV/TSV with translation rows")
    parser.add_argument("--thai-column", default="Thai")
    parser.add_argument("--id-column", default="ID")
    parser.add_argument("--bank-column", default="Bank")
    parser.add_argument("--max-slots", type=int, help="Verified glyph bank capacity, if known")
    parser.add_argument("--output", type=Path, help="New JSON report; never overwrite existing files")
    args = parser.parse_args(argv)
    try:
        report = build_report(args.input, args.thai_column, args.id_column, args.bank_column, args.max_slots)
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            if args.output.resolve() == args.input.resolve():
                raise ValueError("Refusing to overwrite source file")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("x", encoding="utf-8") as target:
                target.write(payload)
        else:
            print(payload, end="")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
