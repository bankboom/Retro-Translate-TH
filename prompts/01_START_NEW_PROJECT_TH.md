# คำสั่งสำหรับ Codex: เริ่มเกมใหม่

โปรเจกต์: `projects/<SLUG>` (เปลี่ยน <SLUG> เป็นชื่อโฟลเดอร์จริง)

โปรดอ่าน `AGENTS.md` ของ repository และของเกม, `docs/FRAMEWORK_V3_TH.md`, `docs/QUALITY_GATES.md`, `projects/<SLUG>/project_profile.json` และใช้ skill `retro-rom-analysis`.

ทำงานเป็นลำดับ:
1. ตรวจว่าไฟล์ ROM ต้นฉบับมีจริงหรือไม่; ห้ามเดาพาธหรือ region.
2. ตรวจ read-only game/platform/revision, SHA256/CRC32 และบันทึกการตรวจจริง.
3. ตรวจหา text data/font/rendering/encoding/compression/pointer/file tree โดยระบุสิ่งที่ยืนยันได้และสมมติฐานแยกกัน.
4. ทำแผน extraction / injection เฉพาะเกมพร้อมความเสี่ยงและ rollback.
5. ทดสอบ round-trip แบบไม่เปลี่ยนเนื้อหา แล้วทำ micro-patch แค่ 1–5 ข้อความเมื่อเป็นไปได้.
6. อย่าประกาศว่าทำครบ 100%, แปลเสร็จ หรือ emulator ผ่านถ้ายังไม่มีหลักฐาน.

รายงานไฟล์ที่สร้างหรือแก้จริง, ผล G0-G5, blockers และคำสั่งที่ให้ผู้ใช้ทดลองต่อ.
