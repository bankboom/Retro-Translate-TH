#!/usr/bin/env python3
"""Read, apply, and create VERIFIED BPS1 patches without overwriting clean ROMs.

Intended as the independent final integrity layer for Omega P4.6 and newer
game-specific rebuilt targets. This does NOT modify NARC/MSG or invent native
Thai glyphs. It cannot create translated text from an untranslated ROM.

Commands:
  inspect --bps x.bps [--clean clean.nds]
  apply --clean clean.nds --bps x.bps --out private_patched.nds
  create --clean clean.nds --target PRIVATE_REBUILT.nds --out patch.bps
         (verifies the new BPS by applying it to clean ROM in a temp file)

Read only on --clean and --target; all outputs exclusive new files.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mmap
import os
import tempfile
import zlib
from pathlib import Path

MAX_TARGET = 512 * 1024 * 1024
BLOCK = 128 * 1024
MAX_LITERAL_BUFFER = 1024 * 1024


class BPSError(ValueError):
    pass


def number_encode(number: int) -> bytes:
    if number < 0:
        raise BPSError("NEGATIVE_BPS_NUMBER")
    data = bytearray()
    while True:
        x = number & 0x7f
        number >>= 7
        if number == 0:
            data.append(x | 0x80)
            return bytes(data)
        data.append(x)
        number -= 1


def number_decode(data: bytes, pos: int, end: int) -> tuple[int, int]:
    value = 0
    shift = 1
    for _ in range(12):
        if pos >= end:
            raise BPSError("TRUNCATED_NUMBER")
        byte = data[pos]
        pos += 1
        value += (byte & 0x7f) * shift
        if byte & 0x80:
            return value, pos
        shift <<= 7
        value += shift
    raise BPSError("OVERSIZE_BPS_NUMBER")


def signed_decode(value: int) -> int:
    return -(value >> 1) if value & 1 else value >> 1


def fingerprint(path: Path) -> dict:
    digest = hashlib.sha256()
    crc = 0
    size = 0
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
            crc = zlib.crc32(block, crc)
            size += len(block)
    return {"sha256": digest.hexdigest(), "crc32": crc & 0xffffffff, "bytes": size}


def read_header(data: bytes) -> dict:
    """Parse the complete patch header and validate the full patch CRC."""
    if len(data) < 16 or data[:4] != b"BPS1":
        raise BPSError("NOT_BPS1")
    recorded = int.from_bytes(data[-4:], "little")
    actual = zlib.crc32(data[:-4]) & 0xffffffff
    if actual != recorded:
        raise BPSError("BPS_PATCH_CRC_MISMATCH")
    limit = len(data) - 12
    pos = 4
    src_len, pos = number_decode(data, pos, limit)
    dst_len, pos = number_decode(data, pos, limit)
    meta_len, pos = number_decode(data, pos, limit)
    if pos + meta_len > limit:
        raise BPSError("BPS_METADATA_OVERFLOW")
    pos += meta_len
    if dst_len > MAX_TARGET:
        raise BPSError("TARGET_TOO_LARGE")
    source_crc = int.from_bytes(data[-12:-8], "little")
    target_crc = int.from_bytes(data[-8:-4], "little")
    return {
        "source_bytes": src_len, "target_bytes": dst_len,
        "source_crc32": source_crc, "target_crc32": target_crc,
        "patch_crc32": recorded, "metadata_bytes": meta_len,
        "command_start": pos, "command_end": limit,
    }


def inspect_patch(bps: Path, clean: Path | None = None) -> dict:
    info = read_header(bps.read_bytes())
    info["patch_crc_valid"] = True
    info["target_crc_verified_by_apply"] = False
    if clean is not None:
        current = fingerprint(clean)
        if current["bytes"] != info["source_bytes"]:
            raise BPSError("SOURCE_SIZE_MISMATCH")
        if current["crc32"] != info["source_crc32"]:
            raise BPSError("SOURCE_CRC_MISMATCH")
        info["clean_sha256"] = current["sha256"]
    return info


def _assert_new_output(out: Path, *protected: Path):
    resolved = out.resolve()
    if any(resolved == p.resolve() for p in protected):
        raise BPSError("OUTPUT_MUST_NOT_OVERWRITE_INPUT")
    if out.exists():
        raise BPSError("OUTPUT_ALREADY_EXISTS")
    if not out.parent.is_dir():
        raise BPSError("OUTPUT_DIRECTORY_MISSING")


def apply_patch(clean: Path, bps: Path, out: Path, expected_sha: str | None = None,
                expected_clean_sha: str | None = None) -> dict:
    """Apply all four BPS actions, including overlap-safe TargetCopy.

    Target bytes are staged on disk and only published after final CRC & SHA.
    The original clean ROM is opened read-only and never changed.
    """
    _assert_new_output(out, clean, bps)
    data = bps.read_bytes()
    header = read_header(data)
    original = fingerprint(clean)
    if expected_clean_sha and original["sha256"] != expected_clean_sha.lower():
        raise BPSError("CLEAN_ROM_SHA256_MISMATCH")
    if original["bytes"] != header["source_bytes"]:
        raise BPSError("SOURCE_SIZE_MISMATCH")
    if original["crc32"] != header["source_crc32"]:
        raise BPSError("SOURCE_CRC_MISMATCH")
    pos = header["command_start"]
    limit = header["command_end"]
    dst_len = header["target_bytes"]
    dst_pos = 0
    source_rel = 0
    target_rel = 0
    commands = [0, 0, 0, 0]
    tmp_name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w+b", prefix=".bps-apply-",
                                         dir=out.parent, delete=False) as dst, \
             clean.open("rb") as src:
            tmp_name = dst.name
            while pos < limit:
                value, pos = number_decode(data, pos, limit)
                op = value & 3
                n = (value >> 2) + 1
                if n > dst_len - dst_pos:
                    raise BPSError("TARGET_COMMAND_OVERFLOW")
                commands[op] += 1
                if op == 0:  # SourceRead at current output position.
                    if dst_pos + n > original["bytes"]:
                        raise BPSError("SOURCE_READ_OVERFLOW")
                    src.seek(dst_pos)
                    remaining = n
                    while remaining:
                        x = src.read(min(remaining, BLOCK))
                        if not x:
                            raise BPSError("TRUNCATED_SOURCE")
                        dst.write(x)
                        remaining -= len(x)
                elif op == 1:  # TargetRead literal bytes from patch.
                    if pos + n > limit:
                        raise BPSError("LITERAL_OVERFLOWS_COMMAND_AREA")
                    dst.write(data[pos:pos+n])
                    pos += n
                elif op == 2:  # SourceCopy with signed relative delta.
                    v, pos = number_decode(data, pos, limit)
                    source_rel += signed_decode(v)
                    if source_rel < 0 or source_rel + n > original["bytes"]:
                        raise BPSError("SOURCE_COPY_OOB")
                    src.seek(source_rel)
                    remaining = n
                    while remaining:
                        x = src.read(min(remaining, BLOCK))
                        if not x:
                            raise BPSError("TRUNCATED_SOURCE_COPY")
                        dst.write(x)
                        remaining -= len(x)
                    source_rel += n
                else:  # TargetCopy; copies may overlap newly-written bytes.
                    v, pos = number_decode(data, pos, limit)
                    target_rel += signed_decode(v)
                    if target_rel < 0 or target_rel >= dst_pos:
                        raise BPSError("TARGET_COPY_FUTURE_OR_OOB")
                    remaining = n
                    while remaining:
                        available = dst_pos - target_rel
                        chunk_size = min(remaining, available, BLOCK)
                        dst.seek(target_rel)
                        chunk = dst.read(chunk_size)
                        if len(chunk) != chunk_size:
                            raise BPSError("TARGET_COPY_TRUNCATED")
                        dst.seek(dst_pos)
                        dst.write(chunk)
                        dst_pos += chunk_size
                        target_rel += chunk_size
                        remaining -= chunk_size
                    dst.flush()
                    dst.seek(dst_pos)
                    continue
                dst_pos += n
            if dst_pos != dst_len:
                raise BPSError("TARGET_LENGTH_MISMATCH")
            dst.flush()
            os.fsync(dst.fileno())
        computed = fingerprint(Path(tmp_name))
        if computed["crc32"] != header["target_crc32"]:
            raise BPSError("TARGET_CRC_MISMATCH")
        if expected_sha and computed["sha256"].lower() != expected_sha.lower():
            raise BPSError("TARGET_SHA256_MISMATCH")
        # Exclusive publication. Recheck to avoid overwriting an output created
        # while processing. File content was fully verified before this point.
        _assert_new_output(out, clean, bps)
        os.link(tmp_name, out)
        os.unlink(tmp_name)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
    return {
        "source_sha256": original["sha256"],
        "target_sha256": computed["sha256"],
        "target_crc32": f"{computed['crc32']:08x}",
        "bytes": computed["bytes"],
        "commands_per_action": dict(zip(
            ("SourceRead", "TargetRead", "SourceCopy", "TargetCopy"), commands)),
        "actual_patch_applied": True, "target_checksum_verified": True,
        "output": str(out),
    }


def _action_code(op: int, length: int) -> bytes:
    if length <= 0:
        raise BPSError("EMPTY_ACTION")
    return number_encode(((length - 1) << 2) | op)


def create_patch(clean: Path, target: Path, out: Path,
                 expected_clean_sha: str | None = None,
                 verify_apply: bool = True) -> dict:
    """Create legal BPS1 using aligned SourceRead/TargetRead (no copy ops).

    Optimized for game ROMs that differ only in few NARC ciphertext bytes.
    Dirty blocks scanned at byte level; clean blocks compared in bulk.
    """
    _assert_new_output(out, clean, target)
    source_fp = fingerprint(clean)
    target_fp = fingerprint(target)
    if target_fp["bytes"] > MAX_TARGET:
        raise BPSError("TARGET_TOO_LARGE")
    if expected_clean_sha and source_fp["sha256"] != expected_clean_sha.lower():
        raise BPSError("CLEAN_SHA256_MISMATCH")

    # All content is written to a temporary patch until verified.
    tmp_name = None
    counters = {"SourceRead": 0, "TargetRead": 0}
    written_crc = 0
    def write_chunk(f, data: bytes):
        nonlocal written_crc
        f.write(data)
        written_crc = zlib.crc32(data, written_crc)
    try:
        with tempfile.NamedTemporaryFile(mode="w+b", prefix=".bps-create-",
                                         dir=out.parent, delete=False) as dst, \
             clean.open("rb") as source, target.open("rb") as new:
            tmp_name = dst.name
            write_chunk(dst, b"BPS1")
            write_chunk(dst, number_encode(source_fp["bytes"]))
            write_chunk(dst, number_encode(target_fp["bytes"]))
            write_chunk(dst, number_encode(0))  # no metadata
            pending_kind = None
            same_count = 0
            literals = bytearray()

            def flush():
                nonlocal same_count, pending_kind
                if pending_kind == 0 and same_count:
                    write_chunk(dst, _action_code(0, same_count))
                    counters["SourceRead"] += 1
                elif pending_kind == 1 and literals:
                    write_chunk(dst, _action_code(1, len(literals)))
                    write_chunk(dst, bytes(literals))
                    counters["TargetRead"] += 1
                same_count = 0
                literals.clear()
                pending_kind = None

            def emit(kind, data):
                nonlocal same_count, pending_kind
                if pending_kind is not None and pending_kind != kind:
                    flush()
                pending_kind = kind
                if kind == 0:
                    same_count += int(data)
                else:
                    literals.extend(data)
                    if len(literals) >= MAX_LITERAL_BUFFER:
                        flush()

            # For unequal-length inputs, only aligned original bytes may use
            # SourceRead; target suffix is always a TargetRead.
            remaining = target_fp["bytes"]
            shared = min(source_fp["bytes"], target_fp["bytes"])
            while remaining:
                n = min(remaining, BLOCK)
                new_block = new.read(n)
                if len(new_block) != n:
                    raise BPSError("TARGET_CHANGED_WHILE_READING")
                offset = target_fp["bytes"] - remaining
                common = max(0, min(n, shared - offset))
                old_block = source.read(common) if common else b""
                if len(old_block) != common:
                    raise BPSError("SOURCE_CHANGED_WHILE_READING")
                if common == n and old_block == new_block:
                    emit(0, n)
                else:
                    # Only inspect individual bytes in differing blocks.
                    pos = 0
                    while pos < n:
                        equal = pos < common and new_block[pos] == old_block[pos]
                        j = pos + 1
                        while j < n and (
                            (j < common and new_block[j] == old_block[j]) == equal
                        ):
                            j += 1
                        if equal:
                            emit(0, j - pos)
                        else:
                            emit(1, new_block[pos:j])
                        pos = j
                remaining -= n
            flush()
            write_chunk(dst, source_fp["crc32"].to_bytes(4, "little"))
            write_chunk(dst, target_fp["crc32"].to_bytes(4, "little"))
            dst.write((written_crc & 0xffffffff).to_bytes(4, "little"))
            dst.flush()
            os.fsync(dst.fileno())

        # Validation before publication: BPS parser & CRC.
        patch_info = inspect_patch(Path(tmp_name), clean)
        if patch_info["target_bytes"] != target_fp["bytes"]:
            raise BPSError("CREATED_PATCH_SIZE_INVALID")
        if patch_info["target_crc32"] != target_fp["crc32"]:
            raise BPSError("CREATED_PATCH_TARGET_CRC_INVALID")

        if verify_apply:
            # Verify by actually applying the patch to a scratch ROM, not just
            # trusting the BPS trailer. Never publish scratch ROM.
            with tempfile.TemporaryDirectory(prefix=".bps-verify-",
                                             dir=out.parent) as directory:
                scratch = Path(directory) / "verified_target.nds"
                checked = apply_patch(clean, Path(tmp_name), scratch,
                                      expected_sha=target_fp["sha256"])
                if checked["target_sha256"] != target_fp["sha256"]:
                    raise BPSError("APPLIED_TARGET_SHA_INVALID")
        _assert_new_output(out, clean, target)
        os.link(tmp_name, out)
        os.unlink(tmp_name)
        tmp_name = None
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
    return {
        "bps_sha256": fingerprint(out)["sha256"],
        "source_sha256": source_fp["sha256"],
        "target_sha256": target_fp["sha256"],
        "source_bytes": source_fp["bytes"],
        "target_bytes": target_fp["bytes"],
        "action_counts": counters,
        "actual_apply_verified": verify_apply,
        "source_unchanged": True,
        "out": str(out),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="command", required=True)
    a = subs.add_parser("apply")
    a.add_argument("--clean", required=True, type=Path)
    a.add_argument("--bps", required=True, type=Path)
    a.add_argument("--out", required=True, type=Path)
    a.add_argument("--expected-target-sha256")
    a.add_argument("--expected-clean-sha256")
    b = subs.add_parser("create")
    b.add_argument("--clean", required=True, type=Path)
    b.add_argument("--target", required=True, type=Path)
    b.add_argument("--out", required=True, type=Path)
    b.add_argument("--expected-clean-sha256")
    i = subs.add_parser("inspect")
    i.add_argument("--bps", required=True, type=Path)
    i.add_argument("--clean", type=Path)
    args = p.parse_args()
    if args.command == "apply":
        result = apply_patch(args.clean, args.bps, args.out,
                             args.expected_target_sha256,
                             args.expected_clean_sha256)
    elif args.command == "create":
        result = create_patch(args.clean, args.target, args.out,
                              args.expected_clean_sha256)
    else:
        result = inspect_patch(args.bps, args.clean)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
