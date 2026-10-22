# Pokémon Omega Paradox TH — P4.1 Translation + Control QA Checkpoint

วันที่: 22 ตุลาคม 2026
อ้างอิงฐานข้อมูล: P4.0 Full Real-Data Audit (56,700/56,700 records; 25,976 White TH TM entries)
**สถานะ: STATIC REVIEW/DRAFT UPDATED; NEW ROM/BPS NOT BUILT; NO EMULATOR PASS CLAIMED**

## 1) ความเสี่ยงจาก P3.5 เดิม 9 รายการ

วิเคราะห์ `P4_0_Risk_And_Conflict_Queue.csv` เฉพาะ 9 แถวชนิด `P35_THAI_HARD_CONTROL_DIFFERENCE`: ทั้ง 9 แถวมีจำนวน control operations เท่ากับต้นฉบับ จำนวน `F000븀` และ `F000븁` เท่ากัน และลำดับ/พารามิเตอร์ของ operation อื่นยังคงเหมือนเดิมทุกจุด แต่ลำดับสองรหัสนี้สลับในบางตำแหน่ง อาจเปลี่ยนการเลื่อนหน้าข้อความ

**Static triage: COMPLETE 9/9. Runtime page-flow QA: PENDING 9/9.** ห้ามใช้การสลับคืนอย่างเดาสุ่มหรือแปลว่าโค้ดพังทั้งหมด

อ่านผลรายจุด: `docs/P4_1_P35_CONTROL_REVIEW_9_CASES_TH.md`

## 2) เนื้อเรื่อง Omega ใหม่

เพิ่ม `translation/P4_1_OMEGA_STORY_EARLY_DRAFTS.csv` จำนวน **40 message IDs** ที่เป็นข้อความจริงจากคิว P4.0 เฉพาะเนื้อเรื่อง Omega ช่วงต้น โดยไม่ทับ draft P3.8/P3.9 ที่มีแล้ว

- คำแปลใหม่อยู่ระดับ `DRAFT_NEEDS_CONTEXT` **40 รายการ**; ไม่ใช่ `REVIEWED`
- ลำดับ token `F000` พร้อม operand และ `FFFE/FFFF` ตรงต้นฉบับ **40/40**
- Segment อักษรไทยแบบ Unicode ทั้งหมดไม่เกิน **35 codepoints** หลังย่อข้อความ Fennel; **pixel-width ยังไม่ได้ทดสอบ**
- ชื่อ NPC และศัพท์เกมบางส่วนคงภาษาอังกฤษเพื่อรอ glossary/scene review ตาม Framework
- **ยังไม่เข้ารหัส E8xx และยังไม่ใส่ ROM** ห้ามฉีด Unicode U+0E... เข้าเกมโดยตรง

## 3) Automated QA

Workflow `.github/workflows/omega-p40-static-tests.yml` และชุด `tools/test_p41_draft_integrity.py` ได้รับการอัปเดตแล้ว

**GitHub Actions:** [Run 39763010231](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39763010231) — `success` ยืนยันการ Compile และ **20/20 Python unit tests ผ่าน** รวม 4 ชุดทดสอบ integrity จาก 40 คำแปลใหม่ นี่คือผล Static QA ไม่ใช่ผลแปลครบหรือ Emulator QA

## 4) งานต่อที่ไม่ซ้ำ

1. รักษา P3.7B เป็น fallback (ภาพไทยแสดงแล้วบางข้อความ) และตรวจ Cynthia 44/24 แบบสองบรรทัดตามคำแปลแก้ก่อนหน้า
2. ทำ native dialogue-bank E8xx encoder ที่พิสูจน์ mapping และ roundtrip ได้ ห้ามใช้ PUA จากเมนูผิด bank
3. ตรวจบริบท 40 drafts และทำ glossary การสะกดชื่อ/ยิม/โปเกมอน แล้วเฉพาะ REVIEWED IDs ไปสู่ injection queue
4. ทดสอบ 1–5 ข้อความเมื่อสร้าง BPS ใหม่โดยใช้ source ROM Omega SHA-256 `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`
5. QA page flow 9 จุดเมื่อถึงฉากจริง; ไม่จำเป็นต้องปิดทุกฉากก่อนเริ่มคำแปลใหม่
6. เดินหน้าคิวคัดกรองเดิม 20,096 โดยเน้น Omega 1,619, Story 970, System 17,507 และระบุสถานะราย ID; ห้ามบวกเป็นเปอร์เซ็นต์ตรวจผ่านทั้งเกม

**Gates:** G0 input identity established; G1 new P4.1 BPS=PENDING; G2 Context=PENDING; G3 Thai font per affected scene=PENDING; G4 gameplay=PENDING; G5 release=PENDING.
