# Emulator-First Fast Lane — universal policy

**Goal:** Get a small, reversible *test* ROM/patch into a real emulator as early as it can be built safely. Do not wait for full translation, story/event reverse engineering, all glyphs, or G2–G5 release approval.

This is the **default** route when the user asks to translate a game or continue a project. The full-depth research process is on-demand only for a blocker that affects the specific smoke candidate.

## Three milestones, not dozens of prerequisites

| Milestone | Minimum task | Completion evidence |
| --- | --- | --- |
| **A. Identity + reachable string** | Verify clean ROM once (G0); choose **one known visible, isolated string** from an already confirmed table; identify codec and selected file ID | ROM hash, original text ID, verified source encoding, candidate bank and expected screen |
| **B. Safe smoke candidate** | Change just **one to five strings**, starting with a reversible ASCII or known-supported-character substitution if Thai glyphs are not yet supported; preserve control tokens, record count, decompression correctness and file/section references | candidate ROM or BPS **only if it was actually built**, hash and diff, build log, unchanged source hash, rollback; else a precise blocker |
| **C. Real emulator feedback** | Ask the user to launch the candidate in an appropriate emulator as soon as B is proven; compare original and candidate screen, boot/menu/save. Then trial Thai font and representative vowel/tone words | build-specific screenshot/log, PASS/FAIL observations; G3/G4 stay PENDING without actual run |

**A smoke candidate is NOT a release.** It may have no Thai glyphs yet. A reversible English test is useful to validate reinjection, but it must not be called a Thai translation patch. For a Thai micro-test, use an encoded font mapping proven for this game; do not assume UTF-16 codepoints render Thai.

## Prohibited artificial blockers

- Do NOT demand that *all* story events/overlays/ARM functions be mapped before testing **an independent confirmed menu text table**.
- Do NOT wait for 50%/70% translation draft coverage to produce a smoke candidate.
- Do NOT keep translating more batches when the user specifically requests a playable test and injection has not yet been proven.
- Do NOT require a full ARM disassembler if the selected change path doesn't touch or depend on ARM code.
- Do NOT wait for complete G2/G3/G4/G5 **release** gates to invite an early emulator smoke-test; distinguish `SMOKE_READY` (built and statically validated) from `VERIFIED_IN_EMULATOR`.
- Do NOT keep producing multiple pages of analysis when one practical next experiment can determine a build path.

## Hard safety boundary: no unsafe shortcut

1. Never modify the source ROM; work on a separate candidate with verified source revision/hash.
2. Where a ROM's metadata and FAT payloads are interleaved, **do not use a suffix-relocation repacker**. Prefer a carefully validated same-offset/same-size replacement (no FAT or header movement), or develop the minimal necessary game-specific repack logic.
3. For a compressed resource, validate **read → edit → serialize → compress → decompress → parse**; preserve all protected bytes. If new compressed length differs, do not blindly overwrite adjacent data or assume trailing padding is safe. Prove the chosen size/padding/loader assumption on a disposable fixture and then on an isolated candidate.
4. Inspect **only the dependencies of the target candidate**. If no safe injection route is established, report the single blocking invariant and the shortest test to resolve it. Do not fake a candidate or mark G1 PASS.
5. Apply BPS only to exact clean ROM. Never overwrite a known-good build. Record patch hash, changed byte ranges and revert path.
6. No emulator availability => `SMOKE_READY / EMULATOR_NOT_RUN` if a candidate exists. Never say `EMULATOR PASS` without evidence.
7. Existing G0–G5 gates remain in place for QA/release. Smoke-stage progress is tracked **separately** and never upgrades global release gates automatically.

## Escalation ladder (stop at the first safe working level)

1. **No code changes:** a confirmed message table + codec, fixed-size in-place replacement, preserve metadata.
2. **Narrow metadata update:** adjust one selected file's FAT end only when proven the loader supports it, **without moving** other file starts, metadata or overlaps.
3. **Dedicated relocator:** only if 1/2 cannot work; map exact section and pointer constraints rather than the entire game.
4. **ARM/code debugger/disassembler:** only when required for this target's reader/renderer or for custom font support.
5. Unrelated event archives and full-game completion **must not block** a menu smoke test.

## Token discipline

Read root `AGENTS.md`, active `project_profile.json`, `docs/NEXT_TASK.md`, and **only** target-bank sources. Run scripts over local data, not AI over entire dumps. Show only `Build attempt | Changed | Test artifact | Emulator status | One blocker | Next action` with minimal details. Continue with one concrete candidate experiment per iteration. If no candidate yet, explicitly say **NOT BUILT**.

## Codex-ready chat request

> ใช้โหมด Emulator-First ของคู่มือ V3.2 ทำโปรเจกต์เดิมต่อ เป้าหมายอันดับแรกคือสร้างแพตช์ทดลอง 1–5 ข้อความจากตารางข้อความที่พิสูจน์แล้ว หยุดขยายคำแปลชั่วคราว ไม่ต้องรอการวิเคราะห์ทุก event/ARM function ตรวจ ROM และสร้าง candidate แบบไม่ย้าย section หรือเขียนทับ ROM เมื่อ build ได้ให้ทดสอบ/ส่ง BPS กับพาธ ROM ที่ตรงและขอภาพจาก Emulator ถ้ายังสร้างไม่ได้ให้ระบุ invariant ที่ติดเพียงข้อเดียว แล้วแก้จุดนั้น ห้ามรายงานว่าทดสอบ Emulator ผ่านโดยไม่มีหลักฐาน
