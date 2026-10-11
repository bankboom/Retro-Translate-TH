# นำโปรเจกต์แปลเดิมมาเข้า framework อย่างปลอดภัย

1. สร้างโปรเจกต์ชื่อใหม่ด้วย `python tools/project_manager.py init --game "..." --platform NDS --slug game-slug`.
2. เก็บ clean ROM + stable patch ที่ใช้งานได้ + previous/candidate patch ในตำแหน่งเดิมก่อน และบันทึก SHA256/CRC32 แต่ละไฟล์.
3. คัดลอกเฉพาะไฟล์งานที่มีสิทธิ เช่น master CSV → `translations/`; glossary → `translations/`; script adapter → `scripts/`; patch → `patches/`; สกรีนช็อตจริง → `qa/screenshots/`.
4. ปรับตาราง CSV ให้มี `Bank,ID,English,Thai` อย่างน้อยและคง source offsets ตามจริง อย่าเพิ่งแก้เนื้อหา/เปลี่ยน encoding แบบเหมารวม.
5. เขียน `project_profile.json` เพิ่มพาธ ROM ภายนอกที่มีสิทธิและ hashes *ที่ตรวจจริง*; ห้ามถือว่า hash สังเกตครั้งแรกเป็น clean verified โดยอัตโนมัติ.
6. ตั้ง `qa/gates.json` ทุกขั้นเป็น `PENDING` จนตรวจย้อนหลังได้; ใช้ `retro_translate_v3.py audit` กับ patch ของเกมนั้นและ clean ROM ที่ตรงกัน.
7. ทดสอบ baseline ใหม่ใน emulator และถ่ายภาพฉากเดิมเทียบ candidate; ถ้ามีปัญหาให้ย้อน baseline อย่างปลอดภัย.

อย่าคัดลอกค่าของเกมอื่น เช่น Game ID, glyph offset, ROM CRC32, patch byte offset, script ที่แก้ pointer หรือตำแหน่ง asset ไปใช้กับเกมใหม่.
