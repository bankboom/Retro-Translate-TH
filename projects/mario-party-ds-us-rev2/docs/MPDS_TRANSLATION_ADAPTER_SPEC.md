# สเปกตัวแยกและประกอบข้อความ Mario Party DS (USA Rev 2)

สถานะ: รอผู้ใช้ตรวจและอนุมัติสเปกก่อนเริ่มพัฒนา  
โครงการ: `mario-party-ds-us-rev2`  
รุ่นเป้าหมาย: Nintendo DS, USA Rev 2, game code `A8TE`

## เป้าหมาย

สร้าง adapter เฉพาะเกมที่ทำงานซ้ำได้ เพื่อสำรวจและแปลข้อความจากตาราง `data/US/mpd_*_LZ.bin` ที่ยืนยันรูปแบบแล้ว พร้อมเส้นทางทดสอบแบบย้อนกลับได้ตั้งแต่ไฟล์ต้นทางจนถึงแพตช์ทดลองขนาดเล็ก

การทำงานต้องรักษา ROM สะอาดเดิมแบบ immutable, แยกไฟล์ข้อความ ฟอนต์ และแพตช์ออกจากกัน และรายงาน G0–G5 ตามหลักฐานจริง กรณีที่ยังไม่มีข้อมูลหรือการทดสอบให้คงสถานะ `PENDING`

## หลักฐานตั้งต้นและข้อจำกัด

- ROM ที่ตรวจมีขนาด 33,554,432 ไบต์, SHA-1 `96054049ac831720f1c7c63023cf18907352d45c`, SHA-256 `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`, CRC32 `4FCBB5C3`; G0 PASS หมายถึงตรงกับตัวระบุรุ่น/แฮชอ้างอิงเท่านั้น ไม่ได้ยืนยันที่มาหรือสิทธิ์ในไฟล์
- ตาราง 35 ไฟล์ในกลุ่ม `mpd_*_LZ.bin` แตกและแปลงกลับเป็นข้อมูลขยายเดิมได้แบบ byte-identical รวม 2,672 แถว การทดสอบนี้ยังไม่ยืนยันการบีบอัดกลับ การประกอบ ROM หรือการทำงานในเกม
- ข้อมูลเนื้อเรื่อง `data/ohanashi_event_data.bin`, ข้อความใน ARM9/overlay, ความหมาย runtime ของ token `[1]`, ฟอนต์ และ renderer ยังไม่ถูกยืนยัน
- รายละเอียดอ้างอิงและผลตรวจอ่านอย่างเดียวอยู่ใน `analysis/ROM_MAP.md` และ `qa/reports/`.

## แนวทางที่เลือก

พัฒนา adapter แบบแบ่งระยะด้วย Python และไลบรารีมาตรฐาน โดยให้การตรวจและแปลงตารางที่ทราบรูปแบบเป็นแกนแรก ใช้ผลทดสอบและหลักฐานจาก Rev 2 ก่อนเปิดใช้การประกอบตารางหรือแพตช์ทดลอง

ไม่พึ่ง GUI editor ของบุคคลที่สามเป็นแหล่งความจริง และไม่ถือว่ารูปแบบที่ระบุในเครื่องมือภายนอกถูกต้องกับ Rev 2 จนกว่าจะทดสอบกับ ROM เป้าหมายแบบไม่เขียนทับ

## โครงสร้างที่เสนอ

- `projects/mario-party-ds-us-rev2/tools/mpds_adapter/`: โมดูล CLI และ parser/serializer เฉพาะเกม
- `projects/mario-party-ds-us-rev2/tests/`: fixtures สังเคราะห์ขนาดเล็กและการทดสอบ format; ห้ามบรรจุ ROM หรือ asset ที่คัดลอกจากเกม
- `projects/mario-party-ds-us-rev2/translations/master.csv`: แหล่งข้อความ/คำแปลตาม schema ของ Framework; แก้เฉพาะแถวที่เปลี่ยน
- `projects/mario-party-ds-us-rev2/qa/reports/`: รายงานสรุป, manifest และหลักฐาน; ไม่เก็บ ROM หรือ payload ที่แตกออกมา
- `projects/mario-party-ds-us-rev2/docs/NEXT_TASK.md`: checkpoint และงานถัดไป ณ จุดหยุด

ชื่อและตำแหน่งไฟล์ข้างต้นเป็นข้อเสนอสำหรับแผนพัฒนา และอาจปรับในแผนโดยคงขอบเขตและ invariants ของสเปกนี้

## ขอบเขตการทำงาน

### ระยะ A — สำรวจและแยกข้อมูลแบบอ่านอย่างเดียว

