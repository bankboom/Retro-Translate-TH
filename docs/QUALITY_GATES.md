# Evidence-based quality gates G0–G5

| Gate | PASS เมื่อ | หลักฐานขั้นต่ำ | ข้อห้าม |
|---|---|---|---|
| G0 ROM Identity | ระบุไฟล์ต้นฉบับ+platform+revision ถูกต้องและเทียบ hash ที่เชื่อถือได้ | SHA-256, CRC32, ขนาด, header, source provenance | ห้ามถือว่าไฟล์ชื่อ (USA) เป็นหลักฐาน region |
| G1 Binary integrity | ตัว repack/build/patch ตรวจ round-trip และ checksum ผ่าน | patch input/output hashes, patch CRC, binary diff, deterministic steps | ห้ามถือว่า BPS CRC ผ่านแล้ว gameplay PASS |
| G2 Text QA | ข้อความครบตาม scope ที่ตรวจจริง, ถูกความหมาย และ tokens ไม่เสีย | inventory, mapped source, glossary, QA reviewer, injection mapping | ห้ามใช้ `Thai != blank` เป็น % สมบูรณ์ |
| G3 Thai layout | ฟอนต์ วรรณยุกต์ สระ ไม่มีซ้อน/ตัด/ล้นในฉากทดสอบ | screenshots/video จริง, scene ID, font size, emulator+version | ห้ามอ้าง visual PASS จาก hex dump |
| G4 Gameplay | บูต/เมนู/บทสนทนา/ฉากสำคัญ/เซฟ/โหลดผ่านจริง | emulator log/screenshot + tested build ID | ไม่ทดสอบจริง = PENDING |
| G5 Release | G0-G4 ผ่านตาม scope, แจกแพตช์+manifest+rollback, reproducible | report, candidate checksum, exact source, known issues | ไม่รวม ROM/BIOS ลิขสิทธิ์ |

ค่าทุก Gate: `PASS` / `FAIL` / `PENDING` / `NOT_APPLICABLE`. ต้องมีผู้รับผิดชอบ/evidence และระบุเหตุผลของ `NOT_APPLICABLE`; G3/G4 ปกติไม่ควร N/A สำหรับเกมที่มีข้อความไทย.

## Progress metrics (ไม่ปะปนกัน)
`Inventory`: จำนวนข้อความค้นพบพร้อม coverage ของ bank. `Draft`: รายการที่ AI ใส่คำแปลไทย. `Reviewed`: ตรวจความหมายและ context แล้ว. `Injected`: map ตำแหน่งแปลลง binary ที่ build นี้สำเร็จ. `Verified`: พบและอ่านข้อความใน emulator จริง. 100% ในหนึ่งหมวดไม่เท่ากับ 100% ของเกม.

## Micro-patch QA cases
ทำกรณีอย่างน้อย หนึ่งคำสั้น, ยาวเกินบรรทัด, control token/ตัวแปร, สระ `า`, สระบน-ล่าง+วรรณยุกต์ (`ต้า`, `ตุ`, `สำ`), save/load และข้อความที่ใช้หลายขนาดฟอนต์.

## Release manifest ข้อแนะนำ
Game/Region/Revision/ID, required clean ROM SHA256+CRC32, Patch format/hash, Tool versions, Build scripts/commands, Source Commit ID (ถ้ามี), Gate evidence links, Known issues, Rollback path, QA sign-off.


## เกณฑ์เพิ่มเติม V3.1
G2 ต้องตรวจความหมาย เนื้อเรื่อง ผู้พูด ไวยากรณ์ การสะกด ความสม่ำเสมอของศัพท์, token/placeholder และค่าตัวเลข. ถ้าบริบทไม่พอให้ PENDING/NEEDS_CONTEXT แม้แปลได้ตามตัวอักษร. G3 ต้องตรวจความงามและความชัดเจนจาก screenshot จริง รวม `ต้า/ต้ ตุ สำ น้ำ` ทุกฟอนต์ที่ใช้งาน. Token optimization ห้ามทำให้ bypass Gate ใด ๆ.


## V3.2 release protections
- Candidate G1 needs binary BPS/file identity and reviewed delta-scope from `regression_guard`. A scope PASS alone is **not** full G1 PASS when rebuild/repack checks absent.
- G2 requires contextual meaning/grammar approval, not just a heuristic queue or draft percentage.
- G3/G4 require **real emulator** screenshot/log/playtest and a reviewer; `font_review_plan` itself stays PENDING.
- `release_audit` is conservative evidence preflight; even `READY_FOR_MANUAL_RELEASE_REVIEW` leaves G5=PENDING pending human signoff. It cannot prove evidence authenticity.

## Emulator-First trial vs release gates
A statically checked, reversible 1–5-string smoke candidate may be **presented for emulator testing before full G2–G5 QA**. Record the distinct, non-gate status `SMOKE_READY`, `EMULATOR_NOT_RUN`, `SMOKE_FAIL`, or `SMOKE_PASS` with build ID and evidence. This never automatically marks G1–G5 PASS. A boot-only ASCII patch is only injection proof, not Thai-font or translation proof. If the binary cannot be constructed safely, do not issue a patch; report exact blocker. See `docs/EMULATOR_FIRST_TH.md`.

## Context QA ในทุกเฟส 1–6 (Universal)

ใช้ `docs/SIX_PHASE_CONTEXT_QA_TH.md` เพื่อกำหนด contextual review ต่อ batch ตั้งแต่ Phase 1, ภาพ Emulator ทบทวนคำแปลใน Phase 2, เป้าหมายแปล **reviewed** 50/70/100% ใน Phase 3–5 และ Final QA ใน Phase 6. ตรวจหกเรื่อง: ความหมาย, สถานการณ์/ผู้พูด, ภาษาไทย, ศัพท์เฉพาะ, ความต่อเนื่อง, และรูปแบบ/ตัวแปร/พื้นที่ UI. ข้อมูลไม่พอให้ `NEEDS_CONTEXT` ไม่ใช่ `REVIEWED`. ห้ามตีความ `DRAFT 50%` เป็น `G2 PASS` หรือ `release 50%`. การทดสอบไฟล์ ASCII ที่ใช้พิสูจน์ reinjection เท่านั้นไม่ใช่การผ่าน QA ภาษาไทย. ห้ามใช้ขั้นตอน QA ทั้งเกมเป็นเงื่อนไขที่ปิดกั้น micro-patch ที่ปลอดภัย.
