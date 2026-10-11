---
name: retro-rom-analysis
description: Inspect and fingerprint a retro game ROM, infer its actual platform/text banks, and build a reversible extraction plan for a Codex localization project. Use before editing or extracting a new game.
---

# ROM Analysis Skill
1. Read repository `AGENTS.md`, `docs/QUALITY_GATES.md` and current `projects/<slug>/project_profile.json`.
2. Check availability of a user-authorized source ROM. Never guess a file path, ROM revision, or a game engine.
3. Run `python tools/project_manager.py inspect --rom "<actual path>"` if a file is available; record output in the project's `qa/reports/`.
4. Confirm whether a known clean/source revision has been established. Hashing does not prove legitimate clean provenance by itself.
5. Identify actual containers/archives, decompression, tables, address translation, pointers, encodings, control codes, font assets and renderer, noting **confirmed vs hypothesized** for each.
6. Produce `analysis/ROM_MAP.md` and a reversible, game-specific extraction/repack plan in `docs/WORKFLOW.md`.
7. Before bulk export, verify an unchanged extract/rebuild round trip (or record why impossible).
8. Do not mark G0 or G1 PASS without evidence. If missing inputs or unsupported formats, mark PENDING and state the exact blocker.

Output: scan hashes, file inventory, technical findings with evidence, next reversible micro-experiment, gate table.