1. ตรวจ header และ hash ของ ROM ก่อนอ่าน โดยปฏิเสธรุ่นที่ไม่ตรงกับ profile และไม่เปิดไฟล์แบบเขียน
2. อ่าน NitroFS/FAT อย่างมีขอบเขต ตรวจ offset/size ของทุกช่วงก่อนอ่านไฟล์
3. ทำ inventory ที่ทำซ้ำได้ของไฟล์ชื่อและ overlay IDs โดยบันทึกเฉพาะ path, offset, size, hash และผลตรวจ ไม่คัดลอก payload ลง repository
4. ระบุไฟล์ตารางเป้าหมายจาก manifest ที่ review แล้ว ไม่เดาจากชื่อหรือผลสแกนที่ยังไม่ยืนยัน
5. แตกตารางเป็น CSV โดยรักษา file ID, row ID, source bytes/ข้อความต้นฉบับที่จำเป็นต่อ round-trip, token ที่ไม่รู้ความหมาย และสถานะ DRAFT/REVIEWED/INJECTED/VERIFIED
6. ทำ parser แบบ strict: ตรวจ signature/header ที่พบจริง, ขนาดขยาย, count, offset table, offset alignment, ขอบเขต string, null terminator และ encoding ผิดรูปแบบ รายการใดไม่ผ่านต้อง fail แบบอธิบายสาเหตุ ห้ามซ่อมหรือข้ามเงียบ ๆ

### ระยะ B — ตรวจ serializer และการบีบอัด

1. serializer ต้องสร้างตารางขยายกลับเป็น byte-identical สำหรับข้อมูลเดิมทั้ง 35 ตาราง
2. ทดสอบ round-trip ของ container บีบอัดกับตัวอย่างเดิมทั้ง 35 ไฟล์ พร้อมบันทึกกฎ flag/back-reference และขอบเขตของ header จากหลักฐาน ไม่ hard-code ข้อสรุปที่ยังไม่ผ่านการทดสอบ
3. ถ้ารูปแบบบีบอัดมีหลายผลลัพธ์ที่ถูกต้อง ให้กำหนด invariant เป็นข้อมูลขยายที่ตรงกันและการแตกกลับที่ตรงกัน; ระบุชัดว่า compressed bytes ไม่จำเป็นต้องตรงต้นฉบับ
4. ตรวจ count/offset/length, integer overflow, overlap ที่ผิดรูปแบบ, ขนาดสูงสุด และกรณีข้อมูลว่าง/ขอบเขตด้วย fixtures สังเคราะห์
5. ห้ามเรียกผล round-trip ว่า G1 PASS จนกว่าการตรวจ binary scope และหลักฐานตาม `docs/QUALITY_GATES.md` จะครบ

### ระยะ C — คำแปลและ token

1. แยกการดึงข้อมูลออกจากการเขียนคำแปล; ให้ใช้ glossary และ Thai quality standard ของ Framework
2. แปลเป็นชุดเล็กที่มีบริบท scene/speaker/UI และออกเฉพาะ diff ของแถวที่เปลี่ยน
3. คง `[1]` และ token/control byte ทุกตัวตามจำนวนและลำดับที่ยืนยันได้ ห้ามตีความ `[1]` จนกว่าจะมีหลักฐาน runtime
4. กำหนดสถานะ DRAFT → REVIEWED → INJECTED → VERIFIED อย่างชัดเจน; CSV audit ไม่เปลี่ยนสถานะเอง และห้ามตั้ง G2 PASS หาก inventory/บริบท/การทบทวนยังไม่ครบ
5. ข้อความที่ยังคลุมเครือหรือไม่มีบริบทต้องถูกตั้งธงและพักไว้ ไม่สร้างความหมายขึ้นเอง

### ระยะ D — micro-patch แบบย้อนกลับได้

1. เริ่มจาก 1–5 แถวที่ผ่านการทบทวนเท่านั้น โดยเลือกแถวที่ไม่มี token ไม่ทราบความหมายเป็นชุดแรก
2. สร้าง candidate แยกจาก clean ROM และ stable baseline; ห้ามแก้ไฟล์ต้นฉบับหรือใช้ candidate เป็นฐาน clean ในรอบถัดไป
3. ก่อน/หลังประกอบ ให้ตรวจ hash, file bounds, pointer/offset bounds และการเปลี่ยนแปลงด้วย `tools/regression_guard.py` พร้อม `allowed_changes` ที่ review แล้ว
4. ทดสอบการย้อนกลับจาก patch ไปยัง baseline แบบ byte-identical ด้วยรูปแบบแพตช์ที่เลือกภายหลังตามผลทดลอง; ห้ามรวม ROM เต็มลง Git, patch release หรือ artifact สาธารณะ
5. บันทึก build ID, input/output hashes, รายการช่วงเปลี่ยน และวิธีย้อนกลับเป็น metadata; หลีกเลี่ยงการเผยแพร่ข้อมูลที่มีลิขสิทธิ์
6. การผ่าน static check หรือ binary scope ไม่ใช่หลักฐาน G3/G4

### ระยะ E — ฟอนต์และ runtime QA (แยกจาก adapter ตาราง)

