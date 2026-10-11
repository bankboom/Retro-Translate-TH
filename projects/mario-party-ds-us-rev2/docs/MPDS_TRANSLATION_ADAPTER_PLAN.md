# แผนพัฒนา Adapter และเริ่มงานแปล Mario Party DS (USA Rev 2)

> สถานะ: อนุมัติแล้ว — ดำเนินการแบบ Native บน GitHub  
> สเปกที่อนุมัติ: [MPDS_TRANSLATION_ADAPTER_SPEC.md](MPDS_TRANSLATION_ADAPTER_SPEC.md)  
> เป้าหมาย: ทำให้การสำรวจ/แยก/ตรวจข้อความที่ยืนยันรูปแบบแล้วทำซ้ำได้ ก่อนขยายงานแปลหรือสร้างแพตช์

## ผลลัพธ์ที่ต้องการ

1. เครื่องมือเฉพาะเกมที่อ่าน ROM แบบ read-only และตรวจรุ่น/ขอบเขตได้
2. Parser/serializer ของ MPDS LZ + UTF-16LE text tables ที่ผ่าน fixture tests และทดสอบกับ 35 ตารางที่ยืนยันแล้ว
3. inventory และ master translation rows ที่เชื่อมโยง file/bank/row IDs และรักษา tokens/status ตาม Framework
4. ชุดข้อความภาษาไทยขนาดเล็กที่ผ่าน contextual review พร้อมหลักฐานว่าพร้อมทดสอบ micro-patch หรือระบุ blocker อย่างตรงไปตรงมา
5. แผนแยกสำหรับ story-event, ARM9/overlay และ Thai font/runtime โดยไม่อนุมานจากชื่อไฟล์

## โครงสร้างไฟล์ที่วางแผนเพิ่ม

- `projects/mario-party-ds-us-rev2/tools/mpds_adapter/`: CLI, ROM/NitroFS reader, MPDS LZ, text-table parser/serializer
- `projects/mario-party-ds-us-rev2/tests/`: unittest สำหรับ synthetic fixtures และ format edge cases
- `projects/mario-party-ds-us-rev2/analysis/`: format notes และ inventory methodology ที่มีหลักฐาน
- `projects/mario-party-ds-us-rev2/qa/reports/`: รายงานสรุป/manifest โดยไม่มี ROM หรือ extracted binary payload
- `projects/mario-party-ds-us-rev2/translations/master.csv`: เพิ่มเฉพาะ IDs ที่แยกได้อย่างยืนยัน พร้อมสถานะที่ถูกต้อง
- `projects/mario-party-ds-us-rev2/docs/NEXT_TASK.md`: อัปเดต checkpoint หลังแต่ละ milestone

โครงสร้างนี้ต้องตรวจชนกับ GitHub tree ก่อนสร้างทุกไฟล์ ถ้าพบไฟล์ที่มีอยู่แล้ว ให้ปรับแผนหรือ merge แบบรักษาเนื้อหาเดิม ห้ามเขียนทับโดยไม่ตรวจ diff

## ขั้นดำเนินงาน

### 0. ยืนยัน baseline และสภาพแวดล้อม

- ตรวจ `main` head, tree และไฟล์สำคัญสดจาก GitHub ก่อนทำงาน; ทำงานบน snapshot ที่ระบุ commit ชัดเจน
- ตรวจ `project_profile.json`, schema ของ `master.csv`, `AGENTS.md`, `NEXT_TASK.md` และ gate policy ก่อนแก้ไฟล์
- เปิด clean ROM แบบ read-only; เทียบขนาด, header, SHA-256/SHA-1/CRC32 กับ profile ก่อนอ่าน และคำนวณซ้ำหลังทำงาน
- เก็บ clean ROM ไว้ภายนอก repository; ไม่สร้างสำเนา ROM, extracted asset หรือ full candidate ROM ใน tree
- บันทึก baseline ของ CSV, gate JSON และ path list เพื่อยืนยันภายหลังว่าแถวเดิม/สถานะเดิมไม่ถูกเลื่อนโดยอัตโนมัติ

