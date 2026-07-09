#!/usr/bin/env python3
import argparse
import math
from pathlib import Path

import numpy as np


def read_pcd_xyz(path):
    header = {}
    header_lines = []

    with open(path, "rb") as f:
        while True:
            line = f.readline()
            if not line:
                raise ValueError("PCD header ended before DATA line")

            decoded = line.decode("ascii", errors="replace").strip()
            header_lines.append(decoded)
            if decoded:
                parts = decoded.split()
                header[parts[0]] = parts[1:]

            if decoded.startswith("DATA"):
                data_type = decoded.split()[1]
                data_offset = f.tell()
                break

        if data_type != "binary":
            raise ValueError(f"Only binary PCD is supported, got DATA {data_type}")

        fields = header.get("FIELDS", [])
        sizes = [int(v) for v in header.get("SIZE", [])]
        types = header.get("TYPE", [])
        counts = [int(v) for v in header.get("COUNT", [])]
        points = int(header["POINTS"][0])

        if counts and any(count != 1 for count in counts):
            raise ValueError("Only scalar PCD fields are supported")
        if not {"x", "y", "z"}.issubset(fields):
            raise ValueError("PCD must contain x, y, z fields")
        if any(size != 4 or typ != "F" for size, typ in zip(sizes, types)):
            raise ValueError("Only float32 PCD fields are supported")

        f.seek(data_offset)
        raw = np.fromfile(f, dtype=np.float32, count=points * len(fields))

    cloud = raw.reshape(points, len(fields))
    x_idx, y_idx, z_idx = fields.index("x"), fields.index("y"), fields.index("z")
    xyz = cloud[:, [x_idx, y_idx, z_idx]]
    return xyz[np.isfinite(xyz).all(axis=1)]


def write_pgm(path, image):
    with open(path, "wb") as f:
        f.write(f"P5\n{image.shape[1]} {image.shape[0]}\n255\n".encode("ascii"))
        f.write(image.astype(np.uint8).tobytes())


def dilate_occupied(grid, radius_cells):
    if radius_cells <= 0:
        return grid

    occupied = np.argwhere(grid == 0)
    if occupied.size == 0:
        return grid

    offsets = []
    for dy in range(-radius_cells, radius_cells + 1):
        for dx in range(-radius_cells, radius_cells + 1):
            if dx * dx + dy * dy <= radius_cells * radius_cells:
                offsets.append((dy, dx))

    h, w = grid.shape
    for dy, dx in offsets:
        ys = np.clip(occupied[:, 0] + dy, 0, h - 1)
        xs = np.clip(occupied[:, 1] + dx, 0, w - 1)
        grid[ys, xs] = 0
    return grid


def build_map(points, resolution, padding, z_min, z_max, inflation):
    sliced = points[(points[:, 2] >= z_min) & (points[:, 2] <= z_max)]
    if sliced.size == 0:
        raise ValueError("No points remain after z filtering; adjust --z-min/--z-max")

    min_x = float(np.min(sliced[:, 0]) - padding)
    min_y = float(np.min(sliced[:, 1]) - padding)
    max_x = float(np.max(sliced[:, 0]) + padding)
    max_y = float(np.max(sliced[:, 1]) + padding)

    width = max(1, int(math.ceil((max_x - min_x) / resolution)))
    height = max(1, int(math.ceil((max_y - min_y) / resolution)))
    grid = np.full((height, width), 254, dtype=np.uint8)

    cols = np.floor((sliced[:, 0] - min_x) / resolution).astype(np.int64)
    rows = np.floor((sliced[:, 1] - min_y) / resolution).astype(np.int64)
    valid = (cols >= 0) & (cols < width) & (rows >= 0) & (rows < height)
    grid[height - 1 - rows[valid], cols[valid]] = 0

    radius_cells = int(math.ceil(inflation / resolution))
    grid = dilate_occupied(grid, radius_cells)
    return grid, (min_x, min_y), sliced.shape[0]


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Point-LIO binary PCD map into a simple Nav2 occupancy map."
    )
    parser.add_argument("pcd", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="Output YAML path")
    parser.add_argument("--resolution", type=float, default=0.05)
    parser.add_argument("--padding", type=float, default=1.0)
    parser.add_argument("--z-min", type=float, default=0.10)
    parser.add_argument("--z-max", type=float, default=1.20)
    parser.add_argument("--inflate", type=float, default=0.15)
    args = parser.parse_args()

    points = read_pcd_xyz(args.pcd)
    image, origin, kept = build_map(
        points,
        resolution=args.resolution,
        padding=args.padding,
        z_min=args.z_min,
        z_max=args.z_max,
        inflation=args.inflate,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pgm_path = args.output.with_suffix(".pgm")
    write_pgm(pgm_path, image)

    yaml_text = (
        f"image: {pgm_path.name}\n"
        f"mode: trinary\n"
        f"resolution: {args.resolution}\n"
        f"origin: [{origin[0]:.6f}, {origin[1]:.6f}, 0.0]\n"
        f"negate: 0\n"
        f"occupied_thresh: 0.65\n"
        f"free_thresh: 0.25\n"
    )
    args.output.write_text(yaml_text, encoding="ascii")

    print(f"read points: {points.shape[0]}")
    print(f"kept points: {kept}")
    print(f"map size: {image.shape[1]} x {image.shape[0]}")
    print(f"wrote: {args.output}")
    print(f"wrote: {pgm_path}")


if __name__ == "__main__":
    main()
