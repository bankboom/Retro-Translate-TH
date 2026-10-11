"""Bounds-checked NDS header and NitroFS reader."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct


class NDSFormatError(ValueError):
    """Raised when an NDS header or NitroFS table is malformed."""


@dataclass(frozen=True)
class NDSHeader:
    title: str
    game_code: str
    maker_code: str
    revision: int
    sections: dict[str, tuple[int, int]]


@dataclass(frozen=True)
class NitroFile:
    file_id: int
    path: str
    start: int
    end: int
    size: int
    sha256: str


@dataclass(frozen=True)
class OverlayEntry:
    cpu: str
    overlay_id: int
    ram_address: int
    ram_size: int
    bss_size: int
    file_id: int
    compressed: bool
    compressed_size: int


def _section(data: bytes, label: str, offset_at: int, size_at: int) -> tuple[int, int]:
    offset = struct.unpack_from("<I", data, offset_at)[0]
    size = struct.unpack_from("<I", data, size_at)[0]
    if size and (offset < 0x200 or offset > len(data) or size > len(data) - offset):
        raise NDSFormatError(
            f"{label} section [0x{offset:X}, 0x{offset + size:X}) is outside ROM bounds"
        )
    return offset, size


def parse_header(data: bytes) -> NDSHeader:
    if len(data) < 0x160:
        raise NDSFormatError(f"ROM header is truncated: {len(data)} bytes")
    title = data[0:12].split(b"\x00", 1)[0].decode("ascii", errors="replace").strip()
    game_code = data[0x0C:0x10].decode("ascii", errors="replace")
    maker_code = data[0x10:0x12].decode("ascii", errors="replace")
    sections = {
        "arm9": _section(data, "ARM9", 0x20, 0x2C),
        "arm7": _section(data, "ARM7", 0x30, 0x3C),
        "fnt": _section(data, "FNT", 0x40, 0x44),
        "fat": _section(data, "FAT", 0x48, 0x4C),
    }
    for label, (offset, size) in sections.items():
        if size and offset < 0x200:
            raise NDSFormatError(f"{label} section starts inside the NDS header")
    return NDSHeader(title, game_code, maker_code, data[0x1E], sections)


def parse_nitrofs(data: bytes) -> list[NitroFile]:
    header = parse_header(data)
    fnt_offset, fnt_size = header.sections["fnt"]
    fat_offset, fat_size = header.sections["fat"]
    if fnt_size < 8:
        raise NDSFormatError("FNT is shorter than its root directory record")
    if fat_size % 8:
        raise NDSFormatError(f"FAT size {fat_size} is not a multiple of 8")
    fnt = data[fnt_offset : fnt_offset + fnt_size]
    directory_count = struct.unpack_from("<H", fnt, 6)[0]
    if directory_count < 1 or directory_count * 8 > len(fnt):
        raise NDSFormatError(f"invalid FNT directory count {directory_count}")

    directories = [struct.unpack_from("<IHH", fnt, i * 8) for i in range(directory_count)]
    named: dict[int, str] = {}
    visited: set[int] = set()

    def walk(directory_index: int, parent: str) -> None:
        if directory_index < 0 or directory_index >= directory_count:
            raise NDSFormatError(f"FNT references invalid directory index {directory_index}")
        if directory_index in visited:
            raise NDSFormatError(f"FNT contains a directory cycle at index {directory_index}")
        visited.add(directory_index)
        entry_offset, first_file_id, _parent_or_count = directories[directory_index]
        position = entry_offset
        file_id = first_file_id
        while True:
            if position >= len(fnt):
                raise NDSFormatError(f"FNT directory {directory_index} has no terminator")
            descriptor = fnt[position]
            position += 1
            if descriptor == 0:
                break
            is_directory = bool(descriptor & 0x80)
            name_length = descriptor & 0x7F
            if name_length == 0 or position + name_length > len(fnt):
                raise NDSFormatError(f"invalid name length in FNT directory {directory_index}")
            try:
                name = fnt[position : position + name_length].decode("utf-8", errors="strict")
            except UnicodeDecodeError as exc:
                raise NDSFormatError(f"invalid UTF-8 filename in FNT: {exc}") from exc
            position += name_length
            if not name or name in (".", "..") or "/" in name or "\\" in name:
                raise NDSFormatError(f"unsafe FNT name {name!r}")
            path = f"{parent}/{name}" if parent else name
            if is_directory:
                if position + 2 > len(fnt):
                    raise NDSFormatError("truncated FNT subdirectory ID")
                directory_id = struct.unpack_from("<H", fnt, position)[0]
                position += 2
                if (directory_id & 0xF000) != 0xF000:
                    raise NDSFormatError(f"invalid FNT directory ID 0x{directory_id:04X}")
                walk(directory_id & 0x0FFF, path)
            else:
                if file_id in named:
                    raise NDSFormatError(f"duplicate FNT file ID {file_id}")
                named[file_id] = path
                file_id += 1

    walk(0, "")
    fat_count = fat_size // 8
    files: list[NitroFile] = []
    for file_id in range(fat_count):
        start, end = struct.unpack_from("<II", data, fat_offset + file_id * 8)
        if start > end or end > len(data):
            raise NDSFormatError(
                f"FAT file {file_id} range [0x{start:X}, 0x{end:X}) is invalid"
            )
        path = named.get(file_id, f"__unnamed_fat/{file_id:04d}")
        payload = data[start:end]
        files.append(
            NitroFile(file_id, path, start, end, end - start, hashlib.sha256(payload).hexdigest())
        )
    unknown_ids = sorted(set(named) - set(range(fat_count)))
    if unknown_ids:
        raise NDSFormatError(f"FNT names file IDs outside FAT: {unknown_ids[:8]}")
    return files


def parse_overlay_tables(data: bytes) -> list[OverlayEntry]:
    """Read ARM9/ARM7 overlay descriptors and validate their FAT references."""
    header = parse_header(data)
    fat_size = header.sections["fat"][1]
    if fat_size % 8:
        raise NDSFormatError(f"FAT size {fat_size} is not a multiple of 8")
    fat_count = fat_size // 8
    overlays: list[OverlayEntry] = []
    for cpu, offset_at, size_at in (("arm9", 0x50, 0x54), ("arm7", 0x58, 0x5C)):
        offset, size = struct.unpack_from("<II", data, offset_at)
        if offset == 0 and size == 0:
            continue
        if size == 0 or size % 32:
            raise NDSFormatError(f"{cpu.upper()} overlay table size {size} is not a nonzero multiple of 32")
        if offset < 0x200 or offset > len(data) or size > len(data) - offset:
            raise NDSFormatError(f"{cpu.upper()} overlay table is outside ROM bounds")
        for position in range(offset, offset + size, 32):
            overlay_id, ram_address, ram_size, bss_size, _static_start, _static_end, file_id, flags = struct.unpack_from("<8I", data, position)
            if file_id >= fat_count:
                raise NDSFormatError(f"{cpu.upper()} overlay {overlay_id} references FAT file {file_id}, but FAT has {fat_count} entries")
            overlays.append(
                OverlayEntry(
                    cpu=cpu,
                    overlay_id=overlay_id,
                    ram_address=ram_address,
                    ram_size=ram_size,
                    bss_size=bss_size,
                    file_id=file_id,
                    compressed=bool(flags & 0x01000000),
                    compressed_size=flags & 0x00FFFFFF,
                )
            )
    return overlays
