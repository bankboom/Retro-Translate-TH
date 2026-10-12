# Mario Party DS (USA Rev 2) — ROM map (read-only)

## Identity and provenance

- Platform: Nintendo DS (`NDS`); title header `MARIOPARTYDS`; game code `A8TE`; maker `01`.
- Header revision byte at `0x1E`: `02` (Rev 2).
- Size: `33,554,432` bytes; SHA-256 `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`; SHA-1 `96054049ac831720f1c7c63023cf18907352d45c`; CRC32 `4FCBB5C3`.
- The observed SHA-1 and CRC32 match the No-Intro-labeled `Mario Party DS (USA) (Rev 2).nds` reference and its 32 MiB size. The uploaded file's chain of custody is not independently known; this match establishes content identity, not legal ownership.
- The uploaded ROM was opened read-only. Its bytes remain outside this repository; no ROM or extracted asset payload is committed.

## NDS container and NitroFS

- Header section scan reports ARM9 at `0x4000` (462,464 bytes), ARM7 at `0x2DEA00` (160,344 bytes), FNT at `0x305E00` (5,642 bytes), FAT at `0x307600` (2,984 bytes); all reported sections are in bounds.
- FAT contains 373 entries. FNT names 265 data files across root, `data/`, and `data/US/`; the first 108 FAT IDs are unnamed overlays. The ARM9 overlay table has 108 entries whose FAT references cover IDs 0–107; ARM7 has no overlay table. All 373 file ranges are in bounds. The descriptors map to files; compressed contents and filename literals are analyzed below, while code/data semantics remain unmapped.
- Additional read-only layout check: the first FAT payload starts at `0x75E00`; ARM9 and its overlay table end before it. ARM7 (`0x2DEA00–0x305C58`), FNT (`0x305E00–0x30740A`), FAT (`0x307600–0x3081A8`), and the banner pointer (`0x308200`) lie later in the address space, in a gap between FAT payloads. No FAT payload range overlaps those sections. A suffix-only relocation from the earliest file would move these referenced sections without moving their header pointers, so the synthetic prototype's conservative precondition fails for this image. It was not called on the clean ROM.
- All 373 FAT ranges are nonempty and nonoverlapping; 367 physical gaps total 273,233 bytes. The final FAT entry ends at `0x16364A0`, matching the header word at `0x80`; the attached file is 32 MiB and has 10,263,392 trailing bytes after that FAT end. Preserve this observed distinction during future layout design; do not replace the header value with physical file length by assumption.
- The banner pointer is `0x308200` and begins with version word `1`. The adjacent named FAT payloads begin at `0x308C00` (`data/dlp_icon.char`, ID 134), leaving a gap around the pointer. Its exact extent was not used to justify any repack.
- Metadata-only file inventory and hashes: [`../qa/reports/nitrofs_inventory.csv`](../qa/reports/nitrofs_inventory.csv).

## Confirmed text-table family

