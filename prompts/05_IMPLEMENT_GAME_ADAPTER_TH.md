# คำสั่งสำหรับ Codex: เขียน game-specific adapter

อ่าน ROM map/AGENTS.md/QUALITY_GATES และใช้ `projects/<SLUG>/scripts/` เป็นที่พัฒนา adapter เกมนี้. เลือก text bank เดียวสำหรับ proof of concept: อธิบาย compression/encoding/pointers/control codes พร้อม offset ที่ตรวจจริง. เพิ่ม extractor อ่านค่าเดิมได้, แล้ว round-trip ทดสอบกับข้อมูลเดิม ก่อนทำ injector ที่ระวัง boundary/align/checksum. เพิ่ม unit tests จาก fixture สังเคราะห์ ไม่คัดลอก ROM มีลิขสิทธิ์. รวบรวมข้อสรุปแบบ verified vs hypothesis และสร้าง micro-patch 1–5 ข้อความ. ห้ามแก้ข้อมูลหลาย bank พร้อมกันโดยยังไม่พิสูจน์ round-trip.
