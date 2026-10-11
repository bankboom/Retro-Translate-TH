# คำสั่งสำหรับ Codex: ปรับความสวยงามฟอนต์ไทย

ใช้ skill `retro-thai-localization` กับ `projects/<SLUG>`.
เปรียบเทียบ known-good baseline กับ candidate; หา font format/table/glyph metrics ของเกมจริง และทดสอบ กา มา ภาษา สำ ต้ ตุ เฉพาะ renderer นั้น. ตรวจความสูง `า`, สระบน/ล่าง, ไม้เอก-ไม้โท, vowel/tone mark overlap, baseline, left/right bearings, word wrap, ตัวเลข/ภาษาอังกฤษ, หลาย font sizes. เปลี่ยนทีละชุด glyph โดยไม่แตะโครงสร้างข้อความที่ไม่เกี่ยว; สร้าง build ID ใหม่และ diff พร้อมเหตุผล. **ถ้าไม่มี screenshot emulator จริง ให้รายงานว่าการพิสูจน์ภาพยัง PENDING** ไม่ต้องแต่งภาพทดสอบปลอม.
