# Game-specific workflow — Mario Party DS USA Rev 2

## Goal and safe input

Translate grounded English strings to natural Thai while preserving story, UI behavior, control tokens and save/game mechanics. Keep the user-provided clean ROM external and immutable. Build only into a separate candidate from a known baseline; distribute only a patch if authorized, never a ROM.

## Evidence-backed findings

1. G0 identity matches the No-Intro-labeled USA Rev 2 SHA-1/CRC32 reference; see `qa/reports/g0_identity.md` and `qa/reports/rom_scan.json`.
2. The NitroFS names 265 files and 373 FAT entries. The 108 ARM9 overlay descriptors map to unnamed FAT IDs 0–107. All 107 compressed overlays now decode to their descriptor RAM sizes; embedded path literals reference title, menu, minigame and story-event assets. Function-level code references remain untraced. See `qa/reports/nitrofs_inventory.csv`, `qa/reports/mpds_adapter_validation.json` and `qa/reports/g1_roundtrip.md`.
3. 35 `data/US/mpd_*_LZ.bin` tables contain 2,672 validated UTF-16LE rows. The local adapter reproduces expanded bytes after parse/serialize and after recompress/decompress for all 35; compressed bytes differ. A conservative in-memory NitroFS replacement prototype passes synthetic two-file relocation/FAT and reversible BPS tests only; it has not been run against the game image. See `qa/reports/text_table_scan.csv` and `qa/reports/g1_roundtrip.md`.
4. 323 text rows are DRAFT in `translations/master.csv`: main-menu IDs 0–59, Story Mode IDs 0–12, and Scenario IDs 0–109. The added Scenario batch preserves source token order/spelling and line-break counts; tokens `[c4]`, `[f]`, `[name1]`, `[w]`, `[c3]`, `[mgname1]`, and `[name2]` are registered as unverified. The first 140 staff-roll personal names are retained in their source romanization pending credit-context review. `[1]` also remains unresolved and must be preserved. This is 323/2,672 (12.09%) of the validated MPD-table inventory only; the `ohanashi_event_data.bin` scope remains unmapped.
5. Read-only layout review found the first FAT payload at `0x75E00`, followed by ARM7, FNT, FAT and the banner pointer in inter-file space. These header-referenced regions would move under a simple suffix rebuild, while their header pointers would not. The synthetic prototype's guard would reject this image; it was not called with the clean ROM. Details and unresolved asset findings are in `analysis/ROM_MAP.md`.
6. The title, main-menu, mode-select and story-mode `*_LZ.bin` resources decode with the known MPDS LZ codec. Overlays 84/86/87/98 contain matching filename literals. Their expanded payload structures are not yet understood; the story-event archive remains unmapped.

## Work sequence

- [x] Read-only ROM identity and NDS header/FNT/FAT bounds check.
- [x] Implement read-only NDS/NitroFS inventory, MPDS LZ/table codec and source-only extraction CLI with synthetic unit tests.
- [x] Map ARM9 overlay descriptors to FAT entries with bounds checks and synthetic tests; do not infer text from the mapping.
- [x] Validate all 35 known MPD tables and compressed decode-after-reencode round trip; keep output bytes and ROM separate.
- [x] Draft sixty main-menu/save-file/mode strings, thirteen Story Mode strings, and 110 Scenario strings (IDs 0–109); preserve the first forty staff-roll personal names in source romanization; keep DRAFT and NOT_INJECTED separate and preserve observed tokens and source line-break counts.
- [x] Test a size-changing NitroFS replacement on a synthetic NDS with two FAT files; verify downstream relocation, FAT references, header size/checksum, and synthetic BPS apply/reverse byte equality.
- [x] Inspect header, overlay-table, FAT and banner-pointer placement against physical FAT ranges read-only; confirm that the current synthetic rebuild precondition fails for this image without invoking it.
- [x] Decode all 107 compressed ARM9 overlays in memory, match decoded sizes to descriptor RAM sizes, and classify embedded asset-path literals.
- [x] Decode the title/main-menu/mode-select/story-mode MPDS-LZ assets and map their filename literals to overlays; keep table/layout semantics unconfirmed.
- [ ] Map `ohanashi_event_data.bin`, ARM9/overlay text and other non-MPD text containers; establish complete game text scope before progress percentages.
- [ ] Trace ARM9/overlay references only after a code-only range and ARM/Thumb mode are independently established. V3.2.1 `portable_code_probe.py` may produce bounded candidates without a full disassembler; do not scan mixed code/data images or treat pattern hits as verified xrefs. Current state: no verified code range/mode, so no scan was run.
- [ ] Determine record boundaries and semantics for the 102-entry `ohanashi_event_data.bin` table; aligned in-bounds offsets are observed, but their interpretation is still hypothetical.
- [ ] Identify font resources, encoding/glyph mapping, renderer and line/width constraints from source and real emulator evidence.
- [ ] Determine whether a game-specific relocator can update every header and embedded offset reference, while preserving observed logical-size/padding behavior, before considering any candidate build.
- [ ] Verify exact-file round-trip and relocation on a disposable validated fixture; only then consider a reversible 1–5-string candidate patch from the exact baseline.
- [ ] Context-review translations, tokens, spelling, terminology and length in small batches; use reviewed glossary/TM only.
- [ ] Run real emulator screenshot checks (including Thai vowels/tone marks) and gameplay/save/load checks. Keep G3/G4 PENDING until evidence is recorded.
- [ ] Release only a patch, manifest, hashes, rollback steps and known issues after G0–G4 pass for stated scope and human sign-off.

## Current blockers

- Story/event strings and full text scope are not mapped; `ohanashi_event_data.bin` has a 102-entry in-bounds offset-like table, but payload grammar is unconfirmed.
- The first FAT payload precedes ARM7/FNT/FAT/banner locations; a suffix-only relocator would invalidate those pointers. ARM9/overlay internal references remain unclassified.
- Thai font/rendering support is unknown; no injection candidate has been built.
- `[1]` substitution semantics are not yet confirmed.
- No emulator/version or screenshots were supplied; G3/G4 cannot pass yet.
- Compressed table outputs do not match original compressed bytes. The synthetic rebuild prototype is not validated for this game image; do not use it on the clean ROM or create a candidate patch until full-image references, logical size/padding behavior and rollback are reviewed.
