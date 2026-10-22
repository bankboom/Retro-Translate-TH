# Pokémon Omega Paradox TH — P4.2 Translation Draft and Token QA

**วันที่:** 22 ตุลาคม 2026

## ผลงานที่เสร็จในรอบนี้
- P4.1 คำแปลเนื้อเรื่องชุดแรก **40 ID** (เดิม)
- P4.2 ชุดต่อเนื่อง **19 ID** ใน `translation/P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv`
- P4.2B ชุดข้อความที่มี Control Code ซับซ้อน **8 ID** ใน `translation/P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv`
- รวม **67 ID ไม่ซ้ำกัน** สำหรับ P4.1–P4.2 โดยมี **27 ID ใหม่** รอบนี้
- คำแปลใหม่รักษาลำดับรหัสควบคุมและ Operand จาก source จริง ตัด segment แสดงข้อความไม่เกิน 35 codepoints *ตาม static estimate เท่านั้น*
- ทุกคำแปลใหม่ยังเป็น `DRAFT_NEEDS_CONTEXT`, `PIXEL_WIDTH_PENDING` ไม่ใช่การอนุมัติคำแปลตามฉากจริง

## การแก้ตัวตรวจรหัสควบคุม
เดิมตัวตรวจ F000 บางส่วนถือว่าสิ้นสุดที่ `\\x0000` เท่านั้น จึงอาจข้ามรหัสที่มี nonzero operand เช่น `\\xF000븉\\x0001\\x0001`.
เพิ่ม `tools/omega_control_tokens.py` ให้จับ opcode + operand โดยไม่กลืนโทเคน `\\xFFFE`, `\\xFFFF` หรือ `\\xF000` ที่ต่อกัน
และทดสอบทั้งหมดด้วย `tools/test_p42b_complex_controls.py`.

## หลักฐานตรวจสอบ
- [GitHub Actions Run #39775878424](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39775878424)
- ผล: **SUCCESS — 28/28 Python tests** รวม source/draft token parity, uniqueness, 35-codepoint segmentation และตัวแปร F000 ลงท้าย `\\x0001`
- เป็น **static QA ของข้อความ CSV + synthetic tests** ไม่ใช่ ROM build, glyph encoding หรือการรัน Emulator

## ยังไม่เสร็จ (Blockers ที่พิสูจน์ได้)
1. ไม่มี general-purpose/native `E8xx` encoder ที่พิสูจน์ codepoint-to-glyph mapping และ roundtrip สำหรับคำแปล Unicode ไทยใหม่ทุกคำ
2. คำแปลทั้ง 67 ID ต้องผ่าน Context QA ตามฉาก, glossary, ผู้พูดและความต่อเนื่อง รวมถึง pixel width ในเกมจริง
3. ต้องรวมเข้ากับต้นฉบับ Omega ผ่าน NARC/MSG packer ที่ตรวจสอบแล้ว โดยรักษา P3.7B เป็น fallback
4. **ยังไม่มี P4.2 BPS ใหม่** และ **ไม่ได้ทดสอบ Emulator** สำหรับ 27 ID นี้
5. Inventory 56,700 รายการถูกตรวจครบแล้วใน P4.0 แต่ **20,096 แถว** ในคิวเดิมยังต้องคัดกรองและตรวจ/แปลตามจริง ห้ามนับ 67 DRAFT เป็น 67 REVIEWED
6. G1 build ใหม่, G2, G3, G4 และ G5 ยัง PENDING; ห้ามอ้างแปลทั้งเกมเสร็จ 100%

## ขั้นต่อไปแบบไม่วนซ้ำ
- ใช้ P4.0 full-data audit เดิม ห้ามสแกนซ้ำหาก SHA input ไม่เปลี่ยน
- ทำ bank-specific native E8xx encoder จาก glyph mapping ที่ยืนยันแล้ว โดยทดสอบ reversible 1 ID ก่อน
- ทดลอง P3.7B + Cynthia system/44/24 ที่เป็นไทยครบภายใต้ Control Code เดิม; หากไม่ผ่านให้แก้เฉพาะ ID
- เพิ่มร่างคำแปลที่ตรวจบริบทแล้วเข้าสู่ ROM แบบ diff-only 1–5 IDs ต่อ smoke build
- หลัง pipeline ผ่านจึงทำ bulk translation and injection ตาม queue ที่ยังต้องแก้; ไม่อ้างว่าได้ BPS หากไม่มีไฟล์จริง
