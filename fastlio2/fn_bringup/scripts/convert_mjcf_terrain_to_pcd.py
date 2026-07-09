#!/usr/bin/env python3
"""Sample static MJCF terrain geoms into an ASCII PCD map."""

from __future__ import annotations

import argparse
import math
import os
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert direct worldbody MJCF terrain geoms into a PointXYZ PCD map."
    )
    parser.add_argument("--xml", required=True, help="Input MJCF/XML scene file.")
    parser.add_argument("--output", required=True, help="Output full-resolution ASCII PCD.")
    parser.add_argument(
        "--viz-output",
        default="",
        help="Optional downsampled PCD copy for RViz display.",
    )
    parser.add_argument(
        "--viz-stride",
        type=int,
        default=5,
        help="Keep every Nth point in --viz-output.",
    )
    parser.add_argument(
        "--resolution",
        type=float,
        default=0.04,
        help="Surface sampling spacing in meters for primitive geoms.",
    )
    parser.add_argument(
        "--floor-padding",
        type=float,
        default=0.5,
        help="Padding around non-plane geoms when sampling finite plane geoms.",
    )
    parser.add_argument(
        "--asset-search-dir",
        action="append",
        default=[],
        help="Additional directory for hfield image assets. Can be specified multiple times.",
    )
    parser.add_argument(
        "--skip-hfield",
        action="store_true",
        help="Skip hfield geoms even when image assets are available.",
    )
    parser.add_argument(
        "--clip-min-z",
        type=float,
        default=None,
        help="Drop sampled points below this world z value. Useful for buried MJCF boxes.",
    )
    parser.add_argument(
        "--top-surface-box-max-thickness",
        type=float,
        default=0.22,
        help=(
            "Near-horizontal boxes no thicker than this full height are treated as walkable slabs. "
            "Their top and side surfaces stay in the main PCD, and their interior can be written to "
            "--forbidden-output so the planner cannot pass through the solid body. Set <= 0 to disable."
        ),
    )
    parser.add_argument(
        "--top-surface-up-axis-min-z",
        type=float,
        default=0.90,
        help=(
            "Minimum absolute world z component of a box local +Z axis before it can use top-surface-only "
            "sampling. Values near 1 restrict the rule to horizontal or gently sloped slabs."
        ),
    )
    parser.add_argument(
        "--forbidden-output",
        default="",
        help="Optional PCD containing floor points that should be marked as non-traversable by the planner.",
    )
    parser.add_argument(
        "--forbidden-volume-z-step",
        type=float,
        default=0.05,
        help="Vertical spacing in meters for forbidden volume samples inside top-surface boxes.",
    )
    parser.add_argument(
        "--remove-floor-under-top-surfaces",
        action="store_true",
        help="Remove sampled floor-plane points underneath top-surface-only boxes from the main output PCD.",
    )
    parser.add_argument(
        "--floor-clearance-margin",
        type=float,
        default=0.02,
        help="Extra XY margin in meters when removing floor-plane points under top-surface-only boxes.",
    )
    return parser.parse_args()


def floats(value: str | None, default: tuple[float, ...]) -> np.ndarray:
    if value is None:
        return np.array(default, dtype=np.float64)
    return np.array([float(v) for v in value.split()], dtype=np.float64)


def quat_to_matrix(quat: np.ndarray) -> np.ndarray:
    quat = quat.astype(np.float64, copy=True)
    norm = np.linalg.norm(quat)
    if norm == 0.0:
        return np.eye(3)
    w, x, y, z = quat / norm
    return np.array(
        [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ],
        dtype=np.float64,
    )


def transform_points(points: np.ndarray, geom: ET.Element) -> np.ndarray:
    pos = floats(geom.get("pos"), (0.0, 0.0, 0.0))
    quat = floats(geom.get("quat"), (1.0, 0.0, 0.0, 0.0))
    rotation = quat_to_matrix(quat)
    return points @ rotation.T + pos


def samples_between(low: float, high: float, resolution: float) -> np.ndarray:
    span = max(high - low, 0.0)
    count = max(2, int(math.ceil(span / resolution)) + 1)
    return np.linspace(low, high, count, dtype=np.float64)


