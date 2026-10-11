# Mario Party DS (USA Rev 2) — ROM map (read-only)

## Identity and provenance

- Platform: Nintendo DS (`NDS`); title header `MARIOPARTYDS`; game code `A8TE`; maker `01`.
- Header revision byte at `0x1E`: `02` (Rev 2).
- Size: `33,554,432` bytes; SHA-256 `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`; SHA-1 `96054049ac831720f1c7c63023cf18907352d45c`; CRC32 `4FCBB5C3`.
- The observed SHA-1 and CRC32 match the No-Intro-labeled `Mario Party DS (USA) (Rev 2).nds` reference and its 32 MiB size. The uploaded file's chain of custody is not independently known; this match establishes content identity, not legal ownership.
- The uploaded ROM was opened read-only. Its bytes remain outside this repository; no ROM or extracted asset payload is committed.

## NDS container and NitroFS

- Header section scan reports ARM9 at `0x4000` (462,464 bytes), ARM7 at `0x2DE400` (160,344 bytes), FNT at `0x305E00` (5,642 bytes), FAT at `0x307600` (2,984 bytes); all reported sections are in bounds.
- FAT contains 373 entries. FNT names 265 data files across root, `data/`, and `data/US/`; the first 108 FAT IDs are unnamed overlays. The ARM9 overlay table has 108 entries whose FAT references cover IDs 0–107; ARM7 has no overlay table. All 373 file ranges are in bounds. This maps descriptors to files only; overlay contents remain unmapped.
- Metadata-only file inventory and hashes: [`../qa/reports/nitrofs_inventory.csv`](../qa/reports/nitrofs_inventory.csv).

## Confirmed text-table family

- 35 files named `data/US/mpd_*_LZ.bin` decompress with the observed MPDS LZ77 variant: byte 0 is retained as an unknown header byte; bytes 1–3 give expanded size; then flag-bit-driven literal/back-reference groups.
- Expanded table structure confirmed on all 35 files: little-endian `uint32` count; `uint32[count]` offsets; null-terminated UTF-16LE strings at those offsets.
- The project-local `tools/mpds_adapter/` now performs bounds-checked identity/NitroFS/overlay inspection, extraction to a source-only CSV, and table round-trip checks. Synthetic unit tests cover NDS and overlay bounds, MPDS LZ, UTF-16LE tables and refuse-overwrite behavior.
- All 35 tables parse and serialize back to byte-identical expanded bytes: 2,672 rows total. Recompressing and decompressing each table also restores the exact expanded bytes, but the compressed container bytes differ for all 35 files. This proves codec round-trip only; it does not prove NitroFS repacking, patch correctness, or runtime behavior.
- Metadata-only adapter evidence: [`../qa/reports/mpds_adapter_validation.json`](../qa/reports/mpds_adapter_validation.json). Full source inventory is intentionally not stored in the repository; the CLI writes it only to the caller-selected output.
- Full table metadata: [`../qa/reports/text_table_scan.csv`](../qa/reports/text_table_scan.csv). Only the first ten main-menu rows are in the translation master; the rest of the game text is not bulk-exported here.
- Game-specific format reference: [Mario Party DS Editor README/source](https://github.com/aleokdev/mario-party-editor), which documents the MPDS LZ77 and UTF-16 text-table layout. This repository's reference implementation is not treated as a verified injector for Rev 2.

## Unknown / not yet mapped

- `data/ohanashi_event_data.bin` (story/event data), ARM9/overlay strings and code, font glyph mapping, text renderer, pointer semantics beyond the confirmed table format, and all non-`mpd_*` candidate containers remain unmapped. Overlay descriptors map to FAT entries, but their content formats are not classified.
- A broad scan of other `_LZ.bin` files produced candidates and decompression failures; those results are not promoted to confirmed text tables.
- No named NitroFS path includes `font` in its filename. This does not establish that fonts are absent; font resources may be unnamed, embedded, or referenced through overlays.
- A conservative in-memory single-file replacement prototype passes synthetic size-change, relocation, FAT/header update and reversible BPS tests. It has not been checked against the full image's metadata references and is not a verified Rev 2 repacker or injector; the third-party editor's workflow remains a format reference.
- Runtime scene assignment, line width, control token `[1]` semantics, Thai glyph availability, and emulator behavior are unverified.

## Current gate state

- G0 identity: PASS for exact revision/hash identity match; upload origin itself is not authenticated.
- G1 binary/patch: PENDING; synthetic relocation/rollback is proven on fixtures, but no game-image repack, candidate ROM build or production patch exists.
- G2 translation: PENDING; ten rows are DRAFT and scope coverage is not complete.
- G3 font/layout: PENDING; no Thai glyph or real emulator screenshot verification.
- G4 gameplay/save/load: PENDING; not tested in an emulator.
- G5 release: PENDING; no release artifact.
