#!/usr/bin/env python3
"""RViz point-click helper for creating terrain zone polygons."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, PointStamped
from rclpy.node import Node
from std_msgs.msg import String
from visualization_msgs.msg import Marker, MarkerArray


def load_zone_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"frame_id": "map", "zones": []}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if "zones" not in data:
        data["zones"] = []
    if "frame_id" not in data:
        data["frame_id"] = "map"
    return data


def save_zone_file(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False, allow_unicode=True)
    tmp.replace(path)


def color_for_type(zone_type: str) -> tuple[float, float, float]:
    palette = {
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


class TerrainZoneSelector(Node):
    def __init__(self) -> None:
        super().__init__("terrain_zone_selector")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter("zones_file", str(Path(bringup_dir) / "config" / "uika_terrain_zones.yaml"))
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("clicked_topic", "/zone_clicked_point")
        self.declare_parameter("command_topic", "/zone_selector_command")
        self.declare_parameter("marker_topic", "/terrain_zones")
        self.declare_parameter("draft_marker_topic", "/terrain_zone_draft")

        self.zones_file = Path(self.get_parameter("zones_file").value).expanduser()
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.data = load_zone_file(self.zones_file)
        self.data["frame_id"] = self.frame_id

        self.active = False
        self.current_type = ""
        self.current_id = ""
        self.current_policy = ""
        self.current_points: list[tuple[float, float]] = []

        qos = rclpy.qos.QoSProfile(depth=1)
        qos.durability = rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        qos.reliability = rclpy.qos.ReliabilityPolicy.RELIABLE

        self.marker_pub = self.create_publisher(MarkerArray, self.get_parameter("marker_topic").value, qos)
        self.draft_pub = self.create_publisher(MarkerArray, self.get_parameter("draft_marker_topic").value, qos)
        self.clicked_sub = self.create_subscription(
            PointStamped,
            self.get_parameter("clicked_topic").value,
            self.on_clicked,
            10,
        )
        self.command_sub = self.create_subscription(
            String,
            self.get_parameter("command_topic").value,
            self.on_command,
            10,
        )
        self.timer = self.create_timer(1.0, self.publish_all_markers)

        self.get_logger().info(
            "terrain_zone_selector ready. Commands: start <type> <id> [policy], finish, undo, clear, delete <id>, reload."
        )
        self.publish_all_markers()

    def on_command(self, msg: String) -> None:
        tokens = msg.data.strip().split()
        if not tokens:
            return
        command = tokens[0].lower()
        if command == "start":
            if len(tokens) < 3:
                self.get_logger().warn("Usage: start <type> <id> [policy]")
                return
            self.current_type = tokens[1]
            self.current_id = tokens[2]
            self.current_policy = tokens[3] if len(tokens) >= 4 else f"{self.current_type}_policy"
            self.current_points = []
            self.active = True
            self.get_logger().info(
                f"Started zone draft id={self.current_id} type={self.current_type} policy={self.current_policy}"
            )
            self.publish_draft()
            return

        if command == "finish":
            self.finish_zone()
            return

        if command == "undo":
            if self.current_points:
                point = self.current_points.pop()
                self.get_logger().info(f"Removed draft vertex {point}")
                self.publish_draft()
            return

        if command in ("clear", "cancel"):
            self.active = False
            self.current_points = []
            self.publish_draft()
            self.get_logger().info("Cleared current zone draft.")
            return

        if command == "delete":
            if len(tokens) < 2:
                self.get_logger().warn("Usage: delete <id>")
                return
            zone_id = tokens[1]
            before = len(self.data.get("zones", []))
            self.data["zones"] = [z for z in self.data.get("zones", []) if z.get("id") != zone_id]
            if len(self.data["zones"]) != before:
                save_zone_file(self.zones_file, self.data)
                self.get_logger().info(f"Deleted zone {zone_id}")
                self.publish_all_markers()
            else:
                self.get_logger().warn(f"Zone {zone_id} not found.")
            return

        if command == "reload":
            self.data = load_zone_file(self.zones_file)
            self.data["frame_id"] = self.frame_id
            self.publish_all_markers()
            self.get_logger().info("Reloaded zone file.")
            return

        self.get_logger().warn(f"Unknown command: {msg.data}")

    def on_clicked(self, msg: PointStamped) -> None:
        if not self.active:
            self.get_logger().warn("Ignoring zone click. Send: start <type> <id> [policy]")
            return
        self.current_points.append((float(msg.point.x), float(msg.point.y)))
        self.get_logger().info(
            f"Added vertex {len(self.current_points)} for {self.current_id}: "
            f"({msg.point.x:.3f}, {msg.point.y:.3f})"
        )
        self.publish_draft()

    def finish_zone(self) -> None:
        if not self.active:
            self.get_logger().warn("No active zone draft.")
            return
        if len(self.current_points) < 3:
            self.get_logger().warn("A polygon needs at least 3 vertices.")
            return

        polygon: list[float] = []
        for x, y in self.current_points:
            polygon.extend([round(x, 4), round(y, 4)])
        zone = {
            "id": self.current_id,
            "type": self.current_type,
            "policy": self.current_policy,
            "polygon": polygon,
        }

        zones = [z for z in self.data.get("zones", []) if z.get("id") != self.current_id]
        zones.append(zone)
        self.data["zones"] = zones
        self.data["frame_id"] = self.frame_id
        save_zone_file(self.zones_file, self.data)

        self.get_logger().info(
            f"Saved zone {self.current_id} with {len(self.current_points)} vertices to {self.zones_file}"
        )
        self.active = False
        self.current_points = []
        self.publish_draft()
        self.publish_all_markers()

    def publish_all_markers(self) -> None:
        markers = MarkerArray()
        markers.markers.append(self.delete_all_marker())
        marker_id = 1
        for zone in self.data.get("zones", []):
            points = polygon_to_points(zone.get("polygon", []), self.frame_id)
            if len(points) < 3:
                continue
            zone_type = str(zone.get("type", "unknown"))
            r, g, b = color_for_type(zone_type)
            line = base_marker(self.frame_id, "terrain_zone_polygon", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            line.scale.x = 0.05
            line.color.r, line.color.g, line.color.b, line.color.a = r, g, b, 1.0
            line.points = points + [points[0]]
            markers.markers.append(line)

            label = base_marker(self.frame_id, "terrain_zone_label", marker_id, Marker.TEXT_VIEW_FACING)
            marker_id += 1
            cx = sum(p.x for p in points) / len(points)
            cy = sum(p.y for p in points) / len(points)
            label.pose.position.x = cx
            label.pose.position.y = cy
            label.pose.position.z = max(0.2, sum(p.z for p in points) / len(points) + 0.3)
            label.scale.z = 0.22
            label.color.r, label.color.g, label.color.b, label.color.a = r, g, b, 1.0
            label.text = f"{zone.get('id', '')}:{zone_type}"
            markers.markers.append(label)
        self.marker_pub.publish(markers)

    def publish_draft(self) -> None:
        markers = MarkerArray()
        markers.markers.append(self.delete_all_marker())
        if self.active and self.current_points:
            points = [Point(x=x, y=y, z=0.05) for x, y in self.current_points]
            marker = base_marker(self.frame_id, "terrain_zone_draft", 1, Marker.LINE_STRIP)
            marker.scale.x = 0.06
            marker.color.r, marker.color.g, marker.color.b, marker.color.a = 1.0, 1.0, 1.0, 1.0
            marker.points = points if len(points) < 3 else points + [points[0]]
            markers.markers.append(marker)
        self.draft_pub.publish(markers)

    def delete_all_marker(self) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.frame_id
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.action = Marker.DELETEALL
        return marker


def polygon_to_points(polygon: list[Any], frame_id: str) -> list[Point]:
    del frame_id
    values = [float(v) for v in polygon]
    points: list[Point] = []
    for i in range(0, len(values) - 1, 2):
        points.append(Point(x=values[i], y=values[i + 1], z=0.06))
    return points


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


def main() -> None:
    rclpy.init()
    node = TerrainZoneSelector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
