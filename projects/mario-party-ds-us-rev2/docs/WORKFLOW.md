# Game-specific workflow — Mario Party DS USA Rev 2

## Goal and safe input

Translate grounded English strings to natural Thai while preserving story, UI behavior, control tokens and save/game mechanics. Keep the user-provided clean ROM external and immutable. Build only into a separate candidate from a known baseline; distribute only a patch if authorized, never a ROM.

## Evidence-backed findings

1. G0 identity matches the No-Intro-labeled USA Rev 2 SHA-1/CRC32 reference; see `qa/reports/g0_identity.md` and `qa/reports/rom_scan.json`.
2. The NitroFS names 265 files and 373 FAT entries (including 108 overlays). See `qa/reports/nitrofs_inventory.csv`.
3. 35 `data/US/mpd_*_LZ.bin` tables contain 2,672 validated UTF-16LE rows. Decode/parse/serialize reproduces expanded bytes for all 35; see `qa/reports/text_table_scan.csv` and `qa/reports/g1_roundtrip.md`.
4. The first five UI strings are drafts in `translations/master.csv`; `[1]` appears as an unresolved runtime token and must be preserved.

## Work sequence

- [x] Read-only ROM identity and NDS header/FNT/FAT bounds check.
- [x] Validate known MPDS text-table format and unchanged expanded-byte round trip.
- [x] Draft five main-menu/save-file strings; keep DRAFT and NOT_INJECTED separate.
- [ ] Map `ohanashi_event_data.bin`, ARM9/overlay text and other non-MPD text containers; establish complete game text scope before progress percentages.
- [ ] Identify font resources, encoding/glyph mapping, renderer and line/width constraints from source and real emulator evidence.
- [ ] Build a game-specific extractor/repacker only after container coverage and format tests are established; never alter input ROM.
- [ ] Verify round-trip of extracted/rebuilt files, then make a reversible 1–5-string candidate patch from the exact baseline.
- [ ] Context-review translations, tokens, spelling, terminology and length in small batches; use reviewed glossary/TM only.
- [ ] Run real emulator screenshot checks (including Thai vowels/tone marks) and gameplay/save/load checks. Keep G3/G4 PENDING until evidence is recorded.
- [ ] Release only a patch, manifest, hashes, rollback steps and known issues after G0–G4 pass for stated scope and human sign-off.

## Current blockers

- Story/event strings and full text scope are not mapped.
- Thai font/rendering support is unknown; no injection candidate has been built.
- `[1]` substitution semantics are not yet confirmed.
- No emulator/version or screenshots were supplied; G3/G4 cannot pass yet.