- 35 files named `data/US/mpd_*_LZ.bin` decompress with the observed MPDS LZ77 variant: byte 0 is retained as an unknown header byte; bytes 1–3 give expanded size; then flag-bit-driven literal/back-reference groups.
- Expanded table structure confirmed on all 35 files: little-endian `uint32` count; `uint32[count]` offsets; null-terminated UTF-16LE strings at those offsets.
- The project-local `tools/mpds_adapter/` now performs bounds-checked identity/NitroFS/overlay inspection, extraction to a source-only CSV, and table round-trip checks. Synthetic unit tests cover NDS and overlay bounds, MPDS LZ, UTF-16LE tables and refuse-overwrite behavior.
- Read-only overlay decompression check: all 107 ARM9 descriptors marked compressed were decoded in memory using the documented backward-LZ code-compression layout. For each entry, the compressed-size field agrees with the low 24 bits of the footer word, the decoded byte count equals the descriptor's RAM size, and no file was written. The single uncompressed overlay was left as-is. This confirms the codec and descriptor lengths for this image, not the meanings of every decoded code/data region.
- Decoded overlay strings expose ASCII asset paths and identifiers. Overlay 84 references `data/US/title_data_LZ.bin`; 86 references `data/US/main_menu_data_LZ.bin`; 87 references `data/US/mode_select_data_LZ.bin`; 96 references `data/ohanashi_event_data.bin` and `data/US/minigame_timeattack_data_LZ.bin`; 106 and 107 reference `data/ohanashi_event_data.bin` and `data/mpds_efc_LZ.bin`. These literals establish references from overlays to those filenames; the calling functions and runtime scene assignments are not yet traced.
- The backward-LZ footer and stream layout follows the implementation documented by [ndspy `codeCompression.py`](https://github.com/RoadrunnerWMC/ndspy/blob/master/ndspy/codeCompression.py). This is an independently maintained NDS format reference, not a game-specific injector.
- All 35 tables parse and serialize back to byte-identical expanded bytes: 2,672 rows total. Recompressing and decompressing each table also restores the exact expanded bytes, but the compressed container bytes differ for all 35 files. This proves codec round-trip only; it does not prove NitroFS repacking, patch correctness, or runtime behavior.
- Metadata-only adapter evidence: [`../qa/reports/mpds_adapter_validation.json`](../qa/reports/mpds_adapter_validation.json). Full source inventory is intentionally not stored in the repository; the CLI writes it only to the caller-selected output.
- Full table metadata: [`../qa/reports/text_table_scan.csv`](../qa/reports/text_table_scan.csv). The translation master contains sixty main-menu rows (IDs 0–59), thirteen Story Mode rows (IDs 0–12), and 110 Scenario rows (IDs 0–109) plus 40 staff-roll credit names retained in their original romanized form. This is 1,123/2,672 (42.03%) of the validated MPD-table inventory; the separate `ohanashi_event_data.bin` text scope remains unmapped, so this is not whole-game completion.
- Game-specific format reference: [Mario Party DS Editor README/source](https://github.com/aleokdev/mario-party-editor), which documents the MPDS LZ77 and UTF-16 text-table layout. This repository's reference implementation is not treated as a verified injector for Rev 2.

## Unknown / not yet mapped

- `data/ohanashi_event_data.bin` is FAT ID 281, 1,784,728 bytes. Its first word is 102 and the following 102 little-endian values are distinct, aligned, in bounds and nonmonotonic. A naive ASCII/UTF-16 scan did not yield coherent event text; the table and payload grammar remain unconfirmed.
- Further read-only structure check: the 102 values are all distinct, 4-byte aligned, and at or beyond `0x330` (after the 412-byte count/table prefix), with a maximum of `0x12B38C` inside the file. They are plausible indexed offsets, but their role is still a hypothesis: targets do not begin with a common recognizable text/table signature, and no record parser or event grammar is confirmed. Overlays 96, 106 and 107 contain the filename literal, linking code/data to this container without identifying individual event records.
- V3.2.1 offline fallback capability check: Capstone, `llvm-objdump`, and `arm-none-eabi-objdump` are unavailable; the standard-library ARM/Thumb subset scanner is available. It was not run on this ROM: the header and overlay descriptors confirm loaded image bounds and RAM bases, but do not establish a code-only range and instruction mode. The scanner cannot infer those boundaries. ASCII literals offer filename-level references only; ARM9/overlay functions, code references and text remain unclassified.
- Filename and raw-signature checks found no named `font` file and no `NFTR`, `RGCN`, `RLCN`, `NSCR`, `NCGR`, `NCLR`, or `SIR0` signatures in NitroFS payloads. Files such as `data/collection_char_data.bin`, `data/dlp_icon.char` / `.pltt`, and menu assets remain candidates only; this scan does not establish that the game lacks an embedded or custom font.
- `data/US/main_menu_data_LZ.bin` decodes with the known MPDS LZ codec from 19,555 to 20,052 bytes. Related title, mode-select and story-mode files also decode: `title_data_LZ.bin` 133,280→122,308; `mode_select_data_LZ.bin` 10,446→11,424; `story_mode_data_LZ.bin` 42,691→43,868. Their first words are 34, 21, and 77 for those three files, versus 23 for main menu; subsequent words resemble tables but do not form a confirmed simple file-relative offset table (some values point inside the presumed table prefix). Payload roles and text relation remain unknown.
- The menu/story filenames appear in decoded overlay literals: title in overlay 84, main menu in 86, mode select in 87, and story mode in 98. These confirm filename references only, not the associated UI functions.
- A bounded probe treated each of the 102 event-table values as a candidate MPDS-LZ segment start ending at the next sorted value. It produced no positive-size valid decode (99 format errors, 3 zero-size headers). This does not prove the values are record starts or rule out another compression scheme inside the event container.
- The known `[1]` token's runtime substitution, ARM9/overlay code references, Thai glyph mapping and renderer are still unconfirmed. No real-emulator evidence exists.
- A broad scan of other `_LZ.bin` files produced candidates and decompression failures; those results are not promoted to confirmed text tables.
- No named NitroFS path includes `font` in its filename. This does not establish that fonts are absent; font resources may be unnamed, embedded, or referenced through overlays.
- A conservative in-memory single-file replacement prototype passes synthetic size-change, relocation, FAT/header update and reversible BPS tests, but its guard rejects this ROM's section placement before any replacement occurs. It is not a verified Rev 2 repacker or injector; the third-party editor's workflow remains a format reference.
- Runtime scene assignment, line width, control token `[1]` semantics, Thai glyph availability, and emulator behavior are unverified.

## Current gate state

- G0 identity: PASS for exact revision/hash identity match; upload origin itself is not authenticated.
- G1 binary/patch: PENDING; synthetic relocation/rollback is proven on fixtures, but no game-image repack, candidate ROM build or production patch exists.
- G2 translation: PENDING; 873 rows (32.67% of the 2,672 validated MPD-table rows) are DRAFT. This percentage excludes unmapped `ohanashi_event_data.bin` and does not represent whole-game completion.
- G3 font/layout: PENDING; no Thai glyph or real emulator screenshot verification.
- G4 gameplay/save/load: PENDING; not tested in an emulator.
- G5 release: PENDING; no release artifact.
