# MPDS Adapter (read-only baseline)

This game-specific Python adapter reads Mario Party DS (USA Rev 2) without
writing to the source ROM. Every ROM-consuming command checks the exact
project identity from `project_profile.json` first. File outputs are created
with exclusive mode and fail if the target already exists.

Run from the repository root with the project tools directory on `PYTHONPATH`:

```sh
export PYTHONPATH=projects/mario-party-ds-us-rev2/tools
python -m mpds_adapter --help
python -m mpds_adapter inspect-rom /path/to/clean.nds
python -m mpds_adapter inventory /path/to/clean.nds --output /tmp/mpds-inventory.json
python -m mpds_adapter roundtrip /path/to/clean.nds --report /tmp/mpds-roundtrip.json
python -m mpds_adapter extract-tables /path/to/clean.nds --output /tmp/mpds-source-inventory.csv
```

`extract-tables` writes a source-only inventory with no translation or
injection status. Review it before moving selected IDs into `translations/master.csv`.
Do not commit full ROMs, extracted game payloads, fonts, or candidate ROMs.

Confirmed scope: NitroFS metadata, ARM9/ARM7 overlay descriptor-to-FAT
mapping, plus the 35 `data/US/mpd_*_LZ.bin` tables (2,672 rows). A separate
in-memory `replace_nitro_file` prototype is covered by synthetic two-file NDS
fixtures, including size growth, alignment, FAT relocation, header size/checksum,
and synthetic forward/reverse BPS application. It returns new bytes and has no
path-writing interface. It rejects known metadata that overlaps or follows the
first FAT payload. This is not yet validated against the full game image; do
not run it on the project ROM or treat it as an injection tool. `roundtrip`
checks expanded bytes and decode-after-recompress;
the recompressed container is not expected to be byte-identical. This does not
prove candidate ROM repacking, a production patch, font support, emulator
rendering, or game behavior. Overlay contents, story-event data, ARM9/overlay
strings, font mapping, and `[1]` token semantics remain unmapped. Gates G1–G5
remain pending until their separate evidence is reviewed.
