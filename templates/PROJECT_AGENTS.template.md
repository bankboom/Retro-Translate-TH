# Game-specific Codex instructions

Read root `AGENTS.md`, this game's `project_profile.json`, `docs/NEXT_TASK.md` only; load task skill on demand. Do not read unrelated game folders. No extractor/injector/font support is assumed until proven.
- Preserve original game story, meaning, characters, UI functions, controls, terminology and all placeholder/control tokens; Thai spelling and grammar must pass context review.
- Thai letters, vowels, tone marks, `ำ`, baselines/advance/wrapping must pass **real emulator screenshot review**; never claim visual pass without evidence.
- Use `translations/glossary.csv` and only reviewed, context-matching translation memory; translate missing/changed IDs in small context packets; respond with deltas only.
- Never modify clean ROM or stable patch. Change candidate only, keep build IDs/hashes and rollback. Work in this game folder unless adding tested shared code.
- Keep `translations/master.csv` compatible with framework tools; record G0–G5 evidence and `docs/NEXT_TASK.md` at checkpoints.

- Use the six-phase **Emulator-First + Context QA** workflow (`docs/SIX_PHASE_CONTEXT_QA_TH.md`): check meaning, game context, Thai style, glossary, continuity and UI/control constraints for every reviewed batch from Phase 1 onward. An ASCII injection smoke is a technical test, not Thai translation approval; `NEEDS_CONTEXT` remains open if game context is missing. Do not claim 50/70/100% approved progress from drafts.
