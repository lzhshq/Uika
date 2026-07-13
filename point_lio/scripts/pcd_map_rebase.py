#!/usr/bin/env python3
import argparse
import math
import sys
from pathlib import Path

import numpy as np


def read_binary_pcd(path):
    header = {}

    with path.open("rb") as stream:
        while True:
            line = stream.readline()
            if not line:
                raise ValueError("PCD header ended before DATA line")
            decoded = line.decode("ascii", errors="strict").strip()
            if decoded and not decoded.startswith("#"):
                parts = decoded.split()
                header[parts[0].upper()] = parts[1:]
            if decoded.upper().startswith("DATA "):
                data_offset = stream.tell()
                break

        if header.get("DATA", [""])[0].lower() != "binary":
            raise ValueError("Only binary PCD files are supported")

        fields = header.get("FIELDS", header.get("FIELD", []))
        sizes = [int(value) for value in header.get("SIZE", [])]
        types = header.get("TYPE", [])
        counts = [int(value) for value in header.get("COUNT", ["1"] * len(fields))]
        points = int(header["POINTS"][0])

        if not fields or not {"x", "y", "z"}.issubset(fields):
            raise ValueError("PCD must contain x, y, and z fields")
        if len(sizes) != len(fields) or len(types) != len(fields):
            raise ValueError("Malformed PCD field metadata")
        if any(count != 1 for count in counts):
            raise ValueError("Only scalar PCD fields are supported")
        if any(size != 4 or field_type != "F" for size, field_type in zip(sizes, types)):
            raise ValueError("Only float32 Point-LIO PCD fields are supported")

        stream.seek(data_offset)
        raw = np.fromfile(stream, dtype=np.float32, count=points * len(fields))

    if raw.size != points * len(fields):
        raise ValueError(
            f"PCD payload is truncated: expected {points * len(fields)} floats, got {raw.size}"
        )

    return raw.reshape(points, len(fields)), fields, sizes, types, counts


def write_binary_pcd(path, cloud, fields, sizes, types, counts):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    points = cloud.shape[0]
    header = (
        "# .PCD v0.7 - Point Cloud Data file format\n"
        "VERSION 0.7\n"
        f"FIELDS {' '.join(fields)}\n"
        f"SIZE {' '.join(str(value) for value in sizes)}\n"
        f"TYPE {' '.join(types)}\n"
        f"COUNT {' '.join(str(value) for value in counts)}\n"
        f"WIDTH {points}\n"
        "HEIGHT 1\n"
        "VIEWPOINT 0 0 0 1 0 0 0\n"
        f"POINTS {points}\n"
        "DATA binary\n"
    )

    with temporary.open("wb") as stream:
        stream.write(header.encode("ascii"))
        np.asarray(cloud, dtype=np.float32).tofile(stream)
    temporary.replace(path)


def collect_clicked_points(topic, expected_frame):
    import rclpy
    from geometry_msgs.msg import PointStamped

    selected = []
    rclpy.init()
    node = rclpy.create_node("pcd_map_rebase_selector")

    def callback(message):
        if message.header.frame_id != expected_frame:
            node.get_logger().error(
                f"Expected clicks in frame '{expected_frame}', got '{message.header.frame_id}'"
            )
            return
        point = np.array(
            [message.point.x, message.point.y, message.point.z], dtype=np.float64
        )
        selected.append(point)
        if len(selected) == 1:
            node.get_logger().info(
                f"Origin selected at {point.tolist()}; now click a point along +X"
            )
        elif len(selected) == 2:
            node.get_logger().info(f"+X reference selected at {point.tolist()}")

    subscription = node.create_subscription(PointStamped, topic, callback, 10)
    node.get_logger().info(
        f"Waiting on {topic}: click the new origin, then click a point along new +X"
    )
    try:
        while rclpy.ok() and len(selected) < 2:
            rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        node.destroy_subscription(subscription)
        node.destroy_node()
        rclpy.shutdown()

    if len(selected) != 2:
        raise RuntimeError("Point selection was interrupted")
    return selected[0], selected[1]