def half_axis_samples(half_extent: float, resolution: float) -> np.ndarray:
    return samples_between(-half_extent, half_extent, resolution)


def box_top_surface_only(
    geom: ET.Element,
    max_thickness: float,
    up_axis_min_z: float,
) -> bool:
    if max_thickness <= 0.0:
        return False
    _, _, half_z = floats(geom.get("size"), (0.0, 0.0, 0.0))[:3]
    full_thickness = 2.0 * half_z
    if full_thickness > max_thickness:
        return False

    quat = floats(geom.get("quat"), (1.0, 0.0, 0.0, 0.0))
    rotation = quat_to_matrix(quat)
    local_z_in_world = rotation[:, 2]
    return abs(float(local_z_in_world[2])) >= up_axis_min_z


def sample_box(geom: ET.Element, resolution: float, top_surface_only: bool = False) -> np.ndarray:
    sx, sy, sz = floats(geom.get("size"), (0.0, 0.0, 0.0))[:3]
    xs = half_axis_samples(sx, resolution)
    ys = half_axis_samples(sy, resolution)
    faces: list[np.ndarray] = []

    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    faces.append(np.column_stack((xx.ravel(), yy.ravel(), np.full(xx.size, sz))))

    zs = half_axis_samples(sz, resolution)

    yy, zz = np.meshgrid(ys, zs, indexing="xy")
    for x in (-sx, sx):
        faces.append(np.column_stack((np.full(yy.size, x), yy.ravel(), zz.ravel())))

    xx, zz = np.meshgrid(xs, zs, indexing="xy")
    for y in (-sy, sy):
        faces.append(np.column_stack((xx.ravel(), np.full(xx.size, y), zz.ravel())))

    return transform_points(np.vstack(faces), geom)


def sample_box_forbidden_volume(geom: ET.Element, xy_resolution: float, z_step: float) -> np.ndarray:
    sx, sy, sz = floats(geom.get("size"), (0.0, 0.0, 0.0))[:3]
    if sx <= 0.0 or sy <= 0.0 or sz <= 0.0:
        return np.empty((0, 3), dtype=np.float64)

    xs = half_axis_samples(sx, xy_resolution)
    ys = half_axis_samples(sy, xy_resolution)
    step = max(z_step, 1.0e-3)
    top_exclusion = min(step * 0.5, sz * 0.5)
    z_high = sz - top_exclusion
    if z_high <= -sz:
        zs = np.array([-sz], dtype=np.float64)
    else:
        zs = np.arange(-sz, z_high + 1.0e-9, step, dtype=np.float64)
        if zs.size == 0:
            zs = np.array([-sz], dtype=np.float64)

    xx, yy, zz = np.meshgrid(xs, ys, zs, indexing="xy")
    local = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))
    return transform_points(local, geom)


def sample_cylinder(geom: ET.Element, resolution: float) -> np.ndarray:
    radius, half_height = floats(geom.get("size"), (0.0, 0.0))[:2]
    theta_count = max(12, int(math.ceil(2.0 * math.pi * radius / resolution)))
    height_count = max(2, int(math.ceil(2.0 * half_height / resolution)) + 1)
    theta = np.linspace(0.0, 2.0 * math.pi, theta_count, endpoint=False, dtype=np.float64)
    z_values = np.linspace(-half_height, half_height, height_count, dtype=np.float64)

    tt, zz = np.meshgrid(theta, z_values, indexing="xy")
    side = np.column_stack((radius * np.cos(tt.ravel()), radius * np.sin(tt.ravel()), zz.ravel()))

    radial_count = max(2, int(math.ceil(radius / resolution)) + 1)
    radial = np.linspace(0.0, radius, radial_count, dtype=np.float64)
    rr, tt = np.meshgrid(radial, theta, indexing="xy")
    cap_xy = np.column_stack((rr.ravel() * np.cos(tt.ravel()), rr.ravel() * np.sin(tt.ravel())))
    top = np.column_stack((cap_xy, np.full(cap_xy.shape[0], half_height)))
    bottom = np.column_stack((cap_xy, np.full(cap_xy.shape[0], -half_height)))

    return transform_points(np.vstack((side, top, bottom)), geom)


