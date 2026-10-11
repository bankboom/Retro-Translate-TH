# ติดตั้งผ่านแชต Codex (V3.2)

**ผู้ใช้ไม่ต้องเปิด BAT หรือรัน Python เอง.** ให้ Codex อ่าน `START_V3_2_CODEX_CHAT_TH.txt` แล้วตรวจ/เรียก Python ตามสิทธิที่มี. ต้องให้ Codex เห็นไฟล์ ZIP/โฟลเดอร์ก่อน. ถ้าไม่มีสิทธิ์เขียน `~/.codex` สามารถใช้กฎใน workspace ชั่วคราวได้ และแจ้งข้อจำกัดชัดเจน.

Compatibility: V3.2 **ใช้ชื่อ Skill `retro-game-th-v3-1` และเส้นทางเดิม** เพื่ออัปเกรดการติดตั้ง V3.1 ไม่สร้าง Skill ซ้ำ. ตัวติดตั้งแก้เฉพาะ managed block `RETRO_THAI_V3_1` และไฟล์ที่เป็นของ framework, ไม่แตะเกมภายใน `~/RetroThaiProjects/projects`. อย่าลบโฟลเดอร์ project/TM/ROM.

Codex ควรรัน `python tools/install_once.py install` เอง และตรวจด้วย `python tools/install_once.py status` หลังได้รับอนุญาต. เมื่อคำสั่งติดตั้งสำเร็จให้เริ่มแชตใหม่เพื่อโหลดกฎ/Skill; หาก Codex ยังไม่เห็น Skill ให้แจ้งตามจริง. ทดสอบ `python -m unittest discover -s tests -p 'test_*.py' -q` ในไดเรกทอรี framework.

เมื่ออัปเกรดห้ามคัดลอกโปรเจกต์เกมเก่ามายัง framework เอง; เลือก workspace เดิมไว้เพื่อให้ TM ที่มีข้อมูลจริงยังใช้งานได้.
