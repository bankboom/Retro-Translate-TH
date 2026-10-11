"""Command-line entry points for read-only MPDS ROM/table analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

from .mpds_lz import compress, decompress
from .nds import NDSFormatError, parse_header, parse_nitrofs, parse_overlay_tables
from .text_table import parse_table, serialize_table


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILE = PROJECT_ROOT / "project_profile.json"
TABLE_NAME = re.compile(r"^data/US/mpd_.*_LZ\.bin$", re.IGNORECASE)
TOKEN_PATTERN = re.compile(r"\[[^\]\r\n]+\]")
CSV_FIELDS = [
    "Bank", "ID", "ROM_Offset", "English", "File_Path", "Token_Candidates",
]


def rom_hashes(data: bytes) -> dict[str, str | int]:
    return {
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "crc32": f"{zlib.crc32(data) & 0xFFFFFFFF:08X}",
    }


def _read_rom(path: Path) -> bytes:
    # Explicit rb mode makes the source ROM read-only for every command.
    with path.open("rb") as stream:
        return stream.read()


def inspect(data: bytes, profile_path: Path = DEFAULT_PROFILE) -> dict:
    header = parse_header(data)
    hashes = rom_hashes(data)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    source = profile["source_rom"]
    expected_sha256 = source.get("expected_clean_sha256") or source.get("observed_sha256")
    expected_sha1 = source.get("expected_clean_sha1")
    expected_crc32 = source.get("expected_clean_crc32")
    if hashes["size_bytes"] != source.get("size_bytes"):
        raise ValueError("ROM size does not match the project profile")
    if expected_sha256 and hashes["sha256"].lower() != expected_sha256.lower():
        raise ValueError("ROM SHA-256 does not match the project profile")
    if expected_sha1 and hashes["sha1"].lower() != expected_sha1.lower():
        raise ValueError("ROM SHA-1 does not match the project profile")
    if expected_crc32 and hashes["crc32"].lower() != expected_crc32.lower():
        raise ValueError("ROM CRC32 does not match the project profile")
    if header.game_code != "A8TE":
        raise ValueError(f"unexpected NDS game code {header.game_code!r}")
    if header.revision != 2:
        raise ValueError(f"unexpected NDS revision byte 0x{header.revision:02X}")
    if header.title != "MARIOPARTYDS":
        raise ValueError(f"unexpected NDS title {header.title!r}")
    return {
        "title": header.title,
        "game_code": header.game_code,
        "maker_code": header.maker_code,
        "revision_byte": header.revision,
        "sections": {key: {"offset": value[0], "size": value[1]} for key, value in header.sections.items()},
        "identity_check": "PASS",
        "provenance_note": "Identity/revision match only; upload chain of custody is not authenticated.",
        "hashes": hashes,
    }


def inventory(data: bytes) -> list[dict]:
    files = parse_nitrofs(data)
    overlays_by_file: dict[int, list[dict]] = {}
    for overlay in parse_overlay_tables(data):
        overlays_by_file.setdefault(overlay.file_id, []).append(
            {
                "cpu": overlay.cpu,
                "overlay_id": overlay.overlay_id,
                "compressed": overlay.compressed,
                "compressed_size": overlay.compressed_size,
            }
        )
    return [
        {
            "file_id": item.file_id,
            "path": item.path,
            "rom_offset": item.start,
            "size": item.size,
            "sha256": item.sha256,
            "lz_candidate": item.path.lower().endswith("_lz.bin"),
            "overlays": overlays_by_file.get(item.file_id, []),
        }
        for item in files
    ]


def _bank_for_path(path: str) -> str:
    master = PROJECT_ROOT / "translations" / "master.csv"
    if master.is_file():
        with master.open("r", encoding="utf-8-sig", newline="") as stream:
            matches = {
                row.get("Bank", "").strip()
                for row in csv.DictReader(stream)
                if row.get("File_Path", "").strip() == path and row.get("Bank", "").strip()
            }
        if len(matches) == 1:
            return next(iter(matches))
        if len(matches) > 1:
            raise ValueError(f"master.csv maps {path} to multiple bank IDs")
    return "US_" + Path(path).stem.upper()


def extract_rows(data: bytes) -> list[dict[str, str]]:
    files = parse_nitrofs(data)
    rows: list[dict[str, str]] = []
    for item in files:
        if not TABLE_NAME.match(item.path):
            continue
        packed = data[item.start : item.end]
        expanded = decompress(packed)
        table = parse_table(expanded)
        bank = _bank_for_path(item.path)
        for row_id, english in enumerate(table.strings):
            tokens = TOKEN_PATTERN.findall(english)
            rows.append(
                {
                    "Bank": bank,
                    "ID": str(row_id),
                    "English": english,
                    "ROM_Offset": str(item.start),
                    "File_Path": item.path,
                    "Token_Candidates": " ".join(tokens),
                }
            )
    return rows


def roundtrip(data: bytes) -> dict:
    files = parse_nitrofs(data)
    checks = []
    for item in files:
        if not TABLE_NAME.match(item.path):
            continue
        original = data[item.start : item.end]
        expanded = decompress(original)
        table = parse_table(expanded)
        serialized = serialize_table(table)
        recoded = compress(serialized, header_byte=original[0])
        if serialized != expanded:
            raise ValueError(f"expanded table round-trip differs: {item.path}")
        if decompress(recoded) != expanded:
            raise ValueError(f"compressed round-trip differs: {item.path}")
        checks.append(
            {
                "file_id": item.file_id,
                "path": item.path,
                "rows": len(table.strings),
                "expanded_size": len(expanded),
                "expanded_sha256": hashlib.sha256(expanded).hexdigest(),
                "original_compressed_size": len(original),
                "recompressed_size": len(recoded),
                "expanded_roundtrip": "PASS",
                "compressed_roundtrip": "PASS",
                "compressed_bytes_identical": recoded == original,
            }
        )
    if not checks:
        raise ValueError("no confirmed MPD text tables found")
    return {
        "table_count": len(checks),
        "total_rows": sum(item["rows"] for item in checks),
        "tables": checks,
    }


def _write_new_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def _write_new_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mpds-adapter")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect-rom", "inventory", "extract-tables", "roundtrip"):
        sub = commands.add_parser(name)
        sub.add_argument("rom", type=Path)
        sub.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
        if name == "inventory":
            sub.add_argument("--output", type=Path, required=True)
        elif name == "extract-tables":
            sub.add_argument("--output", type=Path, required=True)
        elif name == "roundtrip":
            sub.add_argument("--report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data = _read_rom(args.rom)
        if args.command == "inspect-rom":
            result = inspect(data, args.profile)
        else:
            # Every ROM-consuming command verifies the exact project identity first.
            identity = inspect(data, args.profile)
        if args.command == "inventory":
            result = inventory(data)
            _write_new_json(args.output, result)
            result = {"identity_check": identity["identity_check"], "file_count": len(result), "report": str(args.output)}
        elif args.command == "extract-tables":
            result = extract_rows(data)
            _write_new_csv(args.output, result)
            result = {"identity_check": identity["identity_check"], "source_rows": len(result), "output": str(args.output), "note": "Source inventory only; not a translation master and no translation status is assigned."}
        elif args.command == "roundtrip":
            result = roundtrip(data)
            if args.report:
                _write_new_json(args.report, result)
            result = {"identity_check": identity["identity_check"], **result}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, NDSFormatError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
