"""Parser and serializer for MPDS count/offset/UTF-16LE text tables."""

from __future__ import annotations

from dataclasses import dataclass
import struct


class TableFormatError(ValueError):
    """Raised when a text table violates the confirmed binary layout."""


@dataclass(frozen=True)
class TextTable:
    strings: tuple[str, ...]
    raw: bytes


def parse_table(data: bytes, *, max_rows: int = 100_000) -> TextTable:
    if len(data) < 4:
        raise TableFormatError("table is shorter than the row-count field")
    count = struct.unpack_from("<I", data, 0)[0]
    if count > max_rows:
        raise TableFormatError(f"row count {count} exceeds limit {max_rows}")
    table_end = 4 + 4 * count
    if table_end > len(data):
        raise TableFormatError(
            f"offset table ends at 0x{table_end:X}, beyond data size 0x{len(data):X}"
        )

    offsets = struct.unpack_from(f"<{count}I", data, 4) if count else ()
    strings: list[str] = []
    for row_id, offset in enumerate(offsets):
        if offset < table_end:
            raise TableFormatError(
                f"row {row_id} offset 0x{offset:X} overlaps count/offset table ending at 0x{table_end:X}"
            )
        if offset & 1:
            raise TableFormatError(f"row {row_id} has odd UTF-16LE offset 0x{offset:X}")
        if offset + 2 > len(data):
            raise TableFormatError(f"row {row_id} offset 0x{offset:X} is out of bounds")

        end = offset
        while end + 2 <= len(data) and data[end : end + 2] != b"\x00\x00":
            end += 2
        if end + 2 > len(data):
            raise TableFormatError(
                f"row {row_id} at 0x{offset:X} has no UTF-16LE null terminator"
            )
        try:
            value = data[offset:end].decode("utf-16le", errors="strict")
        except UnicodeDecodeError as exc:
            raise TableFormatError(
                f"row {row_id} at 0x{offset:X} has malformed UTF-16LE: {exc}"
            ) from exc
        strings.append(value)
    return TextTable(tuple(strings), bytes(data))


def serialize_table(table: TextTable, strings: tuple[str, ...] | list[str] | None = None) -> bytes:
    values = table.strings if strings is None else tuple(strings)
    if values == table.strings:
        return table.raw
    if len(values) > 0xFFFFFFFF:
        raise TableFormatError("row count exceeds uint32")
    count = len(values)
    payload = bytearray()
    offsets: list[int] = []
    table_end = 4 + 4 * count
    for row_id, value in enumerate(values):
        if "\x00" in value:
            raise TableFormatError(f"row {row_id} contains an embedded NUL")
        try:
            encoded = value.encode("utf-16le", errors="strict")
        except UnicodeEncodeError as exc:
            raise TableFormatError(f"row {row_id} cannot be encoded as UTF-16LE: {exc}") from exc
        offset = table_end + len(payload)
        if offset > 0xFFFFFFFF:
            raise TableFormatError(f"row {row_id} offset exceeds uint32")
        offsets.append(offset)
        payload.extend(encoded)
        payload.extend(b"\x00\x00")
    header = struct.pack("<I", count)
    if offsets:
        header += struct.pack(f"<{count}I", *offsets)
    return header + payload
