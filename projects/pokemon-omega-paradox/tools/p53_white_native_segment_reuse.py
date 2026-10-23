#!/usr/bin/env python3
"""Mine exact English segment -> native Thai PUA donors from owner-owned White TH TM.

This is a read-only candidate index, NOT a Thai grapheme encoder or ROM patcher.
The exported White source/donor pair is evidence of a text substitution; it is
NOT evidence that Omega context, length, layout or emulator are already safe.

Hard guards:
- same ARCHIVE and FILE/renderer bank, never cross-bank auto-transfer
- unchanged ordered F000 operands and FFFE/FFFF tokens in donor
- exact full visible English SEGMENT equality, no approximate translation
- unique native variants only (ambiguous results blocked)
- per-segment 16-bit logical capacity; no control-position modifications
- all missing/incompatible segments reported as HOLD rather than fabricated
- read-only to game files; no public GitHub export of game text
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from omega_control_tokens import CODE, tokens

ROOT = Path(__file__).resolve().parents[1]
# All user-authored Omega whole-message drafts, including P5.2.
from p47_full_scope_merge import DRAFT_FILES

PUA = re.compile(r"\\x(E[0-9A-Fa-f]{3})", re.I)
ESCAPE = re.compile(r"\\x([0-9A-Fa-f]{4})", re.I)
ASCII_PRINTABLE = frozenset(chr(i) for i in range(32,127))

def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)

def split(text: str):
    commands = tokens(text)
    return CODE.split(text), commands

def native_len(text: str) -> int | None:
    """Return native UTF-16 unit count only for explicit PUA escapes and ASCII."""
    pos = n = 0
    while pos < len(text):
        m = ESCAPE.match(text, pos)
        if m:
            v = int(m.group(1), 16)
            # Exact NFTR/CMAP blocks verified from White TH and P3.7B.
            # E300-E7FF and EA7A-EFFF have no certified font map.
            if not (
                0xE000 <= v <= 0xE0FF
                or 0xE100 <= v <= 0xE1FF
                or 0xE200 <= v <= 0xE2A2
                or 0xE800 <= v <= 0xE8FF
                or 0xE900 <= v <= 0xE9FF
                or 0xEA00 <= v <= 0xEA79
            ):
                return None
            pos = m.end()
        elif text[pos] in ASCII_PRINTABLE and text[pos] != "\\":
            pos += 1
        else:
            return None
        n += 1
    return n

def english_len(text: str) -> int | None:
    # This is the conservative fixed-message pilot limit; no non-ASCII or
    # special escaped source glyphs without direct NDS codeunit verification.
    if all(c in ASCII_PRINTABLE and c != "\\" for c in text):
        return len(text)
    return None

def source_key(r):
    return (r["archive"].strip(), str(r["file_id"]).strip())

def message_key(r):
    return (r["archive"].strip(), str(r["file_id"]).strip(), str(r["message_id"]).strip())

def sha(x):
    return hashlib.sha256(x.encode("utf-8")).hexdigest()

def make_index(master_rows):
    """Build exact per-bank phrase index and an audit; skip unsafe whole messages."""
    index = defaultdict(list)
    counts = Counter()
    total = 0
    for row in master_rows:
        total += 1
        english = row["white_english"]
        native = row["white_thai_pua_text"]
        if tokens(english) != tokens(native):
            counts["rejected_control"] += 1
            continue
        src_segments, src_commands = split(english)
        native_segments, native_commands = split(native)
        if src_commands != native_commands or len(src_segments) != len(native_segments):
            counts["rejected_structure"] += 1
            continue
        for pos, (en, th) in enumerate(zip(src_segments, native_segments)):
            if not en or not th:
                continue
            length = native_len(th)
            if length is None or not PUA.search(th):
                counts["rejected_non_native"] += 1
                continue
            if english_len(en) is None:
                counts["rejected_non_ascii_source"] += 1
                continue
            index[(*source_key(row),en)].append((th, message_key(row), pos, length))
            counts["donor_segments"] += 1
    counts["master_messages_read"] = total
    counts["unique_bank_phrase_keys"] = len(index)
    counts["ambiguous_bank_phrase_keys"] = sum(
        len({x[0] for x in vals}) > 1 for vals in index.values()
    )
    return index, counts

def get_draft(r):
    return (
        r.get("original_english",r.get("source_original","")),
        r.get("draft_thai",r.get("thai_draft","")),
    )

def audit(master_rows, draft_rows):
    index, counts = make_index(master_rows)
    results = []
    seen = set()
    for r in draft_rows:
        key = message_key(r)
        if key in seen:
            raise ValueError(f"Duplicate Omega draft key: {key}")
        seen.add(key)
        src, draft = get_draft(r)
        if tokens(src) != tokens(draft):
            raise ValueError(f"Omega draft control change at {key}")
        segments, controls = split(src)
        details = []
        candidates = []
        all_safe = True
        bank = source_key(r)
        for pos, en in enumerate(segments):
            if not en:
                candidates.append("")
                continue
            expected = english_len(en)
            found = index.get((*bank,en),[])
            alternatives = {x[0] for x in found}
            if not found:
                status = "NO_EXACT_SAME_BANK_DONOR"
                value = ""
            elif len(alternatives) > 1:
                status = "AMBIGUOUS_NATIVE_VARIANTS"
                value = ""
            elif expected is None:
                status = "UNKNOWN_SOURCE_CODEUNIT_LENGTH"
                value = ""
            else:
                value = next(iter(alternatives))
                used = native_len(value)
                status = ("PHRASE_DONOR_REVIEW_ONLY"
                          if used is not None and used <= expected
                          else "NATIVE_EXCEEDS_FIXED_SLOT")
                if status != "PHRASE_DONOR_REVIEW_ONLY":
                    value = ""
            if status != "PHRASE_DONOR_REVIEW_ONLY":
                all_safe = False
            candidates.append(value)
            details.append((pos, status, len(found)))
        # Deliberately NEVER emit a 'ready to inject' result: semantic QA and
        # pixel/emulator certification do not follow from English equality.
        successful = sum(x[1] == "PHRASE_DONOR_REVIEW_ONLY" for x in details)
        counts["omega_full_messages"] += 1
        counts["omega_visible_segments"] += len(details)
        counts["native_donor_segments_for_review"] += successful
        if all_safe and details:
            counts["all_segments_have_donor_pending_context"] += 1
        results.append({
            "archive":key[0], "file_id":key[1], "message_id":key[2],
            "source_sha256":sha(src),
            "visible_segments":len(details),
            "donor_review_segments":successful,
            "full_message_status":("ALL_EXACT_DONORS_HOLD_FOR_CONTEXT_AND_PIXEL"
                                   if all_safe and details else
                                   "INCOMPLETE_EXACT_DONOR_COVERAGE"),
            "segments": "|".join(f"{pos}:{status}:{n}" for pos,status,n in details),
            "rom_injected":False, "emulator_verified":False,
        })
    counts["omega_unique_draft_ids"] = len(seen)
    return results, dict(sorted(counts.items()))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--master", type=Path, required=True,
                   help="Owner-owned P3_5_Reuse_Memory.csv")
    p.add_argument("--draft", type=Path, action="append",
                   help="May be supplied more than once; defaults to project draft files")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--expected-master", type=int, default=25976)
    p.add_argument("--expected-drafts", type=int, default=270)
    args = p.parse_args()
    master = list(read_csv(args.master))
    paths = args.draft or [ROOT/"translation"/n for n in DRAFT_FILES]
    drafts = [r for f in paths for r in read_csv(f)]
    if len(master) != args.expected_master or len(drafts) != args.expected_drafts:
        raise ValueError("Refusing partial source data: master/draft counts do not match")
    rows, summary = audit(master, drafts)
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out/"p53_exact_native_donor_review.csv").open("w",
                encoding="utf-8",newline="") as out:
        writer = csv.DictWriter(out,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.out/"p53_native_donor_summary.json").write_text(
        json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
