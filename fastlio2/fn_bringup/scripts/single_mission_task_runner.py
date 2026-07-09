#!/usr/bin/env python3
"""Run one annotated mission task through Nav2 FollowPath."""

from __future__ import annotations

import math
import json
from pathlib import Path
from typing import Any

import rclpy
import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowPath
from nav_msgs.msg import Path as PathMsg
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from tf2_ros import Buffer, TransformException, TransformListener


def point3(value: Any) -> tuple[float, float, float]:
    values = [float(v) for v in value]
    if len(values) < 2:
        raise ValueError(f"point needs at least x/y values: {value}")
    z = values[2] if len(values) >= 3 else 0.0
    return values[0], values[1], z


def yaw_to_quat_z_w(yaw: float) -> tuple[float, float]:
    return math.sin(yaw * 0.5), math.cos(yaw * 0.5)


def distance2d(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


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
        points.append(
            (
                u**3 * p0[0] + 3.0 * u**2 * t * p1[0] + 3.0 * u * t**2 * p2[0] + t**3 * p3[0],
                u**3 * p0[1] + 3.0 * u**2 * t * p1[1] + 3.0 * u * t**2 * p2[1] + t**3 * p3[1],
                u**3 * p0[2] + 3.0 * u**2 * t * p1[2] + 3.0 * u * t**2 * p2[2] + t**3 * p3[2],
            )
        )
    return points


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


def task_route_points(task: dict[str, Any]) -> list[tuple[float, float, float]]:
    bezier_points = bezier_config_points(task.get("bezier_path") or {})
    if bezier_points:
        return bezier_points

    if task.get("path_points"):
        points = [point3(raw_point) for raw_point in task.get("path_points", []) or []]
        if "exit" in task:
            points.append(point3(task["exit"]))
        return points

    points: list[tuple[float, float, float]] = []
    if "entry" in task:
        points.append(point3(task["entry"]))
    points.extend(point3(raw_point) for raw_point in task.get("required_points", []) or [])
    if "exit" in task:
        points.append(point3(task["exit"]))
    return points


def dedupe_points(points: list[tuple[float, float, float]], min_spacing: float) -> list[tuple[float, float, float]]:
    if not points:
        return []
    deduped = [points[0]]
    for point in points[1:]:
        if distance2d(point, deduped[-1]) >= min_spacing:
            deduped.append(point)
        else:
            deduped[-1] = point
    if len(deduped) == 1 and len(points) > 1:
        deduped.append(points[-1])
    return deduped


class SingleMissionTaskRunner(Node):
    def __init__(self) -> None:
        super().__init__("single_mission_task_runner")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter(
            "mission_file",
            str(Path(bringup_dir) / "config" / "uika_obstacle_mission_stair_frame.yaml"),
        )
        self.declare_parameter("task_id", "pole_slalom")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("path_topic", "/mission_follow_path")
        self.declare_parameter("status_topic", "/single_task_runner_status")
        self.declare_parameter("command_topic", "/single_task_runner_command")
        self.declare_parameter("follow_path_action_name", "/follow_path")
        self.declare_parameter("controller_id", "FollowPath")
        self.declare_parameter("goal_checker_id", "general_goal_checker")
        self.declare_parameter("auto_start", True)
        self.declare_parameter("use_robot_pose_as_path_start", False)
        self.declare_parameter("follow_path_wait_timeout", 5.0)
        self.declare_parameter("min_path_point_spacing", 0.02)
        self.declare_parameter("publish_period", 0.5)
        self.declare_parameter("keep_alive_after_result", True)

        self.mission_file = Path(str(self.get_parameter("mission_file").value)).expanduser()
        self.task_id = str(self.get_parameter("task_id").value)
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.controller_id = str(self.get_parameter("controller_id").value)
        self.goal_checker_id = str(self.get_parameter("goal_checker_id").value)
        self.follow_path_action_name = str(self.get_parameter("follow_path_action_name").value)
        self.use_robot_pose_as_path_start = bool(self.get_parameter("use_robot_pose_as_path_start").value)
        self.follow_path_wait_timeout = float(self.get_parameter("follow_path_wait_timeout").value)
        self.min_path_point_spacing = float(self.get_parameter("min_path_point_spacing").value)
        self.keep_alive_after_result = bool(self.get_parameter("keep_alive_after_result").value)

        self.current_path: PathMsg | None = None
        self.active_goal_handle = None
        self.sent_once = False
        self.result_status: int | None = None
        self.last_event = "initialized"

        transient_qos = QoSProfile(depth=1)
        transient_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        transient_qos.reliability = ReliabilityPolicy.RELIABLE
        self.path_pub = self.create_publisher(PathMsg, str(self.get_parameter("path_topic").value), transient_qos)
        self.status_pub = self.create_publisher(String, str(self.get_parameter("status_topic").value), transient_qos)
        self.command_sub = self.create_subscription(
            String,
            str(self.get_parameter("command_topic").value),
            self.on_command,
            10,
        )
        self.follow_path_client = ActionClient(self, FollowPath, self.follow_path_action_name)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(float(self.get_parameter("publish_period").value), self.on_timer)

        self.build_path()
        self.get_logger().info(
            f"single_mission_task_runner ready. task_id={self.task_id}, poses={len(self.current_path.poses) if self.current_path else 0}, "
            f"path_topic={self.get_parameter('path_topic').value}, auto_start={self.get_parameter('auto_start').value}"
        )

    def on_timer(self) -> None:
        self.publish_current_path()
        self.publish_status()
        if bool(self.get_parameter("auto_start").value) and not self.sent_once:
            self.sent_once = True
            self.send_current_path()
        if self.result_status is not None and not self.keep_alive_after_result:
            rclpy.shutdown()

    def on_command(self, msg: String) -> None:
        command = msg.data.strip()
        if command == "send":
            self.send_current_path()
        elif command == "cancel":
            self.cancel_active_goal()
        elif command == "reload":
            self.build_path()
            self.sent_once = False
            self.result_status = None
            self.last_event = "reloaded"
        else:
            self.get_logger().warning(f"Unsupported command: {command}")

    def robot_pose_point(self) -> tuple[float, float, float] | None:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.frame_id,
                self.base_frame,
                rclpy.time.Time(),
                timeout=rclpy.duration.Duration(seconds=0.03),
            )
        except TransformException:
            return None
        t = transform.transform.translation
        return float(t.x), float(t.y), float(t.z)

    def build_path(self) -> None:
        if not self.mission_file.exists():
            raise FileNotFoundError(f"Mission file does not exist: {self.mission_file}")
        with self.mission_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self.frame_id = str(data.get("frame_id", self.frame_id))
        tasks = data.get("tasks", []) or []
        task = next((dict(item) for item in tasks if str(item.get("id", "")) == self.task_id), None)
        if task is None:
            raise ValueError(f"Task '{self.task_id}' not found in {self.mission_file}")

        points = task_route_points(task)
        robot_point = self.robot_pose_point()
        if self.use_robot_pose_as_path_start and robot_point is not None:
            points = [robot_point] + points
        points = dedupe_points(points, self.min_path_point_spacing)
        self.current_path = self.make_path(points)
        self.last_event = "path_built"

    def make_path(self, points: list[tuple[float, float, float]]) -> PathMsg:
        path = PathMsg()
        path.header.frame_id = self.frame_id
        path.header.stamp = self.get_clock().now().to_msg()
        for index, point in enumerate(points):
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = point[0]
            pose.pose.position.y = point[1]
            pose.pose.position.z = point[2]
            yaw = self.path_yaw(points, index)
            pose.pose.orientation.z, pose.pose.orientation.w = yaw_to_quat_z_w(yaw)
            path.poses.append(pose)
        return path

    def path_yaw(self, points: list[tuple[float, float, float]], index: int) -> float:
        if len(points) < 2:
            return 0.0
        if index + 1 < len(points):
            start, end = points[index], points[index + 1]
        else:
            start, end = points[index - 1], points[index]
        return math.atan2(end[1] - start[1], end[0] - start[0])

    def publish_current_path(self) -> None:
        if self.current_path is None:
            return
        self.current_path.header.stamp = self.get_clock().now().to_msg()
        for pose in self.current_path.poses:
            pose.header.stamp = self.current_path.header.stamp
        self.path_pub.publish(self.current_path)

    def publish_status(self) -> None:
        status = "running" if self.active_goal_handle is not None else "idle"
        if self.result_status is not None:
            status = f"result:{self.result_status}"
        msg = {
            "task_id": self.task_id,
            "status": status,
            "poses": len(self.current_path.poses) if self.current_path is not None else 0,
            "last_event": self.last_event,
        }
        self.status_pub.publish(String(data=json.dumps(msg, ensure_ascii=False)))

    def send_current_path(self) -> None:
        if self.current_path is None or len(self.current_path.poses) < 2:
            self.get_logger().warning("Current path is empty or too short")
            return
        if not self.follow_path_client.wait_for_server(timeout_sec=self.follow_path_wait_timeout):
            self.get_logger().warning(f"FollowPath action '{self.follow_path_action_name}' is not available")
            return

        goal = FollowPath.Goal()
        goal.path = self.current_path
        goal.controller_id = self.controller_id
        goal.goal_checker_id = self.goal_checker_id
        self.result_status = None
        self.last_event = "goal_sent"
        self.get_logger().info(f"Sending task '{self.task_id}' FollowPath with {len(goal.path.poses)} poses")
        future = self.follow_path_client.send_goal_async(goal)
        future.add_done_callback(self.on_goal_response)

    def on_goal_response(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.last_event = "goal_rejected"
            self.get_logger().warning("FollowPath goal was rejected")
            return
        self.active_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.on_result)
        self.last_event = "goal_accepted"
        self.get_logger().info("FollowPath goal accepted")

    def on_result(self, future) -> None:
        result = future.result()
        self.result_status = int(result.status)
        self.active_goal_handle = None
        self.last_event = f"goal_result:{self.result_status}"
        self.get_logger().info(f"FollowPath result code={self.result_status}")

    def cancel_active_goal(self) -> None:
        if self.active_goal_handle is None:
            return
        self.active_goal_handle.cancel_goal_async()
        self.active_goal_handle = None
        self.last_event = "cancel_requested"


def main() -> None:
    rclpy.init()
    node = SingleMissionTaskRunner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
