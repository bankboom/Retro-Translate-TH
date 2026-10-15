# Thai Text Pipeline V1.0 — design and safe integration

Source studied: https://www.andaplus.com/games/index.php/gaming-tools-andaplus?view=article&id=4759 (article: การทำเกมเก่าให้เป็นภาษาไทย ทำอย่างไร?)
Related: docs/THAI_GLYPH_ENGINE_RESEARCH_V1_TH.md

## Scope
Add game-agnostic **read-only** preflight checks first. Maintain Framework V3.2.1's six phases, G0–G5 and Emulator-First smoke patch. Do not edit clean ROM, font binaries, ARM hooks or known-good patches as part of this document.

## Pipeline
1. **Source discovery:** Inventory exact ROM revision/hash, NitroFS/ExeFS/RomFS, text banks, glyph/image text, scripts, compression and control codes. Stable text IDs must map back to source locations.
2. **Contextual localization:** Translate only verified source rows; review meaning, speaker, scene, glossary, proper names, numbers, placeholders and UI intent. Preserve unknown controls as immutable tokens.
3. **Encoding:** Use a game-specific mapping from Unicode/semantic characters to encoded byte sequences and glyph IDs; never assume UTF-8/Unicode or one character = one byte. Prove decode(encode(x)) == x for supported test strings. Reject duplicate/ambiguous mappings unless explicit disambiguation is documented.
4. **Glyph shaping:** Distinguish Unicode characters, rendered glyph slots, advances and marks. Thai marks may have zero advance but nonzero offsets. Prefer preserving original font and adding Thai extension if proven safe. Test precomposed/static vs runtime composition per game.
5. **Layout/capacity:** Validate encoded byte budget, display width *in pixels*, line count, glyph slots and control boundaries separately. A 35-character rule alone is insufficient. Do not silently truncate; flag unmeasured widths as UNKNOWN.
6. **Pointer safety:** When relocating records, require verified pointer format, endianness, base address, alignment, target bounds, table bounds and free-space allocation. No writes to shared/unknown or out-of-range regions. Rerun roundtrip and component diff.
7. **Smoke candidate:** Select 1–5 grounded text IDs and a byte-safe patch plan; build from immutable clean ROM, preserve known-good baseline and rollback. If no safe builder exists, stop at the concrete blocker; never manufacture a patch.
8. **Evidence:** Offline validation alone cannot pass G3/G4. Log candidate SHA, emulator/version, exact scene, font size, screenshot/log, expected/actual, and regression matrix. Verify BPS/xdelta reverse application against candidate hash before G5.

## Integration with existing tools
- Reuse `tools/thai_glyph_audit.py` for codepoint inventory and suspicious mark warnings.
- Reuse `font_review_plan.py`, `quality_queue.py`, `regression_guard.py` and `release_audit.py`; do not create parallel quality gate systems.
- `tools/thai_text_preflight.py` is **read-only**: checks stable IDs, duplicate rows, protected token multiset, per-line codepoint cap (advisory), and optional game-provided glyph pixel advances. Pixel advance sum is an estimate and not a substitute for shaping/layout or emulator screenshots.
- A missing metric triggers `UNMEASURED`, not success. Not intended for direct ROM patching.

## Evidence requirements
| Check | Minimum evidence | Gate |
|---|---|---|
| Source identity | ROM hash, region/revision, trusted source provenance | G0 |
| Container/text reinjection | no-op roundtrip, bounded offsets, deterministic diff | G1 |
| Semantic QA | reviewed source IDs, scene, glossary and control matches | G2 |
| Thai glyph & UI | matched in-emulator screenshot/video, no clipping/overlap | G3 |
| Runtime stability | boot, menu, choices, save/load and historical regressions | G4 |
| Distribution | correct source/output hashes, patch reconstruction, signoff | G5 |

## Limitations
Article is general workflow education, not technical proof that a specific NDS/3DS game uses any encoding, font or pointer scheme. Format- or platform-specific adapters require per-game reverse engineering and evidence. Do not infer that the introduced audit can resolve NFTR/BCFNT or runtime VRAM behavior.

## Next safe task
Use approved project source exports (no ROM redistribution) to produce a report, review the missing metrics and control-token exceptions, then target one bounded NDS/3DS string-bank smoke candidate.
