---
name: retro-token-efficient-workflow
description: Minimize Codex tokens during multi-game translation while keeping source fidelity, Thai grammar, font quality and QA; use for context packing, reuse, batching and incremental edits.
---

# Token-aware localization
1. Read `AGENTS.md`, active project's `AGENTS.md`, `project_profile.json`, `docs/NEXT_TASK.md`; read `docs/TOKEN_EFFICIENCY_POLICY.md` only if needed.
2. Never dump complete ROM/binary/CSV or all repo docs. Identify changed rows/IDs, font glyphs, banks and hashes first.
3. Run `python tools/token_saver.py pack --project projects/<slug> --mode missing --limit 40 --max-chars 9000 --output projects/<slug>/working/context_packet.md`; inspect the small packet, then request missing scene context only for uncertain IDs.
4. Use glossary of matching terms. Generate optional exact approved memory suggestions using `suggest`; these do not automatically become translations.
5. For AI edits, output only `ID,Thai,QA_Note` and unresolved IDs. Persist reviewed rows and next steps on disk. No redundant narrative, repeated full scans, or retranslation of approved rows without changed context.
6. Still run spelling/semantic/token/pointer checks and emulator screenshot QA; report PASS only with evidence. Do not estimate actual token usage from character counts.
