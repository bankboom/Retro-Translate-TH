---
name: evidence-release
description: Track real Thai glyph/emulator evidence and block release until full G0-G5 review.
---
Use `tools/font_review_plan.py` to choose scenes, then collect screenshots and gameplay evidence from emulator, not simulations. `tools/release_audit.py` checks evidence paths and patch checksum only, it does NOT validate screenshots. Human signoff for G5 is mandatory. Never promote PASS from an unreviewed report.
