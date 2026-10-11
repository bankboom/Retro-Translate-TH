# V3.2: QA for incremental candidate

อ่าน AGENTS.md + active project NEXT_TASK.md + V3.2 QA guide เท่านั้น แล้ว:
- ตรวจ baseline/candidate hashes และรายการ changed bytes; ใช้ regression_guard พร้อม policy ที่มาจาก offset map จริง. ไม่อ้างว่า binary scope PASS คือ emulator PASS.
- คัด translation delta/risk ด้วย quality_queue และ approved CPTM; ตรวจภาษา/บริบทเฉพาะรายการที่ต้องการ และบันทึกผลเป็นไฟล์แยก.
- สร้าง font_review_plan จากข้อความจริงและตรวจภาพ emulator จริง; ถ้าไม่มีภาพให้ G3 PENDING.
- ตรวจเล่นจริง/เซฟ/โหลด ก่อน G4 PASS.
- ตรวจ release_audit ก่อน G5 review; ไม่แก้เอกสารรับรองให้ PASS อัตโนมัติ.
- ส่งคำตอบ Changed/Tests/Gates/Blocker/Next เท่านั้น, ไม่พ่น CSV หรือ ROM dump จำนวนมาก.
