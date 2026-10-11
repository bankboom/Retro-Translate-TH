#!/usr/bin/env python3
"""Offline read-only ARM/Thumb instruction-pattern candidate scanner.

This is NOT a full disassembler. No code/data partition inference, event grammar
inference, xref proof, pointer modification, or ROM write support.
"""
from __future__ import annotations
import argparse
import json
import shutil
import struct
from pathlib import Path

SUPPORTED = ("arm", "thumb")


def availability():
    try:
        import capstone  # optional, informational only
        cap = True
    except ImportError:
        cap = False
    return {
        "capstone_installed": cap,
        "llvm_objdump_found": shutil.which("llvm-objdump") is not None,
        "arm_none_eabi_objdump_found": shutil.which("arm-none-eabi-objdump") is not None,
        "portable_arm_thumb_subset": True,
        "requires_network": False,
    }


def sign_extend(n, bits):
    v = 1 << (bits - 1)
    return (n ^ v) - v


def arm_decode(data: bytes, offset: int, base: int):
    word = struct.unpack_from("<I", data, offset)[0]
    pc = base + offset + 8
    cond = word >> 28
    if (word & 0x0E000000) == 0x0A000000:
        rel = sign_extend(word & 0xFFFFFF, 24) << 2
        if cond == 15:
            return "blx_immediate", (pc + rel + ((word >> 24 & 1) << 1)) & 0xFFFFFFFF
        return ("bl" if (word & 0x01000000) else "b"), (pc + rel) & 0xFFFFFFFF
    if cond != 15 and (word & 0x0F7F0000) == 0x051F0000 and not (word & 0x00400000):
        disp = word & 0xFFF
        addr = pc + (disp if word & 0x00800000 else -disp)
        if base <= addr <= base + len(data) - 4 and (addr - base) % 4 == 0:
            return "ldr_pc_literal", struct.unpack_from("<I", data, addr - base)[0]
        return "ldr_pc_literal_outside_image", addr & 0xFFFFFFFF
    if cond != 15 and (word & 0x0FFF0000) in (0x028F0000, 0x024F0000):
        rotate = ((word >> 8) & 15) * 2
        imm = word & 255
        value = ((imm >> rotate) | (imm << (32 - rotate))) & 0xFFFFFFFF if rotate else imm
        step = 1 if (word & 0x0FFF0000) == 0x028F0000 else -1
        return "adr_pc", (pc + value * step) & 0xFFFFFFFF
    return None


def thumb_decode(data: bytes, offset: int, base: int):
    hw = struct.unpack_from("<H", data, offset)[0]
    pc = base + offset + 4
    if (hw & 0xF800) == 0xE000:
        return "b", (pc + (sign_extend(hw & 0x7FF, 11) << 1)) & 0xFFFFFFFF, 2
    if (hw & 0xF000) == 0xD000 and (hw & 0x0F00) < 0x0E00:
        return "b_cond", (pc + (sign_extend(hw & 0xFF, 8) << 1)) & 0xFFFFFFFF, 2
    if (hw & 0xF800) == 0x4800:
        addr = (pc & ~3) + ((hw & 255) << 2)
        if base <= addr <= base + len(data) - 4 and (addr - base) % 4 == 0:
            return "ldr_pc_literal", struct.unpack_from("<I", data, addr - base)[0], 2
        return "ldr_pc_literal_outside_image", addr & 0xFFFFFFFF, 2
    if (hw & 0xF800) == 0xA000:
        return "adr_pc", ((pc & ~3) + ((hw & 255) << 2)) & 0xFFFFFFFF, 2
    if (hw & 0xF800) == 0xF000 and offset + 4 <= len(data):
        hw2 = struct.unpack_from("<H", data, offset + 2)[0]
        if (hw2 & 0xF800) == 0xF800:
            return "bl", (pc + (sign_extend(hw & 0x7FF, 11) << 12)
                          + ((hw2 & 0x7FF) << 1)) & 0xFFFFFFFF, 4
    return None


def scan(data: bytes, *, mode: str, base: int, start: int, end: int,
         match_address: int | None = None, max_results: int = 200):
    if mode not in SUPPORTED:
        raise ValueError("unsupported ISA: use an architecture-specific adapter")
    unit = 4 if mode == "arm" else 2
    if start < 0 or end > len(data) or start >= end or start % unit or end % unit:
        raise ValueError("code region must be nonempty, aligned, within decoded image")
    if not 0 <= base <= 0xFFFFFFFF or base + len(data) > 0x100000000:
        raise ValueError("RAM base/image address out of 32-bit range")
    if max_results < 1 or max_results > 10000:
        raise ValueError("max_results must be 1..10000")
    records = []
    i = start
    while i + unit <= end:
        decoded = arm_decode(data, i, base) if mode == "arm" else thumb_decode(data, i, base)
        advance = unit
        if decoded:
            kind, target = decoded[:2]
            if len(decoded) > 2:
                advance = decoded[2]
                if i + advance > end:
                    break
            if match_address is None or match_address == target:
                records.append({
                    "image_offset": f"0x{i:X}",
                    "instruction_address": f"0x{base + i:08X}",
                    "candidate_kind": kind,
                    "candidate_target": f"0x{target:08X}",
                    "proof": "instruction-pattern-only",
                    "confidence": "CANDIDATE"
                })
                if len(records) >= max_results:
                    break
        i += advance
    return records


def int0(value):
    return int(value, 0)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("capabilities")
    s = sub.add_parser("scan", help="scan independently CONFIRMED decoded CODE region")
    s.add_argument("--input", type=Path, required=True)
    s.add_argument("--mode", choices=SUPPORTED, required=True)
    s.add_argument("--base", type=int0, required=True, help="RAM address of input offset zero")
    s.add_argument("--start", type=int0, required=True, help="verified CODE start offset")
    s.add_argument("--end", type=int0, help="verified CODE end exclusive (default EOF)")
    s.add_argument("--match-address", type=int0)
    s.add_argument("--max-results", type=int, default=200)
    args = p.parse_args(argv)
    try:
        if args.command == "capabilities":
            print(json.dumps(availability(), indent=2))
            return
        data = args.input.read_bytes()
        end = args.end if args.end is not None else len(data)
        results = scan(data, mode=args.mode, base=args.base, start=args.start,
                       end=end, match_address=args.match_address,
                       max_results=args.max_results)
        print(json.dumps({
            "tool": "portable_code_probe", "mode": args.mode,
            "evidence_status": "CANDIDATE_ONLY",
            "scope": {"ram_base": f"0x{args.base:08X}", "start": f"0x{args.start:X}",
                      "end": f"0x{end:X}", "input": str(args.input)},
            "notice": "Only verified CODE ranges; candidates are not proven xrefs, "
                      "record boundaries or safe patch locations.",
            "candidates": results,
        }, ensure_ascii=False, indent=2))
    except (OSError, ValueError, struct.error) as error:
        p.exit(2, f"ERROR: {error}\n")


if __name__ == "__main__":
    main()
