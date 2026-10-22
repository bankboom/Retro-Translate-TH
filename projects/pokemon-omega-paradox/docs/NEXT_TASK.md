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

## Update 2026-10-22 — Cross-ID reuse and CI evidence
- Added `tools/p40_cross_id_review.py` to recover EXACT SOURCE + EXACT CONTROL SIGNATURE matches from White TH even where source and destination message IDs differ. It holds conflicting Thai choices, Omega-custom entries, and P3.5-only "already translated" snapshot claims; it does NOT inject messages.
- Added `tools/test_p40_cross_id_review.py`, included in `.github/workflows/omega-p40-static-tests.yml`.
- Evidence: GitHub Actions run 39732260462 on commit `0aef429939f21202a73439739e5de4a870c2344d`: syntax compilation PASS, synthetic test suite PASS **16/16**.
- **Unfinished:** full 56,700-row audit on actual CSVs, source+target CRC/hashes on original Omega/P3.7B patch, glyph-bank-specific Encoder E8xx, real P4.0 BPS, emulator tests. Do not infer a reviewed percentage from static matches.
- Next: execute both read-only audit tools on complete local CSV inputs; review exact and cross-ID queues with context; introduce verified native encoder and 1–5-message smoke patch; retain P3.7B fallback.

## Full real-data audit COMPLETE — 2026-10-22 (supersedes earlier runtime blocker)
- **Read/processed all 56,700 inventory rows**, unique keys 56,700, against the **25,976-row** original Pokémon White TH translation-memory file. Both source CSV SHA-256 digests are recorded in `docs/P4_0_REAL_56700_AUDIT_RESULTS_20261022.md`.
- Result: 25,001 P3.5 snapshot entries with Thai PUA; 20,096 entries requiring review; 11,603 classified nonlinguistic; Omega-custom 1,727 overlaps these groups.
- Exact English text matched same-ID TM for 24,558 entries; **zero new automatic Same-ID / Cross-ID injection candidates** after excluding already-imported P3.5 Thai, Omega-custom and conflict candidates. White TH memory cannot be indiscriminately recopied.
- Targeted QA risks: 9 P3.5 native Thai hard control signature differences; 11 White TH memory hard control differences; 62 ambiguous source-to-Thai master mappings (not all overlap the 9). Report flags require human/context assessment, not automatic regression conclusions.
- Full per-row audit and sorted P1/P2/P3 20,096-item queue are delivered in the associated conversation ZIP, SHA-256 `224447667aa0fe06b1d46e1668f75fc53b81065b593bb0e7c2ae433c178f01bb`. Do NOT put copyrighted raw game text or ROM files into this public repo.
- **Do not confuse data audit COMPLETE with P4.0 ROM build COMPLETE**. No P4.0 BPS built; G2 contextual approval and G3/G4 emulator evidence are still pending. P3.7B original source and BPS CRC checks passed.
- Next: inspect 9 hard control flags, then validate P1 Omega 1,619 / P2 Story 970 / P3 System 17,507 pending queue records; derive bank-specific native E8xx encoding and produce safe pilot BPS preserving P3.7B fallback.

## P4.2 translation and control-parser checkpoint (2026-10-22)
- P4.2 added 19 source-aligned Omega story `DRAFT_NEEDS_CONTEXT` messages; P4.2B added 8 more with complex F000 variable/speaker operands, total **27 new / 67 P4.1–P4.2 distinct IDs**.
- Fixed escaped-text control lexer: `tools/omega_control_tokens.py` treats `F000 opcode + all literal hex operands` as one operation even when final operand is nonzero; never swallow adjacent F000/FFFE/FFFF.
- CI evidence: [run 39775878424](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39775878424) **SUCCESS 28/28 static and synthetic tests**; user game ROM/emulator was NOT exercised.
- New translation CSVs: `translation/P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv` (19) and `translation/P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv` (8).
- Report: `docs/P4_2_20261022_TRANSLATION_AND_TOKEN_QA_TH.md`.
- Remaining critical blocking dependency: verified native E8xx encoding for **new** Unicode Thai text and tested NARC/MSG+BPS builder. The P3.7B fallback is untouched.
- No new BPS; no claim that 100% of the game is translated or reviewed. Use the full 56,700-row P4.0 audit inventory without rescanning.

