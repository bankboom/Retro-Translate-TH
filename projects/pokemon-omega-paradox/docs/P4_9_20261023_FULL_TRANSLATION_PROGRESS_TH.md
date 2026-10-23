# Pokémon Omega Paradox TH — P4.9 verified progress towards 100%

**23 October 2026. Status: full-game 100% translation NOT COMPLETE.**

## Real work performed

- **28** new nonoverlapping, complete Omega-custom message drafts translated from the project owner's `P3_5_Omega_Original_Custom_Queue.csv` English source, using pre-existing Thai terminology and preserving the native control-token sequence:
  - `story/43/0–18` (15 selected message IDs): Team Aqua stealing Gible, Barry, Cynthia, Diantha, pursuit and character reactions. Scene variant messages share consistent Thai wording.
  - `story/45/0–14` (9 selected IDs): item evolution stones, elemental type choice and gesture explanation.
  - `story/56/0,1,4,8` (4 IDs): Cynthia challenge and internal monologue, route to Nimbasa.
- Cumulative distinct full-message draft IDs increased from **121 to 149** after checking duplicates against P3.9/P4.1/P4.2/P4.2B/P4.8; **no duplicate IDs**.
- Draft file: `translation/P4_9_OMEGA_STORY_CONTINUATION_DRAFTS.csv`.
- Structure: source original field from actual Omega queue, same archive/file/message ID, exact ordered `F000` command operands and `FFFE/FFFF` markers, visible Thai segments <=35 codepoints.
- **CI passed 72/72** static/synthetic/source-draft structure tests at [run 39929919641](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39929919641), including 7 new P4.9 tests and the cumulative 149-draft merger.

## Critical story consistency issue flagged

- `story/43/18`: Cynthia refers to herself as a **Champion**, although she could not protect her Gible.
- `story/56/4`: Cynthia claims she will never be as strong as the protagonist, Drake or Diantha.
- The original Omega English text contains both characterizations. Both were translated faithfully and flagged `STORY CONTINUITY FLAG` for contextual review, **not silently retconned** and not falsely marked fully reviewed.
- This is especially important because the P4.6 Cynthia narrator prose was sourced from White TH's Bianca-origin text; the user verified legibility and gameplay, **not that all Bianca/Cynthia personality semantics are correct**.

## Why 100% cannot be claimed

- `P3_5_All_56700_Text_Status.csv`: **56,700** unique entries; prior P4.0 full audit confirmed **25,001 native Thai PUA snapshot entries** and **20,096 pending translation/context decisions**. Nonlinguistic text is not translation debt, and can overlap with special flags.
- **149 complete Thai draft message IDs** are additional source-aligned drafts, but the exact overlap with the 20,096 backlog needs the full 56,700-row merger executed in the owner runtime. Their draft state does **not** count as injected/reviewed/verified.
- Current latest user-tested binary remains **P4.6** with Cynthia two Thai clauses, dialogue advance and Save/Load PASS in those scoped screens. **No newer BPS was built or tested in P4.9**.
- Needed before a 100% release: approve contextual text, derive a verified per-bank Unicode Thai → native E8xx encoder, build/verify all changes against original clean Omega and P4.6 regression, in-emulator layout plus gameplay coverage and G0–G5 signoff.

## Non-repetitive execution order

1. Preserve P4.6 and already-extracted 1,309 PUA glyph master. Do not rescan fonts or retest unchanged Cynthia bytes.
2. Prioritize the Omega-custom story and game-specific unreviewed items, using White TH Translation Memory first wherever full source+context agree; dedupe near-identical lines/variants.
3. Require actual renderer bank, verified semantic glyph mappings and context before promoting drafts to `REVIEWED`.
4. Group *approved* native-coded messages into small reversible source-ROM BPS delta builds; compare against P4.6 for unchanged bytes; expand after gameplay evidence per changed renderer/scene.
5. Gate 100% only after full scoped inventory, all review flags resolved, and G0–G5 evidence. Do not replace that with a test count or extra draft count.

**Artifact boundary:** This update commits only user project translation CSV and QA scripts, no full copyrighted ROM or patch.
