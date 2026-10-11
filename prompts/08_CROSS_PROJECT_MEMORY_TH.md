# Codex Chat Prompt — Cross-Project Memory (V3.1 Add-on)

ใช้คู่มือ V3.1 พร้อม Cross-Project Translation Memory กับเกมที่กำลังทำ โดย:

1. อ่าน AGENTS.md และ docs/CROSS_PROJECT_TRANSLATION_MEMORY_TH.md; ตรวจ `projects/<current>/project_profile.json` และ `translations/master.csv`.
2. ตรวจว่ามีโปรเจกต์เก่าใน `projects/` ที่มีคำแปลผ่าน REVIEWED/APPROVED/VERIFIED; **อย่าสรุปจาก DRAFT**.
3. ถ้ารู้แน่ชัดว่าเป็นซีรีส์เดียวกัน ให้เติม `series_id` ลงใน profile ของแต่ละเกมที่ยืนยันแล้ว (ไม่แก้ publisher โดยเดา).
4. ให้รัน `tools/cross_project_tm.py index`, `suggest`, `terms` เพื่อสร้าง shortlist ใน `working/`; อย่าส่ง CSV ใหญ่ทั้งหมดเข้าบทสนทนา.
5. จัดกลุ่มคำแนะนำ: exact+context+series, exact missing-context, cross-game exact, fuzzy in-series, conflicts.
6. ตรวจความหมาย เนื้อเรื่อง Speaker/Scene/Game mechanics, Glossary, control tokens, ความยาว UI ก่อนนำไปใช้; ไม่มีข้อมูลให้ระบุ NEEDS_CONTEXT.
7. แก้เพียงบรรทัดที่ผ่านการรีวิว บันทึก provenance/เหตุผลลง QA note และทำฟอนต์/Emulator QA ของเกมใหม่เป็นอิสระ.
8. รายงานจำนวน accepted / reviewed-needed / rejected / conflicts แยกจากเปอร์เซ็นต์คำแปลและสถานะ G0–G5 ตามหลักฐานจริง.
9. ประหยัดโทเคน: ใช้ SQL/Python offline, batch สั้น, พิมพ์เฉพาะ delta, ไม่โหลดไฟล์จากทุกเกมมาใส่ prompt.

ห้ามคัดลอกคำแปลที่มีบริบทไม่ตรง และห้ามเปลี่ยนสถานะ G2–G5 เพียงเพราะ CPTM พบคำแปล.
