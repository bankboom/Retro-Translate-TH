# AI Retro Game Translation Framework V3.2.1 — Codex Chat-first

**คุณภาพคำแปลไทย + ฟอนต์ไทยอ่านง่าย + ความเสถียรของแพตช์ + ประหยัดโทเคน**

อ่าน [`README_CHAT_FIRST.md`](README_CHAT_FIRST.md) และ [`docs/V3_2_REGRESSION_AND_RELEASE_TH.md`](docs/V3_2_REGRESSION_AND_RELEASE_TH.md).

**เริ่มจากแชต Codex:** นำ ZIP นี้ไปให้ Codex เข้าถึงแล้วคัดลอกข้อความจาก `START_V3_2_CODEX_CHAT_TH.txt` ส่งให้ Codex ตั้งค่าหรืออัปเกรดเอง โดยผู้ใช้ไม่ต้องรัน BAT. เปิดแชตใหม่หลังติดตั้ง Skill/AGENTS ใหม่. จากนั้นสั่ง `ใช้คู่มือ V3.2.1 แปลเกม <พาธ ROM>` หรือ `ใช้คู่มือ V3.2.1 ทำเกมเดิมต่อจากจุดล่าสุด`.

- มีเครื่องมือจริงสำหรับ NDS/GBA header, BPS, CSV/TM, Thai character sanity, binary-diff guard, QA review queue, font scene plan, release evidence audit.
- V3.2.1 เพิ่มเครื่องมือสแกน candidate ARM/Thumb แบบออฟไลน์; ต้องยืนยัน code range, RAM base และ ISA เองก่อนใช้ และผลไม่ใช่ disassembly หรือหลักฐาน xref ที่ยืนยันแล้ว.
- ไม่ใช่ one-click auto-translate universal ROM engine; game-specific adapter, real emulator testing, and human review remain required.
- ThaiPUA-informed shared composite-glyph workflow (NDS / 3DS / PC): see [`docs/THAI_PUA_CROSS_PLATFORM_TH.md`](docs/THAI_PUA_CROSS_PLATFORM_TH.md) and optional read-only [`tools/thai_composite_plan.py`](tools/thai_composite_plan.py). No ROM editing or emulator PASS is implied.
- ไม่มี ROM/BIOS/แพตช์ของเกมใดรวมในชุดนี้.
