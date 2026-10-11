# คู่มือสถาปัตยกรรม AI Retro Game Translation Framework V3.0

## ขอบเขตและหลักการ
V3.0 เป็น repository-template ที่ให้ Codex ดำเนินงาน reverse engineering และ localization เกมย้อนยุคอย่างมีหลักฐาน ไม่ใช่แอปที่แปล ROM ทุกเกมโดยอัตโนมัติ. เก็บ generic tooling ร่วมกับ game-specific adapters โดยไม่รั่วเงื่อนไขจากเกมหนึ่งไปอีกเกม.

## สถาปัตยกรรม

```text
Codex instructions (AGENTS.md)
  |-- discover skills (rom-analysis | thai-localization | patch-qa)
  |-- project_manager.py init ---> projects/<slug>/project_profile.json
  |                                    |-- scripts/ adapter ของเกมนี้
  |                                    |-- analysis/ mapping/pointers
  |                                    |-- translations/master.csv/glossary
  |                                    |-- fonts/ glyph assets/metrics
  |                                    |-- patches/ candidate/stable
  |                                    |-- qa/gates.json, screenshots/reports
  '-- retro_translate_v3.py ---> ROM audit / BPS apply / CSV audit
```

## งาน 6 บทบาท
**ROM Analyst** พิสูจน์ ROM/header/hash/map. **Extractor Engineer** หา text bank, decompression, pointer graph และ round-trip. **Translator** แปลไทยตามบริบท, terminology, UI และ preserve control tokens. **Font Engineer** ทำ glyph map/compositing/advance/mark positions ตาม renderer. **Patch Engineer** build แบบ reproducible/patch clean ROM และ diff. **QA Tester** พิสูจน์ static+visual+gameplay และเขียน reproduction steps.

ไม่ต้องตั้งเป็นหลายโมเดลหรือหลาย agent จริงก็ได้; Codex ตัวเดียวสลับหน้าที่ตามขั้นได้.

## Workflow ที่ห้ามข้าม

1. **Inventory**: read-only ROM metadata และ file listing, xác SHA-256/CRC32, บันทึกแหล่ง ROM และ expected revision
2. **Mechanics**: ค้นหา encoding/control codes, compressed archives, font renderer, pointers, byte order; อธิบายหลักฐาน/ข้อสมมติ
3. **Round-trip**: extractor/repacker ต้องทำ binary round-trip ที่ควบคุมได้ ก่อนแปลข้อความจำนวนมาก
4. **Micro-patch**: แก้ 1–5 ข้อความ + font glyph ที่ต้องใช้, สร้าง candidate ใหม่และ diff
5. **Translate**: export source mapping → draft → review → inject → in-emulator verify แยกสถานะ
6. **Thai font QA**: รวมสระบน/ล่าง/วรรณยุกต์, ระยะ กา มา ภาษา สำ ต้ ตุ, text clipping, text boxes หลาย font sizes
7. **Regression**: boot/dialog/menu/scene transitions/battle/save/load, อาจต้องมี regression matrix สำหรับแต่ละเกม
8. **Release**: patch+hash+exact source revision+known issues+rollback; ROM ต้นฉบับไม่อยู่ใน package

## หลักการออกแบบ adapter ใหม่
- เก็บ `projects/<slug>/scripts` จนกว่าพิสูจน์ว่าเป็นกฎ reusable จริงแล้วจึงย้ายเข้า `tools/adapters` (สร้างได้ภายหลัง).
- ทุก text entry ต้องมี ID ที่สม่ำเสมอและ map กลับตำแหน่ง/ไฟล์ได้; ห้ามเดา offset และแก้ brute force แบบไม่ตรวจ pointer.
- ไม่สันนิษฐานว่า Unicode UTF-8/UTF-16 ใช้ได้กับ renderer; font ROM เก่ามักใช้ tile/index หรือ proprietary encoding.
- ติดตั้งและเลือก CLI เพิ่มเติมเป็นการตัดสินใจของผู้ใช้/สภาพแวดล้อม ไม่ download binary จากเว็บที่ไม่ตรวจสอบโดยอัตโนมัติ.
- ใช้ open-source library/tool ที่สอดคล้อง license และบันทึกเวอร์ชันของเครื่องมือ.

## Build policy
`clean_rom + reproducible adapter/build steps -> test target -> clean-ROM-specific .bps/.ips/.xdelta` (เลือกชนิดตามระบบและข้อจำกัด). ห้ามแจก clean ROM และ BIOS. อย่า apply patch ซ้อนโดยสมมติ; ต้องมี manifest บอก source revision และการจัดลำดับที่พิสูจน์แล้ว.

## Progress/reporting
รายงาน 5 ขั้นคนละตัวหาร: `discovered`, `draft translated`, `human reviewed`, `binary injected`, `emulator verified`; บันทึก `G0..G5` PASS/FAIL/PENDING/N/A พร้อม evidence จริง.
