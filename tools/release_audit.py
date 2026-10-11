#!/usr/bin/env python3
"""Conservative G0-G5 release preflight; never promotes a gate automatically.

Evidence is a list of workspace-relative file paths in qa/gates.json. Existence
and hashes establish traceability, NOT truth of emulator screenshots or quality.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from retro_translate_v3 import bps_info, BpsError
from pathlib import Path
import sys

GATES=('G0','G1','G2','G3','G4')
STATES={'PASS','PENDING','FAIL','NOT_APPLICABLE'}


def audit_project(project: Path):
    project=project.resolve(strict=True)
    gate_file=project/'qa/gates.json'
    payload=json.loads(gate_file.read_text(encoding='utf8'))
    gates=payload['gates']
    failures=[]; warnings=[]; evidence_checks=[]
    for gate in GATES:
        entry=gates.get(gate,{})
        state=entry.get('status','PENDING')
        if state not in STATES: failures.append(f'{gate}: INVALID_STATUS')
        if state != 'PASS': failures.append(f'{gate}: {state}')
        ev=entry.get('evidence') or []
        if state=='PASS' and not ev: failures.append(f'{gate}: PASS_WITHOUT_EVIDENCE')
        if state=='PASS' and not (entry.get('reviewer') or '').strip():
            failures.append(f'{gate}: NO_SIGNOFF_REVIEWER')
        for rel in ev:
            if not isinstance(rel,str):
                failures.append(f'{gate}: MALFORMED_EVIDENCE');continue
            path=(project/rel).resolve()
            if not path.is_relative_to(project):
                failures.append(f'{gate}: EVIDENCE_OUTSIDE_PROJECT');continue
            if not path.is_file():
                failures.append(f'{gate}: EVIDENCE_MISSING ({rel})');continue
            evidence_checks.append(dict(gate=gate,path=rel,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        if state=='PASS' and gate in ('G3','G4'):
            warnings.append(f'{gate}: screenshot/video/log existence alone does NOT prove genuine emulator coverage')
    patch_manifest=project/'qa/release_manifest.json'
    patch={}
    if not patch_manifest.is_file():
        failures.append('RELEASE_MANIFEST_MISSING')
    else:
        patch=json.loads(patch_manifest.read_text(encoding='utf8'))
        for field in ('build_id','clean_rom_sha256','patch_sha256','patch_path','patch_format','rollback'):
            if not patch.get(field):failures.append(f'MANIFEST_FIELD_MISSING: {field}')
        for field in ('clean_rom_sha256','patch_sha256'):
            if patch.get(field) and not re.fullmatch(r'[0-9a-fA-F]{64}', str(patch[field])):
                failures.append(f'INVALID_SHA256: {field}')
        rel=patch.get('patch_path')
        if rel:
            path=(project/str(rel)).resolve()
            if not path.is_relative_to(project): failures.append('PATCH_OUTSIDE_PROJECT')
            elif not path.is_file(): failures.append('PATCH_MISSING')
            else:
                data=path.read_bytes()
                observed=hashlib.sha256(data).hexdigest()
                patch['observed_patch_sha256']=observed
                if observed != patch.get('patch_sha256','').lower(): failures.append('PATCH_HASH_MISMATCH')
                fmt=str(patch.get('patch_format') or '').upper()
                if fmt=='BPS':
                    try:
                        bps,_,_=bps_info(data, path.name)
                        if not bps['patch_crc_valid']: failures.append('BPS_PATCH_CRC_INVALID')
                        if patch.get('clean_rom_crc32') and bps['source_crc32'] != str(patch['clean_rom_crc32']).upper():
                            failures.append('BPS_SOURCE_CRC_VS_MANIFEST_MISMATCH')
                        patch['bps_patch_crc_valid']=bps['patch_crc_valid']
                    except BpsError: failures.append('INVALID_BPS_FILE')
                else:
                    warnings.append('PATCH_FORMAT_NOT_PARSED: validate with a reputable external format-specific patch tool and record evidence')
    result=dict(project=str(project),decision='BLOCKED' if failures else 'READY_FOR_MANUAL_RELEASE_REVIEW',
                blockers=failures,warnings=warnings,evidence_files=evidence_checks,manifest=patch,
                g5='PENDING',
                note='Manual signoff required; tool only checks presence/hash and never claims emulator passed or sets G5.')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description='G0-G4 evidence preflight; no automatic release approval')
    p.add_argument('--project',required=True);p.add_argument('--output')
    x=p.parse_args(argv)
    try:
        d=audit_project(Path(x.project));s=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
        if x.output:
            path=Path(x.output).resolve()
            project=Path(x.project).resolve()
            if path.exists() or path == project/'qa/gates.json' or path == project/'qa/release_manifest.json':
                raise ValueError('Refusing to overwrite report or input')
            path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding='utf-8')
        print(s,end='')
        return 0 if d['decision'] == 'READY_FOR_MANUAL_RELEASE_REVIEW' else 1
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print('ERROR:',exc,file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
