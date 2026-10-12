# MPD table translation coverage evidence

Date: 2026-10-12  
Project: Mario Party DS (USA Rev 2)  
ROM identity: SHA-256 `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433`

## Scope and result

The adapter extracted 2,672 rows from the 35 validated `data/US/mpd_*_LZ.bin` UTF-16LE tables. `translations/master.csv` now contains all 2,672 unique source IDs with a nonempty Thai draft.

| Check | Result |
| --- | ---: |
| Validated MPD source rows | 2,672 |
| Master rows | 2,672 |
| Unique IDs | 2,672 |
| Missing / extra / duplicate IDs | 0 / 0 / 0 |
| Source English mismatches | 0 |
| Empty Thai fields | 0 |
| Control-token sequence mismatches | 0 |
| Source line-break-count mismatches | 0 |
| Status | 2,672 DRAFT / NOT_INJECTED |

## Limits

This verifies row coverage, source alignment, token order and line-break counts only. It does not verify Thai meaning, grammar, terminology, scene context, pixel width, font glyphs, rendering, gameplay, save/load or patch correctness. G2–G5 remain PENDING as applicable. The event archive, ARM9/overlay strings and other non-MPD containers remain unmapped, so 100% refers only to the validated MPD-table inventory.

The source ROM was read-only and remains outside the repository. No candidate ROM or patch was produced.
