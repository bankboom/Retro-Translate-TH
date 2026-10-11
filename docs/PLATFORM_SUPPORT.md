# ขอบเขตเครื่องเกมที่รองรับ

**Framework workflow** ใช้ได้ทั่วไป แต่ **CLI audit ROM แบบ header เชิงลึก** ยังตรวจเฉพาะ `NDS` และ `GBA`. `retro_translate_v3.py` รองรับ BPS กับไบนารีที่ใส่หน่วยความจำได้ไม่เกิน 512 MiB โดยไม่ขึ้นกับเครื่องเกม และ CSV QA เท่านั้น.

| กลุ่ม | เครื่องเกม | งาน adapter ที่ต้องพัฒนาเพิ่ม |
|---|---|---|
| Nintendo 8/16-bit | NES, SNES, GB, GBC | bank/mapper, text pointers, tile fonts, compression |
| Nintendo handheld | GBA, NDS | GBA LZ/graphics/pointers; NDS NitroFS/NFTR/overlays/custom banks |
| Nintendo 3D | N64, GameCube, Wii, 3DS | game archive, proprietary fonts, disc/archive rebuild, emulator |
| Sega | Master System, Game Gear, Mega Drive, Saturn, Dreamcast | ROM banking, charset/font, endianess, CD/GDI rebuild |
| Other handheld | WonderSwan, Neo Geo Pocket, PSP | asset bundles, text codecs, custom glyph layout |
| Other/home | PC Engine, Neo Geo, PS1, PS2, Arcade, PC Classic | CD images or ROM sets, pointer engines, compression, text rendering |

ดู `profiles/platform_profiles.json` สำหรับสมมติฐานเบื้องต้นในการสำรวจ **ไม่ใช่ตัวบ่งชี้ความสามารถที่พัฒนาเสร็จแล้ว**.

## Emulator suggestions (check compatibility per game)
GBA: mGBA; NDS: melonDS; GB/GBC: SameBoy; NES/SNES: Mesen/Snes9x; 3DS: Azahar; PS1: DuckStation; PSP: PPSSPP. การติดตั้ง/CLI automation ไม่รวมใน Framework และอาจมีความต่างตามเวอร์ชัน.
