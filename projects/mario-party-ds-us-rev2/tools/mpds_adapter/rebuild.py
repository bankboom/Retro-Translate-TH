"""Conservative NitroFS file replacement for synthetic/validated NDS images.

This module is deliberately separate from the read-only adapter commands. It
returns a new byte string and never opens or writes a ROM path. It refuses
images whose known NDS metadata is not wholly before the FAT file payloads.
"""

from __future__ import annotations

import struct

from .nds import NDSFormatError, parse_header, parse_nitrofs, parse_overlay_tables


class RebuildError(ValueError):
    """Raised when a safe in-memory NitroFS rebuild cannot be established."""


def _crc16_header(data: bytes) -> int:
    """Nintendo DS header CRC16 (CRC-16/IBM over bytes 0x000..0x15D)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc & 0xFFFF


def _align4(value: int) -> int:
    return (value + 3) & ~3


def replace_nitro_file(data: bytes, file_id: int, payload: bytes) -> bytes:
    """Replace one FAT file in a new image, relocating later files and FAT.

    Opaque gaps between FAT ranges and the trailing suffix are copied verbatim.
    Known NDS sections and overlay tables must be entirely before the first FAT
    file. Inputs with overlapping FAT ranges or out-of-range metadata are
    rejected instead of guessed at. The input object is never mutated.
    """
    if not isinstance(data, bytes) or not isinstance(payload, bytes):
        raise TypeError("data and payload must be bytes")
    try:
        header = parse_header(data)
        files = parse_nitrofs(data)
        parse_overlay_tables(data)
    except NDSFormatError as exc:
        raise RebuildError(str(exc)) from exc

    selected = next((item for item in files if item.file_id == file_id), None)
    if selected is None:
        raise RebuildError(f"FAT file ID {file_id} does not exist")
    if not files:
        raise RebuildError("NitroFS has no FAT file entries")
    if data[0x12] != 0:
        raise RebuildError("DSi-enhanced or nonstandard unit-code images are unsupported")

    ordered = sorted(files, key=lambda item: (item.start, item.end, item.file_id))
    first_start = ordered[0].start
    previous_end = first_start
    for item in ordered:
        if item.start < previous_end:
            raise RebuildError(f"FAT file ranges overlap at file ID {item.file_id}")
        if item.end > item.start:
            previous_end = item.end

    metadata_ranges = list(header.sections.values())
    for cpu, offset_at, size_at in (("ARM9", 0x50, 0x54), ("ARM7", 0x58, 0x5C)):
        offset, size = struct.unpack_from("<II", data, offset_at)
        if offset == 0 and size == 0:
            continue
        if not size or offset < 0x200 or offset > len(data) or size > len(data) - offset:
            raise RebuildError(f"{cpu} overlay table is outside ROM bounds")
        metadata_ranges.append((offset, size))
    banner_offset = struct.unpack_from("<I", data, 0x68)[0]
    if banner_offset:
        # Reserve the largest standard DS banner size to avoid moving through
        # a banner section without having to interpret its version first.
        banner_size = 0x3000
        if banner_offset < 0x200 or banner_offset > len(data) or banner_size > len(data) - banner_offset:
            raise RebuildError("banner metadata is outside ROM bounds")
        metadata_ranges.append((banner_offset, banner_size))
    if len(data) >= 0x168:
        debug_offset, debug_size = struct.unpack_from("<II", data, 0x160)
        if debug_offset or debug_size:
            if debug_offset < 0x200 or debug_offset > len(data) or debug_size > len(data) - debug_offset:
                raise RebuildError("debug ROM section is outside ROM bounds")
            metadata_ranges.append((debug_offset, debug_size))
    if any(size and offset + size > first_start for offset, size in metadata_ranges):
        raise RebuildError("known NDS metadata overlaps or follows the first FAT file")

    replacements = {file_id: payload}
    rebuilt = bytearray(data[:first_start])
    relocated: dict[int, tuple[int, int]] = {}
    cursor = first_start

    for item in ordered:
        if item.start < cursor:
            raise RebuildError(f"FAT file ID {item.file_id} overlaps a preceding file")
        rebuilt.extend(data[cursor:item.start])
        cursor = item.start
        file_payload = replacements.get(item.file_id, data[item.start:item.end])
        if file_payload:
            aligned = _align4(len(rebuilt))
            rebuilt.extend(b"\x00" * (aligned - len(rebuilt)))
        start = len(rebuilt)
        rebuilt.extend(file_payload)
        relocated[item.file_id] = (start, len(rebuilt))
        cursor = item.end

    rebuilt.extend(data[cursor:])
    if len(rebuilt) > 0xFFFFFFFF:
        raise RebuildError("rebuilt image exceeds 32-bit NDS header size")

    fat_offset, _fat_size = header.sections["fat"]
    for item in files:
        start, end = relocated[item.file_id]
        struct.pack_into("<II", rebuilt, fat_offset + item.file_id * 8, start, end)

    # Keep the ROM size field and header checksum consistent with the new image.
    struct.pack_into("<I", rebuilt, 0x80, len(rebuilt))
    struct.pack_into("<H", rebuilt, 0x15E, _crc16_header(rebuilt[:0x15E]))
    return bytes(rebuilt)
