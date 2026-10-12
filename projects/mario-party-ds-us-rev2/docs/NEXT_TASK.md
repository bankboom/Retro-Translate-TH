# Next Codex task — Mario Party DS USA Rev 2

## Checkpoint — 2026-10-12

- `translations/master.csv` now covers all **2,672 / 2,672** unique rows in the 35 validated `data/US/mpd_*_LZ.bin` tables (100% draft coverage of this supported table inventory).
- Every row remains `DRAFT / NOT_INJECTED`. Source IDs and English strings match the read-only ROM extraction; token sequences and source line-break counts match, and no translated field is empty. See [translation coverage evidence](../qa/reports/translation_coverage.md).
- The 100% figure applies only to the 35 validated MPD tables. `ohanashi_event_data.bin`, ARM9/overlay strings, font/rendering and other containers are still unmapped; this is not full-game completion or release readiness.
- The source ROM remains outside Git and unchanged (SHA-256: `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`). No candidate ROM or patch has been built.

## Next work

1. Review translations in small contextual batches against actual scenes, speakers, glossary and mechanics. Keep uncertain rows flagged and all rows DRAFT until semantic review is recorded.
2. Measure actual text widths and validate Thai glyph coverage, baseline, combining marks and wrapping with real emulator screenshots. Keep G3 pending until evidence exists.
3. Continue read-only investigation of the event archive and non-MPD text containers; do not infer record grammar or code references from candidates alone.
4. Validate a game-specific rebuild path and rollback on disposable fixtures before attempting any candidate. The current suffix-only repacker is incompatible with the observed layout and has not been run on the clean ROM.
5. Keep G0–G5 statuses evidence-based. File, CSV and static-lint checks do not pass contextual QA, emulator rendering, gameplay/save testing or human release sign-off.
