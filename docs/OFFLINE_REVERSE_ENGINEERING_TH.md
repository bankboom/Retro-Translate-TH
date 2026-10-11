# V3.2.1 — Offline tool fallback for all game projects

This is a **shared framework policy**, not a Mario Party DS or Yu-Gi-Oh! dependency.

## When ARM disassembler is missing
1. Run `python tools/portable_code_probe.py capabilities`. No internet/install required.
2. Continue independent verified work: ROM header/container inventory, decompression, text extraction, table round-trip, contextual translation QA.
3. Only if ISA (ARM or Thumb), decoded code bytes, **actual loaded RAM base** and exact CODE region are independently verified, run a bounded, read-only candidate scan:

```bash
python tools/portable_code_probe.py scan --input /private/confirmed_code.bin --mode arm --base 0x02000000 --start 0x0 --end 0x1000 --max-results 40
```

Numbers here are examples, **not established values for any real ROM**. `--start`/`--end` are decoded-image offsets; `--base` is RAM address at image offset zero. Don't scan unknown event data as code or substitute a ROM file offset for RAM base.

Supported subset: ARM branches/PC-relative word literal loads/ADR; Thumb conditional/unconditional branches, BL, literal loads/ADR. This is **not** a full disassembler. Pattern matches may be data; treat every match as `CANDIDATE_ONLY`. No function/call graph, xref, event-record boundary, injection location or safe ROM-relocation inference. Use independently validated debugger traces/full disassembly when available.

For other architectures, select/build a separate architecture adapter; never decode MIPS/6502/etc. as ARM. The framework can remain universal in workflow without claiming universal automatic reverse engineering.

## Mario Party DS USA Rev 2 checkpoint
Already verified in its project: G0 identity PASS, 35 text tables / 2,672 rows, 107 overlay decompressions. `data/ohanashi_event_data.bin` has 102 plausible aligned offsets but **unconfirmed record grammar**. Don't transfer Yu-Gi-Oh TraceKit. Preserve G1–G5 PENDING; no ROM patch without more evidence. The portable probe alone cannot clear the blocker of *verifying* event reader semantics. If no confirmed CODE range is available, report that specific blocker and continue data-only work.

Keep responses compact: `Changed | Tests | Gates | Blocker | Next`. Never publish game ROM/assets in Git.
