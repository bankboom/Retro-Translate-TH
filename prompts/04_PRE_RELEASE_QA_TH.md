# คำสั่งสำหรับ Codex: ตรวจแพตช์ก่อนปล่อย

ใช้ skill `retro-patch-qa` กับ `projects/<SLUG>`.
ยืนยัน source clean ROM revision และ hash. ตรวจ patch source/target integrity, reconstruct ROM แบบแยก output, เปรียบเทียบ delta กับ stable, inventory CSV, glossary and placeholder controls. ตรวจหลักฐานใน emulator จริงสำหรับ boot/menu/dialog/scene transitions/font/save/load. สรุปผล G0-G5 พร้อม evidence. ถ้าขั้นใดยัง PENDING/FAIL ห้ามเรียก production release ให้เสนอ test build พร้อมรายการตรวจที่เหลือ. ส่งเฉพาะแพตช์และ metadata ที่มีสิทธิใช้งาน ไม่แจก ROM/BIOS.