def sample_plane(geom: ET.Element, bounds: tuple[float, float, float, float], resolution: float) -> np.ndarray:
    min_x, max_x, min_y, max_y = bounds
    xs = samples_between(min_x, max_x, resolution)
    ys = samples_between(min_y, max_y, resolution)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    local = np.column_stack((xx.ravel(), yy.ravel(), np.zeros(xx.size, dtype=np.float64)))
    return transform_points(local, geom)


def box_footprint(geom: ET.Element) -> tuple[np.ndarray, np.ndarray, float, float]:
    pos = floats(geom.get("pos"), (0.0, 0.0, 0.0))
    quat = floats(geom.get("quat"), (1.0, 0.0, 0.0, 0.0))
    sx, sy, _ = floats(geom.get("size"), (0.0, 0.0, 0.0))[:3]
    return pos, quat_to_matrix(quat), float(sx), float(sy)


def split_floor_under_footprints(
    points: np.ndarray,
    footprints: list[tuple[np.ndarray, np.ndarray, float, float]],
    margin: float,
) -> tuple[np.ndarray, np.ndarray]:
    if not footprints or points.size == 0:
        return points, np.empty((0, 3), dtype=np.float64)

    remove = np.zeros(points.shape[0], dtype=bool)
    for pos, rotation, half_x, half_y in footprints:
        local = (points - pos) @ rotation
        remove |= (np.abs(local[:, 0]) <= half_x + margin) & (np.abs(local[:, 1]) <= half_y + margin)
    return points[~remove], points[remove]


def resolve_asset(asset_file: str, xml_path: Path, search_dirs: list[Path]) -> Path | None:
    candidates = [xml_path.parent / asset_file]
    asset_name = Path(asset_file).name
    for search_dir in search_dirs:
        candidates.append(search_dir / asset_file)
        candidates.append(search_dir / asset_name)
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def sample_hfield(
    geom: ET.Element,
    hfield_assets: dict[str, ET.Element],
    xml_path: Path,
    search_dirs: list[Path],
) -> tuple[np.ndarray | None, str | None]:
    hfield_name = geom.get("hfield")
    if not hfield_name or hfield_name not in hfield_assets:
        return None, f"missing hfield asset {hfield_name!r}"

    asset = hfield_assets[hfield_name]
    size = floats(asset.get("size"), (0.0, 0.0, 0.0, 0.0))
    if size.size < 4:
        return None, f"hfield {hfield_name!r} has invalid size"

    asset_file = asset.get("file")
    if not asset_file:
        return None, f"hfield {hfield_name!r} has no file"
    image_path = resolve_asset(asset_file, xml_path, search_dirs)
    if image_path is None:
        return None, f"hfield image not found: {asset_file}"

    image = Image.open(image_path).convert("L")
    height = np.asarray(image, dtype=np.float64) / 255.0
    rows, cols = height.shape
    xs = np.linspace(-size[0], size[0], cols, dtype=np.float64)
    ys = np.linspace(-size[1], size[1], rows, dtype=np.float64)
    xx, yy = np.meshgrid(xs, ys, indexing="xy")
    zz = height * size[2]
    local = np.column_stack((xx.ravel(), yy.ravel(), zz.ravel()))
    return transform_points(local, geom), str(image_path)


def include_geom(geom: ET.Element) -> bool:
    if geom.get("contype") == "0" and geom.get("conaffinity") == "0":
        return False
    return True


def direct_world_geoms(root: ET.Element) -> list[ET.Element]:
    worldbody = root.find("worldbody")
    if worldbody is None:
        raise RuntimeError("MJCF has no worldbody.")
    return [child for child in list(worldbody) if child.tag == "geom"]


def estimate_geom_xy_bounds(
    geom: ET.Element,
    resolution: float,
    hfield_assets: dict[str, ET.Element],
    xml_path: Path,
    search_dirs: list[Path],
    skip_hfield: bool,
) -> np.ndarray | None:
    geom_type = geom.get("type", "sphere")
    if geom_type == "plane" or not include_geom(geom):
        return None
    try:
        if geom_type == "box":
            points = sample_box(geom, max(resolution * 5.0, 0.2))
        elif geom_type == "cylinder":
            points = sample_cylinder(geom, max(resolution * 5.0, 0.2))
        elif geom_type == "hfield" and not skip_hfield:
            points, _ = sample_hfield(geom, hfield_assets, xml_path, search_dirs)
            if points is None:
                return None
        else:
            return None
    except Exception:
        return None
    return np.array([points[:, 0].min(), points[:, 0].max(), points[:, 1].min(), points[:, 1].max()])


