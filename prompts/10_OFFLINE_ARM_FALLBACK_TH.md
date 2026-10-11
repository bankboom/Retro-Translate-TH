ใช้ Framework V3.2.1 แก้ blocker "ไม่มี ARM disassembler" โดยไม่เริ่มโปรเจกต์ใหม่

อ่าน AGENTS.md, docs/OFFLINE_REVERSE_ENGINEERING_TH.md, project_profile.json และ docs/NEXT_TASK.md เฉพาะโปรเจกต์เป้าหมาย

1. ตรวจ ROM/provenance และงานที่ยืนยันไว้แล้ว ห้ามนำ TraceKit/offset จากเกมอื่นมาอ้างเป็นของเกมนี้
2. รัน python tools/portable_code_probe.py capabilities ไม่ติดตั้งแพ็กเกจจากอินเทอร์เน็ตโดยไม่ได้รับอนุญาต
3. หากมี confirmed decoded ARM/Thumb code region พร้อม RAM base/mode ให้ scan แบบ read-only และส่ง candidate แบบจำกัดจำนวนเท่านั้น
4. หากยังยืนยันขอบเขตโค้ดไม่ได้ ให้ดำเนินการ data-only (inventory/table/parser round-trip) ต่อได้; ไม่เดา code xrefs/record grammar
5. ไม่แก้ clean ROM ไม่สร้าง candidate patch จากตำแหน่งที่ยังไม่พิสูจน์ ไม่เปลี่ยน G1–G5 เป็น PASS ตามผล probe อย่างเดียว
6. แยกรายงาน confirmed/candidate/unknown, สรุป Changed | Tests | Gates | Blocker | Next สั้น ๆ เพื่อประหยัดโทเคน
