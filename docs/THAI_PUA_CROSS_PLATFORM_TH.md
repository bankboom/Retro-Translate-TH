# ThaiPUA-informed Composite Glyph Workflow — Shared / Cross-Platform

Status: **researched + optional read-only planner**. Not an NFTR/BCFNT converter, not an ARM9 hook, not emulator proof. This document is for the reusable root framework, **not any single game**.

Primary reference: [akkaraponsala/thaipua](https://github.com/akkaraponsala/thaipua) (MIT; reviewed README, AGENTS.md, cluster/grid/text-encoding and font-composer source, October 2026). Its included Sarabun font has a **separate OFL license**. This framework is inspired by concepts; it does **not** copy original files, font assets, or translated game data.

## What ThaiPUA contributes

- Represents supported combinations as a **Thai consonant + below/above vowel + tone-mark cluster**; precomposes glyph outlines using fontTools to bypass reliance on runtime mark shaping.
- Uses deterministic, versioned PUA layout; v2 indexes 42 modern consonants x 60 reserved combinations = 2,520 positions, of which 48 combinations per consonant are materialized by its current exclusion list (**2,016 candidates**). This is **not** a requirement to inject 2,016 glyphs into any game.
- Normalizes SARA AM (U+0E33) into NIKHAHIT + SARA AA for processing. Cluster matching prefers longer input patterns, with encode/decode testing.
- Allows per-consonant, vowel and mark offsets, alternate substitutions, bounding-box alignment, glyph occupancy/conflict checks, and font identity profiles.
- Works with TTF/OTF and plain text / Bethesda *.STRINGS, *.DLSTRINGS, *.ILSTRINGS. **There is no claim of native Nintendo DS/3DS format support.**
- Source has known exclusions and characters needing renderer attention (notably leading vowels `โ ใ ไ` and other cases). Precomposing attached marks is **not a complete Thai layout solution**.

## Per-game decision matrix

| Verified game capability | Preferred action | Must verify |
|---|---|---|
| Unicode + editable TTF/OTF with PUA cmap | Evaluate ThaiPUA font + text mapping **outside** original assets | correct PUA decode, conflicts, missing characters, font license, in-game rendering |
| Bitmap font, NFTR/BCFNT, custom glyph bank | Use **only composite cluster images / plans**; implement format-specific asset and encoding adapters separately | source-byte mapping, slot capacity, glyph size/advance, tile/cache/VRAM, no-op roundtrip |
| Text rendered into sprites/tiles | Prepare bounded precomposed bitmap samples for an isolated scene | palette, format, graphics path, sprite transparency and measured bounds |
| Existing shaping engine supports Thai | Prefer existing shaping and native Thai glyph coverage; **do not add PUA as a default** | mark anchors, wrapping and screenshots |
| Renderer/encoding not identified | Inventory and one safe existing scene before writing any resource | code/overlay refs, glyph lookup, pointer bounds, source SHA; PENDING |

**PUA Unicode U+E000+ is not the same as a Nintendo ROM glyph ID or byte.** Any `PUA -> game byte(s) -> glyph ID` binding must be proven for the exact engine and revision. Never assume Unicode bytes can be pasted into an NDS ROM.

## Cross-project ownership and reuse

- **Shareable in root framework**: pure cluster analyzer, common regression corpus, reference placements and source license notes, a reusable test planner and stable `U+XXXX` cluster keys.
- **Per-project only**: game-specific byte encodings, physical glyph bank/slot allocation, NFTR/BCFNT layouts, pointers, hook addresses, overlay memory, font metrics, target region/revision, and renderer-specific placement.
- **Do not share binary PASS** between games/regions/ROM hashes. Even placement profiles must be reviewed at target pixel size and font identity.
- Never replace the existing `font_review_plan.py`, `thai_glyph_audit.py`, `quality_queue.py`, `regression_guard.py` or release gates. Use the planner as **additional input** to the normal 1–5-string Emulator-First smoke workflow.
- Preserve user-owned font sources, game assets, and known-good build; use **MIT attribution** for any actual incorporated ThaiPUA code and respect the separate OFL terms for fonts. Reimplement concepts when practical.

## Universal implementation steps

1. Select one target text bank already grounded to source IDs; reuse approved glossary and current translation master.
2. Inspect `tools/thai_glyph_audit.py` for character inventory; run `tools/thai_composite_plan.py` for **unique observed Thai mark clusters** (do not build the complete Cartesian product).
3. Capture renderer/font evidence and real glyph-capacity limits. Without a verified capacity the tool reports `UNMEASURED`. Proposed composite keys are **demands, not assigned slots**.
4. Choose a game adapter: Unicode PUA path only where proven; otherwise glyph bitmap precomposition plus verified game encoding.
5. Compare a font/renderer baseline, run a **no-op roundtrip** on target asset, then change only the required 1–5 text IDs and few glyphs. Preserve controls; do not patch ARM9 until trace evidence proves necessary.
6. Review screenshot against `ต้า ตุ สำ น้ำ กิ่ กุ้ง ปี้ ฝ้า มีผู้เล่นกี่คน`; inspect one/two-line layout, mixed ASCII/Thai, scene and different font sizes.
7. Record build hashes, image evidence, font profile ID, expected and actual, G3/G4 explicitly PENDING until live evidence. Then expand only after smoke pass.

## Read-only planner command

```sh
# Reuse any game's existing translation master (Bank,ID,Thai columns).
python tools/thai_composite_plan.py projects/your-game/translations/master.csv --output projects/your-game/qa/reports/composite_plan.json

# If verified capacity is available for one shared font bank:
python tools/thai_composite_plan.py translations/master.csv --max-slots 128

# TSV or different column names:
python tools/thai_composite_plan.py translations.tsv --thai-column thai --id-column id
```

The planner produces a deterministic per-cluster priority list and flags unbound marks / unsupported stack combinations and leading-vowel follow-up. It does **not** export PUA mappings or change text. A `--max-slots` count is advisory only if all the selected strings use one verified common bank; otherwise calculate capacity per bank/renderer separately. The tool refuses to overwrite output files.

## Integration gates

- **G0:** clean ROM and revision SHA, game renderer family and font profile identified.
- **G1:** no-op asset roundtrip, safe/isolated allocation, verified byte diff and deterministic patch builder.
- **G2:** actual context review, protected tokens, per-game encoding, source ID and completeness of reviewed scope.
- **G3:** actual Thai glyph screenshot in emulator at the correct font size and scene (never infer from composite PNG / FontTools).
- **G4:** boot, text flow, menus, transitions, save/load and historical regression scenes.
- **G5:** patch reconstructs intended candidate against known source hash, no ROM/BIOS, reviewer approval.

## Explicit current limitations

Read-only planning only. This does not currently rasterize ThaiPUA TTF/OTF into Nintendo tiles, assign binary glyph IDs, shape `โ ใ ไ`, parse every control-code dialect, solve runtime glyph cache, or certify an emulator screenshot.

## References

- https://github.com/akkaraponsala/thaipua
- https://github.com/hyt24/nds-game-localization-skill
- https://github.com/Ich73/TranslationToolkit
- https://github.com/krirk0137/PassTheFearModThai
- docs/THAI_GLYPH_ENGINE_RESEARCH_V1_TH.md
- docs/THAI_TEXT_PIPELINE_V1_TH.md
- docs/EMULATOR_FIRST_TH.md
- docs/QUALITY_GATES.md
