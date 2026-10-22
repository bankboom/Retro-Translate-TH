# Omega Paradox P4.5 — ROM-Verified Thai Glyph Master

**Scope:** Completed extraction of the native NFTR/CMAP/CGLP glyph tables from the user-supplied `Pokemon_White_Thai.nds`. This checkpoint is **glyph extraction complete**, NOT an encoder, new BPS, or complete-game localization.

## Real-ROM provenance

- White Thai ROM SHA-256: `1daeb35e3d508196cb84697f77179f3e62a31824cb68a1ce49e8ef68e2d7702c`
- Source font NitroFS path: `/a/0/2/3`, a NARC whose NFTR members are 0, 1, 2
- P3.7B target rebuilt in memory from the **original clean Omega** source via its original-sourced BPS. The P3.7B font NARC matches White Thai font NARC **byte-for-byte**.
- Font 0: 12×15 pixels, 2bpp, SHA-256 `c6eecc0aea8ce16347d67033a7b4228d5e47b95d6146c07fe65889e17ca165cb`
- Font 1: 10×10 pixels, 2bpp, SHA-256 `e853f49451d98cb71a74721a27e506741cd348ee2e08d1cb42bb5af3bdda5087`
- Font 2: 11×13 pixels, 2bpp, SHA-256 `6b71deafca60a8308d3668a8c372cbfbd315cb19f7735a6334c6334be7fb6edd`

## Extraction results

- **1,309 mapped PUA codes per NFTR**, **3,927 nonblank font/code pairs** across 3 fonts.
- Groups: `E000–E0FF` 256, `E100–E1FF` 256, `E200–E2A2` 163, `E800–E8FF` 256, `E900–E9FF` 256, `EA00–EA79` 122.
- **E800–E8FF: 256/256 mapped and nonblank in each font.**
- Font 0 has 1,309 distinct PUA glyph indexes; fonts 1 and 2 map 1,309 codes to **675 distinct glyph indexes each**, i.e. 634 aliases. Some E800 codes alias E000 on these smaller fonts. Do NOT infer a universal `codepoint->glyph index` arithmetic rule.
- Actual text parsed from 56,700 messages in White Thai: **1,225 distinct PUA codes; none missing in any font.**
- Actual text parsed from 56,700 messages in rebuilt P3.7B: **1,201 distinct PUA codes; none missing in any font.**
- All font byte equality and text lookup audits were performed against the real ROM/patch, not synthetic test CSVs.

## Master output (local project artifact)

The complete ZIP delivered in ChatGPT is named `Pokemon_Omega_Paradox_WhiteTH_ROM_Verified_1309_Glyph_Master_3Fonts_20261022.zip`.

It contains:
- 3 original, unmodified NFTR font resource members
- 18 PNG sprite atlas sheets covering 1,309 PUA codes × 3 fonts (plus E8xx-focused visual samples)
- 3 CSV character maps (including all 3,927 PUA font/code pairs)
- ROM/P3.7B SHA & font provenance verification JSON, per-file manifest, read-only parser and tests

**Do not upload the NFTR assets or ROM images to the public GitHub repository.** They were extracted from game resources provided by the project owner, so the binary pack stays with the project owner.

## What is / is not certified

- **PASS — ROM static evidence:** NFTR structures, actual PUA CMAP indexes, 2bpp glyph cell pixel data, bitmap ink nonblank, 3-font equality to P3.7B, PUA code coverage in both real ROM text archives.
- **PENDING — game-specific semantic encoder:** Mapping each PUA code to a verified Unicode Thai consonant/vowel/cluster. The NFTR alone stores PUA numeric codes and glyph pixels, not a validated Thai-language inverse table.
- **PENDING — proportional advance width/layout:** NFTR header size and CWDH first/last metadata in these particular assets are not canonical. Preserve the original font bytes; do not claim CWDH width metrics are decoded until engine semantics are confirmed.
- **PENDING — full gameplay:** Prior screenshots validate some P3.7B routes, not every font in every scene. No new BPS built.

## Next work (do not repeat glyph extraction)

1. Use this immutable NFTR master per font and verify any new code point via the actual CMAP, not arithmetic.
2. Derive Unicode Thai cluster -> native PUA encoding using **verified source Thai strings and context**; mark every unresolved grapheme as `UNKNOWN` and block release, rather than guessing by similarity.
3. Test encode/decode round-trip, CWDH/renderer pixel advances and page control tokens with a small reversible patch, preserving P3.7B fallback.
4. Only then scale localization and gate progress through G2–G5.
