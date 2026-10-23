# Pokémon Omega Paradox TH — P5.0–P5.1 Translation and Context Review Report
**Date:** 23 October 2026
**Scope:** Real source-aligned project translation drafts, not a full-game release.
**Status:** **65 new complete-message Thai drafts created this turn**; **214 unique complete-message drafts cumulative**. No new BPS or full-game emulator certification.

## Provenance and reuse policy
- The source text for the 65 newly translated IDs was read from the project owner's actual `P3_5_Omega_Original_Custom_Queue.csv` (the existing indexed file content, not imagined dialogue or new story writing).
- Prior `Pokemon_White_Thai.nds` provided 25,976 translation-memory entries and 1,309 PUA glyph codes for three fonts; the P3.5 snapshot already included 25,001 Thai-coded entries. **Do not re-import White TH into already-translated IDs.**
- P3.9–P4.9 previously held **149** unique complete-message Thai drafts. New P5.0 = **47** and P5.1 = **18**, total = **214** distinct message IDs. Previous 149 retained unchanged, except no P4.6 ROM modification.
- P5.0 files: `translation/P5_0_CASTELIA_NIMBASA_CONTEXT_DRAFTS.csv`
- P5.1 files: `translation/P5_1_LEGENDS_AND_MASKED_MAN_DRAFTS.csv`
- Per-ID QA matrix: `translation/P5_1_CONTEXT_QA_214_MESSAGE_MATRIX.csv` (every ID named with source draft filename and remaining stage gates).

## Context decisions grounded in the actual Omega story
1. **Truth ≠ Ideals**: `story/61/6` preserves Truth/ความจริง, while `story/61/7` preserves Ideals/อุดมคติ. Two variants exist for a narrative reason, never dedupe by English similarity.
2. **Cynthia/Gible rescue**: `story/43/2` shows Cynthia's Gible was stolen, and `story/61/16–23` shows her reunion, subsequent thanks, and Diantha's objection. Local Thai wording revised so Cynthia clearly speaks to Gible (not vice versa).
3. **Cynthia Champion role**: `story/43/18` calls her Champion; `story/56/4` suggests insecurity about her strength; `story/67/27` explicitly says her father believes she lost the title after Sinnoh. This may form part of Omega's altered character arc, but **chronology must be checked**. Do not rewrite dialogue to fit other Pokémon games.
4. **Father pronoun**: `story/67/34` includes ambiguous English 'he got demoted during the Masked Man attack'; kept source meaning provisionally and flagged unclear referent.
5. **Masked Man arc**: `story/69/0–8` contains special `F000븉` controls and references to a professor's death, Ferris wheel, Team Aqua and challenge to the Champion. Preserve tokens exactly. Verify speaker turns and source-specific lore.
6. **Meta lines** such as `story/67/25` mentioning Pokémon BW2 and `system/38/62` promoting Blaze Black 2 are in original Omega; retain their game-title identity rather than normalizing away.
7. **Terminology baseline**: keep `โปเกมอน`, `เทรนเนอร์`, `ยิม`, `ทีมอควา`, `เจ็ดปราชญ์` and named characters consistent; do not confuse glossary alignment with verified native glyph encoding.

## QA results on 214 full-message drafts
- **214/214** preserve ordered literal `F000` operations and operands, `FFFE` and `FFFF` according to the actual exported source text.
- **203** have max visible Unicode segment <=35 codepoints.
- **11** early P3.9 `system/38` entries exceed that threshold: IDs `3–11`, `53`, `63`. None should be silently marked pixel-safe or shortened by dropping meaning; require renderer width/space inspection.
- The 65 new P5.0/P5.1 full-message drafts passed source-aligned static token and 35-codepoint checks before commit.
- All 214 remain unapproved for native Unicode Thai → PUA encoding, binary injection, and game-screen QA. Source-draft structural correctness **does not constitute 100% translation completeness**.

## Remaining full-game scope
- Original full inventory: **56,700** entries.
- P3.5 native-Thai-coded snapshot: **25,001** entries (not necessarily all emulator verified).
- Backlog requiring translation/context/classification review in P4.0: **20,096** entries, not all of which are necessarily new spoken sentences. The **214 total draft IDs are not subtracted mechanically** from 20,096 until exact full-inventory deduplication is rerun on current data.
- Current user-tested safe BPS: **P4.6** only, Cynthia two Thai clauses, normal text progression and Save/Load; no later new ROM patch completed or verified in this work.
- **No full-game 100%** claim, **no G2–G5 global PASS**, and **no fabricated translated rows**.

## Critical path, without repeated experiments
1. Run current `tools/p47_full_scope_merge.py` against the complete 56,700-row owner's inventory to get 214 per-ID source-exactness and actual remaining review counts. Do not use the truncated File preview.
2. Review contextual holds and the 11 codepoint-width/pixel-width flags; revise only differences confirmed against the scene and text box.
3. Use the certified extracted three-font NFTR/PUA master for bank-aware encoder mapping; do not regenerate fonts. Source-fingerprint strict.
4. Build a conservative BPS for a small set of approved **newly translated** messages from the clean original Omega ROM; regression compare to P4.6. Request in-emulator evidence for only newly modified scenes and gameplay state, not repeat unchanged Cynthia smoke checks.
5. Continue deduplicated translation batches until every linguistic inventory entry is context-approved and in-game-verified; G5 comes only after complete end-to-end coverage.

**Important boundary:** This public GitHub report contains process/QA outcomes and per-ID references; full ROM/NFTR binary game assets are not committed.
