---
name: retro-patch-qa
description: Verify a source-specific retro game BPS patch, compare candidate ROM bytes with a known-good baseline, and manage static/visual/gameplay QA gates. Use before releasing a translation build.
---

# Patch QA Skill
1. Confirm clean ROM path and verified revision; never apply an unrelated region/revision patch or overwrite originals.
2. For BPS run `python tools/retro_translate_v3.py bps-info --patch <file>` and `audit --rom <clean> --candidate <patch> --output <game>/qa/reports/static_audit.json`.
3. Check source/target/patch CRCs; if an external format (IPS/xdelta) is used, find reliable tooling and record validation steps (this CLI does not parse it).
4. When comparing builds, pass `--baseline` / `--previous` separately; inspect changed offset ranges and justify changes. Static byte diff does NOT prove exact font pixels changed.
5. Arrange real emulator testing with matching build ID: boot/menu/dialog/battle/transitions/save/load, multiple font sizes, Thai diacritics and clipping. Record screenshot paths, scene IDs, emulator name/version.
6. Update G0–G5 with statuses `PASS`, `FAIL`, `PENDING`, `NOT_APPLICABLE`, evidence and limitations; do not claim tests happened without actual logs/screenshots.
7. Release only patch/source-hash/manifest/known issues/rollback, never bundled copyrighted ROM/BIOS.

Output: static audit summary, delta table, visual test coverage, QA gate table, release/blocker decision.
