---
name: retro-game-th-v3-1
description: Activate only for translating, reviewing, Thai-font fixing or patch testing a retro game. Thai phrase triggers include คู่มือ V3.1, คู่มือ V3.2, Framework V3.2, แปลเกมเป็นภาษาไทย, แก้ฟอนต์ไทย, ทำแพตช์เกม. Works with NES SNES GB GBC GBA NDS PS1 PSP 3DS and other platforms requiring adapters. Token-efficient and evidence-based.
---
# Retro Thai V3.2 — chat-first Codex skill (legacy skill ID retained)
<!-- RETRO_THAI_V3_1_OWNED_SKILL -->
Use the framework installed under `$CODEX_HOME/retro-game-th-v3-1/framework` (usually `~/.codex/retro-game-th-v3-1/framework`).
Do not pre-read all docs; read ONLY `AGENTS.md` and relevant prompt: `prompts/07_CHAT_ONLY_TH.md` or `prompts/09_REGRESSION_LOW_TOKEN_TH.md`. Read `docs/THAI_QUALITY_STANDARD.md`, `docs/TOKEN_EFFICIENCY_POLICY.md` or `docs/QUALITY_GATES.md` when relevant.

Process:
1. Work in user's current writable Codex workspace; prefer existing `projects/` root or configured workspace (`~/RetroThaiProjects`). Never create/change unrelated dirs. Locate user-provided ROM by explicit path or attached file; never crawl entire home. Confirm ROM identity and version before editing anything.
2. If new ROM use `python <framework>/tools/chat_project.py new --rom "<rom_path>" --output-root "<workspace>/projects" [--platform NDS]`; when continuing run `python <framework>/tools/chat_project.py find --game "<game_title>" --output-root "<workspace>/projects"`, then select existing `project_profile.json` by verified title, game identity/hash and reported path. If multiple candidates, ask which one. If ROM file isn't accessible ask user to supply it.
3. Keep original ROM immutable. For NDS/GBA tooling inspect supported headers; for other systems adapter/provenance gate can remain PENDING, not fabricated PASS.
4. Use source/scene context for translation; Thai should be grammatical, character-faithful and fit UI, preserve mechanics, placeholders, control codes, and terminology; review high-risk entries. Cross-game TM can suggest, never auto-approve. Punctuation/diacritics need emulator-based visual proof.
5. Cross-project TM: when a sequel/related game or any earlier reviewed project exists, read `docs/CROSS_PROJECT_TRANSLATION_MEMORY_TH.md`; run `<framework>/tools/cross_project_tm.py index --projects "<workspace>/projects" --db "<workspace>/shared_memory/cross_project_tm.sqlite"`, then `suggest` and `terms` for the active `--project`. Use game/series/context evidence and compare conflicting variants. Output is review-only; never inject automatically or reuse binary font/patch/pointers across platforms.
6. Token discipline: work in bounded delta packets, use approved TM/glossary (check title and scene), avoid whole-ROM dumps, avoid re-sending previously reviewed rows or long logs. Apply diff to IDs only; store a compact checkpoint in `docs/NEXT_TASK.md`.
7. Before candidate release, run `tools/regression_guard.py` (verified byte-offset scope), `quality_queue.py` (bounded translation delta), `font_review_plan.py` (emulator screenshot plan), and `release_audit.py` (human signoff preflight); read `docs/V3_2_REGRESSION_AND_RELEASE_TH.md` on demand. Gates G0/G1/G2/G3/G4/G5 require evidence. A binary check does not prove rendered Thai or actual gameplay; use screenshots, logs or explicit user tester. Never claim 100% before all gates.
8. Answer briefly in Thai: changed files/IDs; actual tests; gates altered; blockers; next action. Do not request manual folder creation.
