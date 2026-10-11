# Work plan

## Goal / game-specific constraints
Pending ROM verification.

## Investigate (G0/G1)
- [ ] Record ROM provenance, sha256/CRC32, platform, region, revision
- [ ] Locate text data, font assets, pointers, encoding and compression
- [ ] Create extraction/repack round-trip test with unchanged data

## Translate and validate (G2–G4)
- [ ] Create master CSV and glossary, source map
- [ ] Draft/review first 1–5 strings, inject as a reversible micro-patch
- [ ] Verify Thai glyph display in emulator with screenshots
- [ ] Verify menu/dialog/battle/save/load and regressions

## Release (G5)
- [ ] Finalize patch for one clean ROM revision
- [ ] Re-apply patch from clean ROM, record hashes and reproducibility
- [ ] Attach gate evidence + issues + rollback instructions