def build_rebase_transform(origin, x_axis_point):
    direction = x_axis_point[:2] - origin[:2]
    distance = float(np.linalg.norm(direction))
    if distance < 0.10:
        raise ValueError("The +X reference must be at least 0.10 m from the origin")

    heading = math.atan2(direction[1], direction[0])
    cosine = math.cos(heading)
    sine = math.sin(heading)
    rotation = np.array(
        [[cosine, sine, 0.0], [-sine, cosine, 0.0], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    translation = -(rotation @ origin)
    return rotation, translation, heading


def transform_cloud(cloud, fields, rotation, translation):
    transformed = cloud.copy()
    xyz_indices = [fields.index(name) for name in ("x", "y", "z")]
    xyz = cloud[:, xyz_indices].astype(np.float64)
    transformed[:, xyz_indices] = (xyz @ rotation.T + translation).astype(np.float32)

    normal_names = ("normal_x", "normal_y", "normal_z")
    if all(name in fields for name in normal_names):
        normal_indices = [fields.index(name) for name in normal_names]
        normals = cloud[:, normal_indices].astype(np.float64)
        transformed[:, normal_indices] = (normals @ rotation.T).astype(np.float32)
    return transformed


def write_transform_metadata(
    path, source_pcd, output_pcd, frame, origin, x_axis_point, rotation, translation, heading
):
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = rotation
    matrix[:3, 3] = translation
    rows = "\n".join(
        "    - [" + ", ".join(f"{value:.12f}" for value in row) + "]"
        for row in matrix
    )
    text = (
        f"source_pcd: {source_pcd}\n"
        f"output_pcd: {output_pcd}\n"
        f"selection_frame: {frame}\n"
        "transform_equation: p_rebased = R * p_original + t\n"
        "origin_in_source: ["
        + ", ".join(f"{value:.12f}" for value in origin)
        + "]\n"
        "x_axis_point_in_source: ["
        + ", ".join(f"{value:.12f}" for value in x_axis_point)
        + "]\n"
        f"source_x_heading_rad: {heading:.12f}\n"
        f"source_to_target_yaw_rad: {-heading:.12f}\n"
        "source_to_target_matrix:\n"
        f"{rows}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="ascii")


def main():
    parser = argparse.ArgumentParser(
        description="Rebase a Point-LIO PCD using a selected origin and +X direction."
    )
    parser.add_argument("pcd", type=Path, help="Input Point-LIO binary PCD")
    parser.add_argument("--output", type=Path, required=True, help="Output rebased PCD")
    parser.add_argument(
        "--metadata", type=Path, help="Transform YAML; defaults beside the output PCD"
    )
    parser.add_argument("--interactive", action="store_true", help="Use two RViz clicks")
    parser.add_argument("--topic", default="/clicked_point")
    parser.add_argument("--frame", default="map")
    parser.add_argument("--origin", nargs=3, type=float, metavar=("X", "Y", "Z"))
    parser.add_argument("--x-axis", nargs=2, type=float, metavar=("X", "Y"))
    parser.add_argument(
        "--origin-z", type=float, help="Override the Z value of the selected origin"
    )
    try:
        from rclpy.utilities import remove_ros_args

        command_line = remove_ros_args(args=sys.argv)[1:]
    except ImportError:
        command_line = sys.argv[1:]
    args = parser.parse_args(command_line)

    if args.output.exists():
        parser.error(f"Output already exists: {args.output}")
    if args.interactive and (args.origin or args.x_axis):
        parser.error("Use either --interactive or explicit --origin/--x-axis values")

    if args.interactive:
        origin, x_axis_point = collect_clicked_points(args.topic, args.frame)
    else:
        if args.origin is None or args.x_axis is None:
            parser.error("Explicit mode requires --origin X Y Z and --x-axis X Y")
        origin = np.array(args.origin, dtype=np.float64)
        x_axis_point = np.array(
            [args.x_axis[0], args.x_axis[1], origin[2]], dtype=np.float64
        )

    if args.origin_z is not None:
        origin[2] = args.origin_z

    cloud, fields, sizes, types, counts = read_binary_pcd(args.pcd)
    rotation, translation, heading = build_rebase_transform(origin, x_axis_point)
    transformed = transform_cloud(cloud, fields, rotation, translation)
    write_binary_pcd(args.output, transformed, fields, sizes, types, counts)

    metadata = args.metadata or args.output.with_suffix(".transform.yaml")
    write_transform_metadata(
        metadata,
        args.pcd,
        args.output,
        args.frame,
        origin,
        x_axis_point,
        rotation,
        translation,
        heading,
    )

    transformed_origin = rotation @ origin + translation
    transformed_x_axis = rotation @ x_axis_point + translation
    print(f"points: {cloud.shape[0]}")
    print(f"selected heading: {math.degrees(heading):.6f} deg")
    print(f"origin check: {transformed_origin.tolist()}")
    print(f"+X check: {transformed_x_axis.tolist()}")
    print(f"wrote: {args.output}")
    print(f"wrote: {metadata}")


if __name__ == "__main__":
    main()
