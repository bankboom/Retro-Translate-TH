#!/usr/bin/env python3
"""AI Retro Game Translation Framework V3 — safe, stdlib-only ROM / BPS / CSV QA.
Read-only by default. Never changes input files. Use ROMs you have rights to modify.
"""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
import struct
import sys
import zlib
from pathlib import Path

MAX_ROM_BYTES = 512 * 1024 * 1024


def crc32(buf: bytes) -> str:
    return f'{zlib.crc32(buf) & 0xffffffff:08X}'


def sha256(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()


def read_rom(p: Path) -> bytes:
    if not p.is_file():
        raise ValueError(f'ROM not found: {p}')
    if p.stat().st_size > MAX_ROM_BYTES:
        raise ValueError('ROM >512 MiB: use a streaming tool for larger disc images')
    return p.read_bytes()


def u32(data: bytes, pos: int) -> int:
    return struct.unpack_from('<I', data, pos)[0]


def rom_info(data: bytes, name: str = '') -> dict:
    info = {'filename': name, 'size_bytes': len(data), 'crc32': crc32(data), 'sha256': sha256(data)}
    suffix = Path(name).suffix.lower()
    if suffix in ('.nds', '.srl') or (suffix not in ('.gba', '.gb', '.gbc') and len(data) >= 0x200 and data[0x0C:0x10].isalnum() and data[0x10:0x12].isalnum() and data[0x20:0x24] != b'\0'*4):
        # Detect NDS from user-supplied filename first; header fields are not proof of a valid ROM.
        if len(data) < 0x200:
            raise ValueError('NDS file too short for header')
        info['platform'] = 'NDS'
        info['game_title'] = data[0:12].rstrip(b'\0').decode('ascii', 'replace')
        info['game_code'] = data[12:16].decode('ascii', 'replace')
        info['maker_code'] = data[16:18].decode('ascii', 'replace')
        sections = {
            'ARM9': (u32(data, 0x20), u32(data, 0x2C)),
            'ARM7': (u32(data, 0x30), u32(data, 0x3C)),
            'FNT': (u32(data, 0x40), u32(data, 0x44)),
            'FAT': (u32(data, 0x48), u32(data, 0x4C)),
            'ARM9_OVERLAY_TABLE': (u32(data, 0x50), u32(data, 0x54)),
            'ARM7_OVERLAY_TABLE': (u32(data, 0x58), u32(data, 0x5C)),
        }
        info['sections'] = {k: {'offset': v[0], 'size': v[1], 'in_bounds':
                         (v[0] + v[1] <= len(data) and (v[1] == 0 or v[0] > 0))}
                            for k, v in sections.items()}
        info['section_bounds_pass'] = all(v['in_bounds'] for v in info['sections'].values())
        # Inspect file allocation entries without guessing compression or strings.
        fat_off, fat_size = sections['FAT']
        if fat_size and fat_size % 8 == 0 and fat_off + fat_size <= len(data):
            total = fat_size // 8
            invalid = 0
            nonempty = 0
            for i in range(total):
                s, e = struct.unpack_from('<II', data, fat_off + i*8)
                if s > e or e > len(data): invalid += 1
                if 0 <= s < e <= len(data): nonempty += 1
            info['nitrofs_fat'] = {'file_count': total, 'nonempty_files': nonempty,
                                  'invalid_entries': invalid, 'bounds_pass': invalid == 0}
        else:
            info['nitrofs_fat'] = {'bounds_pass': False, 'reason': 'bad FAT header or size'}
        return info
    if suffix == '.gba':
        if len(data) < 0xC0: raise ValueError('GBA ROM too short')
        info['platform'] = 'GBA'
        info['game_title'] = data[0xA0:0xAC].rstrip(b'\0').decode('ascii','replace')
        info['game_code'] = data[0xAC:0xB0].decode('ascii','replace')
        checksum = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF
        info['gba_header_checksum_expected'] = f'{checksum:02X}'
        info['gba_header_checksum_actual'] = f'{data[0xBD]:02X}'
        info['gba_header_checksum_pass'] = checksum == data[0xBD]
        return info
    info['platform'] = 'UNKNOWN / GENERIC BINARY'
    return info


class BpsError(ValueError):
    pass


def read_bps_varint(b: bytes, pos: int, limit: int) -> tuple[int,int]:
    value, shift = 0, 1
    for _ in range(12):
        if pos >= limit: raise BpsError('truncated BPS varint')
        x = b[pos]
        pos += 1
        value += (x & 0x7F) * shift
        if x & 0x80: return value, pos
        shift <<= 7
        value += shift
        if value > 2**64: raise BpsError('overflow in BPS varint')
    raise BpsError('too-long BPS varint')


def bps_info(patch: bytes, name: str = '') -> tuple[dict,int,int]:
    if len(patch) < 19 or patch[:4] != b'BPS1':
        raise BpsError('not a BPS1 patch / file too short')
    limit = len(patch) - 12
    pos = 4
    source_size, pos = read_bps_varint(patch,pos,limit)
    target_size, pos = read_bps_varint(patch,pos,limit)
    meta_size, pos = read_bps_varint(patch,pos,limit)
    if pos+meta_size > limit: raise BpsError('metadata outside patch payload')
    metadata = patch[pos:pos+meta_size]
    pos += meta_size
    source_crc, target_crc, patch_crc = struct.unpack_from('<III',patch,limit)
    computed = zlib.crc32(patch[:-4]) & 0xffffffff
    info = {
        'filename': name, 'format': 'BPS1', 'patch_size_bytes': len(patch),
        'patch_sha256': sha256(patch), 'source_size_bytes': source_size,
        'target_size_bytes': target_size,
        'source_crc32': f'{source_crc:08X}', 'target_crc32': f'{target_crc:08X}',
        'patch_crc32_expected': f'{patch_crc:08X}', 'patch_crc32_computed': f'{computed:08X}',
        'patch_crc_valid': computed == patch_crc,
        'metadata_utf8': metadata.decode('utf-8','replace')[:1000] if metadata else '',
    }
    return info, pos, limit


def apply_bps(source: bytes, patch: bytes) -> tuple[bytes,dict]:
    info, pos, limit = bps_info(patch)
    if not info['patch_crc_valid']: raise BpsError('patch CRC32 invalid')
    if len(source) != info['source_size_bytes']:
        raise BpsError(f'wrong source size: expected {info["source_size_bytes"]}, got {len(source)}')
    if crc32(source) != info['source_crc32']:
        raise BpsError(f'wrong source CRC32: expected {info["source_crc32"]}, got {crc32(source)}')
    if info['target_size_bytes'] > MAX_ROM_BYTES:
        raise BpsError('target >512 MiB: unsupported in this memory-based tool')
    out = bytearray()
    src_relative = 0
    dst_relative = 0
    modes = collections.Counter()
    while len(out) < info['target_size_bytes']:
        action, pos = read_bps_varint(patch, pos, limit)
        mode, count = action & 3, (action >> 2) + 1
        if len(out) + count > info['target_size_bytes']: raise BpsError('action exceeds target size')
        modes[['SourceRead','TargetRead','SourceCopy','TargetCopy'][mode]] += 1
        if mode == 0:
            start = len(out)
            if start+count > len(source): raise BpsError('SourceRead out of bounds')
            out.extend(source[start:start+count])
        elif mode == 1:
            if pos+count > limit: raise BpsError('TargetRead out of bounds')
            out.extend(patch[pos:pos+count]); pos += count
        elif mode == 2:
            delta, pos = read_bps_varint(patch,pos,limit)
            src_relative += -(delta >> 1) if delta & 1 else (delta >> 1)
            if src_relative < 0 or src_relative+count > len(source):
                raise BpsError('SourceCopy out of bounds')
            out.extend(source[src_relative:src_relative+count]); src_relative += count
        elif mode == 3:
            delta, pos = read_bps_varint(patch,pos,limit)
            dst_relative += -(delta >> 1) if delta & 1 else (delta >> 1)
            if dst_relative < 0 or dst_relative >= len(out):
                raise BpsError('TargetCopy pointer invalid')
            remaining = count
            while remaining:
                chunk = min(remaining, len(out)-dst_relative)
                if chunk <= 0: raise BpsError('TargetCopy no progress')
                out.extend(out[dst_relative:dst_relative+chunk])
                dst_relative += chunk; remaining -= chunk
    if pos != limit:
        raise BpsError(f'unparsed patch command payload ({limit-pos} bytes)')
    target = bytes(out)
    if crc32(target) != info['target_crc32']:
        raise BpsError(f'target CRC32 mismatch: computed {crc32(target)}, expected {info["target_crc32"]}')
    info['source_crc_valid'] = True
    info['target_crc_valid'] = True
    info['commands_by_mode'] = dict(modes)
    return target, info


def compare_roms(a: bytes, b: bytes, max_regions: int=40) -> dict:
    if len(a)!=len(b):
        return {'same_size': False, 'a_size':len(a), 'b_size':len(b), 'changed_byte_count':None}
    changed = 0
    ranges = []
    max_region = 2000
    # Fast skip equal blocks; run per-byte only when bytes differ.
    active_start, active_end = None, None
    total_regions = 0
    for pos in range(0,len(a),32768):
        ea,eb = a[pos:pos+32768],b[pos:pos+32768]
        if ea==eb:
            if active_start is not None:
                total_regions += 1
                if len(ranges)<max_regions:ranges.append([active_start,active_end])
                active_start,active_end=None,None
            continue
        for i,(x,y) in enumerate(zip(ea,eb)):
            idx=pos+i
            if x!=y:
                changed+=1
                if active_start is None: active_start = idx
                active_end = idx+1
            elif active_start is not None:
                total_regions+=1
                if len(ranges)<max_regions:ranges.append([active_start,active_end])
                active_start,active_end=None,None
    if active_start is not None:
        total_regions+=1
        if len(ranges)<max_regions:ranges.append([active_start,active_end])
    return {'same_size':True,'changed_byte_count':changed,'changed_region_count':total_regions,
            'first_regions_hex':[{'start':f'0x{s:08X}','end_exclusive':f'0x{e:08X}'} for s,e in ranges],
            'note':'Differences are bytes, not verified glyph pixels; gameplay still requires emulator testing.'}


TOKEN_RE = re.compile(r'(\{[^{}]+\}|\[[A-Z_][A-Z_0-9]*\]|<[a-zA-Z][^<>]*>|\\[nrt])')

def audit_csv(path: Path) -> dict:
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        columns=reader.fieldnames or []
        required={'Bank','ID','English','Thai'}
        if not required.issubset(columns): raise ValueError(f'CSV missing columns {sorted(required-set(columns))}')
        count=0; blank=0; thai_present=0; dup=0; token_mismatch=0
        statuses=collections.Counter(); injections=collections.Counter(); banks=collections.Counter()
        identifiers=set(); examples=[]; token_examples=[]
        for row in reader:
            count+=1
            banks[(row.get('Bank') or '').strip()]+=1
            key=((row.get('Bank') or '').strip(),(row.get('ID') or '').strip())
            if key in identifiers:dup+=1
            identifiers.add(key)
            english=row.get('English') or ''
            thai=row.get('Thai') or ''
            if thai.strip():thai_present+=1
            else:
                blank+=1
                if len(examples)<15:examples.append({'Bank':key[0],'ID':key[1],'English':english[:120]})
            statuses[(row.get('TranslationStatus') or '').strip()]+=1
            injections[(row.get('InjectionStatus') or '').strip()]+=1
            src_tokens=collections.Counter(TOKEN_RE.findall(english))
            tgt_tokens=collections.Counter(TOKEN_RE.findall(thai))
            if thai.strip() and src_tokens!=tgt_tokens:
                token_mismatch+=1
                if len(token_examples)<12:
                    token_examples.append({'Bank':key[0],'ID':key[1],
                         'src_tokens':dict(src_tokens),'dst_tokens':dict(tgt_tokens)})
    return {'source_file':path.name,'count':count,'thai_nonempty':thai_present,
            'thai_nonempty_percent':round(thai_present/count*100,2) if count else 0,
            'thai_blank':blank,'duplicate_bank_ids':dup,'token_mismatches_heuristic':token_mismatch,
            'translation_status_distribution':dict(statuses),
            'injection_status_distribution':dict(injections),
            'bank_counts':dict(banks),
            'first_untranslated':examples,'first_possible_token_issues':token_examples,
            'caution':'Nonempty Thai is not QA-approved or proven to have been injected into a playable ROM.'}


def command_audit(args):
    report = {'framework':'AI Retro Game Translation Framework','version':'3.0',
              'emulator_test':'NOT RUN by this CLI', 'safe_mode':'READ ONLY; no ROM included in distribution'}
    rom = read_rom(args.rom)
    report['rom'] = rom_info(rom,args.rom.name)
    report['patches']={}
    target_bytes={}
    for label,p in [('baseline',args.baseline),('candidate',args.candidate),('previous',args.previous)]:
        if not p: continue
        patch = p.read_bytes()
        try:
            target,pinfo=apply_bps(rom,patch)
            pinfo['filename']=p.name
            pinfo['target_rom_info']=rom_info(target,args.rom.name)
            pinfo['changed_from_clean_rom']=compare_roms(rom,target,12)
            report['patches'][label] = {'result':'PASS patch roundtrip / source-target CRC', **pinfo}
            target_bytes[label]=target
        except Exception as e:
            try: info,_,_=bps_info(patch,p.name)
            except Exception: info={'filename':p.name}
            report['patches'][label]={'result':'FAIL','error':str(e),**info}
    for a,b in [('baseline','candidate'),('previous','candidate')]:
        if a in target_bytes and b in target_bytes:
            report[f'compare_{a}_to_{b}']=compare_roms(target_bytes[a],target_bytes[b],30)
    if args.csv:
        report['translation_csv']=audit_csv(args.csv)
    report['gates']={
       'G0_rom_identified': report['rom']['platform']!='UNKNOWN / GENERIC BINARY' and (report['rom'].get('section_bounds_pass', True)) and (report['rom'].get('gba_header_checksum_pass', True)),
       'G1_patch_integrity': ('PENDING' if not report['patches'] else all(v['result'].startswith('PASS') for v in report['patches'].values())),
       'G2_translation_qa_complete':'NOT VERIFIED',
       'G3_thai_font_visual':'NOT VERIFIED — screenshots/emulator required',
       'G4_gameplay_save_load':'NOT VERIFIED — emulator required',
    }
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print('Wrote',args.output)
    print('ROM',report['rom']['platform'],report['rom'].get('game_code'), 'CRC32',report['rom']['crc32'])
    for label, result in report['patches'].items():
        print('PATCH',label,result['result'],'SOURCE',result.get('source_crc32'),'TARGET',result.get('target_crc32'))
    for key in ('compare_baseline_to_candidate','compare_previous_to_candidate'):
        if key in report: print(key,'changed bytes',report[key]['changed_byte_count'])
    if 'translation_csv' in report:
        print('CSV total',report['translation_csv']['count'], 'Thai nonempty', report['translation_csv']['thai_nonempty'], 'blanks',report['translation_csv']['thai_blank'])
    print('Emulator/font/playtest NOT VERIFIED by static scan')
    if report['gates']['G1_patch_integrity'] is False:sys.exit(2)


def command_patch(args):
    rom=read_rom(args.rom)
    patch=args.patch.read_bytes()
    result,info=apply_bps(rom,patch)
    if args.out.resolve()==args.rom.resolve():
        raise ValueError('refusing to overwrite the clean source ROM')
    if args.out.exists() and not args.force:
        raise ValueError(f'output exists (use --force to overwrite): {args.out}')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_bytes(result)
    print('Patched ROM created:',args.out,'size:',len(result),'CRC32:',crc32(result),'target CRC verified:',info['target_crc_valid'])


def command_patch_info(args):
    info,_,_=bps_info(args.patch.read_bytes(),args.patch.name)
    print(json.dumps(info,indent=2,ensure_ascii=False))
    if not info['patch_crc_valid']:sys.exit(2)


def command_csv(args):
    rep=audit_csv(args.csv)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(rep,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in rep.items() if k not in ('first_untranslated','first_possible_token_issues')},indent=2,ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description='RetroTranslate V3 — ROM/BPS/CSV quality gates; stdlib only')
    sub=parser.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('audit',help='Analyze clean ROM, apply patches in memory, compare versions and audit CSV')
    a.add_argument('--rom',required=True,type=Path)
    a.add_argument('--baseline',type=Path)
    a.add_argument('--candidate',type=Path)
    a.add_argument('--previous',type=Path)
    a.add_argument('--csv',type=Path)
    a.add_argument('--output',type=Path)
    a.set_defaults(func=command_audit)
    b=sub.add_parser('apply',help='Apply a BPS patch to a clean ROM and save a new ROM')
    b.add_argument('--rom',required=True,type=Path)
    b.add_argument('--patch',required=True,type=Path)
    b.add_argument('--out',required=True,type=Path)
    b.add_argument('--force',action='store_true')
    b.set_defaults(func=command_patch)
    c=sub.add_parser('bps-info',help='Read patch CRC metadata, without source ROM')
    c.add_argument('--patch',required=True,type=Path)
    c.set_defaults(func=command_patch_info)
    d=sub.add_parser('csv-audit',help='Check translated/blank entries and token controls')
    d.add_argument('--csv',required=True,type=Path)
    d.add_argument('--output',type=Path)
    d.set_defaults(func=command_csv)
    args=parser.parse_args()
    try: args.func(args)
    except (BpsError, ValueError, FileNotFoundError, OSError) as e:
        print('ERROR:',e,file=sys.stderr)
        sys.exit(2)

if __name__=='__main__':main()
