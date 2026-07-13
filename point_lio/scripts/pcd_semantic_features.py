#!/usr/bin/env python3
"""Render coordinate-aware height, roughness, and density views of a PCD map."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_pcd_xyz(path):
    header = {}
    with path.open("rb") as stream:
        while True:
            line = stream.readline()
            if not line:
                raise ValueError("PCD header ended before DATA")
            decoded = line.decode("ascii", errors="replace").strip()
            if decoded:
                parts = decoded.split()
                header[parts[0]] = parts[1:]
            if decoded.startswith("DATA"):
                data_kind = decoded.split()[1]
                data_offset = stream.tell()
                break

        fields = header["FIELDS"]
        points = int(header["POINTS"][0])
        xyz_indices = [fields.index(axis) for axis in ("x", "y", "z")]
        if data_kind == "binary":
            sizes = [int(value) for value in header["SIZE"]]
            types = header["TYPE"]
            counts = [int(value) for value in header.get("COUNT", ["1"] * len(fields))]
            if any(size != 4 for size in sizes) or any(kind != "F" for kind in types):
                raise ValueError("Only float32 binary PCD fields are supported")
            if any(count != 1 for count in counts):
                raise ValueError("Only scalar PCD fields are supported")
            stream.seek(data_offset)
            raw = np.fromfile(stream, dtype=np.float32, count=points * len(fields))
            xyz = raw.reshape(points, len(fields))[:, xyz_indices]
        elif data_kind == "ascii":
            stream.seek(data_offset)
            raw = np.loadtxt(stream, dtype=np.float32, max_rows=points)
            xyz = raw[:, xyz_indices]
        else:
            raise ValueError(f"Unsupported PCD DATA type: {data_kind}")
    return xyz[np.isfinite(xyz).all(axis=1)]


def grid_features(points, resolution, bounds, z_min, z_max, z_offset):
    min_x, min_y, max_x, max_y = bounds
    width = int(np.ceil((max_x - min_x) / resolution))
    height = int(np.ceil((max_y - min_y) / resolution))

    selected = points[
        (points[:, 0] >= min_x)
        & (points[:, 0] < max_x)
        & (points[:, 1] >= min_y)
        & (points[:, 1] < max_y)
        & (points[:, 2] >= z_min)
        & (points[:, 2] <= z_max)
    ].copy()
    if not selected.size:
        raise ValueError("No points remain in the requested XY/Z bounds")
    selected[:, 2] += z_offset

    cols = ((selected[:, 0] - min_x) / resolution).astype(np.int64)
    rows = ((selected[:, 1] - min_y) / resolution).astype(np.int64)
    flat = rows * width + cols
    cells = height * width

    count = np.bincount(flat, minlength=cells).astype(np.float32)
    z_sum = np.bincount(flat, weights=selected[:, 2], minlength=cells)
    z_sq_sum = np.bincount(flat, weights=selected[:, 2] ** 2, minlength=cells)
    z_min_grid = np.full(cells, np.inf, dtype=np.float32)
    z_max_grid = np.full(cells, -np.inf, dtype=np.float32)
    np.minimum.at(z_min_grid, flat, selected[:, 2])
    np.maximum.at(z_max_grid, flat, selected[:, 2])

    valid = count > 0
    mean = np.full(cells, np.nan, dtype=np.float32)
    std = np.full(cells, np.nan, dtype=np.float32)
    mean[valid] = z_sum[valid] / count[valid]
    variance = np.maximum(0.0, z_sq_sum[valid] / count[valid] - mean[valid] ** 2)
    std[valid] = np.sqrt(variance)
    z_max_grid[~valid] = np.nan
    z_min_grid[~valid] = np.nan

    shape = (height, width)
    return {
        "count": count.reshape(shape),
        "mean": mean.reshape(shape),
        "std": std.reshape(shape),
        "min": z_min_grid.reshape(shape),
        "max": z_max_grid.reshape(shape),
        "range": (z_max_grid - z_min_grid).reshape(shape),
        "selected_count": selected.shape[0],
    }


def render(features, bounds, output, title, height_limit, roughness_limit):
    extent = [bounds[0], bounds[2], bounds[1], bounds[3]]
    figure, axes = plt.subplots(2, 2, figsize=(16, 12), constrained_layout=True)
    panels = [
        (features["max"], "Maximum obstacle height (m)", "turbo", 0.0, height_limit),
        (features["mean"], "Mean return height (m)", "turbo", 0.0, height_limit),
        (features["range"], "Vertical range per cell (m)", "magma", 0.0, roughness_limit),
        (np.log1p(features["count"]), "Point density log(1 + hits)", "viridis", 0.0, None),
    ]
    for axis, (data, label, color_map, vmin, vmax) in zip(axes.flat, panels):
        image = axis.imshow(
            data,
            origin="lower",
            extent=extent,
            interpolation="nearest",
            cmap=color_map,
            vmin=vmin,
            vmax=vmax,
            aspect="equal",
        )
        axis.axhline(0.0, color="cyan", linewidth=0.8, alpha=0.8)
        axis.axvline(0.0, color="cyan", linewidth=0.8, alpha=0.8)
        axis.plot(0.0, 0.0, marker="+", color="white", markersize=11, markeredgewidth=2)
        axis.set_title(label)
        axis.set_xlabel("map X (m)")
        axis.set_ylabel("map Y (m)")
        axis.grid(color="white", alpha=0.18, linewidth=0.5)
        figure.colorbar(image, ax=axis, shrink=0.82)
    figure.suptitle(title, fontsize=15)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=150)
    plt.close(figure)


def render_height_layers(points, bounds, resolution, output, title, layers):
    extent = [bounds[0], bounds[2], bounds[1], bounds[3]]
    figure, axes = plt.subplots(2, 2, figsize=(16, 13), constrained_layout=True)
    for axis, (label, z_min, z_max) in zip(axes.flat[:3], layers):
        features = grid_features(points, resolution, bounds, z_min, z_max, 0.0)
        density = np.log1p(features["count"])
        image = axis.imshow(
            density,
            origin="lower",
            extent=extent,
            interpolation="nearest",
            cmap="viridis",
            vmin=0.0,
            vmax=max(3.0, float(np.nanpercentile(density, 99.5))),
            aspect="equal",
        )
        axis.set_title(f"{label}: z = {z_min:.2f} .. {z_max:.2f} m")
        figure.colorbar(image, ax=axis, shrink=0.82)

    composite = np.zeros((*features["count"].shape, 3), dtype=np.float32)
    for channel, (_, z_min, z_max) in enumerate(layers):
        layer = grid_features(points, resolution, bounds, z_min, z_max, 0.0)["count"]
        layer = np.log1p(layer)
        scale = max(1.0, float(np.nanpercentile(layer, 99.0)))
        composite[:, :, channel] = np.clip(layer / scale, 0.0, 1.0)
    axes.flat[3].imshow(
        composite,
        origin="lower",
        extent=extent,
        interpolation="nearest",
        aspect="equal",
    )
    axes.flat[3].set_title("Composite: red=low, green=mid, blue=high")

    for axis in axes.flat:
        axis.axhline(0.0, color="cyan", linewidth=0.8, alpha=0.8)
        axis.axvline(0.0, color="cyan", linewidth=0.8, alpha=0.8)
        axis.plot(0.0, 0.0, marker="+", color="white", markersize=11, markeredgewidth=2)
        axis.set_xlabel("map X (m)")
        axis.set_ylabel("map Y (m)")
        axis.grid(color="white", alpha=0.18, linewidth=0.5)
    figure.suptitle(title, fontsize=15)
    figure.savefig(output, dpi=150)
    plt.close(figure)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pcd", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resolution", type=float, default=0.05)
    parser.add_argument("--bounds", nargs=4, type=float, metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"))
    parser.add_argument("--z-min", type=float, default=-0.20)
    parser.add_argument("--z-max", type=float, default=1.20)
    parser.add_argument("--z-offset", type=float, default=0.0)
    parser.add_argument("--height-limit", type=float, default=0.8)
    parser.add_argument("--roughness-limit", type=float, default=0.5)
    parser.add_argument("--title", default="PCD semantic feature views")
    parser.add_argument(
        "--layers-output",
        type=Path,
        help="Optional height-layer density image",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    points = read_pcd_xyz(args.pcd)
    if args.bounds:
        bounds = tuple(args.bounds)
    else:
        bounds = (
            float(np.floor(points[:, 0].min())),
            float(np.floor(points[:, 1].min())),
            float(np.ceil(points[:, 0].max())),
            float(np.ceil(points[:, 1].max())),
        )
    features = grid_features(
        points, args.resolution, bounds, args.z_min, args.z_max, args.z_offset
    )
    render(
        features,
        bounds,
        args.output,
        args.title,
        args.height_limit,
        args.roughness_limit,
    )
    if args.layers_output:
        args.layers_output.parent.mkdir(parents=True, exist_ok=True)
        layer_points = points.copy()
        layer_points[:, 2] += args.z_offset
        render_height_layers(
            layer_points,
            bounds,
            args.resolution,
            args.layers_output,
            f"{args.title}: height layers",
            [
                ("low obstacle", 0.05, 0.20),
                ("medium obstacle", 0.20, 0.50),
                ("high obstacle", 0.50, 1.20),
            ],
        )
    print(f"read points: {points.shape[0]}")
    print(f"selected points: {features['selected_count']}")
    print(f"bounds: {bounds}")
    print(f"wrote: {args.output}")
    if args.layers_output:
        print(f"wrote: {args.layers_output}")


if __name__ == "__main__":
    main()
