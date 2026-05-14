#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import shutil
import struct
import sys
from pathlib import Path, PurePosixPath


PAK_MAGIC = 0xBAC04AC0
PAK_VERSION = 0
FILEFLAGS_END = 0x80


def _to_posix(path: Path) -> str:
    return path.as_posix()


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def _parse_xor_key(value: object) -> int:
    if isinstance(value, int):
        key = value
    elif isinstance(value, str):
        key = int(value, 0)
    else:
        raise ValueError("pakXorKey must be an integer or string")
    if not 0 <= key <= 0xFF:
        raise ValueError("pakXorKey must be in byte range")
    return key


def _load_config(path: Path) -> dict:
    if not path.exists():
        print(f"Resource pack config is missing, using built-in defaults: {path}", file=sys.stderr)
        return {
            "sourceDir": "res",
            "output": "main.pak",
            "include": ["**/*"],
            "exclude": [
                ".git/**",
                ".git",
                ".gitkeep",
                "README.md",
                "properties/**",
                "main.pak",
                "*.pak",
                "*.md",
            ],
            "looseDirs": ["properties"],
            "copyLooseProperties": True,
            "pakXorKey": "0xF7",
        }
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _is_empty_source(source_dir: Path) -> bool:
    if not source_dir.exists() or not source_dir.is_dir():
        return True
    return not any(source_dir.iterdir())


def _collect_files(source_dir: Path, include: list[str], exclude: list[str]) -> list[Path]:
    files: list[Path] = []
    for path in source_dir.rglob("*"):
        if not path.is_file():
            continue
        rel = _to_posix(path.relative_to(source_dir))
        if include and not _matches_any(rel, include):
            continue
        if _matches_any(rel, exclude):
            continue
        files.append(path)
    return sorted(files, key=lambda path: _to_posix(path.relative_to(source_dir)).lower())


def _build_pak(source_dir: Path, files: list[Path], xor_key: int) -> bytes:
    header = bytearray()
    payload = bytearray()
    header.extend(struct.pack("<II", PAK_MAGIC, PAK_VERSION))

    for path in files:
        rel = PurePosixPath(_to_posix(path.relative_to(source_dir))).as_posix()
        name = rel.encode("utf-8")
        if len(name) > 255:
            raise ValueError(f"pak path is too long: {rel}")

        data = path.read_bytes()
        mtime = int(path.stat().st_mtime)
        header.extend(struct.pack("<BB", 0, len(name)))
        header.extend(name)
        header.extend(struct.pack("<IQ", len(data), mtime))
        payload.extend(data)

    header.extend(struct.pack("<B", FILEFLAGS_END))
    plain = header + payload
    return bytes(byte ^ xor_key for byte in plain)


def _copy_loose_dirs(source_dir: Path, output_dir: Path, loose_dirs: list[str]) -> None:
    for directory in loose_dirs:
        src = source_dir / directory
        dst = output_dir / directory
        if dst.exists():
            shutil.rmtree(dst)
        if src.exists() and src.is_dir():
            shutil.copytree(src, dst)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack PvZ resources into main.pak.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--stamp", type=Path)
    args = parser.parse_args()

    config = _load_config(args.config)
    source_dir = (args.source or Path(config.get("sourceDir", "res"))).resolve()
    output_dir = args.out.resolve()
    output_name = config.get("output", "main.pak")
    output_path = output_dir / output_name
    stamp_path = args.stamp or (output_dir / "resource-pack.stamp")

    output_dir.mkdir(parents=True, exist_ok=True)

    if _is_empty_source(source_dir):
        output_path.unlink(missing_ok=True)
        stamp_path.write_text("missing source resources\n", encoding="utf-8")
        print(f"Resource source is empty or missing: {source_dir}", file=sys.stderr)
        return 0

    include = list(config.get("include", ["**/*"]))
    exclude = list(config.get("exclude", []))
    files = _collect_files(source_dir, include, exclude)
    if not files:
        output_path.unlink(missing_ok=True)
        stamp_path.write_text("no packable resources\n", encoding="utf-8")
        print(f"No packable resource files found in: {source_dir}", file=sys.stderr)
        return 0

    xor_key = _parse_xor_key(config.get("pakXorKey", "0xF7"))
    output_path.write_bytes(_build_pak(source_dir, files, xor_key))

    loose_dirs = list(config.get("looseDirs", []))
    if config.get("copyLooseProperties", True) and "properties" not in loose_dirs:
        loose_dirs.append("properties")
    _copy_loose_dirs(source_dir, output_dir, loose_dirs)

    stamp_path.write_text(
        f"packed {len(files)} files from {source_dir}{os.linesep}",
        encoding="utf-8",
    )
    print(f"Packed {len(files)} files into {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
