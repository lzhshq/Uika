#!/usr/bin/env python3
"""Publish a transformed half-field mission for RViz review only."""

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
    return values[0], values[1], values[2] if len(values) > 2 else 0.0


def sample_bezier(raw_segments: list[Any], samples: int) -> list[tuple[float, float, float]]:
    route: list[tuple[float, float, float]] = []
    for raw_segment in raw_segments:
        if len(raw_segment) != 4:
            raise ValueError("Each Bezier segment must contain four control points")
        p0, p1, p2, p3 = [point3(value) for value in raw_segment]
        segment = []
        for index in range(max(samples, 2)):
            t = index / float(max(samples - 1, 1))
            u = 1.0 - t
            segment.append(
                tuple(
                    u**3 * p0[axis]
                    + 3.0 * u**2 * t * p1[axis]
                    + 3.0 * u * t**2 * p2[axis]
                    + t**3 * p3[axis]
                    for axis in range(3)
                )
            )
        route.extend(segment if not route else segment[1:])
    return route


def task_route(task: dict[str, Any]) -> list[tuple[float, float, float]]:
    bezier = task.get("bezier_path", {}) or {}
    segments = bezier.get("segments", []) or []
    if segments:
        return sample_bezier(segments, int(bezier.get("samples_per_segment", 12)))
    if task.get("path_points"):
        return [point3(value) for value in task["path_points"]]
    raw = [task.get("entry"), *(task.get("required_points", []) or []), task.get("exit")]
    return [point3(value) for value in raw if value is not None]


def contains_xy(
    polygon: list[tuple[float, float, float]], point: tuple[float, float]
) -> bool:
    inside = False
    px, py = point
    for first, second in zip(polygon, polygon[1:] + polygon[:1]):
        x1, y1 = first[:2]
        x2, y2 = second[:2]
        crosses = (y1 > py) != (y2 > py)
        if crosses and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


