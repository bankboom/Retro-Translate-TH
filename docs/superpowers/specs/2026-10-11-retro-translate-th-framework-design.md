# Retro-Translate-TH V3.2 Repository Bootstrap — Design

## Purpose

Initialize the public `bankboom/Retro-Translate-TH` repository as a reusable,
multi-game AI Retro Game Translation Framework V3.2 workspace. The result must
include the framework's `AGENTS.md`, `README.md`, `docs/`, `prompts/`, `tools/`,
quality-gate entry point, and reusable game-project templates. The first real
game project remains uninitialized until the user selects a game.

## Verified starting state

- GitHub repository metadata reports public visibility, size 0 KB, and default
  branch `main`.
- The repository contents endpoint reports the repository is empty; querying
  `main` reports no branch. There are no existing paths to replace.
- The Library package `AI_Retro_Game_Translation_Framework_V3.2_Codex_Chat_First.zip`
  contains 74 files, including root `AGENTS.md`, `README.md`, `docs/`,
  `prompts/`, `tools/project_manager.py`, `templates/`, tests, and
  `PACKAGE_SHA256.json`.

## Selected approach

Copy all 74 files from the verified V3.2 package to the repository root,
preserving their contents and paths. Add `quality_gates/README.md` as a small
index to the existing canonical `docs/QUALITY_GATES.md`; it must not restate
gate rules, so there is one normative source. The existing `templates/` files
and `tools/project_manager.py init` are the game-project template mechanism.
Keep `projects/.gitkeep`; do not initialize a sample game or add game-specific
ROM, patch, translation, font, or emulator results.

## Required invariants

1. Treat the clean source ROM as immutable and keep ROM/BIOS binaries outside
   the repository. Never overwrite the clean ROM or include it in a patch or
   release package.
2. Keep translation, Thai-font/layout, patch/binary, gameplay, and release
   states distinct. Report G0–G5 only as `PASS`, `FAIL`, `PENDING`, or
   justified `NOT_APPLICABLE`, with evidence. A CSV draft, static audit, or
   unobserved emulator run cannot establish a later gate.
3. Preserve package files byte-for-byte and retain the upstream package hash
   manifest. Only the new `quality_gates/README.md` and this repository's
   design/plan records are additional files.
4. Before remote writes, re-read repository contents and confirm they remain
   empty; abort rather than overwrite if any path has appeared.
5. Initialize `main` through the GitHub connector. Since the repository has no
   existing parent commit, use the supported bootstrap path and record any
   resulting intermediate commit explicitly; finish with one commit containing
   the complete V3.2 tree and verify the branch's final contents.

## Acceptance criteria

- The initial public repository contains the complete 74-file V3.2 package at
  its original paths, plus `quality_gates/README.md` and design/plan records.
- Required paths `AGENTS.md`, `README.md`, `docs/`, `prompts/`, `tools/`,
  `quality_gates/`, `templates/`, and `projects/` exist.
- `PACKAGE_SHA256.json` validates the copied package files; added repository
  records do not alter or replace upstream files.
- No game-specific project is created and no ROM, BIOS, or patch binary is
  added.
- GitHub `main` resolves and a post-write contents listing confirms the final
  paths. The work report names commit SHAs and reports the verification result.
