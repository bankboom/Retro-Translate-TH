# Pokémon Omega Paradox TH — P4.0 Bulk Reuse Runbook

## Scope / status
P4.0 is the **reuse-and-translation phase**. The project currently holds a P3.7B experimental patch with on-screen evidence for selected Thai text. This runbook and the static reuse auditor **do not constitute a P4.0 BPS patch or a 70% REVIEWED milestone**.

Existing evidence:
- Omega clean target SHA-256: 29c45c1031d630b2e2e8f31aecd9b279d26da7291f5db340d9ec5fb1657b812b.
- P3.5 inventory: 56,700 records; ~25,001 rows observed with Thai PUA in that snapshot, **not 25,001 QA-passed rows**.
- Remaining unclassified work queue: 20,096; Omega-custom text: 1,727 (these groups can overlap).
- P3.9 added 31 drafts with ordered control-unit checks, not encoded or injected.
- P3/P3.2 and P3.5 broke certain scenes with question marks/freezes. P3.7B shows mixed English/Thai Cynthia. Not proof of full gameplay.

## Inputs (supplied by project owner; do not add any ROM to git)
- Pokemon Omega Paradox.nds (original Omega; SHA-256 above).
- Pokemon - White Version (USA, Europe) (NDSi Enhanced).nds.
- Pokemon_White_Thai.nds.
- P3.7B BPS built against original Omega ROM, plus its previous binary QA and build scripts.
- P3_5_All_56700_Text_Status.csv.
- P3_5_Reuse_Memory.csv.
- P3_5_Omega_Original_Custom_Queue.csv and P3_9_OMEGA_CUSTOM_CONTEXT_DRAFTS.csv.

## Step 1 — Conservative reuse audit, no ROM write
From repository root, with the CSVs available in a working folder:

    python -m unittest discover -s projects/pokemon-omega-paradox/tools -p 'test_p40_reuse_audit.py' -v

    python projects/pokemon-omega-paradox/tools/p40_reuse_audit.py \
      --inventory /path/to/P3_5_All_56700_Text_Status.csv \
      --memory /path/to/P3_5_Reuse_Memory.csv \
      --out /path/to/output/p40

The audit **must stop** if the full count differs from 56,700, if IDs conflict, or if file fields are missing. It creates:
- p40_static_candidates.csv (exact master English and control signature; STILL context pending).
- p40_held_entries.csv (Omega-custom, source mismatches, unknowns, unsafe codes, already-Thai and other exclusions).
- p40_reviewed_reuse_manifest.csv (only if a separate explicitly reviewed approval CSV was supplied).
- p40_reuse_audit.json (counts and blockers).

For approval, supply CSV with:
archive,file_id,message_id,source_sha256,qa_status,scene_id,reviewer
and pass --approved-context /path/to/approval.csv. Source hash must match exact source text, QA must be REVIEWED, and human reviewer/scene must be present. **Approval does not mean injected.**

## Step 2 — Restore native Thai encoder from the working build
1. Read back P3.7B message bytes, keeping P3.7B as a protected fallback.
2. Derive font-bank-specific Thai PUA sequences only from confirmed dialogue strings.
3. For every candidate, prove encode/decode roundtrip and correct logical glyph mapping.
4. Preserve ALL control operations AND their operands, message terminators, page breaks, NARC member indexes, FAT bounds and pointers.
5. Check line wrapping against measured pixels, not only 35 Unicode codepoints.
6. Do not feed raw Unicode U+0E Thai characters to the NDS message serializer.
7. Never copy a whole White TH archive over Omega custom dialogue.

## Step 3 — Build a new candidate ROM without modifying originals
- Start from the same source Omega ROM and checked P3.7B working state.
- Apply only approved, exact-source/context-matched translations; keep Omega-custom text unchanged until separately reviewed.
- Record manifest of ALL replaced bank/file/message IDs and raw byte regions.
- Source ROM SHA, target ROM SHA, BPS CRC, target CRC and reproducibility/roundtrip checks must pass.
- Name release candidate P4.0 only once these checks pass, not when only the static audit completes.
- Do not distribute a complete ROM; produce only BPS plus QA evidence.

## Step 4 — Emulator validation
- First smoke: isolated Cynthia message 44/24 full Thai, then message 44/8, then message 44/9, 1–5 messages per pilot; keep rollback.
- Next regression: professor intro, Drake, Cynthia, choices, Bag/item, Pokemon names, move names, combat messages, Pokemon status screens, event transitions, saving and loading.
- Recheck text with combining marks: น้ำ สำ ตุ ต้า เก่ง ผู้ใหญ่, plus actual lines in every used font style.
- Collect emulator/version, patched build SHA, scene/ID, screenshot/log and tester.
- A screenshot that shows one line is only a line-level observation, not 100% gameplay QA.

## Gates to finish
- G0: ROM identity checked.
- G1: deterministic BPS and asset/binary invariants PASS on **P4.0 build**.
- G2: review/approval evidence for every row claimed REVIEWED.
- G3: in-emulator font/width tests cover modified scenes.
- G4: in-emulator gameplay smoke and regression.
- G5: NOT YET; final release requires whole-game closure and final audit.

## Known blocker, 2026-10-22
The working session's binary execution runtime returned system errors; new ROM bytes cannot be built or verified here. Consequently no P4.0 BPS or claimed binary QA success has been produced by this runbook. The project must not label this stage FULL/PASS or claim 70% reviewed based on raw PUA counts alone.
