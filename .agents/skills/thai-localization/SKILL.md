---
name: retro-thai-localization
description: Thai translation accuracy, story fidelity, grammar, terminology, game-specific encoding, vowel/tone marks, glyph layout and on-screen font QA. Use after extraction mapping is confirmed.
---

# Thai Localization — meaning first, typography first
1. Read active game `AGENTS.md`, `project_profile.json`, applicable `translations/glossary.csv`, `control_codes.csv`, task IDs and `docs/THAI_QUALITY_STANDARD.md` when evaluating quality.
2. Every translation must preserve plot, character voice, game mechanics, numeric values, control codes, placeholders, order and important punctuation; make Thai natural, grammatically correct and consistent. Flag context ambiguity, don't guess.
3. Use approved glossary and exact reviewed translation memory before new AI translation. For batches use `tools/token_saver.py pack`; include only relevant context; output changed rows, not full files.
4. Track source mapping, context, draft/review/injection/visual status separately; never infer injected from CSV nonempty.
5. Inspect actual renderer: encoding/mapping, pixel glyphs, bearing, advance, line spacing, baseline, stacked diacritics, `ำ`, wrapping/clipping, 8/10/12/14 pixels only if used by this game. No assumed native Unicode.
6. Check `ต้ ตุ สำ น้ำ ภาษา ปัญหา ผู้ใหญ่ ม้า` plus game-specific strings with emulator screenshots and long text, different screens, sizes, contrast. Compare with known-good candidate on identical scene; keep G3 PENDING without real evidence.
7. Micro-patch 1–5 strings before full bank; preserve rollback and never overwrite stable baseline.

8. Use six-phase guidance `docs/SIX_PHASE_CONTEXT_QA_TH.md` when planning project milestones: contextual QA is continuous across Phase 1–6, including in-emulator recheck, not deferred to final release. To mark a row `REVIEWED`, evaluate meaning, scene/speaker, Thai grammar, terminology, continuity, and technical tokens/length; missing credible context => `NEEDS_CONTEXT`. Keep `DRAFT / NEEDS_CONTEXT / REVIEWED` independent from `INJECTED` and logged `IN_GAME_VERIFIED`; don't infer a 50/70/100% reviewed checkpoint from draft counts. The ASCII injection smoke candidate is a technical experiment, not Thai QA completion.

9. ThaiPUA-informed workflow (optional across ALL games): when native Thai shaping is absent, read `docs/THAI_PUA_CROSS_PLATFORM_TH.md`; run `tools/thai_composite_plan.py` on the active game's verified translation master for a **read-only demand plan**. Reuse approved glyphs, allocate only observed clusters; no automatic PUA/ROM glyph ID assignment, no blind font replacement or ARM9 hook, no passing G3 from a font preview. Every game keeps its own adapter, encoding, glyph bank and emulator evidence.

Return only changed IDs, translation rationale where ambiguous, glyph/diff observations, QA evidence, unresolved issues and next action.
