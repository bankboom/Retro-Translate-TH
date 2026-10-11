#!/usr/bin/env python3
"""Codex-friendly workspace initializer and read-only project status.
Only standard-library dependencies. No ROM bytes are copied into project directories.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sys

from retro_translate_v3 import read_rom, rom_info, audit_csv

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = {
    'NES', 'SNES', 'GB', 'GBC', 'GBA', 'NDS', 'MASTER_SYSTEM', 'GAME_GEAR',
    'MEGA_DRIVE', 'WONDERSWAN', 'NEO_GEO_POCKET', 'PC_ENGINE', 'NEO_GEO',
    'N64', 'PS1', 'PS2', 'PSP', 'GAMECUBE', 'WII', '3DS', 'SATURN',
    'DREAMCAST', 'ARCADE', 'PC_CLASSIC'
}
DIRS = ('analysis','translations','fonts','builds','patches','qa/screenshots',
        'qa/reports','scripts','working','docs','logs')
GATES = {
    'G0': 'ROM identity / baseline provenance',
    'G1': 'Binary and patch integrity',
    'G2': 'Translation inventory, context and token QA',
    'G3': 'Thai font, diacritics and layout visual QA',
    'G4': 'Emulator gameplay, save and load QA',
    'G5': 'Release readiness and reproducibility',
}


def slugify(text: str) -> str:
    # Path separators and '..' are rejected, never silently sanitized into a safe-looking name.
    if not text.strip() or '/' in text or '\\' in text or '..' in text:
        raise ValueError('Invalid project slug/path; use a simple filename')
    slug = re.sub(r'[^a-z0-9_-]+','-',text.strip().lower()).strip('-_')
    if not slug or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,59}', slug):
        raise ValueError('Provide --slug using 1-60 ASCII letters, digits, dash or underscore')
    return slug


def load_profile(project: Path) -> dict:
    f = project / 'project_profile.json'
    if not f.is_file(): raise ValueError('Not a project: missing project_profile.json')
    return json.loads(f.read_text(encoding='utf-8'))


def write_json(p: Path, value: dict) -> None:
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def init_project(args) -> Path:
    slug = slugify(args.slug or args.game)
    plat = args.platform.upper()
    if plat not in SUPPORTED:
        raise ValueError('Unknown platform. Choose from: ' + ', '.join(sorted(SUPPORTED)))
    root = Path(args.output_root).expanduser().resolve() if args.output_root else (ROOT / 'projects')
    project = root / slug
    if project.exists(): raise ValueError(f'Project already exists; refusing overwrite: {project}')
    # Project directory is created only after input validation.
    scan = None
    if args.rom is not None:
        rom_path = Path(args.rom).expanduser().resolve(strict=True)
        scan = rom_info(read_rom(rom_path), rom_path.name)
        if scan['platform'] != plat and scan['platform'] != 'UNKNOWN / GENERIC BINARY':
            raise ValueError(f'Platform mismatch: chosen {plat}, file identified as {scan["platform"]}')
    root.mkdir(parents=True, exist_ok=True)
    project.mkdir()
    try:
        for d in DIRS:
            p = project / d
            p.mkdir(parents=True, exist_ok=True)
            (p / '.gitkeep').write_text('', encoding='utf-8')
        for src,dest in [('translation_master_template.csv','translations/master.csv'),
                         ('glossary_template.csv','translations/glossary.csv'),
                         ('control_codes_template.csv','translations/control_codes.csv'),
                         ('playtest_scenes_template.csv','qa/playtest_scenes.csv'),
                         ('PROJECT_AGENTS.template.md','AGENTS.md'),
                         ('PROJECT_WORKFLOW.template.md','docs/WORKFLOW.md')]:
            shutil.copyfile(ROOT / 'templates' / src, project / dest)
        profile = {
            'schema_version': '3.2', 'project_slug': slug, 'game_title': args.game,
            'platform': plat, 'region': args.region, 'revision': args.revision,
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'source_rom': {
                'path': str(rom_path) if scan is not None else None,
                'provenance': 'UNVERIFIED — confirm legitimate clean dump and exact revision',
                'observed_sha256': scan['sha256'] if scan else None,
                'observed_crc32': scan['crc32'] if scan else None,
                'expected_clean_sha256': None, 'expected_clean_crc32': None,
            },
            'baseline_patch': None, 'candidate_patch': None,
            'emulator': None, 'adapter_status': 'NEEDS_GAME_SPECIFIC_IMPLEMENTATION',
            'notes': 'No automatic text extraction, injection, patch generation or emulator test has run.'
        }
        write_json(project / 'project_profile.json', profile)
        statuses={k:{'status':'PENDING','description':v,'evidence':[],'reviewer':None}
                  for k,v in GATES.items()}
        write_json(project/'qa/gates.json',{'schema_version':'3.0','gates':statuses})
        (project/'docs/NEXT_TASK.md').write_text(
            f'# Next Codex task — {args.game}\n\n'
            '1. Read root `AGENTS.md` and this project `AGENTS.md`.\n'
            '2. Validate ROM identity and region/revision (G0) before modification.\n'
            '3. Map text containers, fonts, pointers, compression and dependencies.\n'
            '4. Record evidence, then implement a game-specific adapter if feasible.\n'
            '5. Make one reversible micro-patch; leave G3/G4 PENDING until emulator evidence.\n',encoding='utf-8'
        )
    except Exception:
        shutil.rmtree(project)
        raise
    return project


def status_project(args) -> dict:
    project=Path(args.project).expanduser().resolve()
    profile=load_profile(project)
    gates=json.loads((project/'qa/gates.json').read_text(encoding='utf-8'))['gates']
    csv_file=project/'translations/master.csv'
    result={'project':str(project),'title':profile['game_title'],
            'platform':profile['platform'],'source_rom':profile['source_rom'],
            'gate_statuses':{k:v['status'] for k,v in gates.items()},
            'translation':audit_csv(csv_file) if csv_file.is_file() else None}
    if args.output:
        write_json(Path(args.output), result)
    return result


def inspect_rom(args) -> dict:
    p=Path(args.rom).expanduser().resolve(strict=True)
    info=rom_info(read_rom(p),p.name)
    if args.output:
        dest=Path(args.output)
        dest.parent.mkdir(parents=True, exist_ok=True)
        write_json(dest,info)
    return info


def main(argv=None):
    p=argparse.ArgumentParser(description='RetroTranslate V3: initialize/manage independent Codex projects')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('init',help='Create a new independent game project (never copies a ROM)')
    a.add_argument('--game',required=True,help='Human-readable game title')
    a.add_argument('--platform',required=True,help='NDS, GBA, SNES, PS1, etc.')
    a.add_argument('--slug',help='ASCII folder name, recommended for Thai titles')
    a.add_argument('--region',default='UNKNOWN')
    a.add_argument('--revision',default='UNKNOWN')
    a.add_argument('--rom',help='Optional ROM path to scan; original stays untouched')
    a.add_argument('--output-root',help='Optional projects directory, mainly for tests')
    b=sub.add_parser('status',help='Read project profile, gate state and CSV; no changes')
    b.add_argument('--project',required=True)
    b.add_argument('--output')
    c=sub.add_parser('inspect',help='Read-only generic ROM info and hash report')
    c.add_argument('--rom',required=True)
    c.add_argument('--output')
    args=p.parse_args(argv)
    try:
        if args.command=='init':
            obj=init_project(args)
            print('CREATED:',obj)
            print('Next: read',obj/'docs/NEXT_TASK.md','in Codex; project folder was created automatically')
        else:
            result = status_project(args) if args.command=='status' else inspect_rom(args)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError,OSError,KeyError,json.JSONDecodeError) as e:
        print('ERROR:',str(e),file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':sys.exit(main())
