# G1 — Read-only MPDS table round-trip probe

Status: **PENDING** for binary/patch integrity.

- Scope: all 35 `data/US/mpd_*_LZ.bin` entries (2,672 rows).
- Overlay metadata: all 108 ARM9 overlay descriptors map one-to-one to unnamed FAT file IDs 0–107; this confirms descriptor mapping only, not overlay contents or text.
- Read method: the project-local `mpds_adapter` verifies the exact profile identity, scans NitroFS/FAT bounds, decodes the MPDS LZ77 stream, parses the count/offset table and UTF-16LE strings, then serializes and compresses them.
- Result: 35/35 expanded byte streams matched byte-for-byte after parse/serialize, and 35/35 recompressed containers decode to the same expanded bytes. The compressor's output bytes differ from the original container for all 35 files; this is expected for the current deterministic encoder and is recorded in `mpds_adapter_validation.json`.
- Safety: the ROM is opened read-only; before/after SHA-256 remains `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`. Source inventory output was created only in temporary storage and is not in the repository.
- Limits: the adapter does not repack the NitroFS image, relocate files, update FAT/FNT, produce a BPS, or run a candidate build. No patch or candidate ROM exists. G1 therefore remains PENDING.
- The unknown leading compression byte, control-token grammar, `ohanashi_event_data.bin`, overlay contents and other binary containers remain outside this probe.
