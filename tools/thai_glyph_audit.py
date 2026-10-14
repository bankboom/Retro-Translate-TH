#!/usr/bin/env python3
"""Read-only Thai character inventory and conservative mark diagnostics.

CSV/TSV with header. Optional fontTools cmap check: NOT Nintendo glyph coverage,
NOT complete Thai shaping, and NOT emulator visual verification.
"""
import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path

MARKS = set(range(0x0E31, 0x0E3B)) | set(range(0x0E47, 0x0E4F))
LEADING = set(range(0x0E40, 0x0E45))
TONES = set(range(0x0E48, 0x0E4C))


def thai(ch):
    return 0x0E00 <= ord(ch) <= 0x0E7F


def inspect_text(value):
    warnings = []
    for i, ch in enumerate(value):
        n = ord(ch)
        if n in MARKS:
            prior = value[i - 1] if i else ''
            if not prior or not thai(prior) or ord(prior) in LEADING:
                warnings.append({'offset': i, 'kind': 'possibly_orphan_mark', 'char': ch})
        if n in TONES and i and ord(value[i-1]) in TONES:
            warnings.append({'offset': i, 'kind': 'consecutive_tone_marks', 'char': ch})
    return warnings


def load_cmap(path):
    try:
        from fontTools.ttLib import TTFont
    except ImportError as exc:
        raise RuntimeError('For --font install fonttools: pip install fonttools') from exc
    f = TTFont(path)
    try:
        return set(f.getBestCmap() or {})
    finally:
        f.close()


def audit(path, column='thai', font=None):
    contents = path.read_text(encoding='utf-8-sig')
    rows = csv.DictReader(contents.splitlines(), delimiter='\t' if path.suffix.lower() == '.tsv' else ',')
    if column not in (rows.fieldnames or []):
        raise ValueError('Missing translation column: ' + column)
    cmap = load_cmap(font) if font else None
    counts, warnings, total = Counter(), [], 0
    for rowno, row in enumerate(rows, 2):
        total += 1
        value = row.get(column) or ''
        counts.update(ch for ch in value if thai(ch))
        warnings.extend({'row': rowno, **warning} for warning in inspect_text(value))
    missing = sorted({ord(ch) for ch in counts if cmap is not None and ord(ch) not in cmap})
    return {
        'source': str(path), 'column': column, 'rows': total,
        'distinct_thai_codepoints': len(counts),
        'thai_characters': [{'char': ch, 'unicode': f'U+{ord(ch):04X}', 'count': n, 'name': unicodedata.name(ch, '')} for ch, n in sorted(counts.items())],
        'warnings': warnings, 'cmap_checked': cmap is not None,
        'missing_font_cmap': [f'U+{cp:04X}' for cp in missing],
        'limitations': ['not Thai shaping', 'not Nintendo glyph mapping', 'emulator screenshot still required']
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    ap.add_argument('--column', default='thai')
    ap.add_argument('--font', type=Path)
    ap.add_argument('--output', type=Path)
    ap.add_argument('--fail-on-missing', action='store_true')
    args = ap.parse_args()
    report = audit(args.input, args.column, args.font)
    content = json.dumps(report, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(content, encoding='utf-8')
    else:
        print(content, end='')
    return 2 if args.fail_on_missing and report['missing_font_cmap'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
