# นโยบายใช้โทเคนอย่างประหยัด (Token Efficient, ไม่ลด QA)

**หลัก:** ประหยัดโทเคนผ่าน offline preprocessing, การเรียกใช้ข้อมูลเฉพาะส่วน และการลดงานซ้ำ; **ไม่ลดความถูกต้องของคำแปลหรือการตรวจฟอนต์**

## กฎการทำงาน
1. **Selective context**: ทุกงาน Codex เริ่มจาก AGENTS.md + active project `AGENTS.md`, `project_profile.json`, `docs/NEXT_TASK.md`; อ่าน skill/doc อื่น *เฉพาะช่วงทำงาน*; อย่าเปิด source bank ใหญ่หรือไฟล์จากเกมอื่นทั้งก้อน
2. **Disk is memory**: บันทึกผล scan, source ID+offset, codec spec, hash, decisions และหลักฐานลงไฟล์; ในบทสนทนาต่อไปใช้ path/ID และ diff แทนการเล่าประวัติยาว
3. **Offline first**: ใช้สคริปต์/hash/regex/CSV filters สำหรับ duplicate discovery, exact TM suggestion, placeholder checks, status counts; อย่าส่งไบต์ ROM หรือ CSV ทั้งหมดให้โมเดล
4. **Approved glossary + TM**: ใช้ glossary เฉพาะคำที่สัมพันธ์กับ batch; TM นำกลับมาใช้ได้เฉพาะ source ตรง 100% + Context_Key ตรง + `Reviewed=true` และ placeholder signature ตรง. ข้าม context ไม่ได้ ต้องให้ AI/มนุษย์ทบทวนใหม่. Suggestions ไม่ใช่ injected/reviewed
5. **Incremental translation**: แปลเฉพาะ missing, invalidated by source changes, or `NEEDS_CONTEXT`; ใช้ batch 20–60 entries (ปรับตามความยาว), จำกัดบริบทเป็น `--max-chars` ไม่ใช่ token guarantee; ใช้ `tools/token_saver.py pack` เพื่อเตรียมงาน
6. **Compact output**: ส่ง `{ID, Thai, QA_Note}` เฉพาะรายการที่แก้หรือมีปัญหา; ห้ามพิมพ์ rows ที่ไม่เปลี่ยน; อย่าส่ง raw full logs หาก tests ผ่าน; เวลา QA ให้ระบุเฉพาะ defect+location+proposed fix
7. **No pointless reruns**: ตรวจก่อนว่าข้อมูล/sha256/adapter/font baseline เปลี่ยนหรือไม่; reuse static reports ที่ตรง hash; ถ้าเปลี่ยนเฉพาะ glyph ให้ทดสอบเฉพาะ glyph/ฉากที่เกี่ยวข้องและ regression set จาก stable
8. **Targeted escalations**: ผ่าน deterministic QA → ให้ AI ตรวจบรรทัดกำกวม/ยาว/มี token/เนื้อเรื่องสำคัญ → ทดสอบภาพใน emulator → ผู้ใช้รับรอง; อย่าให้ AI คิดซ้ำกับบรรทัด approved โดยไม่มีการเปลี่ยน source/context
9. **Checkpoint after each batch**: บันทึก `docs/NEXT_TASK.md` (งานที่ทำ, hashes, pending IDs, blocker) และเพิ่ม TM เฉพาะบรรทัดที่ review ผ่าน; เปิด Codex รอบใหม่ไม่ต้องส่งบริบทเดิมซ้ำ
10. **Cost observability**: บันทึก counts (input/output chars, rows, approved reuse, AI-reviewed rows) และจำนวนโทเคนจริงจาก provider **ถ้ามี**; อย่าแปลง char เป็น token แล้วอ้างเป็น usage จริง; ยังไม่สามารถรับประกันเปอร์เซ็นต์ประหยัดได้จนวัดจริง

## ตัวอย่างวงรอบต้นทุนต่ำ
```powershell
python tools/token_saver.py pack --project projects/my-nds-game --mode missing --limit 40 --max-chars 9000 --output projects/my-nds-game/working/context_packet.md
python tools/token_saver.py suggest --project projects/my-nds-game --tm shared_memory/approved_tm.csv --output projects/my-nds-game/working/tm_suggestions.csv
```

- ส่ง Codex เฉพาะ `working/context_packet.md` และไฟล์ฉาก/ศัพท์ที่จำเป็น; หากไม่พอ ให้ค้นบริบทเพิ่มทีละ ID
- `suggest` ไม่เขียนทับ master; ต้องตรวจ suggestions ก่อนคัดลอกเข้า master
- ห้ามอ้างว่าทดสอบ renderer ผ่านเพียงเพราะประหยัดโทเคนได้

### Offline text lint (ช่วยลด AI tokens แต่ไม่แทนการตรวจภาษา)
`python tools/thai_text_lint.py --csv projects/my-nds-game/translations/master.csv --output projects/my-nds-game/qa/reports/thai_lint.json` ตรวจ token/สระลอยบางกรณีโดยใช้ heuristic เท่านั้น ไม่สามารถตัดสินไวยากรณ์หรือคุณภาพฟอนต์ในเกม.

## Cross-Project Translation Memory
เมื่อมีหลายโปรเจกต์ให้ใช้ `tools/cross_project_tm.py index/suggest/terms` ตรวจคำแปลที่ผ่าน REVIEWED/APPROVED/VERIFIED และ glossary จากทุกเกมแบบ offline; ส่งเฉพาะ shortlist ของเกมใหม่เข้า Codex ตามความจำเป็น ดู `docs/CROSS_PROJECT_TRANSLATION_MEMORY_TH.md` ทั้งนี้การเข้าคลังไม่ใช่การอนุมัติคำแปลของเกมใหม่ และการประหยัดโทเคนจริงต้องวัด usage.
