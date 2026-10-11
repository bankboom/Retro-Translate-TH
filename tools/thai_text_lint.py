#!/usr/bin/env python3
"""Conservative, offline Thai-text sanity checks. NOT a grammar or emulator validator."""
from __future__ import annotations
import argparse
import collections
import csv
import json
import re
from pathlib import Path
import sys

TOKEN_RE = re.compile(r'(\{[^{}]+\}|\[[A-Z_][A-Z_0-9]*\]|<[a-zA-Z][^<>]*>|\\[nrt]|%(?:\d+\$)?[+#0 .\-]*\d*(?:\.\d+)?[sdfixXu])')
MARKS = set(chr(i) for i in [0x0e31, *range(0x0e34, 0x0e3b), *range(0x0e47, 0x0e4f)])
TONES = set('่้๊๋')


def lint_pair(source: str, thai: str) -> list[str]:
    issues = []
    if '\ufffd' in thai:
        issues.append('REPLACEMENT_GLYPH')
    if collections.Counter(TOKEN_RE.findall(source)) != collections.Counter(TOKEN_RE.findall(thai)):
        issues.append('POSSIBLE_CONTROL_TOKEN_CHANGE')
    for idx, ch in enumerate(thai):
        if ch in MARKS and (idx == 0 or thai[idx-1].isspace()):
            issues.append('ORPHAN_COMBINING_MARK'); break
    if any(thai[i] in TONES and thai[i-1] in TONES for i in range(1,len(thai))):
        issues.append('CONSECUTIVE_TONE_MARKS')
    return issues


def audit(path: Path, cap: int = 30) -> dict:
    with path.open('r', encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        if not {'ID', 'Thai'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV must have ID and Thai columns')
        counts=collections.Counter(); examples=[]; checked=0
        for row in reader:
            thai=row.get('Thai', '') or ''
            if not thai.strip(): continue
            checked+=1
            original=row.get('Source_Text') or row.get('English') or ''
            issues=lint_pair(original, thai)
            counts.update(issues)
            if issues and len(examples)<cap:
                examples.append({'Bank':row.get('Bank', ''),'ID':row.get('ID', ''),'issues':issues})
    return {'checked_translated_entries':checked,'issue_counts':dict(counts),'examples':examples,
            'caution':'Heuristic only. Thai spelling/grammar, meaning, glyph beauty, font metrics and emulator play must be reviewed separately.'}


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True);p.add_argument('--output')
    args=p.parse_args(argv)
    try:
        result=audit(Path(args.csv))
        content=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content,encoding='utf-8')
        print(content,end='')
        return 0
    except (OSError,ValueError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
