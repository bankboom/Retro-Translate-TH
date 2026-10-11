#!/usr/bin/env python3
"""Initialize or resume a game project from a Codex chat with no manual mkdir.
ROMs are never copied or modified. Platform extension is a hint, not clean-ROM proof.
"""
from __future__ import annotations
import argparse
import hashlib
import zlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from types import SimpleNamespace
from project_manager import SUPPORTED, init_project, status_project
from retro_translate_v3 import read_rom, rom_info, MAX_ROM_BYTES

EXTENSION_PLATFORM={
    '.nds':'NDS','.srl':'NDS','.gba':'GBA','.gbc':'GBC','.gb':'GB',
    '.nes':'NES','.sfc':'SNES','.smc':'SNES','.3ds':'3DS','.cia':'3DS',
    '.n64':'N64','.z64':'N64','.v64':'N64','.ws':'WONDERSWAN',
    '.wsc':'WONDERSWAN','.gg':'GAME_GEAR','.sms':'MASTER_SYSTEM',
    '.md':'MEGA_DRIVE','.gen':'MEGA_DRIVE','.gdi':'DREAMCAST',
}

def safe_slug(title,plat):
    norm=unicodedata.normalize('NFKD', title)
    norm=''.join(c for c in norm if not unicodedata.combining(c))
    slug=re.sub(r'[^a-z0-9]+','-',norm.lower()).strip('-')[:43].strip('-')
    return slug or (plat.lower()+'-'+hashlib.sha256(title.encode('utf8')).hexdigest()[:10])

def title_from_path(path):
    return re.sub(r'\s*\((USA|EUR|Europe|Japan|JPN|Rev\s*\d+)[^)]*\)', '',path.stem,flags=re.I).strip() or path.stem

def existing_projects(root):
    if not root.is_dir():return []
    return sorted((p for p in root.iterdir() if p.is_dir() and (p/'project_profile.json').is_file()),key=lambda x:x.name)

def select_matching(root, sha, path, game, plat):
    candidates=[]
    for p in existing_projects(root):
        try: prof=json.loads((p/'project_profile.json').read_text(encoding='utf8'))
        except (ValueError,OSError):continue
        src=prof.get('source_rom') or {}
        if prof.get('platform')!=plat:continue
        previous_sha=src.get('observed_sha256')
        if sha and previous_sha:
            if previous_sha==sha: candidates.append(p)
            continue  # Same path but changed ROM bytes is not a match.
        if path and not sha and src.get('path')==str(path): candidates.append(p);continue
        if not path and prof.get('game_title','').casefold()==game.casefold():candidates.append(p)
    if len(candidates)>1:raise ValueError('Multiple projects match this game; select one explicitly: '+', '.join(str(p) for p in candidates))
    return candidates[0] if candidates else None

def stream_info(path:Path):
    hasher=hashlib.sha256()
    crc=0
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):
            hasher.update(chunk)
            crc=zlib.crc32(chunk,crc)
    return {'platform':'UNKNOWN / GENERIC BINARY','sha256':hasher.hexdigest(),
            'crc32':f'{crc & 0xffffffff:08X}', 'size_bytes':path.stat().st_size}

def find_game(game,output_root):
    root=Path(output_root).expanduser().resolve() if output_root else Path.cwd()/'projects'
    candidates=[]
    for p in existing_projects(root):
        try: profile=json.loads((p/'project_profile.json').read_text(encoding='utf8'))
        except (ValueError,OSError): continue
        if game.casefold() in (profile.get('game_title') or '').casefold() or game.casefold() in p.name.casefold():
            candidates.append(p)
    if not candidates: raise ValueError('No existing project matched: '+game)
    exact=[p for p in candidates if json.loads((p/'project_profile.json').read_text(encoding='utf8')).get('game_title','').casefold()==game.casefold()]
    if len(exact)==1:return exact[0]
    if len(candidates)==1:return candidates[0]
    raise ValueError('Ambiguous game name; specify exact project: '+', '.join(str(p) for p in candidates))

