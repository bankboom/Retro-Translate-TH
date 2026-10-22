# Pokémon Omega Paradox TH — P4.3 Native E8xx QA checkpoint

**วันที่:** 22 ตุลาคม 2026
**สถานะ:** P4.3 Static Encoder Gate = ผ่านการทดสอบ, **P4.3 ROM/BPS = ยังไม่สร้าง**
**ไม่ใช่** รายงานแปลครบ 100% หรือ Emulator PASS

## งานที่ลง GitHub จริง
- `tools/p43_native_e8_encoder.py`: แปลงข้อความ Unicode ไทยเป็น logical native E8xx stream เฉพาะเมื่อมี mapping จากฉาก/renderer เดียวกันและสถานะ `IN_GAME_VERIFIED` พร้อม build+scene; ปฏิเสธ glyph ไม่รู้จักและ mapping ขัดแย้ง
- รักษา `F000 + opcode/operands`, `FFFE`, `FFFF` ระหว่างเตรียมข้อความ และทดสอบ encode/decode roundtrip ของแผนที่ตัวอย่าง
- `tools/test_p43_native_e8_encoder.py`: ทดสอบด้วยข้อมูลสังเคราะห์ 10 กรณี
- `tools/p43_preflight_existing_drafts.py`: ตรวจคำแปล P4.1–P4.2 ทุก 67 ID ตามสถานะและหลักฐาน glyph
- `glyph_maps/P4_3_NATIVE_E8_PENDING.csv`: โครงสร้าง mapping ยังว่างโดยตั้งใจ — **ไม่มีหลักฐานรองรับการเดารหัส glyph ใหม่**
- `.github/workflows/omega-p40-static-tests.yml`: ตรวจทั้งหมดใน GitHub Actions และบันทึก artifact ผล Preflight

## ผล CI ที่ตรวจได้จริง
- [GitHub Actions Run 39781176864](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39781176864): **SUCCESS**
- Python compilation + **38/38 synthetic/static unit tests PASS**
- ตรวจคำแปลจาก P4.1, P4.2, P4.2B: **67/67 distinct IDs**
- ผล Preflight: **67 CONTEXT_NOT_REVIEWED**, **0 ผ่าน static encoder readiness**
- แผนที่ renderer ที่มี verified fragment: **0** (ยังไม่อนุมานจากภาพ screenshot ว่า codepoint ไหนเป็น glyph ใด)
- ROM หรือ BPS จากงานใหม่นี้: **ไม่มี**

## สิ่งที่ต้องทำเพื่อสร้างแพตช์ (ห้ามอ้างว่าผ่านล่วงหน้า)
1. อ่านไฟล์ builder จากชุด P3.7B/P3.7A ที่เคยทำงาน และใช้ original Omega ROM SHA-256 `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`; ห้ามสร้าง parser ROM ใหม่โดยไร้เหตุผล
2. จัดทำ bank-specific source-to-native mapping ที่ตรวจจาก **bytes ของ White TH และภาพเกม** ไม่ใช่ค่ารหัส E8xx ที่เดา ให้แยก `REFERENCE_EXTRACTED / SMOKE_ONLY` จาก `IN_GAME_VERIFIED / RELEASE_OK` เพื่อไม่เกิดวงจรติดอยู่กับการขอหลักฐานก่อนสร้างแพตช์ทดลอง
3. ทดลอง **เฉพาะ System 44 / Message 24 (Cynthia)** ภายใต้ control/pointer/length เดิม; รักษา P3.7B เป็น fallback
4. ยืนยัน read-back ROM message, NARC/FAT integrity, source/target BPS CRC/SHA และ differential regression กับ P3.7B ก่อนส่งให้ทดสอบบน melonDS
5. เพิ่มฉากอื่น 1–5 ID ต่อชุด แล้วจึงไปต่อการแปล 20,096 รายการที่คัดกรอง (ไม่ใช่ 20,096 ที่ต้องแปลใหม่ทุก ID)
6. G2, G3, G4 และ G5 ไม่ผ่านจนกว่าจะมี Context QA, real gameplay, และ release evidence

**ขอบเขตหลักฐาน:** ภาพ P3.7B ที่ผู้ใช้ส่ง แสดงข้อความไทย Cynthia หนึ่งบรรทัดเท่านั้น ไม่พิสูจน์ full-game stability.
