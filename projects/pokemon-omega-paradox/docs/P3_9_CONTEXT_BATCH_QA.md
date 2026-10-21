# Omega Paradox P3.9 translation draft QA

- Source: user's P3.5 Omega custom queue; archive and message IDs maintained.
- Newly drafted full-message entries: **31**.
- Ordered `\\xNNNN` control-code signature check: **31/31 passed**. This checks the numeric control units in order; parameter semantics and layout still need emulator verification.
- Longer-than-35-codepoint segment flag: **11 messages** (codepoint length is not rendered pixel width).
- Each row remains **DRAFT_CONTEXT_REVIEW**, not approved for injection. Some notification and proper-name rows require screen-width review.
- Duplicate event bulletin IDs 38/10 and 38/11 intentionally preserved.

## Critical safeguards
- Do NOT write Unicode Thai U+0E to NDS directly: earlier P3 and P3.2 attempts produced question marks and freezes.
- Require native E8xx font-bank/lookup encoding based on actually tested dialogue, with token/length round-trip and exact per-message source matching. Menu-bank glyph IDs do not necessarily map to dialogue.
- Keep header, ARM and prior passing overlays/fonts unchanged. Patch only original Omega source ROM with BPS, validate CRC32/SHA256 and test each 1–5-message pilot in Emulator.
- P3.7B showed text in the Cynthia scene but did not establish all game-play checkpoints. P3.5 failed at Drake, so do not use P3.5 as a build base.
- Next candidate: system 44 / 8, then system 44 / 9; separately repair system 44 / 24 Cynthia full Thai from the existing P3.8 translation draft.
- No P3.9 BPS was built or emulator tested with this translation-only commit.
