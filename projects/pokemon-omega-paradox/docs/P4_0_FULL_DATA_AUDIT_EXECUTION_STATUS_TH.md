# Pokémon Omega Paradox TH — P4.0 Real Dataset Execution Status

วันที่: 22 ตุลาคม 2026
สถานะ: **BLOCKED / FULL 56,700-ROW AUDIT NOT EXECUTED**
ไม่ใช่ผลลัพธ์จากการประมวลผลครบทั้งเกม และยังไม่มี BPS P4.0

## Input raw files verified in the user's Library
| Input | Size in bytes | Scope |
|---|---:|---|
| `P3_5_All_56700_Text_Status.csv` | 22,914,268 | P3.5 Inventory, intended 56,700 rows |
| `P3_5_Reuse_Memory.csv` | 11,227,366 | White TH translation memory |

The two complete files were successfully materialized as *raw files* to the working container, but Python/container execution returned `ClientError`, including trivial interpreter commands. This is an environment issue, NOT evidence of a source CSV error.

## Partial, read-only preview smoke check — NOT full input
The Files text preview is truncated to approximately 755 inventory data records and 997 TM data records. A read-only parser examined **only those visible records**, yielding:

- Inventory records inspected: **755** (IDs 0–754)
- Translation Memory records available: **997** (IDs 0–996)
- Matching archive+file_id+message_id within visible subsets: **489**
- Matches with identical English source: **489**
- Among those, pairs with matching parsed control-token signature: **342**
- Rows marked `THAI_IN_ROM` in this P3.5 preview: **489**
- Newly eligible for injection as a result of this preview: **NOT DETERMINED** (these are snapshot rows, not P3.7B final-build proof)

**DO NOT extrapolate** these counts to the full 56,700 records, and do not claim any 50%, 70% or 100% reviewed coverage. Neither whole dataset nor current P3.7B target was exhaustively inspected.

## Verified automation unrelated to raw game data
GitHub Actions run [39732260462](https://github.com/bankboom/Retro-Translate-TH/actions/runs/39732260462) passed 16/16 **synthetic** tests for same-ID and cross-ID matching tools. This DOES NOT mean the user's real CSVs were run.

## Required completion gate
1. Run `tools/p40_reuse_audit.py` against both complete raw CSVs; require exact 56,700 unique inventory IDs.
2. Run `tools/p40_cross_id_review.py` on the same complete CSVs.
3. Save the actual `p40_reuse_audit.json` and `p40_cross_id_candidates.json` and resulting full CSV queues (without publishing copyrighted dialogue to a public repository).
4. Verify no conflicts, bad control tokens, misclassification of Omega-custom rows; calculate real counts from audit JSON only.
5. Keep context review/encoded/injected/in-game verified states distinct. This audit does not create a ROM nor BPS.

## Current blocker
The native container and Python runtimes returned `ClientError` consistently and the Library text preview cannot be used as a substitute for the original 56,700-row raw file. **Full requested task remains incomplete**; do not rename preview results as real-data audit.
