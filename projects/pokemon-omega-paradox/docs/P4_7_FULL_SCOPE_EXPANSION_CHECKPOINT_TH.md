# Pokémon Omega Paradox TH — P4.7 Full-Scope Translation Expansion Checkpoint

Date: 22 October 2026. Current status: **translation inventory merger implemented and unit-tested; full-game localization NOT complete.**

## Actual repo material incorporated

| Source file | Distinct full-message drafts | QA state |
| --- | ---: | --- |
| `P3_9_OMEGA_CUSTOM_CONTEXT_DRAFTS.csv` | 31 | DRAFT / context & glyph pending |
| `P4_1_OMEGA_STORY_EARLY_DRAFTS.csv` | 40 | DRAFT / context & glyph pending |
| `P4_2_OMEGA_STORY_CONTINUATION_DRAFTS.csv` | 19 | DRAFT / context & glyph pending |
| `P4_2B_OMEGA_COMPLEX_CONTROL_DRAFTS.csv` | 8 | DRAFT / context & glyph pending |
| **Total** | **98 distinct Message IDs** | **NOT injected / NOT emulator-verified** |

Do not include `P3_8_PRIORITY_THAI_DRAFTS.csv` automatically: it contains multiple **fragments** for some one-message IDs rather than a complete, control-validated target message. Merging the fragments as if they were full messages would destroy terminators or control tokens.

## New executable file

`tools/p47_full_scope_merge.py` performs a complete, fail-closed, read-only merge using the existing **56,700-row inventory** and all 98 full-message drafts:
- Enforces exact 56,700 unique archive/file/message keys, no truncated Library preview.
- Verifies source text equals the P3.5 inventory source **at that ID**.
- Verifies the ordered `F000` control payload and `FFFE/FFFF` tokens.
- Freezes duplicate conflicting variants, stale source strings, and unsafe control sequences.
- Classifies every message as existing P3.5 Thai snapshot, a draft needing context, backlog needing translation, Omega-custom hold, nonlinguistic or P4.6 scoped checkpoint.
- Writes `p47_all_inventory_states.csv`, `p47_context_draft_queue.csv`, `p47_blockers.csv`, `p47_missing_draft_ids.csv`, `p47_summary.json`.
- Makes **no ROM writes** and **no BPS**, and cannot mark drafts reviewed from a static CSV match.

Run against the user-owned raw inventory (local path only; never upload copyrighted ROM to GitHub):

```bash
python projects/pokemon-omega-paradox/tools/p47_full_scope_merge.py \
  --inventory /path/to/P3_5_All_56700_Text_Status.csv \
  --out /path/to/local/p47
```

For just the committed 98 drafts:

```bash
python projects/pokemon-omega-paradox/tools/p47_full_scope_merge.py \
  --check-drafts-only
```

## Verified GitHub Actions evidence

[Actions run 39818271371](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39818271371) completed successfully on commit `cc7457a5c68dcaff9bd506b8ece872d8efa8d7d7`.
- Python compileall PASS.
- **59/59** synthetic/static tests PASS, including 9 new scope merger tests, and 98 distinct real draft IDs confirmed.
- The CI does **not** contain the user's private/full P3.5 inventory or ROM, so it does **not** prove all 98 drafts exactly match that inventory, nor does it create a new patch.

## What is actually stable

**P4.6 is still the tested reference**, BPS SHA-256 `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`.

User validated **both Cynthia clauses in Thai, readable without question marks, dialogue advances, and Save + Load**. This is scoped G3/G4 PASS for the tested build, not full-game G4. P3.7B remains rollback. **Do not repeat unchanged Cynthia glyph tests.**

## Material blockers preventing full translation/BPS

1. The previously audited **20,096** messages still need context decisions/translation review; the 98 full-message drafts are **not** a substitute for 20,096 certified translations. Exact overlap must be calculated by running the merger on the full raw inventory.
2. Native E8xx semantic Unicode-to-PUA glyph/cluster encoding is not certified across the required renderer banks. The real extracted NFTR atlas and P4.6 donor are proven, but they are not themselves a general-purpose inverse encoder.
3. The actual native ROM builder used to produce P4.6 is available in the user's P4.6 zip, not in this GitHub repo; container execution for this turn returned ClientError, so the user's raw ROM and zip were **not processed** and no new BPS could be truthfully produced.
4. Context QA and pixel/layout QA must be performed for each newly injected message and relevant scene; the reused White TH narration for Cynthia remains semantically unapproved despite correct rendering.

## Next work without repeated loops

- Reuse the **verified P4.6** binary as regression baseline and original ROM as BPS source. Do not regenerate NFTR.
- Run the full CSV merger on the owner's existing data. Resolve blockers and source conflicts **before** encoding.
- Build a bank-specific Unicode Thai grapheme/cluster-to-PUA mapping with independent source-and-screen evidence.
- Apply newly reviewed messages in reversible, grouped, pixel-safe BPS builds; collect only new G3/G4 evidence for changed bank/scene.
- Expand until all nonlinguistic exclusions are justified, 100% text is reviewed/injected, and the complete game passes G0–G5.
