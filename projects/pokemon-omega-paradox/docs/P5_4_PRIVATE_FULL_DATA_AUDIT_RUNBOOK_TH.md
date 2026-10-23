# Pokémon Omega Paradox TH — P5.4 Full-data execution runbook

**Date:** 23 October 2026  
**Build status:** PRIVATE RECONCILIATION TOOL IMPLEMENTED + CI TESTED, **not** a full-game translation release.

## What is ready

- Script: `tools/p54_one_pass_private_audit.py`
- It reuses prior `p47_full_scope_merge.py` (source-aligned 56,700-message inventory / 270 full-message drafts) and `p53_white_native_segment_reuse.py` (real 25,976-row White TH original-English -> native PUA exact phrase donor review).
- It fingerprints the two original CSVs and, if present, the user's original Omega ROM and original-sourced P4.6 BPS. BPS check includes patch trailer/patch CRC and original source CRC; the target CRC is NOT verified without actually applying patch.
- It detects truncated data, duplicate source IDs, conflicting draft variants, altered command tokens, wrong file hashes, bank-incompatible donor source, unknown Native PUA glyphs, and native lengths that cannot fit a fixed slot.
- It writes private local per-ID queues and a JSON audit manifest. It **never alters the original ROM or constructs a new BPS**.

## Exact private input hashes

| Input | Required rows | SHA-256 |
| --- | ---: | --- |
| `P3_5_All_56700_Text_Status.csv` | 56,700 | `d5a680554e1130eb63b99f515b410937179acfb7f943c2420a4e7f4010f65e34` |
| `P3_5_Reuse_Memory.csv` | 25,976 | `c352a547d9b44dfc881eafddb1e146e9f1fd4b5a2ec49678e99debcd4b688557` |
| Clean `Pokemon Omega Paradox.nds` | — | `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b` |
| P4.6 original-ROM BPS | — | `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6` |

**Use files as provided by the project owner, not GitHub-hosted ROM content.** Copy user files only into the user's own trusted local/private Codex workspace. Never upload the private ROM/White-Thai assets/complete translation memory to the public repository.

## Execute once when the original uploaded binaries are available

The following paths are illustrative of the paths recorded in the previous Omega chat container, not a claim that they are available inside the current GitHub runner:

```bash
python projects/pokemon-omega-paradox/tools/p54_one_pass_private_audit.py \
  --inventory "/mnt/data/files/P3_5_All_56700_Text_Status.csv" \
  --white-memory "/mnt/data/files/P3_5_Reuse_Memory.csv" \
  --clean-rom "/mnt/data/Pokemon Omega Paradox.nds" \
  --p46-bps "/mnt/data/Pokemon_Omega_Paradox_TH_P4_6_Cynthia_CompleteNative_Pilot/Pokemon_Omega_Paradox_TH_P4_6_Cynthia_Full_Thai_Pilot_from_Clean_Omega.bps" \
  --out "/mnt/data/Pokemon_Omega_Paradox_TH_P5_4_Private_QA"
```

If clean-ROM and BPS are temporarily absent, **omit `--clean-rom` and `--p46-bps`**; this performs only a data reconciliation and must be marked `ROM_BINARY_PENDING`.

Generated local-only outputs:
- `private_full_audit_summary.json` — full row counts, SHA/CRC checks and real per-state review counters, always marks new BPS/full release false.
- `inventory/p47_all_inventory_states.csv` — **all 56,700 original message IDs** with per-row QA state.
- `inventory/p47_context_draft_queue.csv` — 270 draft IDs with exact source/control overlap results.
- `inventory/p47_blockers.csv` — source/control/variant disagreements.
- `native_donor_review.csv` — direct native-PUA matching results, not a Unicode Thai glyph encoder.

## Validation evidence for the program

[GitHub Actions run 39974279240](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39974279240): **SUCCESS, 120/120 static/synthetic/integration tests**, including:
- Incomplete 56,700-inventory input fails before any output;
- source SHA mismatch fails before any output;
- duplicate draft IDs fail;
- BPS patch trailer CRC mismatch is detected;
- reusable same-bank native donor remains `REVIEW_ONLY`, never auto-released;
- old original source arrays and P4.6 verified fallback are not modified.

**This success does not mean 56,700 real rows were processed during this turn.** Local binary tools were unavailable; previous Files extraction only provided a clipped text preview. Neither private ROM nor full original TM is in GitHub CI.

## Stages required before a 100% patch

1. Run the above one-pass real-data report. Review precisely flagged changes since P5.3, not the entire old completed audit.
2. Confirm contexts and exact native donors for all candidate messages. For missing donors, derive a verified per-bank Unicode Thai grapheme-to-native-PUA mapping; never guess.
3. Use the user-owned P4.6 build package to build **one small real changed-bank BPS** from the exact clean ROM. Perform actual patch apply CRC/SHA and ciphertext/FAT/pointer regression against the P4.6 target; do not treat trailer checks as applied-target verification.
4. Validate only new/changed scenes on melonDS; keep P4.6 Cynthia dialogue + Save/Load as existing scoped pass unless related bytes change.
5. Progress with diff-based batches through remaining reviewed text and no-text classifications; finally test full story, menu, items/moves, saves, battles, graphics text and edge cases before granting G5.

### Clear boundary

The owner previously validated **P4.6 Cynthia two translated clauses, no question marks, dialogue advancement, Save/Load**. That is still the only user-confirmed scoped stable patch. The 270 later complete-message Unicode Thai drafts have not been incorporated in a newer BPS. A claim of **100% translated/emulator-tested** would be incorrect.
