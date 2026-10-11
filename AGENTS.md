# Codex rules — Retro Game Translation Framework V3.2

Scope: This is a reusable framework; one game per `projects/<slug>/`. Reply in Thai. Read this file + active project's `AGENTS.md`, `project_profile.json`, `docs/NEXT_TASK.md`. **Do not preload other docs or unrelated projects**; open only task-relevant skills/docs.

## Non-negotiable priorities
1. Meaning: faithful to source, story, character, era/tone, gameplay, numerical data, terminology; natural, correctly spelled Thai. Never invent details or change mechanics. Respect context ambiguity and flag it.
2. Typography: all Thai consonants, vowels, tone marks and diacritics must display legibly with proper baseline/advance/stacking/spacing, within UI. Verify with real emulator screenshots (including `ต้ ตุ สำ น้ำ ภาษา`).
3. Safety: immutable clean ROM and known-good patches; verify hash/revision, preserve control bytes/tokens, pointer bounds and rollback. No unauthorised ROM/BIOS distribution.
4. Tokens: avoid repeated full scans and repeated full prompts; exact approved glossary/TM first; prepare small incremental context packets; output **changed rows/diffs only**; work by batches, preserve checkpoints. Never sacrifice semantics or QA to reduce tokens.

## Execution
- G0 identity → G1 binary/round-trip → G2 context & translation QA → G3 Thai visual QA → G4 gameplay/save QA → G5 release. Only PASS/FAIL/PENDING/NOT_APPLICABLE, with evidence; never claim 100% from a CSV.
- No fabricated files, hashes, translations, emulator evidence, or percent. If missing ROM/adapter, report exact blocker.
- Translate only grounded extracted IDs. Preserve format strings, placeholders, control codes, punctuation required by game, and UI length constraints. Separate DRAFT / REVIEWED / INJECTED / VERIFIED.
- Test 1–5 string reversible micro-patch before scaling. Change only the affected file/bank/glyph. Compare with stable baseline and keep candidate versioned.
- Use relevant skill only: `.agents/skills/rom-analysis/SKILL.md`, `thai-localization/SKILL.md`, `patch-qa/SKILL.md`, `token-efficient-workflow/SKILL.md`.
- Detailed specifications on demand: `docs/THAI_QUALITY_STANDARD.md`, `docs/TOKEN_EFFICIENCY_POLICY.md`, `docs/QUALITY_GATES.md`.
- When editing shared Python tools, run `python -m unittest discover -s tests -p "test_*.py" -v`.

## Minimal response at each turn
`Changed: <files/IDs> | Tests: <facts> | Gates: <changed states only> | Blocker: <if any> | Next: <one step>`. Give full logs only upon request. Never dump entire ROM, CSV, or code if a delta suffices.

## Cross-project approved TM (V3.1 add-on)
- For new games and sequels, inspect `docs/CROSS_PROJECT_TRANSLATION_MEMORY_TH.md` only if related prior translations exist.
- Offline index reviewed strings with `tools/cross_project_tm.py index`; `suggest`/`terms` produce **read-only candidate lists**, never auto-apply or assert approved target QA.
- Cross-platform reuse is limited to meaning/glossary, not pointer, ROM patch, font binary, layout or emulator results.
- `series_id` may connect sequels when verified. Publisher alone is insufficient. Any context mismatch, fuzzy source or conflicting approved target must be escalated.
- Never spend AI tokens retranslating approved context-equivalent strings until shortlist review; summarize delta only.


## V3.2 mandatory regression and review process
- Before every candidate patch, establish the exact known-good base, compare baseline/candidate using `tools/regression_guard.py` with reviewed `allowed_changes` ranges, and STOP on out-of-scope or protected-range modifications. `scope_status=PASS` is **binary change-scope only**, not G3/G4 PASS. PENDING means blocked for promotion.
- Feed `tools/quality_queue.py` only new/changed translation rows to AI; use the smallest batches. Translation AI review must compare in-game context and grammar; static lint is not semantic approval.
- Generate `tools/font_review_plan.py` suggestions from real strings, then collect matched emulator screenshot evidence per build, scene, and font size. Image-generation/rendered previews are not emulator evidence. Mark untested G3 PENDING.
- Run `tools/release_audit.py` before publishing. G5 remains PENDING until a human explicitly signs off and evidence is genuine. Never promote statuses automatically.
- Continue using cross-project approved TM and project checkpoints from V3.1.1; do not duplicate user project data or migrate ROM binaries into the framework.
- New V3.2 docs and skills: `docs/V3_2_REGRESSION_AND_RELEASE_TH.md`, `.agents/skills/regression-quality/SKILL.md`, `.agents/skills/evidence-release/SKILL.md`. Load on demand only.
- Chat triggers `คู่มือ V3.2`, `Framework V3.2`, or older `V3.1` (compatibility). Maintain the existing managed user skill/paths where installed to avoid breaking previous Codex setup.