**ผ่านเมื่อ:** hash ตรง profile, ROM ไม่เปลี่ยน, ไม่มีไฟล์เดิมถูกเขียนทับ และ G0 ระบุความหมายจำกัดเป็น identity/revision match พร้อม caveat เรื่อง provenance

### 1. เขียน tests ก่อน parser

- สร้าง synthetic NDS/NitroFS fixtures ที่ไม่บรรจุเนื้อหาจากเกม สำหรับ header, FNT/FAT, ช่วงไฟล์ใน/นอกขอบเขต และ directory records
- สร้าง synthetic MPDS LZ vectors สำหรับ literal, back-reference, flag groups, boundary, ขนาดประกาศไม่ตรง, truncation และ output เกินขนาด
- สร้าง table vectors สำหรับ count/offsets, UTF-16LE terminator, offset ไม่ align, offset ซ้ำ/ย้อน, missing terminator, malformed UTF-16 และ token preservation
- ใช้ `unittest` มาตรฐาน; tests ต้องตรวจทั้งผลสำเร็จและการปฏิเสธข้อมูลผิดรูปแบบโดยมี error ระบุตำแหน่ง

**คำสั่งตรวจ:** `python -m unittest discover -s projects/mario-party-ds-us-rev2/tests -p "test_*.py" -v`

### 2. ทำ read-only ROM/NitroFS reader และ inventory

- เขียน `inspect-rom` ให้ตรวจ magic/header/sections, platform/revision และ hash โดยไม่เปิดโหมดเขียน
- เขียน `inventory` ให้อ่าน NitroFS/FAT ด้วย bounds checks และรายงาน path, file ID, offset, size, container signature และ hash
- ทดสอบกับ synthetic fixture ก่อน จากนั้นอ่าน ROM เป้าหมายจริงแบบ read-only
- ทำรายงาน metadata ของไฟล์ทั้งหมดที่มีชื่อและ unnamed overlay IDs; ห้ามเหมารวมไฟล์ที่ชื่อคล้ายกันว่าเป็นข้อความ
- ตรวจ path traversal, integer overflow, overlap/invalid ranges และกรณีชื่อไฟล์ซ้ำ

**ผ่านเมื่อ:** inventory ทำซ้ำได้, จำนวน/ช่วงตรงกับรายงาน baseline หรือมีรายงานอธิบายความต่าง, ไม่มีไฟล์ payload หลุดเข้า Git

### 3. ทำ MPDS LZ + text-table adapter

- เขียน decompressor/compressor ตามรูปแบบที่วัดได้จาก Rev 2; เก็บ raw header byte และแยกจาก expanded-size field
- เขียน parser/serializer ของ count + offset table + UTF-16LE strings พร้อมคง row IDs, raw/token representation และ encoding rules
- ใช้ 35 ไฟล์ `data/US/mpd_*_LZ.bin` เป็น corpus ตรวจในเครื่อง แต่เก็บใน repository เฉพาะ metadata และผล checksum ไม่เก็บ container bytes
- ยืนยัน 35/35 parse + serialize ของ expanded form แบบ byte-identical; ตรวจ compressed round-trip แยกต่างหากและระบุว่า compressed bytes ต้องตรงหรือเพียง decompress เป็นข้อมูลเดิมตามผลจริง
- เพิ่ม regression checks สำหรับ total 2,672 rows และยืนยันว่าการ parse ไม่สร้าง/ลบ/สลับ IDs

**ผ่านเมื่อ:** synthetic tests ผ่าน, 35 ตารางผ่านผลที่ระบุ, ไม่มี bounds/token errors ที่ถูกกลบ; G1 ยัง PENDING จนกว่าจะมี binary-scope/build/patch evidence ตาม gate policy

### 4. เชื่อม CSV และเริ่มแปลเป็นชุด

