# Pokémon Omega Paradox TH — P4.6 Native Cynthia BPS Pilot (22 Oct 2026)

## Result
**Built real BPS from original clean Omega ROM; independent Binary QA PASS.**
This is a reversible, one-message pilot, NOT a 100% translated game or an emulator-verified release.

- Source ROM: `Pokemon Omega Paradox.nds`, SHA-256 `29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b`.
- P3.7B known baseline target SHA-256: `73009450390e2fded1abe7adfb7e8914ff3dc3443bd068ddf164a2e3196c08bf`.
- P4.6 patched ROM target SHA-256: `945c0bc11b137580311af9c38b6f62852a6cf688e16a89854e7d64ed00427a04`.
- P4.6 BPS SHA-256: `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`, source and target CRC validated.
- Distributable user-owned artifact: `Pokemon_Omega_Paradox_TH_P4_6_Cynthia_Native_Thai_BPS_Test_Package.zip`. No ROM or BIOS is included in package; do not commit copyrighted ROM bytes to the public repository.

## Change scope
**System archive /a/0/0/2, file/member 44, message 24 ONLY**.

In P3.7B the narrator's second page still had English first clause `She's a little flighty,`, then a Thai native 20-unit second clause `but she works very hard.`. Copied the complete 29-unit native-Thai first clause from the user's actual White TH ROM, after verifying the original English source matches its White clean equivalent.

All game-custom Cynthia name codepoints were **preserved** from P3.7B; the source White Thai message describes Bianca in its first clause, hence the **Cynthia character-context QA is still pending**. Removed six trailing spaces after `Cynthia.` to fit the native first clause within the original 83-code-unit message; no glyph truncated or guessed.

Validated:
- Message remains **83 UTF-16 code units**, same compressed/encrypted allocation.
- Identical ordered control operations and parameters: `F000 BE01 0000`, `FFFE`, `FFFE`, `F000 BE01 0000`.
- First F000 and first FFFE offsets shift **28→22 and 31→25**; second FFFE and last F000 unchanged at 55 and 80. These two offsets need emulator validation!
- 31 unique E8xx native PUA glyph codes from these two clauses have valid nonblank mapped bitmap glyphs in **all three exact P3.7B-compatible NFTR fonts**.
- Independent P3.7B vs P4.6 binary regression: **64 different ROM bytes**, all in the encrypted ciphertext belonging to this single message; all other NARC members and all other ROM bytes identical.
- BPS apply, source CRC, target CRC, patch CRC, target SHA256: PASS; final target ROM held only in working memory.

## QA stage and next action
- **G0:** Source SHA-256 validated for this build.
- **G1:** Binary patch integrity and delta scope PASS for this pilot.
- **G2:** Native master phrase exact-English source matched; Cynthia speaker/story semantics remain NEEDS_CONTEXT, no 100% translation claim.
- **G3:** NFTR glyph coverage static PASS for 31 used codes, real screen spacing/mark stacking pending.
- **G4:** Emulator PENDING; must see both Cynthia lines, press through dialogue and test Save/Load.
- **G5:** Full release PENDING; 20,096 context-review rows and uncovered game content remain.

## Test instructions
Apply only to the **original Omega ROM** with the exact source SHA above; do **not** patch an already patched P3.7B ROM. On melonDS Android start/continue intro to Drake then Cynthia, verify name, two Thai narration clauses, no ???? or clipping, advance all dialogue and test Save/Load. If regression occurs restore the unmodified P3.7B patch.

## Reusable source
The local user-owned ZIP includes `tools/build_p46.py`, exact-source NFTR lookups and `tools/regression_verify_p46.py`; it requires the owner's three ROMs and P3.7B BPS to rebuild deterministically. Native phrase donor lookup is **not** a certified Unicode Thai-to-PUA cluster encoder. Do not start another large bulk injection without solving the per-bank encoder/renderer layout and contextual QA.

## User-reported P4.6 Save / Load test — 22 Oct 2026
- The project owner reported directly in chat: **"ตรวจแล้ว save และ load ได้ปกติ"** (Save and Load both work normally).
- Evidence class: **user manual playtest report**. Scope: **Save PASS / Load PASS** for the P4.6 candidate discussed in this project. No screenshot/video, emulator version, or save-slot details were supplied with this specific observation.
- **G4 PARTIAL:** this confirms the requested Save/Load smoke step only. It does **not** establish full-game gameplay PASS, the visual integrity/meaning of both Cynthia clauses, dialogue advancing, any specific glyph layout, or G2/G3/G5 signoff.
- Next visual checkpoint: collect in-game Cynthia both Thai clauses and confirm both dialogue screens render clearly and progress correctly; keep G2 character semantics pending until reviewed.
- Keep user feedback attached to the P4.6 BPS SHA-256 `48f60e64dff45dd505d9d00d44dfc6493690d20383201ce36a22f61c8fb88ce6`; a different patched ROM build must be tested independently.
