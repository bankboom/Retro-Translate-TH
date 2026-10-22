# Omega Paradox P4.0 — Full real-data audit (2026-10-22)

**Status:** ALL 56,700 INPUT ROWS PROCESSED and exported. **P4.0 BPS NOT BUILT.** This is a translation-database audit, not Context QA or gameplay sign-off.

## Verified input identity

- `P3_5_All_56700_Text_Status.csv` 22,914,268 bytes; SHA-256 `d5a680554e1130eb63b99f515b410937179acfb7f943c2420a4e7f4010f65e34`
- `P3_5_Reuse_Memory.csv` 11,227,366 bytes; SHA-256 `c352a547d9b44dfc881eafddb1e146e9f1fd4b5a2ec49678e99debcd4b688557`
- Original `Pokemon Omega Paradox.nds` 202,029,033 bytes; SHA-256 `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`
- Prior experimental P3.7B BPS source CRC `8a62e7cb` matches original Omega; BPS CRC `9eee279a` verified, target CRC listed `f0a06605`. This is CRC verification **only**, not gameplay verification.

## Complete dataset audit counts

| Category | Count |
|---|---:|
| Inventory source rows; unique archive/file/message keys | 56,700 / 56,700 |
| System / story text rows | 48,839 / 7,861 |
| White TH translation-memory keys (unique) | 25,976 |
| Same-ID English-source exact matches | 24,558 |
| Same-ID matches but English source different | 1,418 |
| P3.5 snapshot rows with native Thai PUA | 25,001 |
| Rows classified as needing translation/context review | 20,096 |
| Nonlinguistic numeric / empty / control | 11,603 |
| Omega-custom rows (overlaps other categories) | 1,727 |
| Omega-custom requiring review | 1,619 |
| Omega-custom with existing PUA snapshot | 85 |
| Omega-custom nonlinguistic | 23 |
| New *automatic* same-ID reuse candidates after holds | 0 |
| New *automatic* cross-ID reuse candidates after holds | 0 |
| P3.5 Thai rows with equal hard-control signature | 24,992 |
| P3.5 Thai rows requiring hard-control review | 9 |
| White TH TM rows requiring hard-control review | 11 |
| Distinct ambiguous master source-to-Thai mappings | 62 |
| Auditable exceptional-risk rows | 32 |

The 25,001 PUA / 20,096 review / 11,603 nonlinguistic status groups partition the 56,700 entries. The Omega-custom flag **overlaps** them.

**Critical interpretation:** The master-to-target matched records were mostly imported in the P3.5 snapshot. A result of zero *new automatic candidates* is not zero untranslated text, and not proof that all P3.5 imports have been screen-verified. The exact-original/context gate was intentionally strict to prevent substituting White's dialogue into Omega-specific scenes.

## Review queue ordering

- P1 Omega-custom needing review: **1,619**
- P2 Story needing review, excluding Omega-custom: **970**
- P3 System needing review, excluding Omega-custom: **17,507**

All 20,096 queue records are `NEEDS_CONTEXT`. They may include names and other text that should legitimately remain romanized. No row was automatically promoted to `REVIEWED` by this audit.

## Token and glyph QA

Hard control fingerprint uses `\\xF000` operation + parameter tokens and `\\xFFFF` terminators; it treats `\\xFFFE` as a soft line break, which localized Thai may legitimately reflow. The 9 existing-Thai and 11 master differences are targeted review flags, **not** automatic evidence that the game is broken. There are also 9 held cross-ID master conflicts and 2 held ambiguous cross-ID placements; some risk categories overlap.

## Deliverable artifacts

The complete audit, source/PUA snapshot, sorted 20,096 review queue, 32-row risk list, 62-row source-collision list, QA metadata, and Thai README were generated as separate CSV/JSON files in the current conversation output. The packaged ZIP SHA-256 is `224447667aa0fe06b1d46e1668f75fc53b81065b593bb0e7c2ae433c178f01bb` (ZIP consistency tested). No ROM has been uploaded to GitHub.

## G0–G5 / next work

- G0: original ROM identity/source CRC confirmed.
- G1: only P3.7B patch CRC tested here; **P4.0 BPS not created**.
- G2: per-row translation/context QA still pending; **no release-reviewed %**.
- G3/G4: only earlier scene screenshot evidence; not full game.
- G5: PENDING.

**Next action:** close 9 hard-control differences individually with evidence; process sorted P1 Omega translation queue in context-aware batches, then P2/P3, implement native bank-specific E8xx encoding, and build a reproducible P4.0 BPS on original Omega after verification. Keep P3.7B protected as fallback. Never reimport all 25,976 master entries blindly.