- เพิ่ม extractor ที่เขียน source-only CSV แยกจาก `master.csv` โดยเก็บเฉพาะ Bank, ID, ROM_Offset, English, File_Path และ token candidates; ไม่กำหนด TranslationStatus/InjectionStatus ให้แถวที่ยังไม่ใช่คำแปล
- เขียน source inventory ไปยัง path ใหม่หรือตำแหน่งชั่วคราวเท่านั้น; ย้ายเฉพาะ IDs ที่เลือกและมีบริบทไปยัง `master.csv` หลังตรวจ schema/diff; เพิ่มแถวแปลตามคำสั่งผู้ใช้เป็นชุดเล็กชุดละ 5 โดยคง `DRAFT` / `NOT_INJECTED` จนผ่านการตรวจบริบท; ก่อนฉีดหรือขยายเกิน 10 แถว ต้องพิสูจน์เส้นทาง micro-patch/repack และฟอนต์
- ตรวจจำนวน source rows เทียบ inventory, uniqueness ของ (bank, ID), CSV quoting/newlines, UTF-16 round-trip และจำนวน tokens
- ใช้ glossary/TM ที่ context ตรงกัน; ตรวจตัวอย่าง 5 DRAFT ปัจจุบันก่อนเพิ่ม batch; คง `[1]` เป็น token ที่ยังไม่ทราบความหมาย
- แปลเป็น batch เล็กพร้อม scene/context evidence; ให้ AI ส่งเฉพาะ changed rows แล้วทำ human/contextual review ก่อนเปลี่ยนเป็น REVIEWED
- แยกจำนวน Inventory / Draft / Reviewed / Injected / Verified; ห้ามรายงานเปอร์เซ็นต์ความคืบหน้าจากแถวที่ไม่ครบ scope

**ผ่านเมื่อ:** export/import ไม่ทำข้อมูลต้นฉบับเสีย, ไม่มี ID/token mismatch, คำแปลใหม่ไม่ถูกทำเครื่องหมาย REVIEWED โดยอัตโนมัติ และ G2 คง PENDING จน coverage/context review ตาม scope ครบ

### 5. สำรวจ story/event, overlay และ Thai font แยก workstream

- สร้าง candidate inventory แบบ read-only ของ `ohanashi_event_data.bin`, ARM9, overlays และ compressed containers อื่น; ไม่ parse เป็นข้อความจนมี format hypothesis ที่ทดสอบซ้ำได้
- สร้าง test vectors แยกต่อ format; คงสถานะ “unknown” หากยังไม่มี proof และไม่บล็อกความถูกต้องของ MPD table adapter
- ทบทวนเฉพาะแนวทางและ mapping metadata จากงานศึกษาฟอนต์ NDS ไทยเดิมของผู้ใช้เป็นข้อมูลอ้างอิง; ห้ามคัดลอก glyph/font binary หรือถือว่า encoding/indices ใช้ร่วมกันได้โดยไม่มีหลักฐานจากเกมนี้
- ทำ mapping chain ของ codepoint/encoded value → glyph index → glyph data → renderer/width; ระบุ glyph ที่ขาด/เครื่องหมายประกอบและขนาดฟอนต์
- สร้าง test strings และ font review plan รวม `ต้ ตุ สำ น้ำ ภาษา`; เตรียม scene/build ID สำหรับ screenshot จาก emulator จริง

**ผ่านเมื่อ:** format ที่เพิ่มเข้ามามี evidence/test vectors ของตัวเอง; ฟอนต์ไม่ถูกเปลี่ยนจากการคาดเดา; G3/G4 คง PENDING จนมีภาพ/ผล playtest จริงและผู้ตรวจ

### 6. พิจารณา micro-patch หลัง prerequisite ผ่านเท่านั้น

