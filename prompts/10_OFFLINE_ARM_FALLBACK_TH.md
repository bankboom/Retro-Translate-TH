ใช้คู่มือ V3.2.1 เพื่อแก้ปัญหาขาด ARM disassembler โดยไม่เริ่มโปรเจกต์เกมใหม่

อ่าน AGENTS.md, docs/OFFLINE_REVERSE_ENGINEERING_TH.md, และเฉพาะ project_profile.json / docs/NEXT_TASK.md ของโปรเจกต์ปัจจุบัน

- เช็กความสามารถด้วย python tools/portable_code_probe.py capabilities ห้ามติดตั้งจาก network โดยพลการ
- ห้ามนำ TraceKit หรือโค้ดอ้างอิงของคนละเกมมาเป็นหลักฐาน
- ทำ inventory / decompression / text table round-trip ของเกมที่ยืนยันแล้วต่อ
- ถ้ารู้ ARM/Thumb instruction mode, RAM base, code range จากหลักฐานของเกมนี้จริง ๆ จึงใช้ portable_code_probe.py scan แบบอ่านอย่างเดียว จำกัดผลลัพธ์และบันทึกเป็น CANDIDATE เท่านั้น
- อย่าเดา event record grammar หรืออาศัย candidate ไปแก้ pointers/ROM; G1–G5 คง PENDING จนมีหลักฐานที่ตรง gate
- รายงาน Changed | Tests | Gates | Blocker | Next สั้น ๆ และทำงานเฉพาะ delta เพื่อลดโทเคน
