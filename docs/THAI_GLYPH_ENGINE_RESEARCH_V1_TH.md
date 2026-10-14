# Thai Glyph Engine Research V1.0 — NDS / 3DS

Status: **Research + read-only audit prototype** (not a Nintendo font injector or emulator-proven renderer).

## Goal
Extend Framework V3.2.1 without replacing 6 phases, G0–G5, existing `font_review_plan.py`, `regression_guard.py`, or the Emulator-First 1–5 string smoke test. Do not restart existing game projects; reuse reviewed glyphs and known-good ROM baselines.

## Sources to evaluate
- HarfBuzz: https://github.com/harfbuzz/harfbuzz; Python binding: https://github.com/harfbuzz/uharfbuzz (offline shaping reference, not directly portable to Nintendo).
- OpenType Thai: https://learn.microsoft.com/en-us/typography/script-development/thai (marks, shaping and positioning).
- NintyFont: https://github.com/hadashisora/NintyFont; Fontendo: https://github.com/retrohead/Fontendo (inspect formats; target-game support must be verified).
- NDS evidence workflow: https://github.com/hyt24/nds-game-localization-skill
- Thai fallback concept: https://github.com/krirk0137/PassTheFearModThai (BepInEx/TMP code is not portable to NDS).

Review upstream licenses before incorporating code, fonts or assets.

## Why bitmap Thai fails
Presence of individual Thai Unicode characters is not proof of rendering correctness. Vowels, tone marks, baseline, advance and mark stacking require placement rules. Some games use encoded glyph IDs, custom fonts, prebaked UI art or runtime tile uploads instead of Unicode.

## Per-game decision tree
1. Confirm clean ROM hash, region/revision, known-good candidate, font/resource family, rendering path and control codes.
2. Prove exact **no-op roundtrip** of every edited resource parser/encoder. Preserve unrecognized bytes.
3. Measure rendered slots and UI bounds; never equate Unicode codepoint count to display-cell count.
4. Prefer (A) preserve original glyphs + Thai extension when renderer supports it, then (B) static precomposed combinations for bounded sets, then (C) verified layered mark offsets. (D) Dynamic ARM hook/cache is last resort and needs runtime evidence of pointers, cursor, upload completion and VRAM residency.
5. Patch an isolated 1–5-string scene first, diff only intended ranges, keep rollback and request emulator screenshot; do not wait for 100% font research.
6. Propagate tested results only to the same game, ROM revision and rendering path; do not reuse emulator PASS from another SHA.

## Thai regression samples
| Case | Samples | Inspect |
|---|---|---|
| Base glyphs | ก ข ค ญ ฐ ป ฝ | outlines, baseline |
| Above vowels | กิ กี กึ กื | positioning |
| Below vowels | กุ กู ญุ ฐุ | clipping |
| Tone marks | ก่า ก้า ก๊า ก๋า | marks stacking |
| Mixed stack | กิ่ กี้ ปี้ ฝ้า | overlap |
| Sara am | น้ำ สำ ทำ | decomposition/visual |
| UI + mixed text | มีผู้เล่นกี่คน; HP ภาษาไทย | width, control boundaries |
| Common labels | เริ่มเกม บันทึก ยกเลิก | small-font clarity |

Log: candidate SHA, emulator and version, scene, font size, screenshots/video, expected/actual and verdict. Offline atlas previews **cannot pass G3**.

## G0–G5 integration
- G0: exact clean ROM identity.
- G1: no-op/format/length guard, known-good baseline diff, deterministic candidate and rollback.
- G2: stable source IDs, scene/speaker, glossary, accurate/natural Thai, placeholders and UI budget.
- G3: Thai glyph layout approved from **real emulator** evidence.
- G4: boot, menus, long text, touch, save/load, scene transitions and past regressions.
- G5: release validated against source hash, reconstructed patch output, reviewer sign-off.

## Read-only prototype
`tools/thai_glyph_audit.py` scans headered CSV/TSV Thai translation columns, counts Thai codepoints, flags likely orphan mark sequences and (optionally) checks TTF/OTF cmap with fonttools. It DOES NOT parse NFTR/BCFNT, assign Nintendo glyph slots, shape text correctly, or prove actual game layout.

```bash
python tools/thai_glyph_audit.py input.tsv --column thai --output audit.json
python tools/thai_glyph_audit.py input.tsv --column thai --font permitted.ttf --fail-on-missing
python -m unittest discover -s tests -p "test_thai_glyph_audit.py" -v
```

Next: adapt report into existing quality queue and scene plan, then implement format-specific font probes **only** after confirming the target game uses those formats.