class CourseMissionPreview(Node):
    COLORS = {
        "stairs": (1.0, 0.55, 0.05, 1.0),
        "wall": (1.0, 0.15, 0.15, 1.0),
        "pole_slalom": (0.05, 0.55, 1.0, 1.0),
        "gravel": (0.95, 0.85, 0.05, 1.0),
        "low_bar": (0.7, 0.2, 1.0, 1.0),
        "slope": (0.1, 0.85, 0.25, 1.0),
        "bridge": (0.0, 0.9, 0.9, 1.0),
        "obstacle": (1.0, 0.2, 0.2, 1.0),
    }

    def __init__(self) -> None:
        super().__init__("course_mission_preview")
        share = Path(get_package_share_directory("point_lio"))
        self.declare_parameter(
            "config_file",
            str(share / "config" / "changdi_map_origin_half_mission.yaml"),
        )
        self.declare_parameter("route_topic", "/course_route")
        self.declare_parameter("marker_topic", "/course_markers")
        self.declare_parameter("publish_markers", True)
        self.declare_parameter("publish_period_s", -1.0)
        self.share = share
        self.config = self.read_yaml(Path(str(self.get_parameter("config_file").value)))
        if not bool(self.config.get("preview_only", False)):
            raise ValueError("Course preview config must set preview_only=true")
        if bool(self.config.get("control_output_enabled", False)):
            raise ValueError("Course preview cannot enable control output")

        source = self.config["source"]
        self.mission = self.read_yaml(self.resolve(source["mission_file"]))
        self.zones = self.read_yaml(self.resolve(source["zones_file"])).get("zones", [])
        self.frame_id = str(self.config.get("frame_id", "map"))
        self.active_ids = set(self.config.get("active_tasks", []))
        self.tasks = [task for task in self.mission.get("tasks", []) if task["id"] in self.active_ids]
        missing = self.active_ids - {task["id"] for task in self.tasks}
        if missing:
            raise ValueError(f"Unknown active task ids: {sorted(missing)}")

        alignment = self.config["alignment"]
        self.source_center = tuple(float(v) for v in alignment["source_center_xy"])
        self.target_center = tuple(float(v) for v in alignment["target_center_xy"])
        self.scale = float(alignment["scale"])
        self.yaw = float(alignment["yaw_rad"])
        self.mirror_y = bool(alignment.get("mirror_y", False))
        self.visual = self.config.get("visualization", {}) or {}
        self.publish_markers = bool(self.get_parameter("publish_markers").value)
        raw_route_start = self.config.get("route_start_map_xy")
        self.route_start = None
        if raw_route_start is not None:
            if len(raw_route_start) < 2:
                raise ValueError("route_start_map_xy must contain map X and Y")
            self.route_start = (
                float(raw_route_start[0]),
                float(raw_route_start[1]),
                float(self.visual.get("route_z", 0.08)),
            )
        self.half_polygon = self.make_half_polygon()
        if bool(alignment.get("required_map_origin_inside_half", False)) and not contains_xy(
            self.half_polygon, (0.0, 0.0)
        ):
            raise ValueError("Configured active half does not contain the map origin")

        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.route_pub = self.create_publisher(
            PathMsg, str(self.get_parameter("route_topic").value), qos
        )
        self.marker_pub = (
            self.create_publisher(
                MarkerArray, str(self.get_parameter("marker_topic").value), qos
            )
            if self.publish_markers
            else None
        )
        self.route = self.make_route()
        self.markers = self.make_markers() if self.publish_markers else None
        self.publish()
        period = float(self.get_parameter("publish_period_s").value)
        if period < 0.0:
            period = float(self.visual.get("publish_period_s", 2.0))
        self.timer = self.create_timer(period, self.publish) if period > 0.0 else None
        self.get_logger().warning(
            f"PREVIEW ONLY: published {len(self.tasks)} tasks and {len(self.route.poses)} route poses; "
            "no velocity or controller topic exists in this node"
        )

    @staticmethod
    def read_yaml(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as stream:
            return yaml.safe_load(stream) or {}

    def resolve(self, value: str) -> Path:
        path = Path(str(value))
        return path if path.is_absolute() else self.share / path

    def transform(self, raw: Any) -> tuple[float, float, float]:
        x, y, _ = point3(raw)
        dx = x - self.source_center[0]
        dy = y - self.source_center[1]
        if self.mirror_y:
            dy = -dy
        cosine = math.cos(self.yaw)
        sine = math.sin(self.yaw)
        return (
            self.target_center[0] + self.scale * (cosine * dx - sine * dy),
            self.target_center[1] + self.scale * (sine * dx + cosine * dy),
            float(self.visual.get("route_z", 0.08)),
        )

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
    def ros_point(value: tuple[float, float, float], z_add: float = 0.0) -> Point:
        return Point(x=value[0], y=value[1], z=value[2] + z_add)

    def transformed_route(self, task: dict[str, Any]) -> list[tuple[float, float, float]]:
        return [self.transform(value) for value in task_route(task)]

    def make_half_polygon(self) -> list[tuple[float, float, float]]:
        bounds = [float(v) for v in self.config["source"]["bounds_xy"]]
        return [
            self.transform((bounds[0], bounds[1], 0.0)),
            self.transform((bounds[2], bounds[1], 0.0)),
            self.transform((bounds[2], bounds[3], 0.0)),
            self.transform((bounds[0], bounds[3], 0.0)),
        ]

    def make_route(self) -> PathMsg:
        message = PathMsg()
        message.header.frame_id = self.frame_id
        all_points: list[tuple[float, float, float]] = (
            [self.route_start] if self.route_start is not None else []
        )
        for task in self.tasks:
            points = self.transformed_route(task)
            if not points:
                continue
            if all_points and math.dist(all_points[-1][:2], points[0][:2]) > 0.02:
                all_points.append(points[0])
            all_points.extend(points if not all_points else points[1:])
        for index, value in enumerate(all_points):
            previous = all_points[max(0, index - 1)]
            following = all_points[min(len(all_points) - 1, index + 1)]
            yaw = math.atan2(following[1] - previous[1], following[0] - previous[0])
            pose = PoseStamped()
            pose.header.frame_id = self.frame_id
            pose.pose.position = self.ros_point(value)
            pose.pose.orientation.z = math.sin(0.5 * yaw)
            pose.pose.orientation.w = math.cos(0.5 * yaw)
            message.poses.append(pose)
        return message

    def add_line(
        self,
        markers: list[Marker],
        marker_id: int,
        namespace: str,
        points: list[tuple[float, float, float]],
        color: tuple[float, float, float, float],
        width: float,
        closed: bool = False,
    ) -> int:
        if len(points) < 2:
            return marker_id
        marker = self.marker(namespace, marker_id, Marker.LINE_STRIP)
        marker.scale.x = width
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        values = points + points[:1] if closed else points
        marker.points = [self.ros_point(value) for value in values]
        markers.append(marker)
        return marker_id + 1

    def add_label(
        self, markers: list[Marker], marker_id: int, value: tuple[float, float, float], text: str
    ) -> int:
        marker = self.marker("course_labels", marker_id, Marker.TEXT_VIEW_FACING)
        marker.pose.position = self.ros_point(value, 0.20)
        marker.scale.z = 0.15
        marker.color.r = marker.color.g = marker.color.b = marker.color.a = 1.0
        marker.text = text
        markers.append(marker)
        return marker_id + 1

    def add_sphere(
        self,
        markers: list[Marker],
        marker_id: int,
        namespace: str,
        value: tuple[float, float, float],
        color: tuple[float, float, float, float],
    ) -> int:
        diameter = float(self.visual.get("point_diameter", 0.14))
        marker = self.marker(namespace, marker_id, Marker.SPHERE)
        marker.pose.position = self.ros_point(value, diameter * 0.5)
        marker.scale.x = marker.scale.y = marker.scale.z = diameter
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        markers.append(marker)
        return marker_id + 1

    def make_markers(self) -> MarkerArray:
        values: list[Marker] = []
        delete_all = Marker()
        delete_all.header.frame_id = self.frame_id
        delete_all.action = Marker.DELETEALL
        values.append(delete_all)
        marker_id = 1

        marker_id = self.add_line(
            values,
            marker_id,
            "active_half_boundary",
            self.half_polygon,
            (1.0, 0.9, 0.0, 0.95),
            float(self.visual.get("half_boundary_width", 0.06)),
            True,
        )

        if self.route_start is not None and self.tasks:
            first_route = self.transformed_route(self.tasks[0])
            if first_route:
                marker_id = self.add_line(
                    values,
                    marker_id,
                    "map_start_connector",
                    [self.route_start, first_route[0]],
                    (0.1, 0.65, 1.0, 1.0),
                    float(self.visual.get("route_width", 0.055)),
                )
                marker_id = self.add_sphere(
                    values,
                    marker_id,
                    "map_route_start",
                    self.route_start,
                    (0.1, 1.0, 0.1, 1.0),
                )
                marker_id = self.add_label(
                    values, marker_id, self.route_start, "map start (0, 0)"
                )

        for zone in self.zones:
            if zone["id"] not in self.active_ids and not zone["id"].startswith("low_bar_"):
                continue
            raw = zone.get("polygon", [])
            points = [self.transform(raw[index : index + 2]) for index in range(0, len(raw), 2)]
            color = self.COLORS.get(str(zone.get("type", "obstacle")), (0.8, 0.8, 0.8, 1.0))
            marker_id = self.add_line(
                values,
                marker_id,
                "course_zones",
                points,
                color,
                float(self.visual.get("zone_width", 0.035)),
                True,
            )

        for task in self.tasks:
            points = self.transformed_route(task)
            color = self.COLORS.get(str(task.get("type", "obstacle")), (0.8, 0.8, 0.8, 1.0))
            marker_id = self.add_line(
                values,
                marker_id,
                "task_routes",
                points,
                color,
                float(self.visual.get("route_width", 0.055)),
            )
            entry = self.transform(task["entry"])
            exit_point = self.transform(task["exit"])
            marker_id = self.add_sphere(values, marker_id, "task_entry", entry, (0.1, 1.0, 0.1, 1.0))
            marker_id = self.add_sphere(values, marker_id, "task_exit", exit_point, (1.0, 0.1, 0.9, 1.0))
            marker_id = self.add_label(
                values, marker_id, entry, f"{task['id']} / {task['policy']}"
            )

            if task.get("type") == "pole_slalom":
                for pole_index, raw_pole in enumerate(task.get("pole_centers", []), start=1):
                    pole = self.transform(raw_pole)
                    marker_id = self.add_sphere(
                        values, marker_id, "pole_centers", pole, (1.0, 0.2, 0.05, 1.0)
                    )
                    marker_id = self.add_label(values, marker_id, pole, f"P{pole_index}")

        return MarkerArray(markers=values)

    def publish(self) -> None:
        stamp = self.get_clock().now().to_msg()
        self.route.header.stamp = stamp
        for pose in self.route.poses:
            pose.header.stamp = stamp
        if self.markers is not None:
            for marker in self.markers.markers:
                marker.header.stamp = stamp
        self.route_pub.publish(self.route)
        if self.marker_pub is not None and self.markers is not None:
            self.marker_pub.publish(self.markers)


def main(args: list[str] | None = None) -> None:
    rclpy.init(args=args)
    node: CourseMissionPreview | None = None
    try:
        node = CourseMissionPreview()
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
