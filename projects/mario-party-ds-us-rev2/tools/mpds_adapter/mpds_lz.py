"""MPDS LZ77 container codec.

The first header byte is retained as opaque data. The following three bytes
store the expanded size in little-endian order. Back-references use a 12-bit
distance-minus-one and a 4-bit length-minus-three, emitted big-endian.
"""

from __future__ import annotations

from collections import defaultdict, deque


class LZFormatError(ValueError):
    """Raised for a malformed or unsupported MPDS LZ stream."""


def decompress(data: bytes, *, max_output_size: int = 64 * 1024 * 1024) -> bytes:
    if len(data) < 4:
        raise LZFormatError("container is shorter than the four-byte header")
    expected = int.from_bytes(data[1:4], "little")
    if expected > max_output_size:
        raise LZFormatError(
            f"expanded size {expected} exceeds configured limit {max_output_size}"
        )
    if expected == 0:
        return b""

    source = 4
    output = bytearray()
    while len(output) < expected:
        if source >= len(data):
            raise LZFormatError(f"missing flag byte at input offset 0x{source:X}")
        flags = data[source]
        source += 1
        for bit in range(7, -1, -1):
            if len(output) >= expected:
                break
            if flags & (1 << bit):
                if source + 2 > len(data):
                    raise LZFormatError(
                        f"truncated back-reference at input offset 0x{source:X}"
                    )
                token = (data[source] << 8) | data[source + 1]
                source += 2
                length = (token >> 12) + 3
                distance = (token & 0x0FFF) + 1
                if distance > len(output):
                    raise LZFormatError(
                        f"back-reference distance {distance} exceeds produced bytes {len(output)}"
                    )
                count = min(length, expected - len(output))
                for _ in range(count):
                    output.append(output[-distance])
            else:
                if source >= len(data):
                    raise LZFormatError(
                        f"truncated literal at input offset 0x{source:X}"
                    )
                output.append(data[source])
                source += 1
    return bytes(output)


def compress(data: bytes, *, header_byte: int = 0x10) -> bytes:
    if not 0 <= header_byte <= 0xFF:
        raise ValueError("header_byte must be in range 0..255")
    if len(data) > 0xFFFFFF:
        raise ValueError("expanded data exceeds the 24-bit MPDS size field")
    result = bytearray((header_byte,))
    result.extend(len(data).to_bytes(3, "little"))
    if not data:
        return bytes(result)

    positions: dict[bytes, deque[int]] = defaultdict(deque)
    index = 0

    def add_position(position: int) -> None:
        if position + 3 <= len(data):
            positions[data[position : position + 3]].append(position)

    while index < len(data):
        flag_index = len(result)
        result.append(0)
        flags = 0
        tokens = bytearray()

        for bit in range(7, -1, -1):
            if index >= len(data):
                break
            best_length = 0
            best_distance = 0
            max_length = min(18, len(data) - index)
            if max_length >= 3:
                candidates = positions.get(data[index : index + 3], ())
                for candidate in reversed(candidates):
                    distance = index - candidate
                    if distance > 0x1000:
                        break
                    length = 3
                    while (
                        length < max_length
                        and data[candidate + length] == data[index + length]
                    ):
                        length += 1
                    if length > best_length:
                        best_length = length
                        best_distance = distance
                        if length == max_length:
                            break

            if best_length >= 3:
                flags |= 1 << bit
                token = ((best_length - 3) << 12) | (best_distance - 1)
                tokens.extend(token.to_bytes(2, "big"))
                amount = best_length
            else:
                tokens.append(data[index])
                amount = 1

            for position in range(index, index + amount):
                add_position(position)
            index += amount

        result[flag_index] = flags
        result.extend(tokens)

    return bytes(result)
