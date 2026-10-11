# Next Codex task — Mario Party DS USA Rev 2

1. Read root `AGENTS.md`, this project's `AGENTS.md`, `project_profile.json` and this file.
2. Use `tools/mpds_adapter/` with the exact project profile for read-only inspection, inventory, extraction and round-trip checks. See its README and `qa/reports/mpds_adapter_validation.json`.
3. Keep the extracted 2,672-row source inventory outside Git until selected IDs are context-reviewed; the master now has ten DRAFT / NOT_INJECTED rows (US_MAIN_MENU IDs 0–9), added in two five-row batches.
4. Map `data/ohanashi_event_data.bin`, ARM9 code and overlay contents/text, Thai font/glyph encoding, renderer and the runtime meaning of `[1]` before claiming complete text coverage. Overlay descriptors already map to FAT IDs 0–107; their contents are still unknown.
5. A conservative in-memory replacement prototype now passes synthetic two-file size-growth, downstream relocation, FAT/header update, and synthetic BPS forward/reverse tests. Do not run it against the clean game image: its complete NDS metadata/layout constraints have not been verified there.
6. Next, extend read-only mapping of NDS metadata plus `ohanashi_event_data.bin`, ARM9/overlay contents, font/glyph encoding and `[1]` runtime meaning; decide whether a dedicated image-specific repack plan can safely account for all references before any candidate build.
7. Keep the master at ten DRAFT / NOT_INJECTED strings until the above checkpoint. Keep G1–G5 PENDING as applicable; G3/G4 require real emulator evidence and G5 requires human sign-off.