def compute_plane_bounds(
    geoms: list[ET.Element],
    resolution: float,
    hfield_assets: dict[str, ET.Element],
    xml_path: Path,
    search_dirs: list[Path],
    skip_hfield: bool,
    padding: float,
) -> tuple[float, float, float, float]:
    bounds = [
        bound
        for geom in geoms
        if (bound := estimate_geom_xy_bounds(geom, resolution, hfield_assets, xml_path, search_dirs, skip_hfield))
        is not None
    ]
    if not bounds:
        return (-5.0, 5.0, -5.0, 5.0)
    stacked = np.vstack(bounds)
    return (
        float(stacked[:, 0].min() - padding),
        float(stacked[:, 1].max() + padding),
        float(stacked[:, 2].min() - padding),
        float(stacked[:, 3].max() + padding),
    )


def write_ascii_pcd(path: Path, points: np.ndarray) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tmp.open("w", encoding="ascii") as handle:
        handle.write("# .PCD v0.7 - Point Cloud Data file format\n")
        handle.write("VERSION 0.7\n")
        handle.write("FIELDS x y z\n")
        handle.write("SIZE 4 4 4\n")
        handle.write("TYPE F F F\n")
        handle.write("COUNT 1 1 1\n")
        handle.write(f"WIDTH {len(points)}\n")
        handle.write("HEIGHT 1\n")
        handle.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        handle.write(f"POINTS {len(points)}\n")
        handle.write("DATA ascii\n")
        np.savetxt(handle, points.astype(np.float32), fmt="%.6f %.6f %.6f")
    os.replace(tmp, path)


