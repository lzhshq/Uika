#!/usr/bin/env python3
"""Publish a configured slalom route and its safety geometry for RViz review."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from visualization_msgs.msg import Marker, MarkerArray


def point3(value: Any) -> tuple[float, float, float]:
    values = [float(item) for item in value]
    if len(values) < 2:
        raise ValueError(f"Expected at least x/y, got {value}")
    return values[0], values[1], values[2] if len(values) > 2 else 0.0


def sample_cubic_bezier(
    control_points: list[tuple[float, float, float]], samples: int
) -> list[tuple[float, float, float]]:
    p0, p1, p2, p3 = control_points
    result: list[tuple[float, float, float]] = []
    for index in range(max(samples, 2)):
        t = index / float(max(samples - 1, 1))
        u = 1.0 - t
        result.append(
            tuple(
                u**3 * p0[axis]
                + 3.0 * u**2 * t * p1[axis]
                + 3.0 * u * t**2 * p2[axis]
                + t**3 * p3[axis]
                for axis in range(3)
            )
        )
    return result


def sample_route(task: dict[str, Any]) -> list[tuple[float, float, float]]:
    bezier = task.get("bezier_path", {}) or {}
    samples = int(bezier.get("samples_per_segment", 18))
    route: list[tuple[float, float, float]] = []
    previous_end: tuple[float, float, float] | None = None
    for index, raw_segment in enumerate(bezier.get("segments", []) or []):
        if len(raw_segment) != 4:
            raise ValueError(f"Bezier segment {index} must contain four points")
        segment = [point3(raw_point) for raw_point in raw_segment]
        if previous_end is not None and math.dist(previous_end, segment[0]) > 1.0e-3:
            raise ValueError(f"Bezier segment {index} is not continuous")
        sampled = sample_cubic_bezier(segment, samples)
        route.extend(sampled if not route else sampled[1:])
        previous_end = segment[-1]
    if not route:
        route = [point3(raw_point) for raw_point in task.get("path_points", [])]
    if len(route) < 2:
        raise ValueError("Route needs at least two sampled points")
    return route


def yaw_quaternion(yaw: float) -> tuple[float, float]:
    return math.sin(0.5 * yaw), math.cos(0.5 * yaw)


class SlalomRoutePreview(Node):
    def __init__(self) -> None:
        super().__init__("slalom_route_preview")
        package_dir = Path(get_package_share_directory("point_lio"))
        self.declare_parameter(
            "route_file", str(package_dir / "config" / "raogan_15m_slalom.yaml")
        )
        self.declare_parameter("route_topic", "/slalom_route")
        self.declare_parameter("marker_topic", "/slalom_markers")
        self.declare_parameter("publish_markers", True)
        self.declare_parameter("publish_period_s", 2.0)

        self.route_file = Path(str(self.get_parameter("route_file").value))
        self.route_topic = str(self.get_parameter("route_topic").value)
        self.marker_topic = str(self.get_parameter("marker_topic").value)
        self.publish_markers = bool(self.get_parameter("publish_markers").value)

        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.route_pub = self.create_publisher(PathMsg, self.route_topic, qos)
        self.marker_pub = (
            self.create_publisher(MarkerArray, self.marker_topic, qos)
            if self.publish_markers
            else None
        )

        self.frame_id, self.task = self.load_config()
        self.route = sample_route(self.task)
        self.route_message = self.make_route_message()
        self.marker_message = self.make_marker_message() if self.publish_markers else None
        self.report_geometry()
        self.publish_preview()
        period = float(self.get_parameter("publish_period_s").value)
        self.timer = self.create_timer(period, self.publish_preview) if period > 0.0 else None

    def load_config(self) -> tuple[str, dict[str, Any]]:
        if not self.route_file.is_file():
            raise FileNotFoundError(f"Slalom route file not found: {self.route_file}")
        with self.route_file.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
        tasks = config.get("tasks", []) or []
        if len(tasks) != 1 or tasks[0].get("type") != "pole_slalom":
            raise ValueError("Preview config must contain exactly one pole_slalom task")
        if bool(config.get("control_output_enabled", False)):
            raise ValueError("Preview config must keep control_output_enabled=false")
        return str(config.get("frame_id", "map")), dict(tasks[0])

    def make_route_message(self) -> PathMsg:
        message = PathMsg()
        message.header.frame_id = self.frame_id
        z_offset = float(self.task.get("route_z_offset", 0.10))
        for index, (x, y, z) in enumerate(self.route):
            next_index = min(index + 1, len(self.route) - 1)
            previous_index = max(index - 1, 0)
            dx = self.route[next_index][0] - self.route[previous_index][0]
            dy = self.route[next_index][1] - self.route[previous_index][1]
            yaw = math.atan2(dy, dx)
            pose = PoseStamped()
            pose.header.frame_id = self.frame_id
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.position.z = z + z_offset
            pose.pose.orientation.z, pose.pose.orientation.w = yaw_quaternion(yaw)
            message.poses.append(pose)
        return message

    def marker(self, namespace: str, marker_id: int, marker_type: int) -> Marker:
        marker = Marker()
        marker.header.frame_id = self.frame_id
        marker.ns = namespace
        marker.id = marker_id
        marker.type = marker_type
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        return marker

    @staticmethod
    def ros_point(point: tuple[float, float, float], z_offset: float = 0.0) -> Point:
        return Point(x=point[0], y=point[1], z=point[2] + z_offset)

    def ring_marker(
        self,
        namespace: str,
        marker_id: int,
        center: tuple[float, float, float],
        radius: float,
        color: tuple[float, float, float, float],
    ) -> Marker:
        marker = self.marker(namespace, marker_id, Marker.LINE_STRIP)
        marker.scale.x = 0.025
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        for index in range(49):
            angle = 2.0 * math.pi * index / 48.0
            marker.points.append(
                Point(
                    x=center[0] + radius * math.cos(angle),
                    y=center[1] + radius * math.sin(angle),
                    z=center[2] + 0.035,
                )
            )
        return marker

    def sphere_marker(
        self,
        namespace: str,
        marker_id: int,
        center: tuple[float, float, float],
        diameter: float,
        color: tuple[float, float, float, float],
    ) -> Marker:
        marker = self.marker(namespace, marker_id, Marker.SPHERE)
        marker.pose.position = self.ros_point(center, diameter * 0.5)
        marker.scale.x = marker.scale.y = marker.scale.z = diameter
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        return marker

    def text_marker(
        self,
        marker_id: int,
        center: tuple[float, float, float],
        text: str,
    ) -> Marker:
        marker = self.marker("mission_task_label", marker_id, Marker.TEXT_VIEW_FACING)
        marker.pose.position = self.ros_point(center, 0.35)
        marker.scale.z = 0.16
        marker.color.r = marker.color.g = marker.color.b = marker.color.a = 1.0
        marker.text = text
        return marker

    def make_marker_message(self) -> MarkerArray:
        markers = MarkerArray()
        delete_all = Marker()
        delete_all.header.frame_id = self.frame_id
        delete_all.action = Marker.DELETEALL
        markers.markers.append(delete_all)
        marker_id = 1

        route_line = self.marker("mission_task_route", marker_id, Marker.LINE_STRIP)
        marker_id += 1
        route_line.scale.x = float(self.task.get("route_width", 0.045))
        route_line.color.r, route_line.color.g, route_line.color.b, route_line.color.a = [
            float(value) for value in self.task.get("route_color", [0.1, 0.55, 1.0, 1.0])
        ]
        z_offset = float(self.task.get("route_z_offset", 0.10))
        route_line.points = [self.ros_point(point, z_offset) for point in self.route]
        markers.markers.append(route_line)

        polygon = [point3(raw_point) for raw_point in self.task.get("zone_polygon", [])]
        if polygon:
            zone = self.marker("mission_zone", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            zone.scale.x = 0.025
            zone.color.r, zone.color.g, zone.color.b, zone.color.a = 0.2, 0.8, 1.0, 0.8
            zone.points = [self.ros_point(point, 0.04) for point in polygon + polygon[:1]]
            markers.markers.append(zone)

        pole_radius = float(self.task.get("estimated_pole_radius", 0.06))
        pole_height = float(self.task.get("estimated_pole_height", 0.80))
        required_clearance = (
            0.5 * float(self.task.get("robot_width", 0.41))
            + pole_radius
            + float(self.task.get("minimum_body_clearance", 0.05))
        )
        for index, raw_point in enumerate(self.task.get("pole_centers", []), start=1):
            center = point3(raw_point)
            pole = self.marker("mission_pole_center", marker_id, Marker.CYLINDER)
            marker_id += 1
            pole.pose.position = self.ros_point(center, pole_height * 0.5)
            pole.scale.x = pole.scale.y = 2.0 * pole_radius
            pole.scale.z = pole_height
            pole.color.r, pole.color.g, pole.color.b, pole.color.a = 1.0, 0.25, 0.05, 0.9
            markers.markers.append(pole)
            markers.markers.append(
                self.ring_marker(
                    "mission_pole_clearance",
                    marker_id,
                    center,
                    required_clearance,
                    (1.0, 0.1, 0.1, 0.75),
                )
            )
            marker_id += 1
            markers.markers.append(self.text_marker(marker_id, center, f"P{index}"))
            marker_id += 1

        mandatory_radius = float(self.task.get("mandatory_zone_radius", 0.175))
        for raw_point in self.task.get("mandatory_zones", []):
            markers.markers.append(
                self.ring_marker(
                    "mission_mandatory_zone",
                    marker_id,
                    point3(raw_point),
                    mandatory_radius,
                    (0.0, 1.0, 0.35, 0.9),
                )
            )
            marker_id += 1

        for raw_point in self.task.get("slalom_gates", []):
            markers.markers.append(
                self.sphere_marker(
                    "mission_slalom_gate",
                    marker_id,
                    point3(raw_point),
                    0.10,
                    (0.0, 0.9, 1.0, 0.9),
                )
            )
            marker_id += 1

        entry = point3(self.task["entry"])
        exit_point = point3(self.task["exit"])
        markers.markers.append(
            self.sphere_marker("mission_entry", marker_id, entry, 0.14, (0.1, 1.0, 0.1, 1.0))
        )
        marker_id += 1
        markers.markers.append(
            self.sphere_marker("mission_exit", marker_id, exit_point, 0.14, (1.0, 0.1, 1.0, 1.0))
        )
        marker_id += 1
        markers.markers.append(self.text_marker(marker_id, entry, "SLALOM START"))
        marker_id += 1
        markers.markers.append(self.text_marker(marker_id, exit_point, "SLALOM EXIT"))
        return markers

    def report_geometry(self) -> None:
        length = sum(math.dist(first[:2], second[:2]) for first, second in zip(self.route, self.route[1:]))
        pole_radius = float(self.task.get("estimated_pole_radius", 0.06))
        required = (
            0.5 * float(self.task.get("robot_width", 0.41))
            + pole_radius
            + float(self.task.get("minimum_body_clearance", 0.05))
        )
        clearances = []
        for raw_pole in self.task.get("pole_centers", []):
            pole = point3(raw_pole)
            clearances.append(min(math.dist(point[:2], pole[:2]) for point in self.route))
        self.get_logger().info(
            f"Loaded {len(self.route)} route points, length={length:.2f} m, "
            f"pole center clearances={[round(value, 3) for value in clearances]}"
        )
        if clearances and min(clearances) < required:
            self.get_logger().warning(
                f"Preview route minimum center clearance {min(clearances):.3f} m is below "
                f"the {required:.3f} m footprint check; do not enable motion yet"
            )

    def publish_preview(self) -> None:
        stamp = self.get_clock().now().to_msg()
        self.route_message.header.stamp = stamp
        for pose in self.route_message.poses:
            pose.header.stamp = stamp
        if self.marker_message is not None:
            for marker in self.marker_message.markers:
                marker.header.stamp = stamp
        self.route_pub.publish(self.route_message)
        if self.marker_pub is not None and self.marker_message is not None:
            self.marker_pub.publish(self.marker_message)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: SlalomRoutePreview | None = None
    try:
        node = SlalomRoutePreview()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
