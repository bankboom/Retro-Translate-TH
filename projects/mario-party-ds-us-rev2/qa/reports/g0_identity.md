# G0 — ROM identity evidence

Status: **PASS** for the exact USA Rev 2 file identity; upload chain-of-custody remains unverified.

| Field | Observed | Reference |
|---|---|---|
| Filename | `Mario Party DS (USA) (Rev 2).nds` | same |
| Size | 33554432 bytes | 33,554,432 bytes |
| Platform / game | NDS / `A8TE` / `MARIOPARTYDS` | Mario Party DS USA |
| Revision | Header byte `0x1E = 02` | Rev 2 |
| SHA-1 | `96054049ac831720f1c7c63023cf18907352d45c` | `96054049ac831720f1c7c63023cf18907352d45c` |
| CRC32 | `4FCBB5C3` | `4FCBB5C3` |
| SHA-256 | `50a8df48d0cc78d45506825217278598fac2c87cb2bb090e0da304a8b4f31433` | No reference SHA-256 recorded |

Observed SHA-1, CRC32, and size match the No-Intro-labeled Rev 2 row. Sources: [OpenRetro No-Intro import record](https://openretro.org/game/ff242a1e-84a7-4b91-ab64-3d677b027975/edit), [independent hash listing marked No-Intro verified](https://romhackplaza.org/romhacks/mario-party-ds-how-to-play-board-nintendo-ds-romhack/), and [No-Intro DAT-o-MATIC Nintendo DS dataset listing](https://datomatic.no-intro.org/index.php?page=download&s=156). The exact row was cross-checked through the first two records; DAT-o-MATIC identifies the current Nintendo DS DAT, but its individual row was not fetched directly in this run.

This records byte identity with the known dump. It does not authenticate where the user-provided attachment originated, prove legal ownership, or authorize redistribution. The ROM remains outside this repository.
