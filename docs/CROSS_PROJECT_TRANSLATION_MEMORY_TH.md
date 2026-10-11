# Cross-Project Translation Memory (CPTM) — V3.1 Add-on

เป้าหมาย: ให้ Codex ใช้คำแปลไทยที่ **ตรวจสอบแล้ว** จากเกมเก่า/ภาคต่อ/เครื่องเดียวกันหรือคนละเครื่อง โดยไม่เอา ROM, แพตช์, ฟอนต์ binary หรือ pointer เดิมไปใช้กับเครื่องใหม่อย่างผิดรูปแบบ

## สิ่งที่ใช้ซ้ำได้
- คำศัพท์เฉพาะ ชื่อบุคคล ไอเทม ทักษะ เมนู ระบบเกม (เลือกตามบริบท)
- ประโยคเดียวกันเมื่อความหมาย เจตนา ตัวละคร และฉากตรงกันจริง
- Glossary และสำนวนในซีรีส์; `publisher` เป็นเพียงตัวช่วยจัดอันดับ ไม่ใช่หลักฐานว่าคำแปลเหมือนกัน
- **ใช้ซ้ำไม่ได้โดยตรง:** glyph/font binary, pointer, offsets, encoding, script control bytes, emulator QA, ตำแหน่ง UI, ตัวเลขที่เปลี่ยนในภาคต่อ

## ข้อกำหนดด้านคุณภาพ
1. Master ของแต่ละเกมต้องมี `TranslationStatus` เป็น `REVIEWED` / `APPROVED` / `VERIFIED` หรือ `Reviewed=yes`. แถว DRAFT หรือไม่มีสถานะไม่นำเข้าเป็น approved memory.
2. `Context_Key` / `Speaker` / `Scene` ต้องถูกเติมจากไฟล์เกมจริงตามที่ทราบ; ไม่มีบริบทให้คง `REVIEW_REQUIRED`.
3. โครงการภาคต่อสามารถใส่ `series_id` เดียวกันใน `project_profile.json` (เช่น `pokemon-core`, `dragon-quest`), และ `publisher` ถ้าทราบจากหลักฐาน. ชื่อเกม/สังกัดค่าย **ไม่เพียงพอ** ให้ระบุซีรีส์ร่วมเองโดยไม่ตรวจ.
4. ทุกข้อเสนอจาก CPTM เป็น **SUGGESTION ONLY** ห้ามลง master โดยอัตโนมัติ, ห้ามนับ reviewed/injected/verified หรือเปลี่ยน Quality Gates.
5. ถ้าแปลไทยจากเกมเดิมมี placeholders/control tokens ไม่ตรงกับต้นฉบับ ระบบจะไม่เก็บแถวนั้นเข้าคลัง; ตัวตรวจเป็น heuristic ต้องใช้ adapter เฉพาะเกมตรวจ token พิเศษเพิ่ม.
6. ประโยคอังกฤษตรงกัน แต่ศัพท์, บทพูด, เวลา, ระดับสุภาพ, ตัวละคร หรือฟังก์ชันต่างกัน ต้องแปลใหม่. คำคล้ายเป็นเพียงทางเลือกและต้องรีวิวเข้มงวด.
7. ห้ามเอาสคริปต์/เนื้อหาลิขสิทธิ์ของผู้อื่นที่ไม่มีสิทธิใช้งานเข้าคลังกลาง; CPTM ใช้กับข้อมูลจากโปรเจกต์ที่ผู้ใช้มีสิทธิเข้าถึง.

## วิธีใช้งานผ่าน Codex chat (ไม่ต้องเปิด Terminal เอง)
เมื่อเริ่มเกมใหม่หรือทำต่อ ให้ Codex รัน Python ตามนี้ โดย **FRAMEWORK** คือโฟลเดอร์ที่ติดตั้งคู่มือ และ **WORKSPACE** คือพื้นที่ทำงานจริง (เช่น `~/RetroThaiProjects`); หากยังไม่ได้ติดตั้งแบบ global และเปิด root framework โดยตรง ให้ใช้ `python tools/cross_project_tm.py` ตามเดิม

