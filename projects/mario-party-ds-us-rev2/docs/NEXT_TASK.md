# Next Codex task — Mario Party DS USA Rev 2

1. Read root `AGENTS.md`, this project's `AGENTS.md`, `project_profile.json` and this file.
2. Use `tools/mpds_adapter/` with the exact project profile for read-only inspection, inventory, extraction and round-trip checks. See its README and `qa/reports/mpds_adapter_validation.json`.
3. Keep the extracted 2,672-row source inventory outside Git until selected IDs are context-reviewed; the master now has ten DRAFT / NOT_INJECTED rows (US_MAIN_MENU IDs 0–9), added in two five-row batches.
4. Read-only physical layout review: first FAT payload begins at `0x75E00`; ARM7, FNT, FAT and the banner pointer occur later in gaps between FAT payloads. The current suffix-only prototype would reject this layout; it was not invoked on the clean ROM. The header word at `0x80` equals the last FAT end `0x16364A0`, while the physical file is padded to 32 MiB. See `analysis/ROM_MAP.md` and `qa/reports/g1_roundtrip.md`.
5. `data/ohanashi_event_data.bin` (FAT 281) has a 102-entry in-bounds but nonmonotonic offset-like table; no payload grammar is confirmed. Continue read-only format analysis. ARM9 overlay descriptors map 108 unnamed FAT files, 107 marked compressed; their contents and compression layout remain unknown.
6. Next, classify event/menu containers and ARM9/overlay references with suitable ARM-capable inspection tools; then identify font/glyph encoding, renderer and `[1]` runtime meaning. Determine whether every header and embedded file-offset reference can be updated by a dedicated relocator before making a candidate.
7. Keep the master at ten DRAFT / NOT_INJECTED strings until the above checkpoint. Keep G1–G5 PENDING as applicable; G3/G4 require real emulator evidence and G5 requires human sign-off.
