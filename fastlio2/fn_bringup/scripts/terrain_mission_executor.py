#!/usr/bin/env python3
"""Execute an annotated terrain mission as a policy-switching state machine."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Point, PoseStamped
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


def dist_xy(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def points_close(a: tuple[float, float, float], b: tuple[float, float, float], eps: float = 1.0e-6) -> bool:
    return math.dist(a, b) <= eps


def append_unique(
    points: list[tuple[str, tuple[float, float, float]]],
    kind: str,
    point: tuple[float, float, float],
) -> None:
    if points and points_close(points[-1][1], point):
        return
    points.append((kind, point))


def task_waypoints(task: dict[str, Any]) -> list[tuple[str, tuple[float, float, float]]]:
    waypoints: list[tuple[str, tuple[float, float, float]]] = []

    if task.get("path_points"):
        for index, raw_point in enumerate(task.get("path_points", []) or []):
            kind = "entry" if index == 0 else "path_point"
            append_unique(waypoints, kind, point3(raw_point))
        if "exit" in task:
            append_unique(waypoints, "exit", point3(task["exit"]))
        return waypoints

    if "entry" in task:
        append_unique(waypoints, "entry", point3(task["entry"]))
    for raw_point in task.get("required_points", []) or []:
        append_unique(waypoints, "required", point3(raw_point))
    if "exit" in task:
        append_unique(waypoints, "exit", point3(task["exit"]))
    return waypoints


def task_constraints(task: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "safe_margin",
        "mandatory_zone_radius",
        "path_mode",
        "require_straight_path",
        "max_lateral_error",
        "speed_limit",
        "min_distance_on_slope",
        "entry_rule",
    )
    return {key: task[key] for key in keys if key in task}


def color_for_type(task_type: str) -> tuple[float, float, float]:
    palette = {
        "stairs": (1.0, 0.55, 0.05),
        "bridge": (0.10, 0.70, 1.0),
        "slope": (0.35, 0.95, 0.35),
        "wall": (1.0, 0.15, 0.15),
        "low_bar": (0.85, 0.35, 1.0),
        "gravel": (0.85, 0.75, 0.30),
        "pole_slalom": (0.20, 0.45, 1.0),
    }
    return palette.get(task_type, (0.85, 0.85, 0.85))


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


class TerrainMissionExecutor(Node):
    def __init__(self) -> None:
        super().__init__("terrain_mission_executor")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter("mission_file", str(Path(bringup_dir) / "config" / "uika_obstacle_mission.yaml"))
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("use_tf_pose", True)
        self.declare_parameter("pose_topic", "/mission_executor_pose")
        self.declare_parameter("command_topic", "/mission_executor_command")
        self.declare_parameter("status_topic", "/mission_executor_status")
        self.declare_parameter("policy_topic", "/mission_executor_policy")
        self.declare_parameter("task_topic", "/mission_executor_task")
        self.declare_parameter("target_topic", "/mission_executor_target")
        self.declare_parameter("marker_topic", "/mission_executor_markers")
        self.declare_parameter("update_period", 0.1)
        self.declare_parameter("reload_period", 1.0)
        self.declare_parameter("waypoint_reach_radius", 0.25)
        self.declare_parameter("dryrun_auto_play", False)
        self.declare_parameter("dryrun_step_period", 0.35)
        self.declare_parameter("initial_task_id", "")
        self.declare_parameter("initial_task_index", -1)
        self.declare_parameter("initial_waypoint_index", 0)

        self.mission_file = Path(str(self.get_parameter("mission_file").value)).expanduser()
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.use_tf_pose = bool(self.get_parameter("use_tf_pose").value)
        self.waypoint_reach_radius = float(self.get_parameter("waypoint_reach_radius").value)
        self.dryrun_auto_play = bool(self.get_parameter("dryrun_auto_play").value)
        self.dryrun_step_period = float(self.get_parameter("dryrun_step_period").value)
        self.initial_task_id = str(self.get_parameter("initial_task_id").value)
        self.initial_task_index = int(self.get_parameter("initial_task_index").value)
        self.initial_waypoint_index = int(self.get_parameter("initial_waypoint_index").value)

        self.name = ""
        self.tasks: list[dict[str, Any]] = []
        self.task_points: list[list[tuple[str, tuple[float, float, float]]]] = []
        self.current_task_index = 0
        self.current_waypoint_index = 0
        self.last_mtime: float | None = None
        self.last_robot_pose: tuple[float, float, float] | None = None
        self.last_event = "initialized"
        self.last_dryrun_step_time = self.get_clock().now()

        transient_qos = rclpy.qos.QoSProfile(depth=1)
        transient_qos.durability = rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        transient_qos.reliability = rclpy.qos.ReliabilityPolicy.RELIABLE

        self.status_pub = self.create_publisher(String, self.get_parameter("status_topic").value, transient_qos)
        self.policy_pub = self.create_publisher(String, self.get_parameter("policy_topic").value, transient_qos)
        self.task_pub = self.create_publisher(String, self.get_parameter("task_topic").value, transient_qos)
        self.target_pub = self.create_publisher(PoseStamped, self.get_parameter("target_topic").value, transient_qos)
        self.marker_pub = self.create_publisher(MarkerArray, self.get_parameter("marker_topic").value, transient_qos)

        self.command_sub = self.create_subscription(
            String,
            self.get_parameter("command_topic").value,
            self.on_command,
            10,
        )
        self.pose_sub = self.create_subscription(
            PoseStamped,
            self.get_parameter("pose_topic").value,
            self.on_pose,
            10,
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.reload_timer = self.create_timer(float(self.get_parameter("reload_period").value), self.reload_if_needed)
        self.update_timer = self.create_timer(float(self.get_parameter("update_period").value), self.on_timer)
        self.reload(force=True)
        self.get_logger().info(
            f"terrain_mission_executor ready. mission_file={self.mission_file}, "
            f"use_tf_pose={self.use_tf_pose}, dryrun_auto_play={self.dryrun_auto_play}"
        )

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
            self.task_points = []
            self.apply_initial_cursor()
            self.last_event = "mission_file_missing"
            self.publish_all()
            return

        with self.mission_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        self.frame_id = str(data.get("frame_id", self.frame_id))
        self.name = str(data.get("name", self.mission_file.stem))
        self.tasks = [dict(task) for task in data.get("tasks", []) or []]
        self.task_points = [task_waypoints(task) for task in self.tasks]
        if force:
            self.apply_initial_cursor()
        else:
            self.current_task_index = min(max(self.current_task_index, 0), len(self.tasks))
        if self.current_task_index < len(self.tasks):
            self.current_waypoint_index = min(
                max(self.current_waypoint_index, 0),
                max(len(self.task_points[self.current_task_index]) - 1, 0),
            )
        else:
            self.current_waypoint_index = 0
        self.last_event = "mission_loaded"
        self.get_logger().info(f"Loaded mission '{self.name}' with {len(self.tasks)} tasks.")
        self.publish_all()

    def apply_initial_cursor(self) -> None:
        task_index = 0
        if self.initial_task_id:
            found_index = None
            for index, task in enumerate(self.tasks):
                if str(task.get("id", "")) == self.initial_task_id:
                    found_index = index
                    break
            if found_index is None:
                self.get_logger().warning(f"initial_task_id not found: {self.initial_task_id}")
            else:
                task_index = found_index
        elif self.initial_task_index >= 0:
            task_index = self.initial_task_index

        self.current_task_index = min(max(task_index, 0), len(self.tasks))
        self.current_waypoint_index = max(self.initial_waypoint_index, 0)

    def on_pose(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        self.last_robot_pose = (float(p.x), float(p.y), float(p.z))

    def on_command(self, msg: String) -> None:
        command = msg.data.strip()
        if not command:
            return

        parts = command.split()
        op = parts[0].lower()
        if op == "reset":
            self.apply_initial_cursor()
            self.last_event = "reset"
        elif op == "reload":
            self.reload(force=True)
            return
        elif op == "advance":
            self.advance_one_step("manual_advance")
        elif op == "next_task":
            self.current_task_index = min(self.current_task_index + 1, len(self.tasks))
            self.current_waypoint_index = 0
            self.last_event = "manual_next_task"
        elif op == "prev_task":
            self.current_task_index = max(self.current_task_index - 1, 0)
            self.current_waypoint_index = 0
            self.last_event = "manual_prev_task"
        elif op == "set" and len(parts) >= 2:
            index = self.find_task_index(parts[1])
            if index is None:
                self.get_logger().warning(f"Unknown task: {parts[1]}")
            else:
                self.current_task_index = index
                self.current_waypoint_index = 0
                self.last_event = f"manual_set:{parts[1]}"
        elif op == "goto" and len(parts) >= 3:
            index = self.find_task_index(parts[1])
            if index is None:
                self.get_logger().warning(f"Unknown task: {parts[1]}")
            else:
                waypoint_index = int(parts[2])
                self.current_task_index = index
                self.current_waypoint_index = min(
                    max(waypoint_index, 0),
                    max(len(self.task_points[index]) - 1, 0),
                )
                self.last_event = f"manual_goto:{parts[1]}:{self.current_waypoint_index}"
        elif op == "pose" and len(parts) >= 4:
            self.last_robot_pose = (float(parts[1]), float(parts[2]), float(parts[3]))
            self.last_event = "manual_pose"
        elif op == "play":
            self.dryrun_auto_play = True
            self.last_event = "dryrun_play"
        elif op == "pause":
            self.dryrun_auto_play = False
            self.last_event = "dryrun_pause"
        else:
            self.get_logger().warning(f"Unsupported executor command: {command}")
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

    def on_timer(self) -> None:
        if self.use_tf_pose and not self.dryrun_auto_play:
            self.update_tf_pose()
        if self.dryrun_auto_play:
            self.step_dryrun_pose()
        self.advance_if_reached()
        self.publish_all()

    def update_tf_pose(self) -> None:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.frame_id,
                self.base_frame,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.02),
            )
        except TransformException:
            return
        t = transform.transform.translation
        self.last_robot_pose = (float(t.x), float(t.y), float(t.z))

    def step_dryrun_pose(self) -> None:
        now = self.get_clock().now()
        elapsed = (now - self.last_dryrun_step_time).nanoseconds / 1.0e9
        if elapsed < self.dryrun_step_period:
            return
        target = self.current_target()
        if target is not None:
            self.last_robot_pose = target["point"]
            self.last_event = "dryrun_step"
        self.last_dryrun_step_time = now

    def advance_if_reached(self) -> None:
        if self.last_robot_pose is None:
            return
        target = self.current_target()
        if target is None:
            return
        distance = dist_xy(self.last_robot_pose, target["point"])
        if distance <= self.waypoint_reach_radius:
            self.advance_one_step(f"reached:{target['kind']}")

    def advance_one_step(self, event: str) -> None:
        if self.current_task_index >= len(self.tasks):
            self.last_event = "already_complete"
            return
        points = self.task_points[self.current_task_index]
        if self.current_waypoint_index + 1 < len(points):
            self.current_waypoint_index += 1
        else:
            self.current_task_index += 1
            self.current_waypoint_index = 0
        self.last_event = event

    def current_task(self) -> dict[str, Any] | None:
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def current_target(self) -> dict[str, Any] | None:
        task = self.current_task()
        if task is None:
            return None
        points = self.task_points[self.current_task_index]
        if not points:
            return None
        index = min(self.current_waypoint_index, len(points) - 1)
        kind, point = points[index]
        return {
            "task_index": self.current_task_index,
            "waypoint_index": index,
            "kind": kind,
            "point": point,
        }

    def state_name(self) -> str:
        if not self.tasks:
            return "empty"
        if self.current_task_index >= len(self.tasks):
            return "complete"
        if self.last_robot_pose is None and not self.dryrun_auto_play:
            return "waiting_for_pose"
        return "active"

    def publish_all(self) -> None:
        payload = self.status_payload()
        current_policy = payload["current_policy"]
        self.status_pub.publish(String(data=json.dumps(payload, ensure_ascii=False)))
        self.policy_pub.publish(String(data=current_policy))
        self.task_pub.publish(String(data=json.dumps(payload["current_task"], ensure_ascii=False)))
        self.publish_target()
        self.publish_markers()

    def status_payload(self) -> dict[str, Any]:
        task = self.current_task()
        target = self.current_target()
        state = self.state_name()
        if task is None:
            current_task: dict[str, Any] = {
                "id": "",
                "type": "complete" if self.tasks else "empty",
                "zone": "",
                "policy": "stop",
                "constraints": {},
            }
            policy = "stop"
        else:
            current_task = {
                "index": self.current_task_index,
                "id": str(task.get("id", f"task_{self.current_task_index}")),
                "type": str(task.get("type", "unknown")),
                "zone": str(task.get("zone", "")),
                "policy": str(task.get("policy", "normal_walk")),
                "constraints": task_constraints(task),
                "waypoint_count": len(self.task_points[self.current_task_index]),
            }
            policy = current_task["policy"]

        distance = None
        if self.last_robot_pose is not None and target is not None:
            distance = round(dist_xy(self.last_robot_pose, target["point"]), 4)

        return {
            "frame_id": self.frame_id,
            "name": self.name,
            "state": state,
            "current_policy": policy,
            "current_task": current_task,
            "current_target": {
                **target,
                "point": list(target["point"]),
            } if target is not None else None,
            "distance_to_target_xy": distance,
            "task_index": self.current_task_index,
            "waypoint_index": self.current_waypoint_index,
            "finished_tasks": [
                str(task.get("id", f"task_{i}")) for i, task in enumerate(self.tasks[: self.current_task_index])
            ],
            "remaining_tasks": [
                str(task.get("id", f"task_{i}"))
                for i, task in enumerate(self.tasks[self.current_task_index + 1 :], start=self.current_task_index + 1)
            ],
            "robot_pose": list(self.last_robot_pose) if self.last_robot_pose is not None else None,
            "dryrun_auto_play": self.dryrun_auto_play,
            "waypoint_reach_radius": self.waypoint_reach_radius,
            "last_event": self.last_event,
        }

    def publish_target(self) -> None:
        target = self.current_target()
        if target is None:
            return
        x, y, z = target["point"]
        msg = PoseStamped()
        msg.header.frame_id = self.frame_id
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z
        msg.pose.orientation.w = 1.0
        self.target_pub.publish(msg)

    def publish_markers(self) -> None:
        markers = MarkerArray()
        markers.markers.append(delete_all_marker(self.frame_id))

        task = self.current_task()
        target = self.current_target()
        if task is None or target is None:
            self.marker_pub.publish(markers)
            return

        marker_id = 1
        task_type = str(task.get("type", "unknown"))
        r, g, b = color_for_type(task_type)
        points = self.task_points[self.current_task_index]

        if len(points) >= 2:
            route = base_marker(self.frame_id, "mission_executor_active_route", marker_id, Marker.LINE_STRIP)
            marker_id += 1
            route.scale.x = 0.045
            route.color.r, route.color.g, route.color.b, route.color.a = r, g, b, 1.0
            route.points = [Point(x=p[0], y=p[1], z=p[2] + 0.18) for _, p in points]
            markers.markers.append(route)

        target_marker = base_marker(self.frame_id, "mission_executor_target", marker_id, Marker.SPHERE)
        marker_id += 1
        x, y, z = target["point"]
        target_marker.pose.position.x = x
        target_marker.pose.position.y = y
        target_marker.pose.position.z = z + 0.22
        target_marker.scale.x = target_marker.scale.y = target_marker.scale.z = 0.24
        target_marker.color.r, target_marker.color.g, target_marker.color.b, target_marker.color.a = 1.0, 1.0, 1.0, 1.0
        markers.markers.append(target_marker)

        label = base_marker(self.frame_id, "mission_executor_label", marker_id, Marker.TEXT_VIEW_FACING)
        label.pose.position.x = x
        label.pose.position.y = y
        label.pose.position.z = z + 0.55
        label.scale.z = 0.22
        label.color.r, label.color.g, label.color.b, label.color.a = 1.0, 1.0, 1.0, 1.0
        label.text = (
            f"{task.get('id', '')}\n"
            f"{task.get('policy', 'normal_walk')}\n"
            f"{target['kind']} {target['waypoint_index'] + 1}/{len(points)}"
        )
        markers.markers.append(label)
        self.marker_pub.publish(markers)


def main() -> None:
    rclpy.init()
    node = TerrainMissionExecutor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