def create_or_resume(rom=None,game=None,platform=None,output_root=None,region='UNKNOWN',revision='UNKNOWN'):
    if not rom and not game:raise ValueError('Provide a readable --rom file or --game title')
    rp=Path(rom).expanduser().resolve(strict=True) if rom else None
    if rp and not rp.is_file():raise ValueError('ROM is not a file')
    plat=(platform or (EXTENSION_PLATFORM.get(rp.suffix.lower()) if rp else None))
    if not plat:
        raise ValueError('Platform is ambiguous; provide --platform (e.g. PS1, PSP, SNES, GBA, NDS)')
    plat=plat.upper()
    if plat not in SUPPORTED:raise ValueError('Unsupported project profile: '+plat)
    name=game or title_from_path(rp)
    root=Path(output_root).expanduser().resolve() if output_root else Path.cwd()/'projects'
    large=bool(rp and rp.stat().st_size>MAX_ROM_BYTES)
    info=(stream_info(rp) if large else rom_info(read_rom(rp),rp.name)) if rp else None
    if info and info['platform'] not in (plat,'UNKNOWN / GENERIC BINARY'):
        raise ValueError(f'Wrong platform: selected {plat}, detected {info["platform"]}')
    sha=info['sha256'] if info else None
    matched=select_matching(root,sha,rp,name,plat)
    if matched:
        return 'EXISTING',matched
    slug=safe_slug(name,plat)
    dest=root/slug
    if dest.exists():
        # Different ROM or region/version: do not reuse accidentally.
        suffix=sha[:10] if sha else hashlib.sha256((name+plat+region+revision).encode('utf8')).hexdigest()[:10]
        slug=(slug[:44].rstrip('-')+'-'+suffix)
        dest=root/slug
    if dest.exists():
        raise ValueError(f'Existing project does not match identity and suffix conflicts: {dest}')
    args=SimpleNamespace(slug=slug,game=name,platform=plat,output_root=str(root),rom=str(rp) if rp and not large else None,region=region,revision=revision)
    project=init_project(args)
    if large:  # Generic disc image: preserve file identity, but no claimed platform-header validation.
        profile_file=project/'project_profile.json'
        profile=json.loads(profile_file.read_text(encoding='utf8'))
        profile['source_rom'].update({'path':str(rp),'observed_sha256':info['sha256'], 'observed_crc32':info['crc32']})
        profile['notes']='Large image hashed by streaming; header/platform remains unverified; G0 PENDING. No ROM bytes copied.'
        profile_file.write_text(json.dumps(profile,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return 'CREATED',project

def main(argv=None):
    p=argparse.ArgumentParser(description='Create/resume a translation workspace from Codex chat')
    sub=p.add_subparsers(dest='cmd',required=True)
    new=sub.add_parser('new')
    new.add_argument('--rom');new.add_argument('--game');new.add_argument('--platform')
    new.add_argument('--output-root');new.add_argument('--region',default='UNKNOWN');new.add_argument('--revision',default='UNKNOWN')
    show=sub.add_parser('status');show.add_argument('--project',required=True)
    find=sub.add_parser('find');find.add_argument('--game',required=True);find.add_argument('--output-root')
    a=p.parse_args(argv)
    try:
        if a.cmd=='new':
            state, project=create_or_resume(a.rom,a.game,a.platform,a.output_root,a.region,a.revision)
            print(state+': '+str(project))
            print('NEXT: Read '+str(project/'docs/NEXT_TASK.md')+'; inspect G0 and project identity before changing any game file.')
        elif a.cmd=='status':
            print(json.dumps(status_project(SimpleNamespace(project=a.project,output=None)),ensure_ascii=False,indent=2))
        else:
            print('FOUND: '+str(find_game(a.game,a.output_root)))
        return 0
    except (ValueError,OSError,KeyError) as e:
        print('ERROR:',e,file=sys.stderr)
        return 2
if __name__=='__main__':raise SystemExit(main())
