# Pokémon Omega Paradox TH — P5.5 verified BPS build/apply checkpoint

**Date: 23 October 2026**

## Why this work was needed

P4.6, the last user-tested patch, includes two readable Thai Cynthia sentences; the user confirmed dialogue progression and Save/Load. Subsequent 270 Unicode Thai *drafts* from P3.9–P5.2 have not been independently injected into Omega. The P5.4 private inventory reconciler did not create binary patches.

**P5.5 adds the missing independent BPS integrity layer** necessary for a reliable patch and rebuild workflow. This is **not** a translated-ROM writer; it does **not** transform Unicode Thai to Native PUA, edit NARC/MSG structures, or create a new game translation by itself.

## New source and test files

- `tools/p55_bps_verified_io.py`: BPS1 `inspect`, `apply`, `create`.
- `tools/test_p55_bps_verified_io.py`: 15 new tests.
- GitHub Actions [run 39979439095](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39979439095): **SUCCESS, 135/135 tests** total.

### Implemented checks

1. Correct BPS1 variable integers, metadata bounds, trailer patch CRC32.
2. Applies all four BPS operations: **SourceRead, TargetRead, SourceCopy, TargetCopy**, including overlapping TargetCopy.
3. Original `clean.nds` is read-only and **cannot be specified as the output**; destination must not exist.
4. Checks original size + BPS source CRC32. Optional **full exact SHA-256 of clean ROM** is checked before any output is written.
5. Writes application output to a temporary file and **publishes only after applied target CRC32 and optional target SHA-256 pass**. An invalid BPS does not leave a deceptively complete output ROM.
6. Creates a valid BPS from clean ROM + **already rebuilt target ROM** using aligned SourceRead/TargetRead. It compares equal ranges by blocks, so mostly unchanged NDS files produce compact patches.
7. By default, a newly created BPS is **actually applied** to a scratch output and the result SHA-256 is compared to the candidate rebuilt target before publishing the BPS.
8. No original ROM, patched ROM or copyrighted resource is committed to this public repository. Tests operate only on synthetic small byte buffers.

## Recheck P4.6 in the owner's local private workspace

Known reference fingerprints, obtained from earlier actual project outputs:
- Original Omega clean ROM SHA256: `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`
- P4.6 BPS SHA256: `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`
- P4.6 **patched target** SHA256: `945c0bc11b137580311af9c38b6f62852a6cf688e16a89854e7d64ed00427a04`.

Run these commands from project checkout. The paths below are placeholders: keep owned ROM/BPS artifacts private.

```powershell
python projects/pokemon-omega-paradox/tools/p55_bps_verified_io.py inspect `
  --clean "D:\Omega\Pokemon Omega Paradox.nds" `
  --bps "D:\Omega\P4_6_Cynthia_from_clean.bps"

python projects/pokemon-omega-paradox/tools/p55_bps_verified_io.py apply `
  --clean "D:\Omega\Pokemon Omega Paradox.nds" `
  --bps "D:\Omega\P4_6_Cynthia_from_clean.bps" `
  --out "D:\Omega\P4_6_verified_result.nds" `
  --expected-clean-sha256 29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b `
  --expected-target-sha256 945c0bc11b137580311af9c38b6f62852a6cf688e16a89854e7d64ed00427a04
```

**Do not run this on a P3.7B or any already patched ROM**; the BPS source is the clean original.

## Create a BPS for a future verified native-Thai rebuilt ROM

**Precondition:** another, game-specific tool has already transformed and validated the exact original ROM into a private `Omega_P5_6_rebuilt.nds` target, including correct Thai PUA/codepoint encodings, safe MSG/NARC repack, pointers, and scene review.

```powershell
python projects/pokemon-omega-paradox/tools/p55_bps_verified_io.py create `
  --clean "D:\Omega\Pokemon Omega Paradox.nds" `
  --target "D:\Omega\Omega_P5_6_rebuilt.nds" `
  --out "D:\Omega\Omega_P5_6_from_clean.bps" `
  --expected-clean-sha256 29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b
```

This commands **builds and verifies BPS**; it does not translate the game on its own.

## Evidence versus remaining blockers

| Gate | Result |
| --- | --- |
| BPS parser/generator/applicator correctness on synthetic data | **PASS 15 new tests; overall CI 135/135** |
| P4.6 known user-scene Thai readability, Save/Load | **USER PASS (scoped)** |
| Applying real P4.6 BPS using P5.5 code inside ChatGPT this turn | **NOT RUN: local container backend failed** |
| Native Unicode Thai -> PUA encoding for 270 draft texts | **PENDING** |
| Game-specific NARC/MSG repacker for newly approved messages | **PENDING** |
| 56,700-row owner inventory re-audit using P5.4 and full White memory | **PENDING this new version** |
| New expanded P5.5 BPS for Omega | **NOT BUILT** |
| Full-game G0-G5 localization certification | **NOT DONE** |

## Next actual bottleneck — not another glyph redesign

Obtain a **game-specific MSG/NARC rebuild that preserves clean-ROM FAT, ciphertext commands, native Thai mapping and pixel layout**. Reuse the already owner-verified P4.6 BPS source package and extracted 3-font master; do not re-invent E8xx offsets. Once a new native-Thai rebuilt ROM exists, call this P5.5 builder to independently produce a verified BPS with full original-source SHA and applied target SHA. Test only changed scene(s) plus targeted save/battle regressions.

**Important:** The 135 passing tests are CI tests on synthetic binary content and code. They do **not** imply the Pokémon ROM was rebuilt, patched, or played end-to-end.
