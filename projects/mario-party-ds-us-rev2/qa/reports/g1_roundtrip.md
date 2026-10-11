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
