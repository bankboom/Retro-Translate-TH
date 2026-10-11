# G1 — Read-only MPDS table round-trip probe

Status: **PENDING** for binary/patch integrity.

- Scope: all 35 `data/US/mpd_*_LZ.bin` entries (2,672 rows).
- Overlay metadata: all 108 ARM9 overlay descriptors map one-to-one to unnamed FAT file IDs 0–107; this confirms descriptor mapping only, not overlay contents or text.
- Read method: the project-local `mpds_adapter` verifies the exact profile identity, scans NitroFS/FAT bounds, decodes the MPDS LZ77 stream, parses the count/offset table and UTF-16LE strings, then serializes and compresses them.
- Result: 35/35 expanded byte streams matched byte-for-byte after parse/serialize, and 35/35 recompressed containers decode to the same expanded bytes. The compressor's output bytes differ from the original container for all 35 files; this is expected for the current deterministic encoder and is recorded in `mpds_adapter_validation.json`.
- Safety: the ROM is opened read-only; before/after SHA-256 remains `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`. Source inventory output was created only in temporary storage and is not in the repository.
- Baseline limits before the synthetic prototype: no full-image repack, production BPS, or candidate ROM existed. The synthetic prototype below does not change those facts for the game image; G1 remains PENDING.

## Synthetic rebuild and rollback test (2026-10-11)

- Added `tools/mpds_adapter/rebuild.py`, a pure in-memory, single-file replacement prototype. It keeps the input immutable, preserves gaps and trailing bytes, aligns relocated payloads, updates FAT ranges, ROM size, and the NDS header CRC16.
- Synthetic two-file NDS fixture: growing FAT file 0 from 5 to 16 bytes moved file 1 from `[0x408, 0x40B)` to `[0x414, 0x417)`; the second payload and protected prefix remained unchanged. `parse_nitrofs` accepted the rebuilt image.
- A generated synthetic BPS patch applied clean → rebuilt, and a reverse synthetic BPS patch restored rebuilt → clean byte-for-byte. The test uses the framework BPS applier; no production patch was generated.
- The prototype rejects unknown IDs, malformed images, overlapping file ranges, and known metadata that overlaps or follows FAT payloads. It has not been run against the actual game ROM. This is implementation evidence for synthetic behavior only; G1 remains PENDING, and no injection is authorized by this result.
- The unknown leading compression byte, control-token grammar, `ohanashi_event_data.bin`, overlay contents and other binary containers remain outside this probe.

## Read-only full-image layout review (2026-10-11)

- Re-ran the profile identity inspection: 32 MiB physical file, SHA-256 unchanged at `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`.
- First FAT payload is at `0x75E00`; ARM9 is `0x4000–0x74E80`, ARM9 overlay table `0x75000–0x75D80`. ARM7 is `0x2DEA00–0x305C58`, FNT `0x305E00–0x30740A`, FAT `0x307600–0x3081A8`, and banner pointer `0x308200`. Those latter references are later than the first file and lie in the gap between FAT payloads; they do not overlap FAT file ranges.
- All 373 FAT ranges are nonempty and nonoverlapping, with 367 gaps. The last FAT end is `0x16364A0`, equal to the observed header word at `0x80`; the physical 32 MiB file continues after that point. Preserve this observed distinction and do not assume physical file length is the correct header value.
- Static precondition review shows the current suffix-only synthetic prototype would refuse this ROM because FNT/FAT and other known referenced regions occur after the first FAT payload. The function was not invoked on the clean ROM. A future image-specific plan must relocate/update those offsets and classify any embedded references first.
- `ohanashi_event_data.bin` (FAT ID 281, 1,784,728 bytes) begins with count 102 and 102 in-bounds, nonmonotonic 32-bit values; its payload did not yield coherent text in a naive ASCII/UTF-16 scan. ARM9 overlay descriptors map 108 unnamed FAT files, 107 marked compressed; compressed payloads now decode to descriptor RAM sizes, but code/data meaning remains unclassified. No standard font/graphics signatures were found in a limited raw-file signature scan, which does not establish font absence.
- No actual ROM rebuild, candidate, patch, or emulator test was performed. G1 remains PENDING.

## Read-only compressed-overlay decode check (2026-10-11)

- Decoded all 107 ARM9 overlays whose descriptors set the compressed flag, entirely in memory. The decoder follows the backward-LZ code-compression format documented by [ndspy](https://github.com/RoadrunnerWMC/ndspy/blob/master/ndspy/codeCompression.py); no third-party code or payload was copied into this repository.
- For all 107 entries, the little-endian footer's low 24-bit compressed length matches the overlay descriptor's compressed-size field, and decoded length equals the descriptor RAM size. The one uncompressed overlay was not transformed.
- ASCII literals expose data-file references from overlay IDs 84, 86, 87, 96, 106 and 107, including title/menu/mode-select assets and `data/ohanashi_event_data.bin`. These findings identify filenames only; no function-level code reference or scene assignment is confirmed.
- A separate event-container check found a 102-entry prefix followed by 102 unique, aligned, in-bounds values (range `0x330`–`0x12B38C`). Treating them as indexed offsets is still a hypothesis; event record boundaries and grammar are unknown.
- ROM SHA-256 before and after remained `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`. No file, ROM, candidate, patch, or emulator output was created. This read-only inspection does not change G1–G5: G0 PASS; G1–G5 PENDING.

## Read-only menu/event container probe (2026-10-11)

- Known MPDS-LZ decoding succeeded for title (133,280→122,308 bytes), main menu (19,555→20,052), mode select (10,446→11,424) and story mode (42,691→43,868). Overlay literals cross-reference title/menu/mode-select/story-mode filenames from IDs 84/86/87/98.
- Their leading words (34/23/21/77 respectively) are followed by integer arrays, but the values do not establish a simple file-relative offset table: some lie inside the presumed count/table prefix. These files stay classified as decoded containers with unknown internal record semantics.
- Treating each of the 102 event-table values as a candidate MPDS-LZ start, bounded by the next sorted value, yielded 99 format errors and three zero-size outputs; there were no positive-size decodes. Since these values may not be chunk starts and the event format may use a different codec, this is only a negative probe, not evidence that the container is uncompressed.
- The ROM stayed read-only and its SHA-256 remained unchanged. No build or emulator evidence was produced; G0 PASS and G1–G5 PENDING.
