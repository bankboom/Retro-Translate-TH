#!/usr/bin/env python3
"""Offline delta + risk review queue. Heuristics, NEVER a semantic Thai verifier."""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import sys
import unicodedata
from thai_text_lint import lint_pair

SOURCE_KEYS=('English','Source_Text','Original','Source')
DONE={'REVIEWED','APPROVED','VERIFIED'}
REVIEW_COLUMNS=('English','Source_Text','Original','Source','Thai','TranslationStatus','Context_Key','Speaker','Scene','Control_Tokens','Max_Width_Px','QA_Note')
QUEUE_COLUMNS=['Bank','ID','English','Thai','Context_Key','Speaker','Scene','TranslationStatus','Priority','Issues']
DIGITS=re.compile(r'(?<![\w])\d+(?:\.\d+)?%?')
AMBIGUOUS=re.compile(r'\b(charge|cast|seal|guard|save|draw|turn|counter|block|level)\b',re.I)


def rows_from(path: Path):
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        r=csv.DictReader(f)
        if not {'ID','Thai','TranslationStatus'}.issubset(r.fieldnames or []) or not any(k in r.fieldnames for k in SOURCE_KEYS):
            raise ValueError('Need ID, Thai, TranslationStatus and source-language column')
        seen=set(); result={}
        for row in r:
            key=(row.get('Bank',''),row['ID'])
            if not row['ID'].strip() or key in seen: raise ValueError(f'Missing or duplicated Bank/ID: {key}')
            seen.add(key);result[key]=row
        return result


def original(r):
    return next((r.get(k,'') for k in SOURCE_KEYS if r.get(k)), '')


def changed(old,new):
    return old is None or any(str(old.get(k,'') or '') != str(new.get(k,'') or '') for k in REVIEW_COLUMNS)


def inspect(row):
    src, th = original(row), row.get('Thai','') or ''
    issues=[]
    if not th.strip(): issues.append('UNTRANSLATED')
    else:
        issues.extend(lint_pair(src,th))
        if unicodedata.normalize('NFC',th) != th: issues.append('NOT_NFC')
        if Counter(DIGITS.findall(src)) != Counter(DIGITS.findall(th)) and DIGITS.search(src):
            issues.append('NUMERIC_DIFFERENCE_REVIEW')
    state=(row.get('TranslationStatus','') or '').upper().strip()
    if th.strip() and state not in DONE: issues.append('NEEDS_CONTEXT_REVIEW')
    if AMBIGUOUS.search(src) and not any((row.get(k) or '').strip() for k in ['Context_Key','Scene','Speaker']):
        issues.append('AMBIGUOUS_WITHOUT_CONTEXT')
    if not issues: return None
    priority='HIGH' if any(x in issues for x in ('UNTRANSLATED','POSSIBLE_CONTROL_TOKEN_CHANGE','REPLACEMENT_GLYPH','NUMERIC_DIFFERENCE_REVIEW','AMBIGUOUS_WITHOUT_CONTEXT','ORPHAN_COMBINING_MARK')) else 'MEDIUM'
    return {**{k:(row.get(k,'') or '') for k in QUEUE_COLUMNS},'English':src,'Priority':priority,'Issues':'|'.join(issues)}


def make_queue(master: Path, previous: Path | None = None, limit: int = 40):
    if limit < 1 or limit > 1000: raise ValueError('limit must be 1..1000')
    current=rows_from(master)
    prior=rows_from(previous) if previous else {}
    delta=[r for k,r in current.items() if changed(prior.get(k),r)]
    flagged=[x for row in delta if (x:=inspect(row))]
    flagged.sort(key=lambda x: (0 if x['Priority']=='HIGH' else 1, x['Bank'],x['ID']))
    summary={'master_rows':len(current),'delta_rows':len(delta),'unchanged_skipped':len(current)-len(delta),
             'flagged_rows':len(flagged),'high_risk':sum(v['Priority']=='HIGH' for v in flagged),
             'medium_risk':sum(v['Priority']=='MEDIUM' for v in flagged),
             'returned_rows':min(len(flagged),limit),'remaining_risk_rows':max(0,len(flagged)-limit),
             'note':'Risk shortlist only; grammar, meaning, graphics and emulator remain unverified.'}
    return flagged[:limit],summary


def main(argv=None):
    p=argparse.ArgumentParser(description='Short AI review queue from changed/unapproved rows')
    p.add_argument('--csv',required=True);p.add_argument('--previous');p.add_argument('--output',required=True)
    p.add_argument('--summary');p.add_argument('--limit',type=int,default=40)
    x=p.parse_args(argv)
    try:
        src=Path(x.csv).resolve();old=Path(x.previous).resolve() if x.previous else None
        out=Path(x.output).resolve(); summary=Path(x.summary).resolve() if x.summary else None
        inputs={src} | ({old} if old else set())
        if out in inputs or out.exists() or (summary and (summary in inputs or summary==out or summary.exists())):
            raise ValueError('Refusing overwrite of input or existing queue/summary')
        rows,stats=make_queue(src,old,x.limit)
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=QUEUE_COLUMNS,extrasaction='ignore');w.writeheader();w.writerows(rows)
        if summary:
            summary.parent.mkdir(parents=True,exist_ok=True)
            summary.write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(stats,ensure_ascii=False,indent=2))
        return 0
    except (ValueError,OSError) as exc:
        print('ERROR:',exc,file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
