# Pokémon Omega Paradox TH — P4.4 Native E8xx Fixed-Slot Smoke

**วันที่:** 22 ตุลาคม 2026
**ผลที่พิสูจน์ได้:** `omega_control_tokens.py` แยกรหัส Native PUA ที่อยู่ติดคำสั่ง F000 ออกจาก operands ของ F000 ได้ถูกต้อง; `p44_fixed_slot_pilot.py` สร้าง logical escaped stream ที่รักษาลำดับคำสั่งและจำนวน native code units ระหว่างแต่ละ command เดิม โดยยังไม่แตะ ROM

## Root-cause corrected in shared token lexer
เดิม regex `F000 + opcode + arbitrary escaped 16-bit operands` จะ **กลืน E8xx native glyph ถ้าตามหลัง F000 ทันที** แล้วเข้าใจว่าเป็น operand ของคำสั่ง ทำให้ QA หรือ text splice อาจปฏิเสธข้อมูลที่ถูกต้อง/เข้าใจตำแหน่งผิด

P4.4 แก้ lexer ให้หยุดก่อนกลุ่ม `E000-EFFF` ที่สงวนไว้เป็น Glyph/PUA (สำหรับตัวแยก text ภายใต้ขอบเขตนี้); ถ้าพบ operand จริงที่อยู่ในย่านนี้ ต้องตรวจรูปแบบ game-specific เพิ่ม ไม่อนุมานเงียบ ๆ

## P4.4 tool usage (one message per pilot)
1. นำ P3.7B/P3.7A reference message bytes มาถอดเป็น `\\xE8NN` code units จาก ROM ของเครื่องตัวเอง โดยเก็บตำแหน่ง archive/file_id/message_id และ SHA256 ของ ROM ที่นำข้อมูลมา (ห้ามเดารหัสจาก Unicode ไทย)
2. ใส่หนึ่งแถวใน `glyph_maps/P4_4_NATIVE_REFERENCE_EXTRACTED_TEMPLATE.csv` โดยไม่อัปโหลด ROM หรือข้อความเกมทั้งชุดลง GitHub สาธารณะ
3. ยืนยันว่าแต่ละ `native_reference` เป็นข้อความไทยถูกบริบทตาม scope; `evidence_state=REFERENCE_EXTRACTED` อนุญาตแค่ static smoke; `IN_GAME_VERIFIED` ต้องมีหลักฐานจากเกมจริง
4. รันแบบ read-only:
```bash
python projects/pokemon-omega-paradox/tools/p44_fixed_slot_pilot.py \
  --input-csv /private/p44_one_message.csv \
  --out /private/p44_fixed_slot_qa.json
```
5. โปรแกรมปฏิเสธ raw Unicode Thai, code E0xx ที่ไม่ได้รับรองให้ใช้กับ renderer นี้, source ที่ไม่ใช่ ASCII/unknown escaped codec, overflow ต่อ segment, control payload เปลี่ยน, หรือต่าง bank
6. แม้ output มี `control_signature_preserved=true` และความยาวคงที่ ก็เป็นเพียง **escaped logical text**; ไม่ใช่ NARC serializer, BPS หรือ Emulator test. ต้องเปรียบเทียบ native bytes กับ reference ROM จริงก่อนฉีด

## Evidence
- GitHub Actions [39786876015](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39786876015): **50/50 static/synthetic tests PASSED**, including new adjacent-F000-E8xx and nonzero-operand checks. ไม่มี ROM ทำงานใน CI
- Clean Omega expected SHA256: `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`
- Tested fallback: P3.7B from original Omega. Do not overwrite or repack its native font/ARM9 without specific issue evidence.

## Remaining / strict finish line
- Binary runtime for uploaded original ROM/P3.7B package currently unavailable; no P4.4 BPS created.
- Need extract real reference units, prove native glyph meanings, add reviewed translation, rebuild correct NARC/MSG and BPS, test on melonDS real runtime, then expand 20,096 review queue/other assets.
- G2–G5 remain pending; 50/50 **does not** imply P4.4 gameplay or full-game translation completed.
