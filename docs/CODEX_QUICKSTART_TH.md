# เริ่มต้น V3.0 ใน Codex แบบทำตามได้จริง

## 1. เปิดโฟลเดอร์หลักเป็นโปรเจกต์
แตก ZIP → เปิด Codex Desktop หรือ VS Code + Codex → Open Folder → เลือกโฟลเดอร์หลักที่มีไฟล์ `AGENTS.md` และ `README.md` ไม่ใช่เปิดเฉพาะไฟล์ prompt หรือเลือกโฟลเดอร์ `tools`.

Codex ใช้กฎ repo ใน `AGENTS.md` และอาจอ่าน skills ใน `.agents/skills` ตามงานที่กำลังทำ. แนะนำให้อ่าน `README.md` และสั่ง Codex ให้ดู `AGENTS.md` ด้วยเมื่อเริ่มรอบแรก.

## 2. เปิด Terminal แล้วสร้างโปรเจกต์เกมแรก

```powershell
python tools/project_manager.py init --game "Example Adventure" --platform NDS --slug example-nds --region USA
```

หากเกมที่จะแปลเป็น GBA: `--platform GBA`; 3DS: `--platform 3DS`; SNES: `--platform SNES`. รายชื่อที่รองรับเป็น **project profiles** ไม่ได้แปลว่าทุกเครื่องมี extractor แล้ว.

`init` จะสร้าง `projects/example-nds/` และสำเนาตารางเปล่าให้อัตโนมัติ โดยไม่แตะไฟล์เกมใด ๆ. ถ้าสร้างซ้ำชื่อเดิมจะปฏิเสธการเขียนทับ.

## 3. ให้ Codex เริ่มงาน
คัดลอก prompt ต่อไปนี้เข้า Codex หรือใช้ `prompts/01_START_NEW_PROJECT_TH.md`:

> โปรดอ่าน AGENTS.md ที่ root, `.agents/skills/rom-analysis/SKILL.md`, `docs/QUALITY_GATES.md` และ `projects/example-nds/project_profile.json`. ให้เริ่มจาก G0 แบบ read-only; ถ้าไม่มี ROM หรือไม่ทราบ clean revision ให้รายงาน PENDING พร้อมสิ่งที่ต้องขอ ไม่แก้ ROM เดิม. วิเคราะห์ไฟล์ข้อมูล ฟอนต์ pointer และเสนอ micro-patch 1-5 ข้อความเมื่อมีหลักฐานเพียงพอ. บันทึกรายงานและสรุปไฟล์ที่แก้จริงในภาษาไทย.

## 4. เชื่อมไฟล์ ROM ที่มีสิทธิใช้
วาง ROM ต้นฉบับไว้ **นอก repo** ในโฟลเดอร์ที่ไม่ปรับเปลี่ยน เช่น `D:\MyROMs\Game.nds` แล้วสั่ง:

```powershell
python tools/project_manager.py inspect --rom "D:\MyROMs\Game.nds" --output projects/example-nds/qa/reports/rom_scan.json
```

หากสร้างโปรเจกต์ไปแล้ว ให้ Codex ตรวจ `project_profile.json` และบันทึก `source_rom.path` หลังยืนยัน. **hash ที่อ่านจากไฟล์ครั้งแรกยังไม่พิสูจน์ว่าเป็น clean dump ที่ถูก region/revision**. ต้องเทียบแหล่งอ้างอิงที่เชื่อถือได้หรือ baseline patch ที่ตรงกัน.

## 5. เริ่มแปลอย่างปลอดภัย
ให้ Codex ตรวจชนิดข้อมูลจริงก่อนว่า text เป็น encoding อะไร, compressed ไหม, pointer อยู่ไหน, ฟอนต์มี mapping แบบใด แล้วทำ *round trip* export → import โดยไม่เปลี่ยนเนื้อหาเพื่อพิสูจน์ toolchain. ทดลองข้อความไทยแค่ 1–5 รายการก่อน.

ทำ `translation_master.csv` จากโครงสร้าง `translations/master.csv` และรักษา control codes. ไฟล์ไทยส่วนหนึ่งที่แปลได้ยังไม่ถือว่าใส่กลับ ROM สำเร็จ.

## 6. ตรวจและทดสอบ

```powershell
python tools/retro_translate_v3.py csv-audit --csv projects/example-nds/translations/master.csv
python tools/project_manager.py status --project projects/example-nds
python -m unittest discover -s tests -p "test_*.py" -v
```

ถ้ามี patch BPS:

```powershell
python tools/retro_translate_v3.py audit --rom "D:\MyROMs\Game.nds" --candidate "D:\Patches\candidate.bps" --output projects/example-nds/qa/reports/static_audit.json
```

ตรวจใน emulator ที่ตรงเครื่องเกมโดยผู้ใช้หรือกระบวนการทดสอบที่สังเกตได้จริง; ส่ง screenshot, version, scene และอาการกลับเข้า Codex; อัปเดต gate G3 และ G4 ตามหลักฐานเท่านั้น.

## 7. ทำโปรเจกต์เกมถัดไป
ใช้ `init` อีกครั้งชื่อ/slug ใหม่; Codex ใช้กฎที่ root เดิม แต่ไฟล์ข้อมูล เกม คำแปล แพตช์ และสคริปต์เฉพาะเกมใหม่ต้องแยกกัน.

## ปัญหาที่พบบ่อย
- `python not found`: ติดตั้ง Python, เปิด Terminal ใหม่, ลอง `py -3` แทน `python` บน Windows.
- `missing clean ROM`: งาน G0 ยัง PENDING; ไม่จำเป็นต้องเริ่มสร้าง patch.
- `ROM header unsupported`: ต้องทำ adapter เฉพาะ platform, อย่ายืนยันเครื่อง/region จาก extension อย่างเดียว.
- `Wrong source CRC`: BPS ใช้กับ ROM คนละ revision หรือไม่ใช่ clean; อย่าฝืนใช้งาน.
- `Emulator not available`: G3/G4 PENDING ไม่ใช่ PASS.


## V3.1: โปรเจกต์คุณภาพสูง/ประหยัด token
ดู `prompts/06_QUALITY_FIRST_LOW_TOKEN_TH.md` ก่อนเริ่มสั่ง Codex; ใช้ `token_saver.py pack` คัดเฉพาะบรรทัดใหม่ ไม่ต้องนำ CSV ทั้งเกมเข้าแชต และทวนภาพจริงใน emulator ก่อนผ่าน G3. `suggest` เป็นข้อเสนอเท่านั้น ไม่เปลี่ยน master.
