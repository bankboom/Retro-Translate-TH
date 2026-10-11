#!/usr/bin/env python3
"""Generates a *test plan*, not a visual test result. No external dependencies."""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import sys

SAMPLES={'upper_vowel':'ิีึืั็','lower_vowel':'ฺุู','tone':'่้๊๋','am':'ำ','descender':'ญฐฎ','long_text':None}
FIELDS=['Bank','ID','Scene','Speaker','Thai','Coverage','Visual_Result','Screenshot_Path','Build_ID','Emulator_Version','Reviewer']


def choose(master: Path, per_feature: int = 3):
    if per_feature < 1 or per_feature > 50: raise ValueError('per-feature must be 1..50')
    with master.open(encoding='utf-8-sig',newline='') as f:
        rdr=csv.DictReader(f)
        if not {'ID','Thai'}.issubset(rdr.fieldnames or []): raise ValueError('Missing ID or Thai')
        rows=list(rdr)
    selected={}; counters={k:0 for k in SAMPLES}
    for row in rows:
        thai=row.get('Thai','') or ''
        if not thai.strip():continue
        categories=[]
        for feature, chars in SAMPLES.items():
            if feature == 'long_text': is_match=len(thai)>=45
            else: is_match=any(c in thai for c in chars)
            if is_match and counters[feature]<per_feature:
                counters[feature]+=1;categories.append(feature)
        if categories:
            key=(row.get('Bank',''),row['ID'])
            selected[key]={**{k:row.get(k,'') or '' for k in FIELDS},
                           'Coverage':'|'.join(categories),'Visual_Result':'PENDING',
                           'Screenshot_Path':'','Build_ID':'','Emulator_Version':'','Reviewer':''}
    missing=[k for k,n in counters.items() if n==0]
    return list(selected.values()),{'selected':len(selected),'coverage_counts':counters,'features_not_found':missing,
                                    'status':'PENDING_VISUAL','note':'Real emulator scene/scale screenshots and human review are required.'}


def main(argv=None):
    p=argparse.ArgumentParser(description='Suggest Thai screen tests from actual extracted rows')
    p.add_argument('--csv',required=True);p.add_argument('--output',required=True);p.add_argument('--per-feature',type=int,default=3)
    x=p.parse_args(argv)
    try:
        src=Path(x.csv).resolve();dest=Path(x.output).resolve()
        if dest==src or dest.exists(): raise ValueError('Refusing to overwrite existing file or input')
        rows,summary=choose(src,x.per_feature)
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore');w.writeheader();w.writerows(rows)
        import json
        print(json.dumps(summary,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError) as exc:
        print('ERROR:',exc,file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
