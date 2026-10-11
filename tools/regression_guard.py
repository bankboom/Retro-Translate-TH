#!/usr/bin/env python3
"""V3.2 binary delta guard. Scope verification only, never visual/gameplay QA.

Input: two ROM-like files, or clean source + two BPS patches. Read-only;
requires an explicit policy of permitted byte intervals for a positive scope PASS.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from retro_translate_v3 import MAX_ROM_BYTES, apply_bps, read_rom


def number(v):
    if isinstance(v, bool):
        raise ValueError('Boolean is not an offset')
    return int(v, 0) if isinstance(v, str) else int(v)


def ranges_from(policy: dict, key: str, length: int):
    parsed = []
    for item in policy.get(key, []):
        a, b = number(item['start']), number(item['end_exclusive'])
        if not (0 <= a < b <= length):
            raise ValueError(f'Invalid {key} range: {item}')
        if key == 'allowed_changes' and not item.get('reason'):
            raise ValueError('Each allowed_changes range must have a documented reason')
        parsed.append((a, b, str(item.get('reason', ''))))
    return parsed


def within(idx: int, intervals):
    return any(a <= idx < b for a,b,_ in intervals)


def audit(baseline: bytes, candidate: bytes, policy: dict | None = None):
    a_hash = hashlib.sha256(baseline).hexdigest()
    b_hash = hashlib.sha256(candidate).hexdigest()
    result = dict(baseline_sha256=a_hash, candidate_sha256=b_hash,
                  baseline_size=len(baseline), candidate_size=len(candidate),
                  changed_bytes=0, changed_regions=0, sample_regions=[],
                  outside_allowed_bytes=0, protected_bytes_changed=0,
                  scope_status='PENDING', visual_qa='PENDING', gameplay_qa='PENDING')
    if len(baseline) != len(candidate):
        result.update(scope_status='FAIL', reason='SIZE_CHANGED: manual binary layout review needed',
                      changed_bytes=None)
        return result
    policy = policy or {}
    allowed = ranges_from(policy, 'allowed_changes', len(baseline))
    protected = ranges_from(policy, 'protected_ranges', len(baseline))
    identity_failure = []
    for key, actual in [('expected_baseline_sha256', a_hash),('expected_candidate_sha256', b_hash)]:
        if policy.get(key) and str(policy[key]).lower() != actual:
            identity_failure.append(key)
    active = None
    examples = []
    for block_start in range(0,len(baseline),65536):
        aa, bb = baseline[block_start:block_start+65536], candidate[block_start:block_start+65536]
        if aa == bb:
            if active is not None:
                result['changed_regions'] += 1
                if len(examples) < 40: examples.append(active)
                active = None
            continue
        for offset,(x,y) in enumerate(zip(aa,bb),block_start):
            if x != y:
                result['changed_bytes'] += 1
                if allowed and not within(offset, allowed): result['outside_allowed_bytes'] += 1
                if within(offset, protected): result['protected_bytes_changed'] += 1
                if active is None: active = [offset, offset+1]
                else: active[1] = offset + 1
            elif active is not None:
                result['changed_regions'] += 1
                if len(examples) < 40: examples.append(active)
                active = None
    if active is not None:
        result['changed_regions'] += 1
        if len(examples) < 40: examples.append(active)
    result['sample_regions'] = [dict(start=f'0x{a:08X}', end_exclusive=f'0x{b:08X}') for a,b in examples]
    if identity_failure:
        result.update(scope_status='FAIL', reason='EXPECTED_HASH_MISMATCH: ' + ', '.join(identity_failure))
    elif result['protected_bytes_changed']:
        result.update(scope_status='FAIL', reason='PROTECTED_RANGE_CHANGED')
    elif allowed and result['outside_allowed_bytes']:
        result.update(scope_status='FAIL', reason='CHANGES_OUTSIDE_ALLOWED_RANGES')
    elif result['changed_bytes'] == 0:
        result.update(scope_status='PASS', reason='NO_BINARY_DIFFERENCE')
    elif not allowed:
        result.update(scope_status='PENDING', reason='NO_APPROVED_CHANGE_RANGES')
    else:
        result.update(scope_status='PASS', reason='ONLY_DECLARED_RANGES_CHANGED; not emulator validation')
    return result


def evaluate(input_baseline: Path | None, input_candidate: Path | None, clean: Path | None,
             baseline_patch: Path | None, candidate_patch: Path | None, policy_path: Path | None):
    if clean:
        if not baseline_patch or not candidate_patch or input_baseline or input_candidate:
            raise ValueError('BPS mode requires --clean-rom --baseline-patch --candidate-patch only')
        src = read_rom(clean)
        a,ainfo = apply_bps(src, baseline_patch.read_bytes())
        b,binfo = apply_bps(src, candidate_patch.read_bytes())
        patch_audit = {'baseline_patch_crc_valid': ainfo['patch_crc_valid'],
                       'candidate_patch_crc_valid': binfo['patch_crc_valid'],
                       'clean_source_sha256': hashlib.sha256(src).hexdigest(),
                       'baseline_patch_sha256': ainfo['patch_sha256'],
                       'candidate_patch_sha256': binfo['patch_sha256']}
    else:
        if not (input_baseline and input_candidate) or baseline_patch or candidate_patch:
            raise ValueError('File mode requires --baseline --candidate (or use complete BPS mode)')
        a, b = read_rom(input_baseline), read_rom(input_candidate)
        patch_audit = {'patch_integrity': 'NOT_CHECKED: raw binary comparison only'}
    policy = json.loads(policy_path.read_text(encoding='utf-8')) if policy_path else None
    return {**audit(a,b,policy), **patch_audit,
            'warning': 'Only checks byte-delta boundaries. Does not validate font shapes, text meaning, game boot, save/load or release.'}


def main(argv=None):
    p=argparse.ArgumentParser(description='Read-only binary regression delta guard')
    for flag in ['baseline','candidate','clean-rom','baseline-patch','candidate-patch','policy','output']:
        p.add_argument('--'+flag)
    x=p.parse_args(argv)
    try:
        d=evaluate(*(Path(getattr(x,f.replace('-','_'))).expanduser().resolve() if getattr(x,f.replace('-','_')) else None
                   for f in ['baseline','candidate','clean-rom','baseline-patch','candidate-patch','policy']))
        payload=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
        if x.output:
            dst=Path(x.output).expanduser().resolve()
            inputs={Path(y).expanduser().resolve() for y in [x.baseline,x.candidate,x.clean_rom,x.baseline_patch,x.candidate_patch,x.policy] if y}
            if dst in inputs or dst.exists(): raise ValueError('Refusing to overwrite existing file or input report path')
            dst.parent.mkdir(parents=True,exist_ok=True)
            dst.write_text(payload,encoding='utf-8')
        print(payload,end='')
        return 1 if d['scope_status']=='FAIL' else 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('ERROR:',exc,file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
