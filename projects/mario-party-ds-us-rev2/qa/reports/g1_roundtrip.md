# G1 — Read-only MPDS table round-trip probe

Status: **PENDING** for binary/patch integrity.

- Scope: all 35 `data/US/mpd_*_LZ.bin` entries (2,672 rows).
- Read method: decode the MPDS LZ77 stream, parse the count/offset table and UTF-16LE null-terminated strings, then serialize the same strings to the same table format.
- Result: 35/35 expanded byte streams matched byte-for-byte after parse/serialize. Compressed input files and source ROM were not modified.
- Limits: this does not repack a NitroFS file, update FAT, produce a BPS, or run a patched build. No patch or candidate ROM exists. G1 therefore remains PENDING.
- The unknown leading compression byte, control-token grammar, `ohanashi_event_data.bin` and other binary containers remain outside this probe.
