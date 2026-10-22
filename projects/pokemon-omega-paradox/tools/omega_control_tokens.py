#!/usr/bin/env python3
"""Tokenize plain-text CSV renderings of Omega/NDS control sequences.

Escaped \xF000 followed by one native opcode codepoint and any \xNNNN
operand units forms ONE token. Unlike earlier heuristics, do not assume that
the last operand is always \x0000: e.g. \xF000븉\x0001\x0001 is valid.
This module is for static translation QA, NOT a ROM encoder/serializer.
"""
from __future__ import annotations
import re

# The CSV exporter writes non-ASCII opcode code units as the literal codepoint
# and operands as backslash-x plus four hex digits.
CODE = re.compile(r"\\xF000[^\\](?:\\x[0-9A-Fa-f]{4})*|\\x(?:FFFE|FFFF)", re.S)


def tokens(message: str) -> tuple[str, ...]:
    return tuple(m.group(0) for m in CODE.finditer(message or ""))


def visible_segments(message: str) -> list[str]:
    return CODE.split(message or "")


def max_visible_segment(message: str) -> int:
    # Count Unicode codepoints, not visible pixels. At runtime measure glyphs!
    return max((len(s) for s in visible_segments(message)), default=0)


def equal_tokens(source: str, candidate: str) -> bool:
    return tokens(source) == tokens(candidate)


def explain_difference(source: str, candidate: str) -> dict:
    return {
        "same": equal_tokens(source, candidate),
        "source": tokens(source),
        "candidate": tokens(candidate),
        "source_visible_segments": len(visible_segments(source)),
        "candidate_visible_segments": len(visible_segments(candidate)),
    }
