#!/usr/bin/env python3
# Copyright (C) 2026 Zhou Qiankang <wszqkzqk@qq.com>
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
# This file is part of PvZ-Portable.
#
# PvZ-Portable is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

"""
Convert the extracted PvZ app icon for every platform target.

Usage:
    python scripts/convert-pvz-icons.py --icon res/icon/app.ico --out res/icon
"""

import argparse
import json
from pathlib import Path
from typing import Iterable

from PIL import Image


ANDROID_DENSITIES = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192,
}


def _load_icon(path: Path) -> Image.Image:
    icon = Image.open(path)
    best_frame = icon.copy()
    best_area = best_frame.width * best_frame.height
    for index in range(getattr(icon, "n_frames", 1)):
        icon.seek(index)
        frame = icon.convert("RGBA")
        area = frame.width * frame.height
        if area > best_area:
            best_frame = frame.copy()
            best_area = area
    return best_frame.convert("RGBA")


def _resize(icon: Image.Image, size: int) -> Image.Image:
    return icon.resize((size, size), Image.Resampling.LANCZOS)


def _save_png(icon: Image.Image, path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _resize(icon, size).save(path, "PNG", optimize=True)
    print(f"Wrote {path}")


def _save_jpeg(icon: Image.Image, path: Path, size: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (size, size), "white")
    canvas.alpha_composite(_resize(icon, size))
    canvas.convert("RGB").save(path, "JPEG", quality=95, optimize=True)
    print(f"Wrote {path}")


def _save_readme(icon: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas = Image.new("RGBA", (650, 450), (0, 0, 0, 0))
    image = _resize(icon, 450)
    canvas.alpha_composite(image, ((canvas.width - image.width) // 2, 0))
    canvas.save(path, "PNG", optimize=True)
    print(f"Wrote {path}")


def _write_ios_catalog(icon: Image.Image, root: Path) -> None:
    catalog = root / "ios" / "Assets.xcassets"
    app_icon = catalog / "AppIcon.appiconset"
    app_icon.mkdir(parents=True, exist_ok=True)
    (catalog / "Contents.json").write_text(
        json.dumps({"info": {"author": "xcode", "version": 1}}, indent=2) + "\n",
        encoding="utf-8",
    )
    (app_icon / "Contents.json").write_text(
        json.dumps(
            {
                "images": [
                    {
                        "filename": "AppIcon.png",
                        "idiom": "universal",
                        "platform": "ios",
                        "size": "1024x1024",
                    }
                ],
                "info": {"author": "xcode", "version": 1},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _save_png(icon, app_icon / "AppIcon.png", 1024)


def _write_android_icons(icon: Image.Image, root: Path) -> None:
    for density, size in ANDROID_DENSITIES.items():
        _save_png(icon, root / "android" / "res" / f"mipmap-{density}" / "ic_launcher.png", size)


def _copy_ico(icon_path: Path, root: Path) -> None:
    output = root / "app.ico"
    if icon_path.resolve() != output.resolve():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(icon_path.read_bytes())
        print(f"Wrote {output}")


def _outputs(root: Path) -> Iterable[Path]:
    yield root / "app.ico"
    yield root / "app.png"
    yield root / "linux.png"
    yield root / "readme.png"
    yield root / "switch.jpg"
    yield root / "3ds.png"
    yield root / "ios" / "Assets.xcassets" / "AppIcon.appiconset" / "AppIcon.png"
    for density in ANDROID_DENSITIES:
        yield root / "android" / "res" / f"mipmap-{density}" / "ic_launcher.png"


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert extracted PvZ icon to platform icon assets.")
    parser.add_argument("--icon", type=Path, default=Path("res/icon/app.ico"))
    parser.add_argument("--out", type=Path, default=Path("res/icon"))
    parser.add_argument("--check", action="store_true", help="Only check that converted outputs exist")
    args = parser.parse_args()

    if args.check:
        missing = [path for path in _outputs(args.out) if not path.exists()]
        if missing:
            for path in missing:
                print(f"Missing {path}")
            raise SystemExit(1)
        return 0

    icon = _load_icon(args.icon)
    args.out.mkdir(parents=True, exist_ok=True)
    _copy_ico(args.icon, args.out)
    _save_png(icon, args.out / "app.png", 512)
    _save_png(icon, args.out / "linux.png", 512)
    _save_readme(icon, args.out / "readme.png")
    _save_jpeg(icon, args.out / "switch.jpg", 256)
    _save_png(icon, args.out / "3ds.png", 48)
    _write_android_icons(icon, args.out)
    _write_ios_catalog(icon, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
