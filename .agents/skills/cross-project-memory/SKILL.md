---
name: cross-project-memory
description: Reuse verified Thai localization, glossary, and context from related games and sequels across platforms with offline indexing and mandatory context QA.
---
# Cross-project Translation Memory
Read `docs/CROSS_PROJECT_TRANSLATION_MEMORY_TH.md` only when reusing cross-game translation.

1. Preserve user data and ROMs; index only REVIEWED/APPROVED/VERIFIED translations and approved glossary terms.
2. Identify `series_id` from project evidence, not from a guess. Platform and publisher do not imply equivalence.
3. Generate offline shortlist with `tools/cross_project_tm.py`. Do not inject results automatically.
4. Check scene/speaker, exact source/control token signatures, glossary conflicts, style and narrative meaning.
5. Every reused string needs review for the target game and target renderer. Save decisions and provenance.
6. Output only the new/changed IDs, summary counts, conflicts, and remaining blockers to save tokens.
