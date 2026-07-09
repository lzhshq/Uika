#!/usr/bin/env python3
"""Convert a binary PCD from FAST-LIO lidar_odom coordinates to map coordinates."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply p_map = R_y(pitch) * p_lidar_odom + translation to a binary PCD."
    )
    parser.add_argument("--input", required=True, help="Input binary PCD in lidar_odom coordinates.")
    parser.add_argument("--output", required=True, help="Output binary PCD in map coordinates.")
    parser.add_argument("--x", type=float, default=0.313, help="Map translation x.")
    parser.add_argument("--y", type=float, default=0.0, help="Map translation y.")
    parser.add_argument("--z", type=float, default=-0.06, help="Map translation z.")
    parser.add_argument("--roll", type=float, default=0.0, help="Roll is accepted for CLI symmetry; must be 0.")
    parser.add_argument("--pitch", type=float, default=1.5707963268, help="Pitch in radians.")
    parser.add_argument("--yaw", type=float, default=0.0, help="Yaw is accepted for CLI symmetry; must be 0.")
    parser.add_argument(
        "--stride",
        type=int,
        default=1,
        help="Keep every Nth point for RViz visualization copies. Use 1 for the full navigation map.",
    )
    return parser.parse_args()


def pcd_dtype(fields: list[str], sizes: list[int], types: list[str], counts: list[int]) -> np.dtype:
    if any(count != 1 for count in counts):
        raise RuntimeError("Only PCD files with COUNT 1 fields are supported.")

    np_types = []
    for size, field_type in zip(sizes, types):
        if field_type == "F" and size == 4:
            np_types.append(np.float32)
        elif field_type == "F" and size == 8:
            np_types.append(np.float64)
        elif field_type == "U" and size == 1:
            np_types.append(np.uint8)
        elif field_type == "U" and size == 2:
            np_types.append(np.uint16)
        elif field_type == "U" and size == 4:
            np_types.append(np.uint32)
        elif field_type == "I" and size == 1:
            np_types.append(np.int8)
        elif field_type == "I" and size == 2:
            np_types.append(np.int16)
        elif field_type == "I" and size == 4:
            np_types.append(np.int32)
        else:
            raise RuntimeError(f"Unsupported PCD field type: TYPE={field_type}, SIZE={size}")
    return np.dtype([(field, np_type) for field, np_type in zip(fields, np_types)])


def read_binary_pcd(path: Path) -> tuple[list[bytes], dict[str, list[str]], bytes]:
    with path.open("rb") as handle:
        header_lines = []
        while True:
            line = handle.readline()
            if not line:
                raise RuntimeError("PCD header ended before DATA line.")
            header_lines.append(line)
            if line.startswith(b"DATA"):
                break
        data = handle.read()

    metadata: dict[str, list[str]] = {}
    header_text = b"".join(header_lines).decode("ascii")
    for line in header_text.splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        metadata[parts[0]] = parts[1:]
    if metadata.get("DATA", [""])[0] != "binary":
        raise RuntimeError("Only binary PCD files are supported.")
    return header_lines, metadata, data


def update_header(header_lines: list[bytes], points: int) -> list[bytes]:
    updated = []
    for raw in b"".join(header_lines).decode("ascii").splitlines():
        if raw.startswith("WIDTH "):
            updated.append(f"WIDTH {points}")
        elif raw.startswith("POINTS "):
            updated.append(f"POINTS {points}")
        else:
            updated.append(raw)
    return [(line + "\n").encode("ascii") for line in updated]


def main() -> None:
    args = parse_args()
    if abs(args.roll) > 1e-9 or abs(args.yaw) > 1e-9:
        raise RuntimeError("This converter currently supports pitch-only rotation for the Uika MID360 mount.")
    if args.stride < 1:
        raise RuntimeError("--stride must be >= 1.")

    src = Path(args.input)
    dst = Path(args.output)
    tmp = dst.with_suffix(dst.suffix + ".tmp")

    header_lines, metadata, data = read_binary_pcd(src)
    fields = metadata["FIELDS"]
    sizes = list(map(int, metadata["SIZE"]))
    field_types = metadata["TYPE"]
    counts = list(map(int, metadata["COUNT"]))
    points = int(metadata["POINTS"][0])
    dtype = pcd_dtype(fields, sizes, field_types, counts)

    cloud = np.frombuffer(data, dtype=dtype, count=points).copy()
    if args.stride > 1:
        cloud = cloud[:: args.stride].copy()

    c = math.cos(args.pitch)
    s = math.sin(args.pitch)
    rotation = np.array(
        [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ],
        dtype=np.float32,
    )
    translation = np.array([args.x, args.y, args.z], dtype=np.float32)

    xyz = np.stack((cloud["x"], cloud["y"], cloud["z"]), axis=1).astype(np.float32, copy=False)
    xyz_map = xyz @ rotation.T + translation
    cloud["x"] = xyz_map[:, 0]
    cloud["y"] = xyz_map[:, 1]
    cloud["z"] = xyz_map[:, 2]

    if {"normal_x", "normal_y", "normal_z"}.issubset(fields):
        normals = np.stack((cloud["normal_x"], cloud["normal_y"], cloud["normal_z"]), axis=1).astype(
            np.float32, copy=False
        )
        normals_map = normals @ rotation.T
        cloud["normal_x"] = normals_map[:, 0]
        cloud["normal_y"] = normals_map[:, 1]
        cloud["normal_z"] = normals_map[:, 2]

    dst.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("wb") as handle:
        handle.writelines(update_header(header_lines, len(cloud)))
        handle.write(cloud.tobytes())
    os.replace(tmp, dst)

    print(f"source: {src}")
    print(f"output: {dst}")
    print(f"points: {len(cloud)}")
    print(f"min xyz: {cloud['x'].min():.6f}, {cloud['y'].min():.6f}, {cloud['z'].min():.6f}")
    print(f"max xyz: {cloud['x'].max():.6f}, {cloud['y'].max():.6f}, {cloud['z'].max():.6f}")


if __name__ == "__main__":
    main()
