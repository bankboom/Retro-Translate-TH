# Pokémon Omega Paradox — Project Rules
Follow repository AGENTS.md and this file. Maintain separate DRAFT / REVIEWED / ENCODED / BINARY_VERIFIED / EMULATOR_VERIFIED states.
Goal: Thai-localize all user-visible game text by reusing compatible Pokémon White Thai translations, then translating remaining Omega-specific text.
Do NOT overwrite Omega-specific messages with White archives merely by matching message ID. Match original text, context/speaker, code signature and rendering bank first.
Keep clean Omega ROM immutable; distribute only BPS. Source SHA256: 29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b.
Use known-good native E8xx dialog glyph sequences from matching context; never assume Unicode U+0Exx or menu-glyph E0xx work in dialogue. Do not invent a character mapping.
Preserve all control codes and operand bytes, page breaks, terminators and length/pointer bounds; check pixel width as well.
Smoke-test small changes before large batches; verify BPS CRC/SHA roundtrip, in-game rendering, dialogue advance, battle/save/load.
Evidence: P3.3A greeting; P3.6B names; P3.7A Drake personality; P3.7B Cynthia partial line. P3.2 and P3.5 failed with question marks/freeze. Images alone do not prove whole-game stability.
This folder contains preparation and drafts, NOT a complete patch or certification of 100% translation.
