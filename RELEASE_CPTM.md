# V3.1.1 — Cross-Project Translation Memory add-on (2026-10-09)

- เพิ่ม `tools/cross_project_tm.py` ให้ Codex ดึงคำแปลที่ผ่านการ review จากทุกโปรเจกต์ที่เปิดให้เข้าถึงใน workspace มาเป็นคลัง SQLite ภายในเครื่อง (Python standard library).
- `index`: index เฉพาะ translation status ที่ REVIEWED/APPROVED/VERIFIED และ glossary ที่ Approved จริง พร้อมตรวจ placeholder signature เบื้องต้น.
- `suggest`: หา exact match ข้ามเครื่อง/ค่าย, fuzzy match เฉพาะซีรีส์ที่มี series_id เดียวกัน, แสดง conflict และ provenance, ไม่แก้ master/ROM.
- `terms`: แนะนำศัพท์ที่เคยอนุมัติพร้อมเกมต้นทาง/สถานะเพื่อให้ตรวจความสอดคล้อง.
- เพิ่ม Codex skill `cross-project-memory`, prompt, docs, global skill instruction extension และ 5 unit tests.
- ยังคงใช้กฎเดิม: คุณภาพเนื้อเรื่อง/ไทย/ฟอนต์ต้องมาก่อนประหยัดโทเคน; ทุก suggestion ต้องทบทวนและทดสอบเกมใหม่แยกต่างหาก.
- **ไม่ยืนยันเปอร์เซ็นต์โทเคนที่ลดจริง** จนกว่าจะมีข้อมูล usage เทียบก่อนและหลัง.
- ไม่รวม ROM, BIOS, แพตช์เกม, ฐานข้อความเกมจริง หรือไบนารีฟอนต์ของเกมใด ๆ.
- ผ่าน unit tests รวม 34 รายการในสภาพแวดล้อมสร้างแพ็กเกจ. ยังไม่ได้ทดสอบกับ Codex desktop ของผู้ใช้ หรือ emulator จริง.

### ใช้งาน Chat-Only
Codex เปิด workspace ที่ติดตั้ง V3.1; ให้พิมพ์:

> ใช้คู่มือ V3.1 พร้อม Cross-Project Translation Memory ทำเกมนี้ต่อ วิเคราะห์ว่ามีคำแปลจากเกมภาคก่อนหรือเกมอื่นที่ใช้ร่วมกันได้บ้าง จัดทำ shortlist โดยอ่านเฉพาะคำแปลที่ผ่าน QA ตรวจบริบทก่อนนำมาใช้ และประหยัดโทเคนสูงสุดโดยไม่ลดคุณภาพ

Codex ต้องเข้าถึง workspace ที่มี project_profile.json และ translations/master.csv ของเกมเดิม. หาก Codex แชตไม่สามารถรันคำสั่งหรือไม่มีสิทธิอ่านไฟล์เหล่านี้ จะยังทำงานไม่ได้ ต้องจัดเตรียมสิทธิ/ไฟล์ก่อน.
