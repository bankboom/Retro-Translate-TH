---
name: regression-quality
description: Guard an incremental candidate ROM patch, audit byte changes versus known-good build and prepare a targeted translation review queue.
---
Load `docs/V3_2_REGRESSION_AND_RELEASE_TH.md` only for patch delta/translation QA tasks. Use `tools/regression_guard.py` with explicit verified allowed byte ranges. Use `tools/quality_queue.py` on changed strings with approved TM context. If any change is outside approved scope or baseline identity mismatch, stop; never claim G3/G4 from binary hashes. Do not touch clean ROM.
