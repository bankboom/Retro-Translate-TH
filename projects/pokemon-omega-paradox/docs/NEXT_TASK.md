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
