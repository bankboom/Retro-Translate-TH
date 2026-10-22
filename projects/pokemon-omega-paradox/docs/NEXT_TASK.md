# Omega Paradox — Next executable translation task

## Existing assets
Reuse existing Library CSV: P3_5_All_56700_Text_Status.csv, P3_5_Reuse_Memory.csv, P3_5_Translation_Backlog_Deduplicated.csv, P3_5_Omega_Original_Custom_Queue.csv and P3_5_Previous_Thai_Drafts_23.csv. Do diff-based work; do not rescan unrelated banks without a changed checksum.
Base tested partial patch: P3.7B; fallback P3.6B/P3.3A. Patch source is always original Omega ROM, not already patched ROM.
## Execute
1. Verify all 3 ROM SHA and existing P3.7B BPS source/target CRC before modification.
2. Pair master by source text+control-code signature+scene, not by index alone. Keep a per-ID QA table.
3. Reuse native White TH strings where original/source/context all match. Preserve Omega custom text.
4. Start with System 44 message 24: translate BOTH lines of Cynthia accurately. Existing output mixes English and Thai, and Thai meaning is incomplete. Keep PUA glyph sequences only if derived from proven dialogue bank.
5. Expand to System 44 messages 8,9,26 in 1–5-message reversible smoke builds, then Omega story changes, then missing system/items/moves.
6. Validate raw/decoded message round-trip, control codes, codeunit length, pixel width, FAT/pointers, BPS CRC/SHA, game dialogue, battle/save-load.
7. Keep separate per-row stages DRAFT/REVIEWED/ENCODED/BINARY_VERIFIED/EMULATOR_VERIFIED. Only claim 100% when reviewed text and full gameplay evidence meet G0–G5.
## Known blocker
Conversation sandbox binary execution currently fails, so no new P3.8 BPS has been built or verified in this turn. This is preparatory project state only.

## Update 2026-10-22 — P3.9 custom translation batch
- Completed 31 distinct Omega-custom *draft* translations; every entry matches the original ordered hexadecimal control-code unit signature (31/31).
- 11 messages need manual line-length/pixel-width review; all 31 need context QA, native Thai E8xx dialogue-bank encoding, binary verification, and emulator testing.
- Source-to-draft table: `translation/P3_9_OMEGA_CUSTOM_CONTEXT_DRAFTS.csv`.
- Gate results and caveats: `docs/P3_9_CONTEXT_BATCH_QA.md`.
- Do **not** claim the 31 entries are already in the ROM. No P3.9 BPS has been made.
- Safest next real binary task: isolated one-message smoke patch from previously tested P3.7B containing only System 44/8 (after deriving exact E8xx encoding from proven dialogue strings), then verify on emulator. Do not add 44/9 until 44/8 is demonstrated.

## P4.0 continuation checkpoint (2026-10-22)
- Implemented conservative reuse-audit code at `tools/p40_reuse_audit.py`, synthetic tests at `tools/test_p40_reuse_audit.py`, and runbook at `docs/P4_0_REUSE_BUILD_RUNBOOK_TH.md`.
- This tool matches Omega original vs White original at exact archive/file/message ID, rejects Omega-custom content, checks **whole-control sequence including parameters**, and prevents mistaking PUA glyphs for controls. It holds ambiguous source-to-Thai mappings and any inventory/master conflicts.
- **Not executed on all 56,700 rows in this environment** due binary runtime errors; candidate counts are unknown. Test workflow has been added but no successful CI result has been observed.
- **P4.0 BPS NOT BUILT**, no new emulator evidence, no gate progression claimed.
- To resume: run synthetic tests and audit against full local CSV, review eligible rows, integrate approved rows into verified game-specific NARC/MSG packer, build BPS against original Omega SHA-256, compare against P3.7B, then obtain emulator test evidence before promoting P4.0.
- Keep P3.7B fallback immutable. Do not copy all White TH messages merely by aligned indexes.