def main() -> None:
    args = parse_args()
    if args.resolution <= 0.0:
        raise RuntimeError("--resolution must be positive.")
    if args.forbidden_volume_z_step <= 0.0:
        raise RuntimeError("--forbidden-volume-z-step must be positive.")
    if args.viz_stride < 1:
        raise RuntimeError("--viz-stride must be >= 1.")
    if not 0.0 <= args.top_surface_up_axis_min_z <= 1.0:
        raise RuntimeError("--top-surface-up-axis-min-z must be in [0, 1].")

    xml_path = Path(args.xml).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    search_dirs = [Path(item).expanduser().resolve() for item in args.asset_search_dir]

    root = ET.parse(xml_path).getroot()
    hfield_assets = {asset.get("name"): asset for asset in root.findall("./asset/hfield") if asset.get("name")}
    geoms = direct_world_geoms(root)
    plane_bounds = compute_plane_bounds(
        geoms,
        args.resolution,
        hfield_assets,
        xml_path,
        search_dirs,
        args.skip_hfield,
        args.floor_padding,
    )

    included = Counter()
    excluded = Counter()
    hfield_sources: list[str] = []
    clouds: list[np.ndarray] = []
    forbidden_clouds: list[np.ndarray] = []
    top_surface_footprints: list[tuple[np.ndarray, np.ndarray, float, float]] = []

    if args.forbidden_output or args.remove_floor_under_top_surfaces:
        for geom in geoms:
            if geom.get("type", "sphere") != "box" or not include_geom(geom):
                continue
            if box_top_surface_only(
                geom,
                args.top_surface_box_max_thickness,
                args.top_surface_up_axis_min_z,
            ):
                top_surface_footprints.append(box_footprint(geom))

    for geom in geoms:
        geom_type = geom.get("type", "sphere")
        if not include_geom(geom):
            excluded[f"{geom_type}:visual"] += 1
            continue
        if geom_type == "box":
            top_surface_only = box_top_surface_only(
                geom,
                args.top_surface_box_max_thickness,
                args.top_surface_up_axis_min_z,
            )
            clouds.append(sample_box(geom, args.resolution, top_surface_only))
            if top_surface_only and args.forbidden_output:
                forbidden_volume = sample_box_forbidden_volume(
                    geom,
                    args.resolution,
                    args.forbidden_volume_z_step,
                )
                if forbidden_volume.size:
                    forbidden_clouds.append(forbidden_volume)
                    included["box:forbidden_volume_points"] += len(forbidden_volume)
            included["box:top_surface"] += int(top_surface_only)
            included["box:solid_surface"] += int(not top_surface_only)
        elif geom_type == "cylinder":
            clouds.append(sample_cylinder(geom, args.resolution))
            included[geom_type] += 1
        elif geom_type == "plane":
            plane_points = sample_plane(geom, plane_bounds, args.resolution)
            kept_plane_points, forbidden_plane_points = split_floor_under_footprints(
                plane_points,
                top_surface_footprints,
                args.floor_clearance_margin,
            )
            if forbidden_plane_points.size:
                forbidden_clouds.append(forbidden_plane_points)
            included["plane:forbidden_floor_points"] += len(forbidden_plane_points)
            if args.remove_floor_under_top_surfaces:
                included["plane:floor_points_removed"] += len(forbidden_plane_points)
                clouds.append(kept_plane_points)
            else:
                clouds.append(plane_points)
            included[geom_type] += 1
        elif geom_type == "hfield":
            if args.skip_hfield:
                excluded["hfield:skipped"] += 1
                continue
            points, source = sample_hfield(geom, hfield_assets, xml_path, search_dirs)
            if points is None:
                excluded["hfield:missing_asset"] += 1
                print(f"warning: {source}")
                continue
            clouds.append(points)
            hfield_sources.append(source or "")
            included[geom_type] += 1
        else:
            excluded[f"{geom_type}:unsupported"] += 1

    if not clouds:
        raise RuntimeError("No terrain points were generated.")

    points = np.vstack(clouds)
    finite = np.isfinite(points).all(axis=1)
    points = points[finite]
    if args.clip_min_z is not None:
        points = points[points[:, 2] >= args.clip_min_z]

    write_ascii_pcd(output, points)
    if args.viz_output:
        write_ascii_pcd(Path(args.viz_output).expanduser().resolve(), points[:: args.viz_stride])
    if args.forbidden_output:
        forbidden_points = (
            np.vstack(forbidden_clouds)
            if forbidden_clouds
            else np.empty((0, 3), dtype=np.float64)
        )
        write_ascii_pcd(Path(args.forbidden_output).expanduser().resolve(), forbidden_points)

    print(f"input: {xml_path}")
    print(f"output: {output}")
    if args.viz_output:
        print(f"viz_output: {Path(args.viz_output).expanduser().resolve()} stride={args.viz_stride}")
    if args.forbidden_output:
        print(f"forbidden_output: {Path(args.forbidden_output).expanduser().resolve()}")
    print(f"resolution: {args.resolution}")
    print(f"top_surface_box_max_thickness: {args.top_surface_box_max_thickness}")
    print(f"top_surface_up_axis_min_z: {args.top_surface_up_axis_min_z}")
    print(f"forbidden_volume_z_step: {args.forbidden_volume_z_step}")
    print(f"remove_floor_under_top_surfaces: {args.remove_floor_under_top_surfaces}")
    print(f"floor_clearance_margin: {args.floor_clearance_margin}")
    if args.clip_min_z is not None:
        print(f"clip_min_z: {args.clip_min_z}")
    print(f"plane_bounds: x=[{plane_bounds[0]:.3f}, {plane_bounds[1]:.3f}], y=[{plane_bounds[2]:.3f}, {plane_bounds[3]:.3f}]")
    print(f"included geoms: {dict(included)}")
    print(f"excluded geoms: {dict(excluded)}")
    if hfield_sources:
        print("hfield_sources:")
        for source in hfield_sources:
            print(f"  {source}")
    print(f"points: {len(points)}")
    print(f"min xyz: {points[:, 0].min():.6f}, {points[:, 1].min():.6f}, {points[:, 2].min():.6f}")
    print(f"max xyz: {points[:, 0].max():.6f}, {points[:, 1].max():.6f}, {points[:, 2].max():.6f}")


if __name__ == "__main__":
    main()