- เริ่มจาก 1–5 rows ที่ผ่านการ review และไม่มี token ที่ไม่ทราบความหมาย; ถ้าฟอนต์ไทยยัง map ไม่ได้ ให้หยุดที่ candidate data และรายงาน blocker
- กำหนด clean baseline และ candidate แยกกัน พร้อม build ID, input/output hashes, allowed-changes และ rollback method
- ใช้ `tools/regression_guard.py` ตรวจ binary scope; สร้าง patch candidate ในพื้นที่ทำงานภายนอก repository และทดสอบ apply/reverse กับ baseline
- ห้ามแก้ clean ROM, ห้ามรวม ROM เต็ม/BIOS/extracted binary/candidate ROM ใน Git และห้ามตั้ง G1/G3/G4 PASS จาก static check
- หากมี emulator ที่เปิด candidate ได้ ให้ทดสอบ boot/menu/save/load และ capture screenshots/log ที่ผูกกับ build ID; ถ้าไม่มี ให้คง gate ที่เกี่ยวข้องเป็น PENDING

**ผ่านเมื่อ:** candidate จำกัดตาม allowed-changes, ย้อนกลับได้, baseline ไม่เปลี่ยน, และ gate มีหลักฐานเฉพาะตนโดยไม่ปะปนสถานะแปล/ฟอนต์/แพตช์

### 7. Regression, review และ checkpoint

- รัน project tests และ framework tests: `python -m unittest discover -s tests -p "test_*.py" -v`
- รัน CSV audit และ token checks กับเฉพาะไฟล์/แถวที่เปลี่ยน
- ตรวจ hash clean ROM ซ้ำ, ตรวจ `git diff --check`, scan ว่าไม่มีไฟล์ ROM/BIOS/patch payload หรือ path ภายในเครื่อง
- อัปเดต `docs/NEXT_TASK.md`, รายงาน QA และ G0–G5 เฉพาะ gate ที่ evidence เปลี่ยน
- ตรวจ commit/tree ว่าเพิ่ม/แก้เฉพาะไฟล์ที่อนุมัติและไม่มีไฟล์เดิมถูกทับ

## เงื่อนไขหยุดทันที

- ROM hash/revision ไม่ตรง, input เปลี่ยนขณะทำงาน หรือมีความพยายามเขียนลง clean ROM
- offset/size/token/encoding ไม่ผ่าน bounds/validation หรือ parser ต้องเดาเพื่อดำเนินต่อ
- test พบ row ID หาย/ซ้ำ/สลับ, CSV เก่าถูกเขียนทับ, หรือ baseline diff เกิน scope
- ยังไม่มีหลักฐาน glyph map แต่กำลังจะสร้าง Thai patch; ยังไม่มี emulator evidence แต่มีข้อเสนอให้เลื่อน G3/G4
- GitHub `main` เปลี่ยนจาก expected head หรือมี path collision: อ่าน head/tree ใหม่และตรวจ diff ก่อนสร้าง commit ใหม่ ห้าม force push

## ขอบเขตของ milestone แรก

Milestone แรกจบเมื่อ adapter อ่านอย่างเดียว, parser/serializer และ CSV round-trip ผ่านข้อทดสอบที่กำหนด พร้อม inventory/translation batch แรกที่มี context ใช้งานได้ การแปลทั้งเกม, การ map event files, Thai font injection, gameplay QA และ release เป็นงานต่อเนื่องและต้องผ่าน evidence/gates แยกกัน

## วิธีดำเนินงานที่ให้เลือก

- **Native บน GitHub (แนะนำ):** ทำ working copy ใน workspace เพื่อรันทดสอบ แล้วเผยแพร่ commit แบบ additive ไปที่ branch ที่เลือกผ่าน GitHub API พร้อม expected-head guard; ไม่ force update
- **Branch + PR:** ทำ working copy เช่นกัน แต่เผยแพร่บน feature branch แล้วเปิด PR เพื่อ review ก่อน merge

เลือกวิธี Native บน GitHub แล้ว; implementation และการตรวจทานดำเนินการใน workspace จากนั้นเผยแพร่ด้วย commit ที่อิง expected head โดยไม่ force push
