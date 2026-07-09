#!/usr/bin/env python3
"""Publish and step through a manually defined obstacle-course mission."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, PoseStamped
from nav_msgs.msg import Path as PathMsg
from rclpy.node import Node
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray


def point3(value: Any) -> tuple[float, float, float]:
    values = [float(v) for v in value]
    if len(values) < 2:
        raise ValueError(f"point needs at least x/y values: {value}")
    z = values[2] if len(values) >= 3 else 0.0
    return values[0], values[1], z


def pose4(value: Any) -> tuple[float, float, float, float]:
    values = [float(v) for v in value]
    if len(values) < 2:
        raise ValueError(f"pose needs at least x/y values: {value}")
    z = values[2] if len(values) >= 3 else 0.0
    yaw = values[3] if len(values) >= 4 else 0.0
    return values[0], values[1], z, yaw


def yaw_to_quat_z_w(yaw: float) -> tuple[float, float]:
    return math.sin(yaw * 0.5), math.cos(yaw * 0.5)


def color_for_type(task_type: str) -> tuple[float, float, float]:
    palette = {
        "normal": (1.0, 1.0, 0.0),
        "stairs": (1.0, 0.55, 0.05),
        "bridge": (0.10, 0.70, 1.0),
        "slope": (0.35, 0.95, 0.35),
        "wall": (1.0, 0.15, 0.15),
        "low_bar": (0.85, 0.35, 1.0),
        "gravel": (0.85, 0.75, 0.30),
        "pole_slalom": (0.20, 0.45, 1.0),
    }
    return palette.get(task_type, (0.85, 0.85, 0.85))


def sample_cubic_bezier(
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
    p3: tuple[float, float, float],
    samples: int,
) -> list[tuple[float, float, float]]:
    samples = max(samples, 2)
    points: list[tuple[float, float, float]] = []
    for i in range(samples):
        t = i / float(samples - 1)
        u = 1.0 - t
        x = u**3 * p0[0] + 3.0 * u**2 * t * p1[0] + 3.0 * u * t**2 * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3.0 * u**2 * t * p1[1] + 3.0 * u * t**2 * p2[1] + t**3 * p3[1]
        z = u**3 * p0[2] + 3.0 * u**2 * t * p1[2] + 3.0 * u * t**2 * p2[2] + t**3 * p3[2]
        points.append((x, y, z))
    return points


def task_bezier_points(task: dict[str, Any]) -> list[tuple[str, tuple[float, float, float]]]:
    bezier = task.get("bezier_path") or {}
    return [("path_point", point) for point in bezier_config_points(bezier)]


def bezier_config_points(bezier: Any) -> list[tuple[float, float, float]]:
    segments = bezier.get("segments", []) if isinstance(bezier, dict) else []
    samples = int(bezier.get("samples_per_segment", 12)) if isinstance(bezier, dict) else 12
    points: list[tuple[float, float, float]] = []
    for segment in segments:
        if not isinstance(segment, list) or len(segment) != 4:
            continue
        sampled = sample_cubic_bezier(
            point3(segment[0]),
            point3(segment[1]),
            point3(segment[2]),
            point3(segment[3]),
            samples,
        )
        if points and sampled:
            sampled = sampled[1:]
        points.extend(sampled)
    return points


def task_route_points(task: dict[str, Any]) -> list[tuple[str, tuple[float, float, float]]]:
    points: list[tuple[str, tuple[float, float, float]]] = []
    bezier_points = task_bezier_points(task)
    if bezier_points:
        return bezier_points
    if task.get("path_points"):
        return [("path_point", point3(raw_point)) for raw_point in task.get("path_points", []) or []]
    if "entry" in task:
        points.append(("entry", point3(task["entry"])))
    for raw_point in task.get("required_points", []) or []:
        points.append(("required", point3(raw_point)))
    if "exit" in task:
        points.append(("exit", point3(task["exit"])))
    return points


def route_color_for_task(task: dict[str, Any], default_color: tuple[float, float, float]) -> tuple[float, float, float, float]:
    raw_color = task.get("route_color")
    if isinstance(raw_color, list) and len(raw_color) >= 3:
        color = [float(value) for value in raw_color[:4]]
        while len(color) < 4:
            color.append(1.0)
        return color[0], color[1], color[2], color[3]
    return default_color[0], default_color[1], default_color[2], 1.0


def task_marker_points(task: dict[str, Any]) -> list[tuple[str, tuple[float, float, float]]]:
    points: list[tuple[str, tuple[float, float, float]]] = []
    hidden_markers = {str(item) for item in task.get("hidden_point_markers", []) or []}
    if "entry" in task:
        if "entry" not in hidden_markers:
            points.append(("entry", point3(task["entry"])))
    for raw_point in task.get("required_points", []) or []:
        if "required" not in hidden_markers:
            points.append(("required", point3(raw_point)))
    for raw_point in task.get("mandatory_zones", []) or []:
        if "mandatory_zone" not in hidden_markers:
            points.append(("mandatory_zone", point3(raw_point)))
    for raw_point in task.get("pole_centers", []) or []:
        if "pole_center" not in hidden_markers:
            points.append(("pole_center", point3(raw_point)))
    for raw_point in task.get("slalom_gates", []) or []:
        if "slalom_gate" not in hidden_markers:
            points.append(("slalom_gate", point3(raw_point)))
    if "exit" in task:
        if "exit" not in hidden_markers:
            points.append(("exit", point3(task["exit"])))
    return points


def task_constraints(task: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "path_mode",
        "require_straight_path",
        "max_lateral_error",
        "speed_limit",
        "min_distance_on_slope",
    )
    return {key: task[key] for key in keys if key in task}


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


class TerrainMissionManager(Node):
    def __init__(self) -> None:
        super().__init__("terrain_mission_manager")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter("mission_file", str(Path(bringup_dir) / "config" / "uika_obstacle_mission.yaml"))
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("mission_marker_topic", "/mission_markers")
        self.declare_parameter("mission_route_topic", "/mission_route")
        self.declare_parameter("mission_plan_topic", "/mission_plan")
        self.declare_parameter("current_task_topic", "/current_task")
        self.declare_parameter("current_policy_topic", "/current_policy")
        self.declare_parameter("mission_status_topic", "/mission_status")
        self.declare_parameter("command_topic", "/mission_command")
        self.declare_parameter("reload_period", 1.0)
        self.declare_parameter("publish_period", 0.5)
        self.declare_parameter("auto_advance", False)
        self.declare_parameter("task_reach_radius", 0.45)
        self.declare_parameter("publish_full_route_line", False)
        self.declare_parameter("publish_connector_lines", True)

        self.mission_file = Path(str(self.get_parameter("mission_file").value)).expanduser()
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.auto_advance = bool(self.get_parameter("auto_advance").value)
        self.task_reach_radius = float(self.get_parameter("task_reach_radius").value)
        self.publish_full_route_line = bool(self.get_parameter("publish_full_route_line").value)
        self.publish_connector_lines = bool(self.get_parameter("publish_connector_lines").value)

        self.frame_id = "map"
        self.name = ""
        self.connect_last_to_first = False
        self.publish_mission_route = True
        self.start: dict[str, Any] = {}
        self.tasks: list[dict[str, Any]] = []
        self.current_index = 0
        self.last_mtime: float | None = None
        self.last_robot_pose: tuple[float, float, float] | None = None

        transient_qos = rclpy.qos.QoSProfile(depth=1)
        transient_qos.durability = rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        transient_qos.reliability = rclpy.qos.ReliabilityPolicy.RELIABLE

        self.marker_pub = self.create_publisher(
            MarkerArray, self.get_parameter("mission_marker_topic").value, transient_qos
        )
        self.route_pub = self.create_publisher(
            PathMsg, self.get_parameter("mission_route_topic").value, transient_qos
        )
        self.plan_pub = self.create_publisher(
            String, self.get_parameter("mission_plan_topic").value, transient_qos
        )
        self.current_task_pub = self.create_publisher(
            String, self.get_parameter("current_task_topic").value, transient_qos
        )
        self.current_policy_pub = self.create_publisher(
            String, self.get_parameter("current_policy_topic").value, transient_qos
        )
        self.status_pub = self.create_publisher(
            String, self.get_parameter("mission_status_topic").value, transient_qos
        )
        self.command_sub = self.create_subscription(
            String,
            self.get_parameter("command_topic").value,
            self.on_command,
            10,
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.reload_timer = self.create_timer(float(self.get_parameter("reload_period").value), self.reload_if_needed)
        self.publish_timer = self.create_timer(float(self.get_parameter("publish_period").value), self.on_timer)
        self.reload(force=True)
        self.get_logger().info(f"terrain_mission_manager ready. mission_file={self.mission_file}")

    def reload_if_needed(self) -> None:
        self.reload(force=False)

    def reload(self, force: bool) -> None:
        mtime = self.mission_file.stat().st_mtime if self.mission_file.exists() else None
        if not force and mtime == self.last_mtime:
            return
        self.last_mtime = mtime
        if not self.mission_file.exists():
            self.get_logger().warning(f"Mission file does not exist: {self.mission_file}")
            self.tasks = []
            self.publish_all()
            return

        with self.mission_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        self.frame_id = str(data.get("frame_id", "map"))
        self.name = str(data.get("name", self.mission_file.stem))
        self.connect_last_to_first = bool(data.get("connect_last_to_first", False))
        self.publish_mission_route = bool(data.get("publish_mission_route", True))
        self.start = dict(data.get("start", {}) or {})
        self.tasks = [dict(task) for task in data.get("tasks", []) or []]
        self.current_index = min(max(self.current_index, 0), len(self.tasks))

        self.publish_all()
        self.get_logger().info(f"Loaded mission '{self.name}' with {len(self.tasks)} tasks.")

    def on_timer(self) -> None:
        self.update_robot_pose()
        if self.auto_advance:
            self.advance_if_reached()
        self.publish_status()

    def on_command(self, msg: String) -> None:
        command = msg.data.strip()
        if not command:
            return

        parts = command.split()
        op = parts[0].lower()
        changed = False

        if op == "next":
            self.current_index = min(self.current_index + 1, len(self.tasks))
            changed = True
        elif op == "prev":
            self.current_index = max(self.current_index - 1, 0)
            changed = True
        elif op == "reset":
            self.current_index = 0
            changed = True
        elif op == "reload":
            self.reload(force=True)
            return
        elif op == "set" and len(parts) >= 2:
            target = parts[1]
            index = self.find_task_index(target)
            if index is None:
                self.get_logger().warning(f"Unknown task for mission command: {target}")
            else:
                self.current_index = index
                changed = True
        else:
            self.get_logger().warning(f"Unsupported mission command: {command}")

        if changed:
            self.get_logger().info(f"Mission command '{command}' -> current_index={self.current_index}")
            self.publish_all()

    def find_task_index(self, target: str) -> int | None:
        if target.isdigit():
            index = int(target)
            if 0 <= index < len(self.tasks):
                return index
            return None
        for index, task in enumerate(self.tasks):
            if str(task.get("id", "")) == target:
                return index
        return None

    def update_robot_pose(self) -> None:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.frame_id,
                self.base_frame,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.02),
            )
        except TransformException:
            self.last_robot_pose = None
            return
        t = transform.transform.translation
        self.last_robot_pose = (float(t.x), float(t.y), float(t.z))

    def advance_if_reached(self) -> None:
        if self.current_index >= len(self.tasks) or self.last_robot_pose is None:
            return
        task = self.tasks[self.current_index]
        if "exit" not in task:
            return
        exit_point = point3(task["exit"])
        distance = math.dist(self.last_robot_pose[:2], exit_point[:2])
        if distance <= self.task_reach_radius:
            self.current_index = min(self.current_index + 1, len(self.tasks))
            self.get_logger().info(
                f"Auto advanced mission at exit of {task.get('id', self.current_index)}; distance={distance:.3f}"
            )
            self.publish_all()

    def publish_all(self) -> None:
        self.publish_markers()
        self.publish_route()
        self.publish_plan()
        self.publish_status()

    def publish_plan(self) -> None:
        payload = {
            "frame_id": self.frame_id,
            "name": self.name,
            "connect_last_to_first": self.connect_last_to_first,
            "publish_mission_route": self.publish_mission_route,
            "start": self.start,
            "tasks": [
                {
                    "index": index,
                    "id": str(task.get("id", f"task_{index}")),
                    "type": str(task.get("type", "unknown")),
                    "zone": str(task.get("zone", "")),
                    "policy": str(task.get("policy", "normal_walk")),
                    "safe_margin": task.get("safe_margin"),
                    "mandatory_zone_radius": task.get("mandatory_zone_radius"),
                    "entry": task.get("entry"),
                    "exit": task.get("exit"),
                    "required_points": task.get("required_points", []),
                    "mandatory_zones": task.get("mandatory_zones", []),
                    "pole_centers": task.get("pole_centers", []),
                    "slalom_gates": task.get("slalom_gates", []),
                    "path_points": task.get("path_points", []),
                    "bezier_path": task.get("bezier_path", {}),
                    "constraints": task_constraints(task),
                }
                for index, task in enumerate(self.tasks)
            ],
        }
        self.plan_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))

    def publish_status(self) -> None:
        current = self.current_task()
        if current is None:
            current_task = {
                "id": "",
                "type": "complete" if self.tasks else "empty",
                "policy": "stop",
                "state": "complete" if self.tasks else "empty",
            }
            policy = "stop"
        else:
            current_task = {
                "id": str(current.get("id", f"task_{self.current_index}")),
                "type": str(current.get("type", "unknown")),
                "zone": str(current.get("zone", "")),
                "policy": str(current.get("policy", "normal_walk")),
                "safe_margin": current.get("safe_margin"),
                "mandatory_zone_radius": current.get("mandatory_zone_radius"),
                "state": "active",
                "index": self.current_index,
                "entry": current.get("entry"),
                "exit": current.get("exit"),
                "required_points": current.get("required_points", []),
                "mandatory_zones": current.get("mandatory_zones", []),
                "pole_centers": current.get("pole_centers", []),
                "slalom_gates": current.get("slalom_gates", []),
                "path_points": current.get("path_points", []),
                "bezier_path": current.get("bezier_path", {}),
                "constraints": task_constraints(current),
            }
            policy = current_task["policy"]

        payload = {
            "frame_id": self.frame_id,
            "name": self.name,
            "current_index": self.current_index,
            "current_task": current_task,
            "finished_tasks": [str(task.get("id", f"task_{i}")) for i, task in enumerate(self.tasks[: self.current_index])],
            "remaining_tasks": [
                str(task.get("id", f"task_{i}")) for i, task in enumerate(self.tasks[self.current_index + 1 :], start=self.current_index + 1)
            ],
            "auto_advance": self.auto_advance,
            "task_reach_radius": self.task_reach_radius,
            "robot_pose": list(self.last_robot_pose) if self.last_robot_pose is not None else None,
        }
        self.current_task_pub.publish(String(data=json.dumps(current_task, ensure_ascii=False)))
        self.current_policy_pub.publish(String(data=policy))
        self.status_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))

    def current_task(self) -> dict[str, Any] | None:
        if 0 <= self.current_index < len(self.tasks):
            return self.tasks[self.current_index]
        return None

    def publish_route(self) -> None:
        path = PathMsg()
        path.header.frame_id = self.frame_id
        path.header.stamp = self.get_clock().now().to_msg()

        if not self.publish_mission_route:
            self.route_pub.publish(path)
            return

        if "pose" in self.start:
            sx, sy, sz, syaw = pose4(self.start["pose"])
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = sx
            pose.pose.position.y = sy
            pose.pose.position.z = sz + 0.12
            pose.pose.orientation.z, pose.pose.orientation.w = yaw_to_quat_z_w(syaw)
            path.poses.append(pose)

        for task in self.tasks:
            for _, (x, y, z) in task_route_points(task):
                pose = PoseStamped()
                pose.header = path.header
                pose.pose.position.x = x
                pose.pose.position.y = y
                pose.pose.position.z = z + 0.12
                pose.pose.orientation.w = 1.0
                path.poses.append(pose)

        self.route_pub.publish(path)

    def publish_markers(self) -> None:
        markers = MarkerArray()
        markers.markers.append(delete_all_marker(self.frame_id))
        marker_id = 1

        if "pose" in self.start:
            sx, sy, sz, _ = pose4(self.start["pose"])
            start_marker = self.point_marker("mission_start", marker_id, (sx, sy, sz), (0.0, 1.0, 0.2), 0.22)
            marker_id += 1
            markers.markers.append(start_marker)
            label = self.text_marker("mission_label", marker_id, (sx, sy, sz + 0.45), f"START\n{self.start.get('id', '')}", (0.0, 1.0, 0.2), 0.28)
            marker_id += 1
            markers.markers.append(label)

        route_points = []
        if "pose" in self.start:
            sx, sy, sz, _ = pose4(self.start["pose"])
            route_points.append(Point(x=sx, y=sy, z=sz + 0.12))

        if self.publish_connector_lines:
            marker_id = self.add_connector_markers(markers, marker_id)

        for index, task in enumerate(self.tasks):
            task_type = str(task.get("type", "unknown"))
            r, g, b = color_for_type(task_type)
            is_active = index == self.current_index
            route_items = task_route_points(task)
            marker_items = task_marker_points(task)
            route_z_offset = float(task.get("route_z_offset", 0.12))
            task_points = [Point(x=x, y=y, z=z + route_z_offset) for _, (x, y, z) in route_items]
            route_points.extend(task_points)

            if len(task_points) >= 2:
                line = base_marker(self.frame_id, "mission_task_route", marker_id, Marker.LINE_STRIP)
                marker_id += 1
                line.scale.x = float(task.get("route_width", 0.12 if is_active else 0.07))
                line.color.r, line.color.g, line.color.b, line.color.a = route_color_for_task(task, (r, g, b))
                line.points = task_points
                markers.markers.append(line)

            for point_kind, point in marker_items:
                color = self.color_for_point(point_kind, (r, g, b), is_active)
                size = 0.28 if is_active else 0.20
                if point_kind == "pole_center":
                    size = 0.18 if is_active else 0.14
                elif point_kind == "mandatory_zone":
                    size = 0.32 if is_active else 0.24
                elif point_kind == "slalom_gate":
                    size = 0.24 if is_active else 0.18
                markers.markers.append(self.point_marker(f"mission_{point_kind}", marker_id, point, color, size))
                marker_id += 1

            label_position = self.task_label_position(marker_items or route_items)
            label_text = (
                f"{index + 1}. {task.get('id', f'task_{index}')}\n"
                f"{task_type} | {task.get('policy', 'normal_walk')}"
            )
            if is_active:
                label_text = "ACTIVE\n" + label_text
            markers.markers.append(
                self.text_marker(
                    "mission_task_label",
                    marker_id,
                    label_position,
                    label_text,
                    (1.0, 1.0, 1.0) if is_active else (r, g, b),
                    0.30 if is_active else 0.22,
                )
            )
            marker_id += 1

        if self.publish_full_route_line and len(route_points) >= 2:
            route = base_marker(self.frame_id, "mission_full_route", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            route.scale.x = 0.04
            route.color.r, route.color.g, route.color.b, route.color.a = 1.0, 1.0, 1.0, 0.75
            route.points = route_points
            markers.markers.append(route)

        self.marker_pub.publish(markers)

    def add_connector_markers(self, markers: MarkerArray, marker_id: int) -> int:
        connectors: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
        if self.tasks and "pose" in self.start and "entry" in self.tasks[0]:
            sx, sy, sz, _ = pose4(self.start["pose"])
            connectors.append(((sx, sy, sz), point3(self.tasks[0]["entry"])))

        for previous, following in zip(self.tasks, self.tasks[1:]):
            if "exit" not in previous or "entry" not in following:
                continue
            connectors.append((point3(previous["exit"]), point3(following["entry"])))

        if (
            self.connect_last_to_first
            and len(self.tasks) >= 2
            and "exit" in self.tasks[-1]
            and "entry" in self.tasks[0]
        ):
            connectors.append((point3(self.tasks[-1]["exit"]), point3(self.tasks[0]["entry"])))

        for start_point, end_point in connectors:
            if math.dist(start_point, end_point) < 1.0e-4:
                continue
            marker = base_marker(self.frame_id, "mission_connector_route", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            marker.scale.x = 0.055
            marker.color.r, marker.color.g, marker.color.b, marker.color.a = 1.0, 1.0, 1.0, 0.9
            marker.points = [
                Point(x=start_point[0], y=start_point[1], z=start_point[2] + 0.12),
                Point(x=end_point[0], y=end_point[1], z=end_point[2] + 0.12),
            ]
            markers.markers.append(marker)
        return marker_id

    def point_marker(
        self,
        namespace: str,
        marker_id: int,
        point: tuple[float, float, float],
        color: tuple[float, float, float],
        size: float,
    ) -> Marker:
        marker = base_marker(self.frame_id, namespace, marker_id, Marker.SPHERE)
        marker.pose.position.x = point[0]
        marker.pose.position.y = point[1]
        marker.scale.x = size
        marker.scale.y = size
        marker.scale.z = size
        marker.pose.position.z = point[2] + size * 0.5
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color[0], color[1], color[2], 1.0
        return marker

    def text_marker(
        self,
        namespace: str,
        marker_id: int,
        point: tuple[float, float, float],
        text: str,
        color: tuple[float, float, float],
        size: float,
    ) -> Marker:
        marker = base_marker(self.frame_id, namespace, marker_id, Marker.TEXT_VIEW_FACING)
        marker.pose.position.x = point[0]
        marker.pose.position.y = point[1]
        marker.pose.position.z = point[2]
        marker.scale.z = size
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color[0], color[1], color[2], 1.0
        marker.text = text
        return marker

    def color_for_point(
        self,
        point_kind: str,
        fallback: tuple[float, float, float],
        active: bool,
    ) -> tuple[float, float, float]:
        if active:
            active_palette = {
                "entry": (0.0, 1.0, 1.0),
                "required": (1.0, 0.0, 1.0),
                "mandatory_zone": (1.0, 0.05, 0.05),
                "pole_center": (1.0, 0.55, 0.0),
                "slalom_gate": (0.0, 1.0, 0.25),
                "exit": (1.0, 0.15, 0.15),
            }
            return active_palette.get(point_kind, (1.0, 1.0, 1.0))
        palette = {
            "entry": (0.0, 0.8, 0.95),
            "required": (0.95, 0.25, 0.95),
            "mandatory_zone": (1.0, 0.10, 0.10),
            "pole_center": (1.0, 0.55, 0.0),
            "slalom_gate": (0.0, 0.9, 0.25),
            "exit": (1.0, 0.30, 0.30),
        }
        return palette.get(point_kind, fallback)

    def task_label_position(self, point_items: list[tuple[str, tuple[float, float, float]]]) -> tuple[float, float, float]:
        if not point_items:
            return 0.0, 0.0, 0.5
        xs = [point[0] for _, point in point_items]
        ys = [point[1] for _, point in point_items]
        zs = [point[2] for _, point in point_items]
        return sum(xs) / len(xs), sum(ys) / len(ys), max(zs) + 0.70


def main() -> None:
    rclpy.init()
    node = TerrainMissionManager()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
