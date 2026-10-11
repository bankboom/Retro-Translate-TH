# Retro-Translate-TH V3.2 Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Populate `bankboom/Retro-Translate-TH` with the verified AI Retro Game Translation Framework V3.2 package and a navigable quality-gate entry point without overwriting existing records or adding a game ROM.

**Architecture:** Preserve the package's 74 files byte-for-byte at their original paths. Add `quality_gates/README.md` as an index to `docs/QUALITY_GATES.md`; retain the existing templates and `tools/project_manager.py init` as the game-project creation path. Publish the additions in one fast-forward commit based on the current `main` head, then verify the resulting tree and commit diff.

**Tech Stack:** Python 3.10+ standard library; AI Retro Game Translation Framework V3.2 ZIP; GitHub Git Database API through the connected GitHub tools.

**Spec:** `docs/superpowers/specs/2026-10-11-retro-translate-th-framework-design.md`

## Global Constraints

- Clean ROMs are immutable, remain outside the repository, and are never included in patches or release packages.
- G0–G5 use only `PASS`, `FAIL`, `PENDING`, or justified `NOT_APPLICABLE`, backed by evidence; translation, font/layout, binary/patch, gameplay, and release states remain distinct.
- Preserve all 74 package files byte-for-byte and keep `PACKAGE_SHA256.json` unchanged.
- Refuse to replace any existing repository path; preserve the already committed design and plan records.
- Do not initialize a game project or add ROM, BIOS, patch, font, translation, or emulator-result binaries.
- Update `main` only as a fast-forward from its freshly read head SHA.

## Review Focus

- **Package drift:** Any missing or changed upstream file must fail the checksum check before staging; verify all 73 manifest entries and the separately retained manifest file.
- **Repository path collision:** Existing design/plan records are expected; any other staged path already present must stop publication. Test with a full recursive path comparison.
- **Concurrent branch change:** If `main` moves after reading its SHA, the ref update must fail its expected-SHA check; re-read and rebuild the additive tree instead of forcing it.
- **Accidental game data:** The package contains framework templates only; confirm no ROM, BIOS, patch, or game-specific project was staged.
- **False readiness:** A successful unit test or project initialization must not promote any game gate; verify the smoke project's G0–G5 all remain `PENDING`.

---

### Task 1: Verify and exercise the V3.2 source package

**Files:**
- Read: `AI_Retro_Game_Translation_Framework_V3.2_Codex_Chat_First.zip`
- Read: `RetroThai_Framework_V3.2_Codex/PACKAGE_SHA256.json`
- Temporary output: extracted framework under a fresh `/tmp` directory

**Interfaces:**
- Consumes: the Library-materialized V3.2 ZIP at `/workspace/scratch/575682bfe9de/AI_Retro_Game_Translation_Framework_V3.2_Codex_Chat_First.zip`.
- Produces: a verified extracted package root whose 73 manifest-listed files match their SHA-256 values; no staged repository paths yet.

- [ ] **Step 1: Extract the archive into a fresh temporary directory** and confirm it contains exactly 74 entries under `RetroThai_Framework_V3.2_Codex/`.
- [ ] **Step 2: Verify package hashes** with a one-off Python standard-library check: load `PACKAGE_SHA256.json`, read each `files_sha256` path from the archive prefix, compare SHA-256, and assert there are exactly 73 entries and zero mismatches.
- [ ] **Step 3: Run the framework unit tests** from the extracted package root.

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

Expected: every discovered test passes; do not infer emulator or game QA from this result.

- [ ] **Step 4: Smoke-test the game-project template** with a fresh temporary output root.

```bash
python tools/project_manager.py init --game 'Smoke Test' --platform NDS --slug smoke-test --region USA --output-root "$TMP_ROOT"
python tools/project_manager.py status --project "$TMP_ROOT/smoke-test"
```

Expected: the project initializes without a ROM, `project_profile.json` records no source ROM hash, every G0–G5 status is `PENDING`, and no ROM is copied. Remove only the temporary smoke-test directory created in this step.

### Task 2: Prepare the additive repository tree

**Files:**
- Copy unchanged: all 74 package files at their archive-relative paths
- Create: `quality_gates/README.md`
- Preserve: `docs/superpowers/specs/2026-10-11-retro-translate-th-framework-design.md`
- Preserve: `docs/superpowers/plans/2026-10-11-retro-translate-th-framework.md`

**Interfaces:**
- Consumes: the verified extracted package from Task 1.
- Produces: 75 new repository paths to add on top of the current `main` tree; existing design and plan files remain untouched.

- [ ] **Step 1: Stage the 74 package files unchanged** at their repository-root-relative paths, retaining `PACKAGE_SHA256.json` and `projects/.gitkeep`.
- [ ] **Step 2: Create `quality_gates/README.md`** as a brief index linking to `../docs/QUALITY_GATES.md` and `../docs/V3_2_REGRESSION_AND_RELEASE_TH.md`; state that `docs/QUALITY_GATES.md` is normative and game evidence lives under each project's `qa/` directory.
- [ ] **Step 3: Compare staged paths with the current GitHub recursive tree** and assert that no staged path overlaps any existing path; separately confirm the already committed design and plan records remain present and unstaged.
- [ ] **Step 4: Check staged file types and directories.** Assert required roots exist (`AGENTS.md`, `README.md`, `docs/`, `prompts/`, `tools/`, `quality_gates/`, `templates/`, `projects/`) and no ROM/BIOS/patch binary or game-specific project exists.
- [ ] **Step 5: Re-run the 73-entry package hash check against the staged tree** and verify the new quality-gate index resolves to the canonical docs path.

### Task 3: Publish and verify the framework on `main`

**Files:**
- Add: the 74 V3.2 package paths and `quality_gates/README.md`
- Preserve: the design and plan records already present in `main`

**Interfaces:**
- Consumes: the Task 2 staged tree and a freshly fetched current `main` commit SHA/tree SHA.
- Produces: one fast-forward commit whose parent is the fetched `main` SHA and whose only changes are the 75 intended additions.

- [ ] **Step 1: Re-read repository metadata, current `main`, and the recursive tree.** Abort if the repository identity/default branch changed, if `main` is unreadable, or if any intended new path already exists.
- [ ] **Step 2: Create Git blobs for the 75 staged additions** in independent batches, using UTF-8 for text files and the empty blob for `projects/.gitkeep`.
- [ ] **Step 3: Create a tree based on the fetched current tree SHA** with the 75 new path/blob entries; do not include existing design or plan paths as replacements.
- [ ] **Step 4: Create one commit** using that tree and the fetched current `main` SHA as its sole parent.
- [ ] **Step 5: Fast-forward `main` with an expected-SHA guard.** If the guard rejects the update, re-read the new head and tree, repeat the collision check, then rebuild the additive tree; never force-update.
- [ ] **Step 6: Verify the published commit and recursive tree.** Confirm all required roots and the two planning records exist, exactly 75 paths were added by the framework commit, `PACKAGE_SHA256.json` and package files are unchanged, and no ROM/BIOS/patch binary or game project was added.
- [ ] **Step 7: Report the commit SHA, package checksum result, unit-test result, smoke-test result, path-count check, and that game-specific gates remain untested/PENDING.**
