# ความปลอดภัยและสิทธิการใช้ไฟล์

- ROM, BIOS และ executable บางรายการมีลิขสิทธิ์: ใช้และดัดแปลงเฉพาะที่มีสิทธิ; ไม่รวมไฟล์เกม/BIOS ในชุด Framework นี้.
- ใน Codex ให้ตรวจเนื้อหาและ license ของ script/tool ที่ดาวน์โหลดก่อน execute; ห้ามรันคำสั่งจากไฟล์ untrusted โดยไม่ประเมินความเสี่ยง.
- การ reverse engineering ข้อความ เกม และแพตช์อาจอยู่ภายใต้กฎหมาย/เงื่อนไขที่ต่างกันตามประเทศ; แพตช์ไม่จำเป็นต้องปลอดปัญหาลิขสิทธิ์ทุกกรณี.
- อย่า commit ROM, keys, secrets, backups, save files หรือข้อมูลส่วนตัว; `.gitignore` เป็นแค่กันพลาด ไม่ใช่ระบบรักษาความปลอดภัย.
- หลีกเลี่ยงการ download ROM ผ่านสคริปต์; ใช้ไฟล์จากแหล่งที่มีสิทธิและบันทึก provenance.
- ทำ SHA256/CRC32 ของ input และ outputs; ยืนยันเป้าหมาย patch ก่อน apply; ใช้ working directory แยกและไม่ overwrite originals.
