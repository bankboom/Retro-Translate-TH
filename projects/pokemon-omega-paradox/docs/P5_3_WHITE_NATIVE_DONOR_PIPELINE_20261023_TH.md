# Pokémon Omega Paradox TH — P5.3 White TH native donor reuse (2026-10-23)

## Purpose: move toward shipping BPS rather than repeating draft cycles
A central blocker after **270 unique Omega full-message Thai drafts** is that these drafts are Unicode Thai text while the game renderer expects native Private Use Area codepoints (often E8xx/E0xx, with fonts differing by bank). The proven ROM-derived **1,309 PUA glyphs in each of 3 NFTR fonts** establish glyph availability, but do **not** establish an inverse Unicode Thai grapheme => PUA mapping.

P4.6 already provides a user-tested proof of **two Cynthia lines in Thai, no question marks, dialogue continuation and Save/Load working**. The user-owned `P4_6_Native_Phrasebook.csv` includes the exact native 29-unit and 20-unit clause sequences, sourced from White Thai and inserted into Omega. This is **two exact phrase donors**, not a general alphabet encoder, and those two sentences should not be rewritten into arbitrary contexts.

## New read-only program

`tools/p53_white_native_segment_reuse.py` searches **actual owner's `P3_5_Reuse_Memory.csv` (expected 25,976 rows)** for donor pairs of exact English segment => native Thai PUA text, then checks the project's 270 Omega full-message drafts.

Before suggesting a candidate, it requires:
1. Exact original English **visible segment**, no fuzzy matches.
2. Same **archive and file / renderer bank**; do not substitute system strings into story bank.
3. Whole source and native donor have **the same ordered F000 opcode+operands, FFFE and FFFF sequence**. **Do not trust the older `control_equal` column as the only control check.**
4. One unambiguous Thai native PUA variant for that English segment in that bank; conflicts go to hold.
5. Native UTF-16 codeunit length <= ASCII source slot capacity for a nonrelocating pilot. If source includes non-ASCII or unsupported units, hold for NDS-specific decoder.
6. Context, visual pixel width, speaker and special grammar are **still pending**, even if all phrases have donors.

**This index never writes a ROM, emits an all-green release status or assembles a BPS.** It emits a per-ID donor-review CSV and JSON summary, keeping copyrighted raw text in the owner's local workspace, not public GitHub.

### Run with full owner CSV

```bash
python projects/pokemon-omega-paradox/tools/p53_white_native_segment_reuse.py \
  --master /owner/path/P3_5_Reuse_Memory.csv \
  --out /owner/local-private-output/p53
```

The program **fails closed** if the master is not exactly 25,976 rows or if the project has fewer/more than its configured 270 draft rows. The 270 expected count must be updated when legitimate new drafts are added.

## What was actually tested

- The user-owned P4.6 native donor file was retrieved via Files and confirmed to contain **29 and 20 native codeunits** for the two Cynthia description clauses. Its original `Emulator_verified` column says NO because that export predates the user's later explicit successful playtest. Do not misrepresent that as a new glyph-to-Unicode proof.
- A retrieval attempt through Files returned only the **first approximately 1,000 parsed text records of the original 25,976-entry White TM**, with later ranges clipped to the same indexed preview. **That preview must NOT be treated as the full translation memory or the basis for an authoritative full-donor count.** The existing full raw owner file is still needed for the real full audit.
- The same owner data in the White TM preview visibly stores native PUA in escaped units such as `\\xE00A`; the encoder script handles these as 16-bit codes, not Unicode Thai text.
- GitHub Actions [39948122661](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39948122661): **PASS 114/114 static/synthetic tests**, including 11 new fail-closed tests covering same-bank donors, control retention, ambiguous translations, slot overflows, context hold, and duplicate draft IDs. No game ROM, complete memory CSV or emulator is present in CI.

## Next build gate

1. Run `p53_white_native_segment_reuse.py` with the **full original 25,976-row raw White memory file** and review its **exact donor candidates for the Omega draft bank**; do not extrapolate from the first 1,000 rows.
2. Use the already user-tested P4.6 BPS and local build package to assemble a **small source-ROM patch** for the first context-approved new message whose entire visible text has valid donor mapping and no width/token violations. If no full same-bank donor exists, do **not** fabricate E8xx codes.
3. For unmatchable new Greek/Thai content, derive Thai grapheme => PUA semantic mapping from verified font+real on-screen text rather than glyph arithmetic; retain P4.6 rollback and recheck only changed scenes.
4. Keep status separate: `DONOR_MATCH_REVIEW` / `CONTEXT_APPROVED` / `ENCODED` / `BINARY_VERIFIED` / `EMULATOR_VERIFIED`. A donor match is never a shipped translation.
5. Continue remaining review inventory toward **all 56,700 classified records**, including 20,096 review candidates, maintaining exclusions for nonlinguistic rows.

No new BPS and no full-game 100% assertion are made in P5.3.