## P4.3 Native E8xx gate checkpoint (2026-10-22)
- Added `tools/p43_native_e8_encoder.py` and `tools/test_p43_native_e8_encoder.py`, plus `tools/p43_preflight_existing_drafts.py` and an empty per-renderer `glyph_maps/P4_3_NATIVE_E8_PENDING.csv` awaiting real evidence.
- GitHub Actions [39781176864](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39781176864): **38/38 static/synthetic Python tests PASS**, plus `67/67` distinct P4.1/P4.2 draft preflight **67 CONTEXT_NOT_REVIEWED / 0 encoding-ready**, map has zero verified fragments. CI artifact `omega-p43-glyph-preflight`.
- Report: `docs/P4_3_20261022_E8XX_GATE_AND_BUILD_BLOCKERS_TH.md`.
- **No new ROM and no BPS.** Verified decoder/encoder *logical text* unit tests are not game-ROM bytecode validation or gameplay approval.
- Must avoid circular proof trap: extract a source-traceable native bank-specific mapping from White TH/P3.7B, label reference material `SMOKE_ONLY` until actual melonDS validation; only then promote to `IN_GAME_VERIFIED`. Never guess glyph codepoints.
- Next practical binary milestone remains: preserve P3.7B fallback; one-message Cynthia system 44/24 pilot; source SHA and BPS CRC/repack/revert checks; user emulator screenshot + next-page progression.

## P4.4 fixed-slot E8 smoke pilot — verified CI checkpoint (22 Oct 2026)
- Fixed a **real parser defect**: previous `F000 + opcode + arbitrary \\xNNNN operand` expression wrongly consumed adjacent native `\\xE8NN` glyph escapes as F000 operands. Shared lexer now stops before E000–EFFF PUA escapes, failing closed on possible unconventional operands.
- Added `tools/p44_fixed_slot_pilot.py` and 12 synthetic tests to enforce per-visible-segment fixed codeunit capacity, exact control token/payload preservation, source-to-reference provenance fields and no Unicode fallback. The output is an **escaped logical message only**.
- GitHub Actions [39786876015](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39786876015) verified **50/50 synthetic/static Python tests PASS** (including all older suites); this tests code logic, not actual ROM bytes.
- `docs/P4_4_NATIVE_E8_FIXED_SLOT_SMOKE_TH.md` and blank `glyph_maps/P4_4_NATIVE_REFERENCE_EXTRACTED_TEMPLATE.csv` document precisely which real White TH/P3.7B native fragments are needed. No fragment or glyph codepoints were fabricated.
- **User goal is not yet complete**: no new P4.4 BPS, no successful binary serialization/ROM diff/emulator QA, and still 20,096 items requiring review/classification from full real-data audit. Continue on original Omega source SHA256; P3.7B is immutable fallback.
- **Do not create further cosmetic draft versions until a genuine native reference extraction + one-message BPS is produced**. Next focused task is System 44 message 24 Cynthia. Require actual P3.7B/White TH bytes and source-exact extraction; if runtime unavailable report blocker instead of calling it done.

## P4.5 — NFTR Glyph ROM Extraction Complete
- REAL-ROM NFTR extraction is **complete** for the three White TH font resources from NitroFS `/a/0/2/3`, members 0–2, byte-identical to the fonts inside the rebuilt P3.7B target.
- All 1,309 mapped PUA codes × 3 fonts = 3,927 actual nonblank bitmap lookup pairs, including E800–E8FF 256/256 per font.
- Parsed actual White TH and P3.7B message archives: 56,700 each; missing PUA glyph lookup = **0** in all font maps.
- Source hashes, bitmap atlases, raw NFTR and parser provided in user-owned ZIP `Pokemon_Omega_Paradox_WhiteTH_ROM_Verified_1309_Glyph_Master_3Fonts_20261022.zip`, not committed as ROM assets to public GitHub.
- Proof and limitations: `docs/P4_5_ROM_VERIFIED_GLYPH_MASTER_TH.md`.
- IMPORTANT: Glyph Bitmap/CMAP complete != verified Unicode Thai cluster-to-PUA encoder or proportional layout metrics. The peculiar CWDH metadata remains unresolved. Do not re-extract/create glyphs without changed source fingerprint.
- **Next blocking goal:** verify Thai semantic reverse mapping/cluster encoder and renderer pixel widths from proven Thai text, then produce a one-message Cynthia system/44/24 BPS smoke patch using the original Omega clean ROM. Retain P3.7B as fallback; no full-game G2–G5 claims.

