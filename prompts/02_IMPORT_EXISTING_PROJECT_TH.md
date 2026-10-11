# คำสั่งสำหรับ Codex: รับช่วงเกมที่แปลค้างอยู่

โปรเจกต์: `projects/<SLUG>`

อ่าน root/game AGENTS.md, `docs/MIGRATE_EXISTING_PROJECT.md`, และรายงานเดิมของโครงการ.
โปรดสำรวจฐานแพตช์ที่ใช้งานได้จริง, รุ่น candidate, แหล่ง ROM ที่ตรง, คำแปลเดิม, font glyphs และสคริปต์ต้นทาง โดยไม่เขียนทับอะไร. สร้าง manifest สำหรับ stable/previous/candidate และสรุปผลต่างของแต่ละรุ่น. รักษาฟอนต์/renderer ที่ใช้ได้ไว้เป็น baseline. ตรวจ CSV ว่ามีคำแปลที่ยังไม่ injected หรือยังไม่มี proof in-emulator กี่รายการ. เสนอการแก้ไขรุ่นถัดไปทีละจุดพร้อม rollback. ถ้าขาดหลักฐานทดสอบให้ระบุ PENDING ตรงไปตรงมา.
