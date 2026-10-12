# Game translation — 6 phases (Emulator-First + Context QA)

Project / ROM revision: PENDING G0 identity confirmation. Source ROM is immutable.
See `docs/SIX_PHASE_CONTEXT_QA_TH.md`, `docs/EMULATOR_FIRST_TH.md` and `docs/QUALITY_GATES.md`.
Use this checklist as milestones; **G0–G5 are separate release quality gates**, not more phases.

## Phase 1 — Safe micro-patch (1–5 strings)
- [ ] Confirm exact ROM hash, platform and revision (G0)
- [ ] Identify one actually reachable string/bank, encoding, tokens and safe patch route
- [ ] For Thai candidate, review **only** test strings in context; if ASCII injector smoke, label as technical-only
- [ ] Build reversible ROM candidate / BPS using isolated output, compare binary scope and rollback; if not safe, note one concrete blocker
- [ ] Request immediate emulator test; do not wait for all event/ARM data to be understood

## Phase 2 — Emulator and Thai font
- [ ] Record actual emulator version, build ID, screen/scene evidence for boot/menu
- [ ] Test Thai consonants, upper/lower vowels, tone marks, wrapping, save/load
- [ ] Compare source/translation against scene/speaker; revise IDs that fail context QA

## Phase 3 — Reviewed translation and patch: 50% of verified scope
- [ ] For changed rows check meaning, real context, Thai, terminology, continuity, control codes and UI constraints
- [ ] Count DRAFT / NEEDS_CONTEXT / REVIEWED / INJECTED / IN_GAME_VERIFIED separately
- [ ] Build a safe versioned patch and test affected scenes in emulator

## Phase 4 — Reviewed translation and patch: 70% of verified scope
- [ ] Verify dialogue/story sequence and character voices as new context becomes available
- [ ] Retest changed scenes plus affected existing scenes; maintain glossary and regression baseline

## Phase 5 — Reviewed translation and patch: 100% of verified scope
- [ ] Review full **mapped** scope; flag any unmapped archives/banks so never claim whole-game coverage without proof
- [ ] Confirm tokens, numerical meaning and consistency across scenes; build/test 100% candidate

## Phase 6 — Final QA and release
- [ ] Recheck representative in-game translation meaning, appearance, scene context, boot/gameplay/save/load
- [ ] Verify G0–G5 evidence, patch checksum, apply from exact clean ROM, rollback
- [ ] Publish patch only (not copyrighted ROM) after actual tests and human sign-off

## Always: six checks per reviewed row
Meaning / Speaker+Scene / Natural Thai / Glossary / Continuity / Control codes+layout. Missing credible context => NEEDS_CONTEXT, not REVIEWED. An ASCII smoke test does not pass language QA.