## P4.6 — REAL BPS PILOT BUILT (2026-10-22)
- First real BPS after P3.7B **BUILT and independently byte-verified**: `Pokemon_Omega_Paradox_TH_P4_6_Cynthia_Full_Thai_Pilot_from_Clean_Omega.bps`, SHA-256 `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`.
- Original clean Omega source unchanged. BPS checks source and target CRC, SHA256, and only 64 ciphertext bytes of `system/44/24` differ from P3.7B. Resulting target SHA `945c0bc11b137580311af9c38b6f62852a6cf688e16a89854e7d64ed00427a04`.
- Native Thai 29-codeunit first narration clause sourced from original White TH `system/44/24` with matching English phrase and command sequence. Second 20-codeunit native clause retained. 31 unique native PUA glyphs verified nonblank in three byte-identical ROM NFTR fonts. Keeps message 83 units long by using 6 trailing spaces after custom Cynthia name. Two *positions* of F000/FFFE shift, requiring user emulator verification.
- Report and limitations: `docs/P4_6_CYNTHIA_NATIVE_THAI_BPS_BUILD_QA_TH.md`. Standalone BPS and ZIP given directly to project owner in the ChatGPT chat, no ROM committed.
- G0 + G1 for this limited patch pass; **G2 contextual character review pending**, G3 rendered-layout pending, G4 emulator pending, G5 full localization pending. This build is **not** 100% translation.
- **Next task**: obtain screenshot from melonDS Android of Cynthia both clauses, transition to next page, and Save/Load. If PASS keep P4.6 as baseline and derive a bank-specific Unicode Thai cluster encoder from proven ROM glyph/text pairs (do not guess). Continue remaining Omega-specific translated DRAFT/NEEDS_CONTEXT queue and validate each injected scene.

## P4.6 emulator feedback — Save/Load verified by user (2026-10-22)
- The user tested the current P4.6 candidate and reported **Save normal; Load normal**.
- Log as `USER_REPORTED_SAVE_PASS` and `USER_REPORTED_LOAD_PASS` for P4.6 only. Do **not** label full G4 PASS or claim the visual QA of Cynthia's first/second clauses, whose screenshot and contextual review remain pending.
- No new BPS was generated from this feedback. Preserve P4.6 plus P3.7B as rollback references.
- Next: verify both Cynthia pages and text advance (no ????/clipping, correct role/context), then expand a targeted native-encoded smoke set using proven glyph/phrase mapping. Avoid redoing proven NFTR extraction or synthetic test loops.

## P4.6 user-confirmed visual + gameplay smoke PASS (2026-10-22)
- User reports: **both Cynthia clauses display in correct readable Thai**, with no `????`, and the dialogue advances normally. Preceding test report confirms **Save / Load normal**.
- Log this as `P4_6_CYNTHIA_TWO_CLAUSES_VISUAL_PASS`, `P4_6_DIALOG_ADVANCE_PASS`, `P4_6_SAVE_LOAD_PASS`, all **user-reported** for the specific P4.6 build. See `docs/P4_6_CYNTHIA_NATIVE_THAI_BPS_BUILD_QA_TH.md`.
- P4.6 becomes a **scoped emulator-tested stable baseline** for these routes, with P3.7B retained as fallback. G3 = PASS within the two Cynthia clauses; G4 = PARTIAL/SMOKE PASS within Cynthia progression and Save/Load, NOT full-game PASS.
- Context/character-semantic G2 remains PENDING since a native clause was originally translated for Bianca. No screenshot artifact was attached to this particular report.
- **Stop repeated Cynthia smoke experiments unless bytes/fonts/renderer/control codes change.** Focus next on unverified game messages and bank-specific Unicode Thai grapheme-to-PUA mapping, review actual context, then build conservative BPS increments with regression comparisons to P4.6.

## P4.7 — 98 DRAFTS UNIFIED, CI PASS, GAME STILL INCOMPLETE (2026-10-22)
- Implemented `tools/p47_full_scope_merge.py` with fail-closed real CSV + 98 full-message draft merge; refuses truncated 56,700-row inventory, duplicate IDs, source mismatch, control sequence mismatch and ambiguous variants.
- Full-message drafts are **98 distinct IDs**: P3.9 = 31; P4.1 = 40; P4.2 = 19; P4.2B = 8. P3.8 has partial message fragments, so must NOT inject directly. **All drafts remain context QA pending**. Do not count as translated/injected or as a 100% completion claim.
- GitHub Actions `39818271371` **PASS 59/59 unit/static tests**, including new scope tests; not a real ROM build. CI proof: https://github.com/bankboom/Retro-Translate-TH/actions/runs/39818271371
- Detailed report and CLI: `docs/P4_7_FULL_SCOPE_EXPANSION_CHECKPOINT_TH.md`.
- **No P4.7 BPS generated**. This working session's native ROM execution environment raised ClientError; actual P4.6 build remains the newest binary and user-scoped emulator-tested checkpoint.
- On restored local ROM execution: (1) run P4.7 tool on the owner's existing 56,700-row CSV and reconcile draft source IDs, (2) derive or load verified bank-specific Unicode->native Thai units and renderer widths, (3) use the actual P4.6 ZIP scripts as baseline to build a small BPS of newly reviewed scenes and compare binary diff, (4) expand genuinely reviewed translations through all remaining backlog, with changes-only emulator regression and final G0–G5 QA.
- Never re-extract already verified 1,309 glyphs or re-run unchanged Cynthia smoke tests. Preserve immutable original Omega and P4.6 binary SHA fingerprints.
