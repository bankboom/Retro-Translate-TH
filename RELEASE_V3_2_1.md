# AI Retro Game Translation Framework V3.2.1 — Offline ARM Fallback

Patch release for all projects: adds offline standard-library ARM/Thumb instruction-pattern candidate scanner, capability detection, safe no-network Codex workflow, tests and Thai documentation. Does not require a BAT installer.

Fixes workflow blocker where a missing ARM disassembler stopped safe, independent translation analysis. **Not a full disassembler or universal game engine**, and does not determine event record boundaries, pointers, or renderer automatically.

No previous game data, ROMs or patches included. Does not change gate states on its own.
