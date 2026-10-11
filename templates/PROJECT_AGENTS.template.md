# Game-specific Codex instructions

Read root `AGENTS.md`, this game's `project_profile.json`, `docs/NEXT_TASK.md` only; load task skill on demand. Do not read unrelated game folders. No extractor/injector/font support is assumed until proven.
- Preserve original game story, meaning, characters, UI functions, controls, terminology and all placeholder/control tokens; Thai spelling and grammar must pass context review.
- Thai letters, vowels, tone marks, `ำ`, baselines/advance/wrapping must pass **real emulator screenshot review**; never claim visual pass without evidence.
- Use `translations/glossary.csv` and only reviewed, context-matching translation memory; translate missing/changed IDs in small context packets; respond with deltas only.
- Never modify clean ROM or stable patch. Change candidate only, keep build IDs/hashes and rollback. Work in this game folder unless adding tested shared code.
- Keep `translations/master.csv` compatible with framework tools; record G0–G5 evidence and `docs/NEXT_TASK.md` at checkpoints.
