#!/usr/bin/env python3
"""Install or upgrade V3.2 using the V3.1 managed skill location for compatibility.
Never edits Codex config.toml, other skills, existing projects or ROMs.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import os
import shutil
import sys
from datetime import datetime

ROOT=Path(__file__).resolve().parent.parent
BEGIN='<!-- RETRO_THAI_V3_1_MANAGED_BEGIN -->'
END='<!-- RETRO_THAI_V3_1_MANAGED_END -->'
SKILL_TAG='<!-- RETRO_THAI_V3_1_OWNED_SKILL -->'


def locations(home:Path, codex_home=None):
    home=home.expanduser().resolve()
    if codex_home:
        codex=Path(codex_home).expanduser().resolve()
    elif os.environ.get('CODEX_HOME'):
        codex=Path(os.environ['CODEX_HOME']).expanduser().resolve()
    else:
        codex=home/'.codex'
    return codex,home/'.agents/skills/retro-game-th-v3-1',home/'RetroThaiProjects'

def replace_managed(text:str, insertion:str|None)->str:
    if text.count(BEGIN)!=text.count(END) or text.count(BEGIN)>1:
        raise ValueError('Malformed/duplicate managed markers: manual inspection needed')
    if BEGIN in text:
        before, rem=text.split(BEGIN,1)
        _, after=rem.split(END,1)
        text=before+after
    text=text.rstrip()
    if insertion:
        text+=(('\n\n' if text else '')+BEGIN+'\n'+insertion.strip()+'\n'+END+'\n')
    elif text:
        text+='\n'
    return text

def global_rules():
    return """# เฉพาะงานแปลเกมย้อนยุค / Retro Thai Framework V3.2
เมื่อผู้ใช้พิมพ์ "คู่มือ V3.2", "Framework V3.2", "คู่มือ V3.1", "Framework V3.1", "แปลเกมเป็นไทย" หรือคำสั่งคล้ายกันที่มีเจตนาแปลเกม:
- ใช้ skill ชื่อ `retro-game-th-v3-1` (ชื่อเดิมเก็บไว้เพื่อไม่ให้โปรเจกต์ V3.1 เสียหาย), เนื้อหาเป็น V3.2 ใน `retro-game-th-v3-1/framework/` และอ่านเฉพาะไฟล์ที่จำเป็น.
- เริ่ม/กลับมาทำโปรเจกต์ใน workspace โดยอัตโนมัติ; ห้ามสั่งผู้ใช้สร้างโฟลเดอร์เอง. ตรวจว่ามี ROM ที่ Codex เข้าถึงได้ก่อน; หากไม่พบ ให้ถามไฟล์/พาธเพียงอย่างเดียว.
- คุณภาพความหมาย-ไวยากรณ์-ฟอนต์ไทย-การเล่นจริงมาก่อน token saving. ใช้ approved TM, delta QA queue, regression guard, font scene plan และ evidence release preflight; ห้ามสรุป 100% หากไม่มีหลักฐาน.
- ห้ามแก้ clean ROM หรืออ้างว่าทดสอบ Emulator แล้วโดยไม่มีหลักฐาน; สรุปสถานะ G0–G5 ตามจริง.
อย่าเรียกใช้ framework สำหรับงานที่ไม่เกี่ยวข้องกับแปลเกม."""

def workspace_agents():
    return """# Codex Workspace for RetroThai V3.2
