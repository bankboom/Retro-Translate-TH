#!/usr/bin/env python3
"""Read-only CSV/TSV Thai localization preflight; NOT ROM injection or text shaping."""
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

TOKEN = re.compile(r'\{[^{}]*\}|<[^<>]*>|\\[nt]')
def analyze(path, source='source', target='thai', key='id', advances=None, max_chars=35, max_pixels=None):
    rows = csv.DictReader(path.read_text(encoding='utf-8-sig').splitlines(), delimiter='\t' if path.suffix.lower()=='.tsv' else ',')
    columns = rows.fieldnames or []
    needed = {source,target,key}
    if not needed.issubset(columns):
        raise ValueError('Missing columns: '+', '.join(sorted(needed-set(columns))))
    problems=[]; seen=set(); count=0; unmeasured=0
    for line,row in enumerate(rows,2):
        count+=1
        rid=row.get(key) or ''
        origin=row.get(source) or ''
        thai=row.get(target) or ''
        if not rid or rid in seen:
            problems.append({'line':line,'id':rid,'code':'MISSING_OR_DUPLICATE_ID'})
        seen.add(rid)
        if not thai.strip():
            problems.append({'line':line,'id':rid,'code':'EMPTY_TRANSLATION'})
        if Counter(TOKEN.findall(origin))!=Counter(TOKEN.findall(thai)):
            problems.append({'line':line,'id':rid,'code':'CONTROL_TOKEN_MISMATCH'})
        lines=thai.split('\\n')
        for section in lines:
            visible=TOKEN.sub('',section)
            if len(visible)>max_chars:
                problems.append({'line':line,'id':rid,'code':'CODEPOINT_LIMIT_ADVISORY','count':len(visible)})
            if max_pixels is not None:
                if advances is None or any(c not in advances for c in visible):
                    unmeasured+=1
                    problems.append({'line':line,'id':rid,'code':'UNMEASURED_PIXEL_WIDTH'})
                else:
                    estimate=sum(advances[c] for c in visible)
                    if estimate>max_pixels:
                        problems.append({'line':line,'id':rid,'code':'PIXEL_ADVANCE_ESTIMATE_EXCEEDED','estimated':estimate})
    return {'rows':count,'issues':problems,'unmeasured_lines':unmeasured,'warning':'Pixel advance sum ignores shaping, mark offsets, and renderer behavior; emulator testing required.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input',type=Path)
    ap.add_argument('--source',default='source')
    ap.add_argument('--target',default='thai')
    ap.add_argument('--id',default='id')
    ap.add_argument('--max-chars',type=int,default=35)
    ap.add_argument('--max-pixels',type=int)
    ap.add_argument('--advances',type=Path,help='Optional JSON char-to-pixel-advance from verified target font')
    ap.add_argument('--output',type=Path)
    args=ap.parse_args()
    advances=json.loads(args.advances.read_text(encoding='utf-8')) if args.advances else None
    result=analyze(args.input,args.source,args.target,args.id,advances,args.max_chars,args.max_pixels)
    body=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(body,encoding='utf-8')
    else: print(body,end='')
    return 1 if result['issues'] else 0

if __name__=='__main__':
    raise SystemExit(main())