1. ทำแผนที่ encoding → glyph index → tile/bitmap → renderer จากหลักฐานจริง; ห้ามสมมติว่า UTF-16LE รองรับ glyph ไทย
2. ตรวจ glyph, advance, baseline, การซ้อนวรรณยุกต์/สระ, kerning/wrapping และพื้นที่ UI จากเกมจริง
3. ต้องมี screenshot จาก emulator จริงที่ผูกกับ build ID, scene และขนาดตัวอักษร รวมชุดอักขระ `ต้ ตุ สำ น้ำ ภาษา`; preview ที่สร้างเองไม่ถือเป็นหลักฐาน
4. รันทดสอบ scene/gameplay, save/load และ rollback ตาม quality gates; หากยังไม่มี emulator หรือหลักฐาน ให้ G3/G4 เป็น PENDING
5. งาน map เนื้อเรื่อง, ARM9/overlay และฟอนต์เป็น workstream แยก อาจเพิ่ม adapter หลังทำ format map และ test vector เฉพาะส่วนนั้นแล้ว

## CLI ที่ต้องการ

ชื่อคำสั่งเป็นข้อกำหนดเชิงพฤติกรรม; syntax สุดท้ายให้กำหนดในแผน:

- `inspect-rom`: ตรวจ identity/header/NitroFS bounds แบบ read-only
- `inventory`: สร้าง metadata manifest ของไฟล์ที่ระบุขอบเขต
- `extract-tables`: แยกเฉพาะ manifest ตารางที่ยืนยันแล้วเป็นข้อมูลพร้อม source IDs
- `validate-tables`: ตรวจ CSV, token, offsets, encodings และสถานะโดยไม่แก้ไฟล์
- `roundtrip`: parse → serialize → compare และรายงานความแตกต่าง
- `build-candidate`: ปิดไว้จนกว่าระยะ A/B ผ่านและแผนอนุมัติจะกำหนดขั้นตอน patch; clean ROM เป็น input read-only เท่านั้น

ทุกคำสั่งต้องคืน exit code ที่ไม่เป็นศูนย์เมื่อข้อมูลผิดรูปแบบ, แฮชไม่ตรง, มี path ซ้ำ, ขอบเขตเกิน หรือเกิดการเขียนทับไฟล์ที่มีอยู่

## เกณฑ์ยอมรับสเปก/งานพัฒนา

- อ่าน ROM ด้วยโหมด read-only และตรวจ hash ก่อนทุก workflow ที่อ่านข้อมูลจากไฟล์นั้น
- ไม่มีคำสั่งใดเขียนทับ clean ROM; ไม่มี ROM, BIOS, extracted game payload, font payload หรือ full candidate ROM ใน repository
- parser ปฏิเสธข้อมูลผิดรูปแบบด้วย error ที่ระบุ file/row/offset; ไม่อ่าน/เขียนนอกขอบเขต
- 35 ตารางที่ยืนยันแล้วให้ extracted row รวม 2,672 แถว และข้อมูลขยาย round-trip byte-identical
- test fixture ครอบคลุม boundary/error cases, token preservation, CSV round-trip และการเปลี่ยน header/count/offset ที่ไม่ถูกต้อง
- ไม่สร้างคำแปลจำนวนมากหรือเปลี่ยนสถานะแถวโดยอัตโนมัติ; แถวทดลองยังคงสถานะตามหลักฐาน
- patch ทดลองไม่เกิน 5 แถว, มี baseline/hash/diff/rollback evidence; ยังต้องมี human review ก่อนเลื่อน gate
- G0–G5 ยังคงแยกกัน โดย G1 ไม่อนุมานจาก parser tests อย่างเดียว; G3/G4 ต้องมี emulator evidence; G5 ต้องมี human sign-off
- สเปกนี้ไม่อ้างว่าเกมแปลไทยเสร็จหรือ release-ready

## นอกขอบเขตของสเปกนี้

- การแปลครบทุกบทสนทนา, UI และข้อความในเกม
- การแก้ `ohanashi_event_data.bin`, ARM9 หรือ overlays ก่อนยืนยันโครงสร้างและ test vectors ของแต่ละ format
- การเปลี่ยน font binary หรือ renderer ก่อนมี glyph map และการทดสอบบน emulator
- การเผยแพร่ ROM, BIOS, full candidate ROM หรือไฟล์เกมที่แตกออกมา
- การตั้ง G1–G5 เป็น PASS จากผล static/automated อย่างเดียว

## จุดตัดสินใจก่อนเริ่มพัฒนา

หลังตรวจสเปก ผู้ใช้จะอนุมัติหรือให้แก้ขอบเขตนี้ก่อน จากนั้นจึงจัดทำ implementation plan ที่แยกงาน parser, serializer, CSV integration, QA และ font/runtime mapping พร้อมจุดตรวจรับก่อนเขียนเครื่องมือ
