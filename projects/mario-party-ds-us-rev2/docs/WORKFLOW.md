# Game-specific workflow — Mario Party DS USA Rev 2

## Goal and safe input

Translate grounded English strings to natural Thai while preserving story, UI behavior, control tokens and save/game mechanics. Keep the user-provided clean ROM external and immutable. Build only into a separate candidate from a known baseline; distribute only a patch if authorized, never a ROM.

## Evidence-backed findings

1. G0 identity matches the project-profile USA Rev 2 SHA-1/CRC32 reference; see `qa/reports/g0_identity.md` and `qa/reports/rom_scan.json`.
2. The NitroFS names 265 files and 373 FAT entries. The 108 ARM9 overlay descriptors map to unnamed FAT IDs 0–107. All 107 compressed overlays decode to their descriptor RAM sizes; embedded path literals reference title, menu, minigame and story-event assets. Function-level code references remain untraced.
3. Thirty-five `data/US/mpd_*_LZ.bin` tables contain 2,672 validated UTF-16LE rows. The local adapter reproduces expanded bytes after parse/serialize and after recompress/decompress for all 35; compressed bytes differ. Synthetic relocation and reversible BPS tests do not prove a game-image repack.
4. `translations/master.csv` now contains all 2,672 unique validated MPD-table IDs as Thai DRAFT / NOT_INJECTED rows. A source comparison found no missing, extra or duplicate IDs; English source fields match the extracted inventory; every Thai field is present; control-token order and line-break counts match. See `qa/reports/translation_coverage.md`. This is 100% coverage of the validated MPD tables only, not complete game-text coverage. Contextual translation review remains pending.
5. Read-only layout review found the first FAT payload at `0x75E00`, followed by ARM7, FNT, FAT and the banner pointer in inter-file space. A suffix-only relocation would move referenced sections without updating their header pointers; the synthetic prototype rejects this layout and was not run on the clean ROM.
6. `data/ohanashi_event_data.bin` (FAT ID 281) has a 102-entry prefix followed by aligned, in-bounds offset-like values, but record grammar is unconfirmed. The archive, ARM9/overlay text, Thai font mapping, renderer and runtime scene assignment remain unmapped or unverified.

## Work sequence

- [x] Verify ROM identity and NDS header/FNT/FAT bounds read-only.
- [x] Implement read-only NDS/NitroFS inventory, MPDS LZ/table codec and source-only extraction CLI with synthetic unit tests.
- [x] Map ARM9 overlay descriptors to FAT entries with bounds checks and synthetic tests; do not infer text from the mapping.
- [x] Validate all 35 known MPD tables and expanded-byte round trips; keep extracted game data and ROM separate.
- [x] Draft all 2,672 validated MPD-table rows; preserve source IDs, control tokens and line-break counts; keep every row DRAFT / NOT_INJECTED. This does not pass G2 semantic QA.
- [x] Check full master coverage against read-only extracted source: 2,672 unique IDs, no missing/extra/duplicate IDs, source text exact, nonempty Thai, matching tokens and line-break counts.
- [ ] Context-review spelling, meaning, terminology, characters, numbers and length in small batches; use only reviewed glossary/TM.
- [ ] Map `ohanashi_event_data.bin`, ARM9/overlay text and other non-MPD containers before claiming full-game text coverage.
- [ ] Trace ARM9/overlay references only after a code-only range and ARM/Thumb mode are independently established. Do not scan mixed code/data or treat candidates as verified xrefs.
- [ ] Identify font resources, encoding/glyph mapping, renderer and line/width constraints from source and real emulator evidence.
- [ ] Validate a game-specific relocator and rollback on disposable fixtures; the current synthetic prototype is not validated for this game image and must not be run on the clean ROM.
- [ ] Run real emulator screenshot checks (including Thai vowels/tone marks) and gameplay/save/load checks. Keep G3/G4 PENDING until evidence is recorded.
- [ ] Release only a patch, manifest, hashes, rollback steps and known issues after applicable gates pass and a human signs off.

## Current blockers

- Story/event strings and the rest of full-game text scope are not mapped.
- The ROM layout places header-referenced sections after the first FAT payload; a suffix-only rebuild would invalidate pointers. Internal ARM9/overlay references remain unclassified.
- Thai glyph coverage, rendering and UI widths are unknown; no candidate has been injected.
- `[1]` substitution semantics are not confirmed.
- No emulator screenshots or gameplay/save/load results exist; G3/G4 remain PENDING.
- G1 remains PENDING: synthetic fixtures are not a game-image rebuild or patch. G2 remains PENDING: 100% table draft coverage is not contextual translation approval. G5 remains PENDING until human sign-off.