```powershell
python "<FRAMEWORK>/tools/cross_project_tm.py" index --projects "<WORKSPACE>/projects" --db "<WORKSPACE>/shared_memory/cross_project_tm.sqlite"
python "<FRAMEWORK>/tools/cross_project_tm.py" suggest --project "<WORKSPACE>/projects/NEW_GAME" --db "<WORKSPACE>/shared_memory/cross_project_tm.sqlite" --output "<WORKSPACE>/projects/NEW_GAME/working/cptm_suggestions.csv"
python "<FRAMEWORK>/tools/cross_project_tm.py" terms --project "<WORKSPACE>/projects/NEW_GAME" --db "<WORKSPACE>/shared_memory/cross_project_tm.sqlite" --output "<WORKSPACE>/projects/NEW_GAME/working/cptm_terms.csv"
```

กรองบรรทัดที่ตรงกับซีรีส์และบริบทก่อน; ส่งให้โมเดลเฉพาะ ID + source + candidate + scene/speaker ใน batch สั้น ๆ. ไม่ต้องส่ง master ของทุกเกมเข้า LLM.

หลังตรวจความถูกต้องตามเนื้อเรื่องกับ style guide ของเกมใหม่ ให้นำคำแปลที่ผ่านการตรวจไปกรอก master (ใช้กระบวนการ review ของโปรเจกต์) แล้วรัน `index` อีกครั้งเพื่อให้เกมถัดไปค้นพบได้.

### ตัวอย่าง
เกม A (GBA): `Potion -> ยาฟื้นพลัง` ผ่านสถานะ REVIEWED; game B (NDS): `Potion` คล้าย/ตรงกัน → Codex เสนอคำแปลเดิม พร้อมข้อมูลเกมต้นทาง; ผู้ตรวจเช็คว่าคำศัพท์กลมกลืนกับ glossary ภาคใหม่ ก่อนยอมรับ. แม้คำแปลตรงก็ยังต้องทดสอบฟอนต์และข้อความใน UI ของเครื่อง NDS เอง.

## ประสิทธิภาพและข้อจำกัด
- การสร้าง SQLite, ค้น exact/fuzzy ใช้ Python offline จึงไม่เรียก AI และไม่มีการใช้โทเคนโมเดลสำหรับการทำดัชนี.
- Fuzzy จำกัดค้นเกมใน `series_id` เดียวกัน และตรวจได้เพียงความคล้ายของข้อความ ไม่ได้พิสูจน์ความหมาย.
- ค้นข้ามค่ายได้ด้วย exact match แต่จะไม่อนุมัติอัตโนมัติ.
- ยังไม่วัดเปอร์เซ็นต์ประหยัดโทเคนจริง ต้องเทียบก่อน/หลังโดยใช้ค่าการใช้งานจาก Codex เมื่อมี.
- ฐาน SQLite สร้างจากไฟล์แปลภายใต้โฟลเดอร์ `--projects` เท่านั้น ไม่เข้าถึงแชตอื่น/เครื่องอื่นหรือไฟล์ที่ Codex มองไม่เห็นโดยอัตโนมัติ. โปรเจกต์เก่าที่อยู่แยก workspace ต้องให้ Codex เข้าถึงและโยกย้าย/เชื่อมไฟล์งานที่ได้รับอนุญาตก่อน.
- การค้นคำที่แพร่หลาย เช่น `Yes`, `Attack`, `Charge` ต้องเทียบ context ของเกมใหม่ก่อนเสมอ.
- อย่านำ SQLite เข้าสู่ Git หรือส่งออกโดยไม่ตรวจสิทธิในข้อความ เพราะคลังนี้เก็บเนื้อหาจากโปรเจกต์จริง.
