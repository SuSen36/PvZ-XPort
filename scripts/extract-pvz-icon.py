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
Extract icon resources from a Windows PE executable.

Usage:
    python scripts/extract-pvz-icon.py PlantsVsZombies.exe --out res/icon
"""

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Union


RT_ICON = 3
RT_GROUP_ICON = 14


@dataclass(frozen=True)
class Section:
    virtual_address: int
    virtual_size: int
    raw_size: int
    raw_pointer: int


@dataclass(frozen=True)
class ResourceData:
    rva: int
    size: int
    data: bytes


ResourceTree = dict[Union[int, str], Union["ResourceTree", ResourceData]]


@dataclass(frozen=True)
class GroupIconEntry:
    width: int
    height: int
    color_count: int
    reserved: int
    planes: int
    bit_count: int
    size: int
    resource_id: int

    @property
    def ico_width(self) -> int:
        return self.width if self.width != 256 else 0

    @property
    def ico_height(self) -> int:
        return self.height if self.height != 256 else 0


@dataclass(frozen=True)
class IconGroup:
    resource_id: Union[int, str]
    language_id: Union[int, str]
    entries: list[GroupIconEntry]

    @property
    def largest_size(self) -> int:
        return max((entry.width or 256) * (entry.height or 256) for entry in self.entries)


class PeFile:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.data = path.read_bytes()
        self.sections: list[Section] = []
        self.resource_rva = 0
        self.resource_size = 0
        self._parse_headers()

    def _parse_headers(self) -> None:
        data = self.data
        if len(data) < 0x40 or data[:2] != b"MZ":
            raise ValueError(f"{self.path} is not a DOS/PE executable")

        pe_offset = _u32(data, 0x3C)
        if data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise ValueError(f"{self.path} does not contain a PE header")

        coff_offset = pe_offset + 4
        section_count = _u16(data, coff_offset + 2)
        optional_size = _u16(data, coff_offset + 16)
        optional_offset = coff_offset + 20
        magic = _u16(data, optional_offset)
        data_directory_offset = {0x10B: 96, 0x20B: 112}.get(magic)
        if data_directory_offset is None:
            raise ValueError(f"unsupported PE optional header magic: 0x{magic:04X}")

        resource_directory = optional_offset + data_directory_offset + 8 * 2
        self.resource_rva = _u32(data, resource_directory)
        self.resource_size = _u32(data, resource_directory + 4)
        if self.resource_rva == 0 or self.resource_size == 0:
            raise ValueError(f"{self.path} has no PE resource directory")

        section_offset = optional_offset + optional_size
        for index in range(section_count):
            offset = section_offset + index * 40
            self.sections.append(
                Section(
                    virtual_address=_u32(data, offset + 12),
                    virtual_size=_u32(data, offset + 8),
                    raw_size=_u32(data, offset + 16),
                    raw_pointer=_u32(data, offset + 20),
                )
            )

    def rva_to_offset(self, rva: int) -> int:
        for section in self.sections:
            size = max(section.virtual_size, section.raw_size)
            if section.virtual_address <= rva < section.virtual_address + size:
                return section.raw_pointer + (rva - section.virtual_address)
        raise ValueError(f"RVA 0x{rva:X} does not map to a file section")

    def resource_tree(self) -> ResourceTree:
        base_offset = self.rva_to_offset(self.resource_rva)
        return _read_resource_directory(self.data, base_offset, 0, self)


def _u16(data: bytes, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _resource_name(data: bytes, base_offset: int, value: int) -> Union[int, str]:
    if value & 0x80000000:
        offset = base_offset + (value & 0x7FFFFFFF)
        length = _u16(data, offset)
        raw = data[offset + 2 : offset + 2 + length * 2]
        return raw.decode("utf-16le")
    return value & 0xFFFF


def _read_resource_directory(
    data: bytes,
    base_offset: int,
    directory_offset: int,
    pe: PeFile,
) -> ResourceTree:
    offset = base_offset + directory_offset
    named_count = _u16(data, offset + 12)
    id_count = _u16(data, offset + 14)
    tree: ResourceTree = {}

    entries_offset = offset + 16
    for index in range(named_count + id_count):
        entry_offset = entries_offset + index * 8
        name = _resource_name(data, base_offset, _u32(data, entry_offset))
        child_value = _u32(data, entry_offset + 4)
        child_offset = child_value & 0x7FFFFFFF
        if child_value & 0x80000000:
            tree[name] = _read_resource_directory(data, base_offset, child_offset, pe)
        else:
            data_entry_offset = base_offset + child_offset
            rva = _u32(data, data_entry_offset)
            size = _u32(data, data_entry_offset + 4)
            file_offset = pe.rva_to_offset(rva)
            tree[name] = ResourceData(rva, size, data[file_offset : file_offset + size])

    return tree


def _leaf_resources(tree: ResourceTree, resource_type: int) -> dict[Union[int, str], ResourceData]:
    type_tree = tree.get(resource_type)
    if not isinstance(type_tree, dict):
        return {}

    result: dict[Union[int, str], ResourceData] = {}
    for resource_id, language_tree in type_tree.items():
        if not isinstance(language_tree, dict):
            continue
        for _, leaf in language_tree.items():
            if isinstance(leaf, ResourceData):
                result[resource_id] = leaf
                break
    return result


def _icon_groups(tree: ResourceTree) -> list[IconGroup]:
    type_tree = tree.get(RT_GROUP_ICON)
    if not isinstance(type_tree, dict):
        return []

    groups: list[IconGroup] = []
    for resource_id, language_tree in type_tree.items():
        if not isinstance(language_tree, dict):
            continue
        for language_id, leaf in language_tree.items():
            if not isinstance(leaf, ResourceData):
                continue
            groups.append(
                IconGroup(
                    resource_id=resource_id,
                    language_id=language_id,
                    entries=_parse_group_icon_entries(leaf.data),
                )
            )
    return groups


def _parse_group_icon_entries(data: bytes) -> list[GroupIconEntry]:
    reserved, icon_type, count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or icon_type != 1:
        raise ValueError("resource is not an icon group")

    entries: list[GroupIconEntry] = []
    for index in range(count):
        offset = 6 + index * 14
        width, height, color_count, reserved_byte, planes, bit_count, size, resource_id = struct.unpack_from(
            "<BBBBHHIH",
            data,
            offset,
        )
        entries.append(
            GroupIconEntry(
                width=width or 256,
                height=height or 256,
                color_count=color_count,
                reserved=reserved_byte,
                planes=planes,
                bit_count=bit_count,
                size=size,
                resource_id=resource_id,
            )
        )

    return entries


def _build_ico(group: IconGroup, icons: dict[Union[int, str], ResourceData]) -> bytes:
    parts: list[bytes] = []
    directory = bytearray(struct.pack("<HHH", 0, 1, len(group.entries)))
    image_offset = 6 + 16 * len(group.entries)

    for entry in group.entries:
        image = icons.get(entry.resource_id)
        if image is None:
            raise ValueError(f"missing icon image resource {entry.resource_id}")
        parts.append(image.data)
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                entry.ico_width,
                entry.ico_height,
                entry.color_count,
                entry.reserved,
                entry.planes,
                entry.bit_count,
                len(image.data),
                image_offset,
            )
        )
        image_offset += len(image.data)

    return bytes(directory) + b"".join(parts)


def _group_filename(group: IconGroup) -> str:
    resource_id = str(group.resource_id).replace("/", "_")
    language_id = str(group.language_id).replace("/", "_")
    return f"app-group-{resource_id}-{language_id}.ico"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract PvZ app icons from a PE executable.")
    parser.add_argument("exe", type=Path, help="Path to PlantsVsZombies.exe")
    parser.add_argument("--out", type=Path, default=Path("res/icon"), help="Output icon directory")
    parser.add_argument("--group", help="Icon group resource id to write as app.ico")
    parser.add_argument("--all-groups", action="store_true", help="Write every icon group as a separate .ico")
    args = parser.parse_args()

    pe = PeFile(args.exe)
    tree = pe.resource_tree()
    icons = _leaf_resources(tree, RT_ICON)
    groups = _icon_groups(tree)
    if not icons or not groups:
        raise SystemExit(f"no icon resources found in {args.exe}")

    if args.group is None:
        selected = max(groups, key=lambda group: (group.largest_size, len(group.entries)))
    else:
        selected_groups = [group for group in groups if str(group.resource_id) == args.group]
        if not selected_groups:
            raise SystemExit(f"icon group {args.group} was not found")
        selected = max(selected_groups, key=lambda group: (group.largest_size, len(group.entries)))

    args.out.mkdir(parents=True, exist_ok=True)
    app_icon = args.out / "app.ico"
    app_icon.write_bytes(_build_ico(selected, icons))
    print(f"Wrote {app_icon}")

    if args.all_groups:
        groups_dir = args.out / "groups"
        groups_dir.mkdir(parents=True, exist_ok=True)
        for group in groups:
            output = groups_dir / _group_filename(group)
            output.write_bytes(_build_ico(group, icons))
            print(f"Wrote {output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