เมื่อได้รับคำสั่งแปลเกม/"Framework V3.2" หรือ "Framework V3.1" ให้เรียกใช้ skill `retro-game-th-v3-1` และอ่านไฟล์ README.md นี้ก่อนเริ่ม.
โปรเจกต์อัตโนมัติอยู่ใน `projects/` ไม่มี ROM ต้นฉบับในโฟลเดอร์นี้โดยอัตโนมัติ.
ห้ามสแกนเกมอื่นโดยไม่จำเป็น ห้ามแก้ ROM ต้นฉบับ หรือสร้าง patch โดยข้าม G0–G5.
"""

def install(home:Path, custom_codex=None):
    codex, skill, workspace = locations(home,custom_codex)
    framework = codex/'retro-game-th-v3-1/framework'
    if framework.resolve()==ROOT.resolve():
        raise ValueError('Installer source cannot equal install target')
    codex.mkdir(parents=True,exist_ok=True)
    agent_file=codex/'AGENTS.md'
    old=agent_file.read_text(encoding='utf8') if agent_file.is_file() else ''
    new=replace_managed(old, global_rules())
    # Do not alter global file until all conflicts checked.
    if skill.exists() and (not (skill/'SKILL.md').is_file() or SKILL_TAG not in (skill/'SKILL.md').read_text(encoding='utf8')):
        raise ValueError('Skill path occupied by non-framework data: '+str(skill))
    if workspace.exists() and workspace.is_file():
        raise ValueError('Expected workspace directory but got file: '+str(workspace))
    if old!=new and agent_file.exists():
        backup=agent_file.with_name('AGENTS.md.before-retro-v3-1.bak')
        if not backup.exists(): shutil.copy2(agent_file,backup)
    # copy framework into a managed directory; overwrite only packaged files, not extra user files
    shutil.copytree(ROOT,framework,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','*.zip'))
    skill.mkdir(parents=True,exist_ok=True)
    (skill/'SKILL.md').write_text((ROOT/'installer/USER_SKILL.md').read_text(encoding='utf8'),encoding='utf8')
    agent_file.write_text(new,encoding='utf8')
    workspace.mkdir(parents=True,exist_ok=True)
    (workspace/'projects').mkdir(exist_ok=True)
    workspace_agents_file=workspace/'AGENTS.md'
    # Don't replace manually edited workspace AGENTS on repeated installs
    if not workspace_agents_file.exists(): workspace_agents_file.write_text(workspace_agents(),encoding='utf8')
    readme=workspace/'README.md'
    if not readme.exists():
        readme.write_text('# RetroThai V3.2 Workspace\n\nเปิดโฟลเดอร์นี้ใน Codex จากนั้นพูดว่า "ใช้คู่มือ V3.2 แปลเกมนี้" พร้อมพาธ ROM ที่คุณมีสิทธิใช้. Codex จะสร้างโปรเจกต์ใน projects/ เอง.\n\nคู่มือเต็มอยู่ที่ `'+str(framework)+'` และบทสนทนาใช้ skill `retro-game-th-v3-1`.\n',encoding='utf8')
    return codex,skill,workspace

def uninstall(home:Path,custom_codex=None):
    codex,skill,workspace=locations(home,custom_codex)
    agent=codex/'AGENTS.md'
    if agent.exists():
        text=agent.read_text(encoding='utf8')
        new=replace_managed(text,None)
        if new!=text: agent.write_text(new,encoding='utf8')
    if skill.exists() and (skill/'SKILL.md').exists() and SKILL_TAG in (skill/'SKILL.md').read_text(encoding='utf8'):
        shutil.rmtree(skill)
    # Retain framework data and workspace/projects to ensure no user data is lost.
    return codex,workspace

def main(argv=None):
    p=argparse.ArgumentParser(description='RetroThai Framework V3.2: once-per-computer Codex integration (V3.1 paths preserved)')
    p.add_argument('command',choices=['install','status','uninstall'])
    p.add_argument('--home',help='Override user home (testing or alternate profile)')
    p.add_argument('--codex-home',help='Override Codex home (for nondefault CODEX_HOME)')
    a=p.parse_args(argv)
    home=Path(a.home).expanduser().resolve() if a.home else Path.home()
    try:
        codex,skill,workspace=locations(home,a.codex_home)
        if a.command=='install':
            install(home,a.codex_home)
            print('INSTALLED: Codex global instruction:',codex/'AGENTS.md')
            print('INSTALLED: reusable skill:',skill/'SKILL.md')
            print('WORKSPACE:',workspace)
            print('NEXT: Open workspace in Codex; start new chat and type: ใช้คู่มือ V3.2 แปลเกมนี้ <path-to-ROM>')
        elif a.command=='status':
            agent=codex/'AGENTS.md'
            print('GLOBAL_RULE:',bool(agent.is_file() and BEGIN in agent.read_text(encoding='utf8')))
            print('SKILL:',bool((skill/'SKILL.md').is_file() and SKILL_TAG in (skill/'SKILL.md').read_text(encoding='utf8')))
            print('FRAMEWORK:',(codex/'retro-game-th-v3-1/framework/AGENTS.md').is_file())
            print('WORKSPACE:',workspace.is_dir())
        else:
            uninstall(home,a.codex_home)
            print('UNINSTALLED managed global rule and skill. Workspace and framework copies were retained.')
        return 0
    except (ValueError,OSError) as e:
        print('ERROR:',e,file=sys.stderr)
        return 2
if __name__=='__main__': raise SystemExit(main())
