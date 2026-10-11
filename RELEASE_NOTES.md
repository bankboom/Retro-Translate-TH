# V3.1.0 — Quality & Token Efficiency (9 Oct 2026)

- Extends generic V3.0 Codex framework; no game-specific ROM/patch included.
- Codex AGENTS.md reorganized for concise default context + on-demand skills.
- Translation meaning, Thai grammar, character/plot fidelity, font screenshot criteria strengthened.
- Added conservative offline `tools/thai_text_lint.py` with explicit false-positive / human QA caveat.
- Added offline `tools/token_saver.py` (bounded context packets, exact approved translation-memory *suggestions*; no network/API/token billing).
- Added policy, skill, ready-to-paste prompt, shared TM template and tests.
- Preserves V3.0 CLI behavior and project structure; no universal extractor/renderer/emulator is implied.
