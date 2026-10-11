# V3.2.1 — Universal Offline Tool Fallback (Codex)

**เป้าหมาย:** Framework ส่วนกลางไม่ผูกกับเกมใดเกมหนึ่ง และไม่หยุดงานทั้งโครงการเพียงเพราะไม่มี package/disassembler หรือ network

## ความสามารถที่จัดระดับตามหลักฐาน

1. `G0 + data-only`: ตรวจแฮช ROM, container, file lists, decompress, parse, round-trip โดยไม่ต้องมี disassembler
2. `ARM/Thumb candidate probe`: เมื่อ ROM ใช้ ARM/Thumb **และ** ยืนยัน binary ที่ถอดแล้ว, RAM load address, ช่วง code, instruction mode ได้จาก header/overlay descriptor/debugger จึงใช้ `tools/portable_code_probe.py` เพื่อหาคำสั่ง branch, PC-relative literal load และ ADR **เฉพาะรูปแบบที่รองรับ**
3. `Full disassembly / debugger`: เมื่อมี Capstone/llvm-objdump/arm-none-eabi-objdump และใช้งานได้จริง ให้ใช้ตรวจทานผล candidate; runtime trace ใช้พิสูจน์ call graph และ event reader เมื่อสามารถทำได้
4. `No safe evidence`: คงงานส่วนที่ต้องอาศัย code semantics เป็น `PENDING`, แต่ดำเนินงาน extraction, translation QA และข้อมูลที่พิสูจน์แล้วต่อได้โดยไม่ข้าม gate

`python tools/portable_code_probe.py capabilities` แสดงสิ่งที่มีในเครื่องโดยไม่ดาวน์โหลดและไม่รันคำสั่งติดตั้งแพ็กเกจ

ตัวอย่างสแกน candidate เฉพาะ **raw ARM9 image ที่ถอด/decode แล้ว** (ค่าตัวอย่าง ไม่ใช่ค่าที่พิสูจน์แล้วของเกมใด):

```bash
python tools/portable_code_probe.py scan \
  --input /private/confirmed_arm9_image.bin \
  --mode arm --base 0x02000000 --start 0x0 --end 0x1000 \
  --max-results 40
```

- `--base`: ที่อยู่ RAM จริงของ byte แรกในไฟล์ input; **อย่านำ file offset ใน ROM มาใช้เป็น RAM base**
- `--start/--end`: offset ภายใน decoded image ซึ่งมีหลักฐานว่าเป็น CODE และเลือก mode `arm`/`thumb` ถูกต้อง; อย่าสแกนไฟล์ event/table เป็นโค้ด
- `--match-address 0x...`: กรอง candidate target โดย exact address ที่ทราบและยืนยันแล้วเท่านั้น; ถ้าเป็น runtime pointer ที่คำนวณแบบอ้อมอาจไม่พบ
- ต้องไม่ commit full ROM, decrypted/decompressed copyrighted payload, หรือข้อมูลส่วนตัว โดยค่าเริ่มต้น CLI ส่ง JSON stdout ซึ่งผู้ใช้ต้องคัดกรองก่อนบันทึกลง Git

## ระดับความน่าเชื่อถือ

- ผลจาก portable probe เป็น **CANDIDATE_ONLY** ไม่ใช่ xref/functions/grammar ที่ยืนยันแล้ว; pattern อาจเกิดในค่าข้อมูล
- ถ้าไม่ยืนยัน ISA, RAM base และ code range ได้ ให้รายงานเพียง `PENDING: no verified code region` และทำ data-only plan ต่อ
- ใช้ trace ต่างเกมร่วมกันไม่ได้ การใช้ชื่อไฟล์หรือ text literal ให้เพียง filename-level reference ไม่ใช่ caller/function reference
- ห้ามใช้ candidate code offsets เพื่อเขียน ROM, relink, patch pointer, หรือยืนยันความปลอดภัยของ repacker จนกว่าจะทดสอบยืนยันโดยอิสระ
- ไม่มีอุปกรณ์ใน Framework ที่รับประกันการแยกโครงสร้างเกม **ทุกเกม**; แต่ framework สามารถเลือกเส้นทางที่ใช้ได้โดยไม่เดาหรือปิดกั้นส่วนที่ปลอดภัย

## แนวทางเฉพาะ Mario Party DS Rev 2

- ใช้ read-only `projects/mario-party-ds-us-rev2/tools/mpds_adapter/` เดิมต่อ: 35 UTF-16LE text tables / 2,672 rows, overlays 107 compressed verified as decoded lengths
- แยกการวิเคราะห์ `data/ohanashi_event_data.bin`: 102 candidate table values **ไม่ใช่** ขอบเขต record ที่ยืนยันแล้ว; ต้องตามรอย event reader จาก overlay ด้วย trace หรือ code-analysis evidence ที่ถูกต้องของ Mario Party DS เอง
- ถ้าไม่มี ROM/decoded overlay ใน Codex ปัจจุบัน อย่าทำเป็นว่า scan เกมจริงแล้ว; ใช้รายงานเดิมและบอกว่ารอ input/verified range
- G0 คง PASS; G1–G5 PENDING จนมีหลักฐานตาม gate โดยอัปเดตเฉพาะส่วนที่พิสูจน์เพิ่ม
