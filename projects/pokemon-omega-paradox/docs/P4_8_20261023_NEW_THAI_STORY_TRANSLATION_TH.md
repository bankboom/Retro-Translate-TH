# Pokémon Omega Paradox TH — P4.8 translation expansion

Date: **23 October 2026**
Scope: **23 NEW unique whole-message Thai DRAFTS** created from the user's original `P3_5_Omega_Original_Custom_Queue.csv` text; **121** whole-message draft IDs cumulative across existing P3.9/P4.1/P4.2/P4.2B/P4.8 files.

## Reuse-First deduplication (do not repeat old work)
- Drafted a source-aligned batch of 32 candidate messages, preserving their exact original archive/file/message IDs.
- Checked all 32 against the **98** previously committed complete-message draft IDs.
- **Nine** messages were already translated in earlier full-message files, so the P4.8 file was reduced to **23 genuinely new IDs** rather than creating conflicting variants.
- Nine excluded duplicate IDs: `system/44/8`, `system/44/9`, `system/53/622`, `story/21/19`, `story/21/21`, `story/21/22`, `story/21/23`, `story/21/24`, `story/21/25`.
- Original **White TH** translation memory has already been reused in the prior P3.5 25,001-Thai-PUA snapshot; new P4.8 Omega-custom context is **translated from original source**, not presented as directly imported or verified White Thai text.

## New full-message coverage by bank
- **system/20/1:** trainer Drayden battle prompt.
- **system/44/26:** full intro/journey narration, all original variable code and page instructions preserved.
- **story/22/11–18, 20–22:** Nacrene museum, Alder, Team Aqua theft, Cynthia/Drake reactions.
- **story/36/7–9, 12–18:** Team Aqua pursuit, Barry, Diantha, Seven Sages and team battle scene.

## Evidence / QA
- Source texts were obtained from the user's own `P3_5_Omega_Original_Custom_Queue.csv` reference, preserving source exact fields in the generated CSV, not recreated from memory.
- For **23/23 complete messages**, ordered F000 opcode + operands, FFFE page/line boundaries and FFFF terminator sequences match the exact original exported strings.
- Visible Thai segments are at most **35 Unicode codepoints** (not a pixel-width claim).
- New draft IDs are unique within P4.8, and cumulative 121 unique IDs have no duplicate conflicting variants.
- **GitHub Actions [39909530338](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39909530338)**: compile PASS; **65/65 tests PASS**; 121-draft merger and preflight PASS.
- Draft CSV: `translation/P4_8_OMEGA_PRIORITY_FULL_MESSAGE_DRAFTS.csv`; its `DRAFT_NEEDS_CONTEXT` stage is intentional. These are NOT reviewed, encoded, injected, or user emulator verified.
- The GitHub CI cannot read the user's separate 56,700-entry Library inventory or run melonDS; source exactness vs live current ROM and 100% scope QA must be validated in the owner environment.

## Known limitations and next action
1. Manual speaker/scene/glossary Context QA needed; items `Dowsing Machine`, `Seven Sages`, `Aster`, `Pokémon Snow Grey`, and named characters must follow project glossary rather than automatic guessing.
2. Native E8xx semantic Unicode Thai->PUA encoder is still pending for arbitrary new Thai strings, so **NO P4.8 BPS** has been built. Existing P4.6 remains the last user-tested stable BPS (Cynthia two clauses, text advances, Save/Load).
3. Start a 1–5-message stable expansion smoke build from the original clean ROM, while preserving P4.6 regression checks, then expand only the newly changed banks/paths.
4. 121 full-message drafts are not 121 emulator-verified messages; the P3.5 broader Thai snapshot is distinct from full-game reviewed translation. Full G2–G5 remains unpassed.

## Do not redo
Do not rescan the already certified 1,309 native PUA glyph CMAP bitmap pairs or redo Cynthia pilot unchanged. Preserve the P4.6 version as rollback and use a diff-based review of new stories, encoding coverage and targeted QA.
