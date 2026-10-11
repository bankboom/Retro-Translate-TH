# คู่มือ V3.2 — Regression, Thai QA, Evidence & Token Saving

## เป้าหมายและการเปิดใช้
ตั้งผ่านแชตตาม `START_V3_2_CODEX_CHAT_TH.txt` และสั่ง `ใช้คู่มือ V3.2 แปลเกม...` หรือ `ใช้คู่มือ V3.2 ทำเกม...ต่อ`. ทำงานต่อในโปรเจกต์เดิม; ห้ามย้าย/ลบ ROM, save, TM, โฟลเดอร์เกมเดิมโดยไม่ได้รับอนุญาต.

## คำแปลและภาษาศาสตร์ (G2)
- ความหมาย/เนื้อเรื่อง/ตัวละคร/กติกา/ค่าเลข/placeholder ต้องตรงต้นฉบับ; ไม่แต่งเพิ่ม. ภาษาธรรมชาติถูกไวยากรณ์ คำศัพท์ทั้งซีรีส์คงที่. ต้องมีบริบทจริงก่อนอนุมัติ.
- อนุมัติ TM ข้ามเกมได้เฉพาะบริบทที่ตรวจแล้ว; คำใกล้เคียงเป็นเพียงคำแนะนำ ไม่แก้ master อัตโนมัติ.
- คัดเฉพาะบรรทัดใหม่และมีความเสี่ยงไปให้ AI ดู (ตัวอย่าง):

```bash
python tools/quality_queue.py --csv projects/EXAMPLE/translations/master.csv --previous projects/EXAMPLE/qa/previous_master.csv --limit 40 --output projects/EXAMPLE/working/review_001.csv --summary projects/EXAMPLE/qa/reports/review_001.json
```

`--previous` เป็นไฟล์ snapshot ที่โปรเจกต์เก็บไว้เอง; หากยังไม่มีให้เว้นพารามิเตอร์ดังกล่าว. เอาต์พุตใหม่ต้องใช้ชื่อใหม่เสมอ เครื่องมือจะไม่แก้ master. รายการที่ผ่าน heuristic ยังไม่ได้รับอนุมัติ G2.

## Regression Guard (G1: ตรวจ delta ไม่ใช่เกมเล่นได้)
- เก็บ clean ROM / known-good baseline แยกไฟล์. ตรวจ patched ROM สองรุ่นด้วย `--baseline`, `--candidate` หรือระบุ `--clean-rom`, `--baseline-patch`, `--candidate-patch` สำหรับ BPS.
- ประกาศช่วงที่อนุญาตให้แก้ใน `policy.json` (จุดเริ่มรวม จุดจบไม่รวม). ช่วงจำกัดต้องมาจากการพิสูจน์ offsets ไม่ใช่เดา. ห้ามแก้ protected ranges.

```json
{
  "allowed_changes": [
    {"start":"0x200", "end_exclusive":"0x220", "reason":"verified text/glyph region — example ONLY"}
  ],
  "protected_ranges": [
    {"start":"0x0", "end_exclusive":"0x200", "reason":"header protected — example ONLY"}
  ]
}
```

```bash
python tools/regression_guard.py --baseline path/to/stable_test.nds --candidate path/to/candidate_test.nds --policy path/to/policy.json --output path/to/unique_binary_audit.json
```

หรือ BPS (ต้องมี clean ROM ที่ตรง patch ทั้งสอง):

```bash
python tools/regression_guard.py --clean-rom path/to/clean.nds --baseline-patch path/to/stable.bps --candidate-patch path/to/candidate.bps --policy path/to/policy.json --output path/to/unique_bps_delta.json
```

ถ้าไม่มี policy การเปลี่ยนไบต์จะเป็น PENDING; แก้ไขออกนอกขอบเขตหรือชน protected range เป็น FAIL. ผล `scope_status=PASS` หมายถึง *ขอบเขตไบต์ตรงตาม policy เท่านั้น* ไม่รับรองกติกาเกม/ฟอนต์/ภาพ/บูต/เซฟ. หากเกมเปลี่ยนขนาดไฟล์ต้อง review โครงสร้างเป็นกรณีพิเศษ.

## Thai Font & Layout (G3)

```bash
python tools/font_review_plan.py --csv projects/EXAMPLE/translations/master.csv --output projects/EXAMPLE/qa/reports/font_plan_001.csv
```

ระบบเลือกข้อความจริงที่มีสระบน/ล่าง วรรณยุกต์ `ำ` อักษรทรงยาว และบรรทัดยาว; ต้องทดสอบเพิ่มจากคำมาตรฐาน `กา มา ภาษา ปัญหา น้ำ สำ ต้ ตุ ตุ๊กตา ม้า ผู้ใหญ่`. ทุกภาพทดสอบต้องมาจากเกมใน emulator จริงพร้อม build ID, scene ID, font size, emulator/version, before/after ที่สเกลเท่ากัน และผู้ตรวจยืนยันว่าไม่มีการทับ/ตัด/ลอยผิด. รายการใน font_plan เริ่ม `PENDING` เสมอ ไม่ใช่ภาพทดสอบจริง.

## Gameplay (G4)
ตรวจ boot, title, menu, battle (ถ้ามี), area/script transitions, save/load และฉากที่เปลี่ยน. ไม่อนุญาตให้แปล gameplay PASS จาก checksum, screenshot จำลอง, AI image หรือแค่รันเครื่องมือ.

## Release Preflight (G5)
`qa/gates.json` ต้องมี G0-G4 รายการ PASS พร้อม `reviewer` และ `evidence` เป็นพาธสัมพัทธ์ในโปรเจกต์; ข้อมูลเป็นหลักฐานที่ต้องตรวจได้ด้วยตา/การเล่นจริง. `qa/release_manifest.json` ต้องบรรจุ `build_id`, `clean_rom_sha256`, `patch_sha256`, `patch_path`, `patch_format`, `rollback`; `patch_path` อยู่ภายในโปรเจกต์. ตัวอย่างโครงสร้างดู `templates/release_manifest_template.json`.

```bash
python tools/release_audit.py --project projects/EXAMPLE --output projects/EXAMPLE/qa/reports/preflight_001.json
```

ถ้า `BLOCKED` ให้แก้ blocker. `READY_FOR_MANUAL_RELEASE_REVIEW` ไม่ใช่ G5 PASS; ต้องมี human signoff และตรวจภาพ/emulator จริง. `release_audit` ไม่เปลี่ยน gates.json. ไฟล์หลักฐานนอกโปรเจกต์จะไม่ผ่าน.

## Token Efficiency
1. อ่าน `AGENTS.md`, `project_profile.json`, `docs/NEXT_TASK.md` แล้วเลือกอ่าน docs เฉพาะเรื่อง
2. Python ทำ binary compare, CSV delta, TM index, lint, QA queue; AI อ่านเฉพาะ snippet/ID/context ของบรรทัดเสี่ยง
3. บันทึก snapshot, evidence, QA failures และ stable build metadata; ไม่ส่ง master หรือ log ทั้งไฟล์เข้า LLM ซ้ำ
4. ถ้าไม่มี adapter/extraction/micro-patch ที่ทดสอบแล้ว อย่าแปลจำนวนมากเพื่อสร้างยอด 100%
5. ใช้ `Change → Test → Evidence → Commit/checkpoint`, และบอกต่อรอบสั้น ๆ ว่า changed/tests/gates/blocker/next
