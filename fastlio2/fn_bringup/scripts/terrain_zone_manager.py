#!/usr/bin/env python3
"""Segment a planned path by manually annotated terrain zones."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import Marker, MarkerArray


def load_zones(path: Path) -> tuple[str, list[dict[str, Any]]]:
    if not path.exists():
        return "map", []
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return str(data.get("frame_id", "map")), list(data.get("zones", []))


def polygon_pairs(polygon: list[Any]) -> list[tuple[float, float]]:
    values = [float(v) for v in polygon]
    return [(values[i], values[i + 1]) for i in range(0, len(values) - 1, 2)]


def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    if len(polygon) < 3:
        return False
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) if abs(yj - yi) > 1.0e-9 else 1.0e-9) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def color_for_type(zone_type: str) -> tuple[float, float, float]:
    palette = {
        "normal": (1.0, 1.0, 0.0),
        "stairs": (1.0, 0.55, 0.05),
        "bridge": (0.10, 0.70, 1.0),
        "slope": (0.35, 0.95, 0.35),
        "wall": (1.0, 0.15, 0.15),
        "low_bar": (0.85, 0.35, 1.0),
        "gravel": (0.85, 0.75, 0.30),
        "pole_slalom": (0.20, 0.45, 1.0),
        "obstacle": (0.05, 0.25, 1.0),
    }
    return palette.get(zone_type, (0.8, 0.8, 0.8))


class TerrainZoneManager(Node):
    def __init__(self) -> None:
        super().__init__("terrain_zone_manager")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter("zones_file", str(Path(bringup_dir) / "config" / "uika_terrain_zones.yaml"))
        self.declare_parameter("planned_path_topic", "/planned_path")
        self.declare_parameter("zone_marker_topic", "/terrain_zones")
        self.declare_parameter("segment_marker_topic", "/terrain_path_segments")
        self.declare_parameter("segments_topic", "/terrain_segments")
        self.declare_parameter("current_terrain_topic", "/current_terrain")
        self.declare_parameter("reload_period", 1.0)

        self.zones_file = Path(self.get_parameter("zones_file").value).expanduser()
        self.frame_id = "map"
        self.zones: list[dict[str, Any]] = []
        self.zone_polygons: list[tuple[dict[str, Any], list[tuple[float, float]]]] = []
        self.last_mtime: float | None = None

        transient_qos = rclpy.qos.QoSProfile(depth=1)
        transient_qos.durability = rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        transient_qos.reliability = rclpy.qos.ReliabilityPolicy.RELIABLE

        self.zone_marker_pub = self.create_publisher(
            MarkerArray, self.get_parameter("zone_marker_topic").value, transient_qos
        )
        self.segment_marker_pub = self.create_publisher(
            MarkerArray, self.get_parameter("segment_marker_topic").value, transient_qos
        )
        self.segments_pub = self.create_publisher(String, self.get_parameter("segments_topic").value, transient_qos)
        self.current_terrain_pub = self.create_publisher(
            String, self.get_parameter("current_terrain_topic").value, transient_qos
        )
        self.path_sub = self.create_subscription(
            PathMsg,
            self.get_parameter("planned_path_topic").value,
            self.on_path,
            transient_qos,
        )

        self.timer = self.create_timer(float(self.get_parameter("reload_period").value), self.reload_if_needed)
        self.reload(force=True)
        self.get_logger().info(f"terrain_zone_manager ready. zones_file={self.zones_file}")

    def reload_if_needed(self) -> None:
        self.reload(force=False)

    def reload(self, force: bool) -> None:
        mtime = self.zones_file.stat().st_mtime if self.zones_file.exists() else None
        if not force and mtime == self.last_mtime:
            return
        self.last_mtime = mtime
        self.frame_id, zones = load_zones(self.zones_file)
        self.zones = zones
        self.zone_polygons = []
        for zone in zones:
            pairs = polygon_pairs(zone.get("polygon", []))
            if len(pairs) >= 3:
                self.zone_polygons.append((zone, pairs))
        self.publish_zone_markers()
        self.get_logger().info(f"Loaded {len(self.zone_polygons)} terrain zones.")

    def classify_point(self, x: float, y: float) -> dict[str, Any]:
        for zone, polygon in self.zone_polygons:
            if point_in_polygon(x, y, polygon):
                zone_type = str(zone.get("type", "unknown"))
                label: dict[str, Any] = {
                    "type": zone_type,
                    "zone_id": str(zone.get("id", zone_type)),
                    "policy": str(zone.get("policy", f"{zone_type}_policy")),
                }
                if "safe_margin" in zone:
                    label["safe_margin"] = float(zone["safe_margin"])
                if "traversable" in zone:
                    label["traversable"] = bool(zone["traversable"])
                return label
        return {"type": "normal", "zone_id": "", "policy": "normal_walk", "traversable": True}

    def on_path(self, msg: PathMsg) -> None:
        if not msg.poses:
            self.publish_segments([], msg)
            return

        labels = [
            self.classify_point(pose.pose.position.x, pose.pose.position.y)
            for pose in msg.poses
        ]
        segments: list[dict[str, Any]] = []
        start = 0
        for idx in range(1, len(labels)):
            if labels[idx] != labels[start]:
                segments.append(self.make_segment(labels[start], start, idx - 1, msg))
                start = idx
        segments.append(self.make_segment(labels[start], start, len(labels) - 1, msg))

        self.publish_segments(segments, msg)
        terrain_summary = next((seg["type"] for seg in segments if seg["type"] != "normal"), "normal")
        self.current_terrain_pub.publish(String(data=terrain_summary))
        self.get_logger().info(
            "Path terrain segments: "
            + " -> ".join(
                f"{seg['type']}({seg['zone_id'] or 'none'}:{seg['start_index']}-{seg['end_index']})"
                for seg in segments
            )
        )

    def make_segment(self, label: dict[str, Any], start: int, end: int, msg: PathMsg) -> dict[str, Any]:
        start_pose = msg.poses[start].pose.position
        end_pose = msg.poses[end].pose.position
        length = 0.0
        for i in range(start + 1, end + 1):
            p0 = msg.poses[i - 1].pose.position
            p1 = msg.poses[i].pose.position
            length += math.dist((p0.x, p0.y, p0.z), (p1.x, p1.y, p1.z))
        segment = {
            "type": label["type"],
            "zone_id": label["zone_id"],
            "policy": label["policy"],
            "start_index": start,
            "end_index": end,
            "length": round(length, 3),
            "entry": [round(start_pose.x, 4), round(start_pose.y, 4), round(start_pose.z, 4)],
            "exit": [round(end_pose.x, 4), round(end_pose.y, 4), round(end_pose.z, 4)],
        }
        if "safe_margin" in label:
            segment["safe_margin"] = label["safe_margin"]
        if "traversable" in label:
            segment["traversable"] = label["traversable"]
        return segment

    def publish_segments(self, segments: list[dict[str, Any]], path_msg: PathMsg) -> None:
        payload = {
            "frame_id": path_msg.header.frame_id or self.frame_id,
            "stamp": {
                "sec": int(path_msg.header.stamp.sec),
                "nanosec": int(path_msg.header.stamp.nanosec),
            },
            "segments": segments,
        }
        self.segments_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))
        self.publish_segment_markers(segments, path_msg)

    def publish_zone_markers(self) -> None:
        markers = MarkerArray()
        markers.markers.append(delete_all_marker(self.frame_id))
        marker_id = 1
        for zone, polygon in self.zone_polygons:
            zone_type = str(zone.get("type", "unknown"))
            r, g, b = color_for_type(zone_type)
            points = [Point(x=x, y=y, z=0.08) for x, y in polygon]
            line = base_marker(self.frame_id, "terrain_zone_polygon", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            line.scale.x = 0.05
            line.color.r, line.color.g, line.color.b, line.color.a = r, g, b, 1.0
            line.points = points + [points[0]]
            markers.markers.append(line)

            label = base_marker(self.frame_id, "terrain_zone_label", marker_id, Marker.TEXT_VIEW_FACING)
            marker_id += 1
            label.pose.position.x = sum(x for x, _ in polygon) / len(polygon)
            label.pose.position.y = sum(y for _, y in polygon) / len(polygon)
            label.pose.position.z = 0.35
            label.scale.z = 0.22
            label.color.r, label.color.g, label.color.b, label.color.a = r, g, b, 1.0
            label.text = f"{zone.get('id', '')}:{zone_type}"
            markers.markers.append(label)
        self.zone_marker_pub.publish(markers)

    def publish_segment_markers(self, segments: list[dict[str, Any]], path_msg: PathMsg) -> None:
        markers = MarkerArray()
        markers.markers.append(delete_all_marker(path_msg.header.frame_id or self.frame_id))
        for marker_id, segment in enumerate(segments, start=1):
            points = []
            for i in range(segment["start_index"], segment["end_index"] + 1):
                p = path_msg.poses[i].pose.position
                points.append(Point(x=p.x, y=p.y, z=p.z + 0.08))
            if len(points) < 2:
                continue
            r, g, b = color_for_type(str(segment["type"]))
            marker = base_marker(path_msg.header.frame_id or self.frame_id, "terrain_path_segment", marker_id, Marker.LINE_STRIP)
            marker.scale.x = 0.12
            marker.color.r, marker.color.g, marker.color.b, marker.color.a = r, g, b, 1.0
            marker.points = points
            markers.markers.append(marker)
        self.segment_marker_pub.publish(markers)


def base_marker(frame_id: str, namespace: str, marker_id: int, marker_type: int) -> Marker:
    marker = Marker()
    marker.header.frame_id = frame_id
    marker.header.stamp = rclpy.clock.Clock().now().to_msg()
    marker.ns = namespace
    marker.id = marker_id
    marker.type = marker_type
    marker.action = Marker.ADD
    marker.pose.orientation.w = 1.0
    return marker


def delete_all_marker(frame_id: str) -> Marker:
    marker = Marker()
    marker.header.frame_id = frame_id
    marker.header.stamp = rclpy.clock.Clock().now().to_msg()
    marker.action = Marker.DELETEALL
    return marker


def main() -> None:
    rclpy.init()
    node = TerrainZoneManager()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
