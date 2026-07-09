#!/usr/bin/env python3
"""Convert the active mission task route into a Nav2 FollowPath request."""

from __future__ import annotations

import json
import math
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
    bezier = task.get("bezier_path") or {}
    bezier_points = bezier_config_points(bezier)
    if bezier_points:
        return bezier_points

    points: list[tuple[float, float, float]] = []
    if task.get("path_points"):
        points.extend(point3(raw_point) for raw_point in task.get("path_points", []) or [])
        if "exit" in task:
            points.append(point3(task["exit"]))
        return points

    if "entry" in task:
        points.append(point3(task["entry"]))
    points.extend(point3(raw_point) for raw_point in task.get("required_points", []) or [])
    if "exit" in task:
        points.append(point3(task["exit"]))
    return points


def nearest_point_index(points: list[tuple[float, float, float]], point: tuple[float, float, float]) -> int:
    if not points:
        return 0
    nearest_index = 0
    nearest_distance = float("inf")
    for index, route_point in enumerate(points):
        distance = distance2d(point, route_point)
        if distance < nearest_distance:
            nearest_index = index
            nearest_distance = distance
    return nearest_index


def interpolate_path_points(
    points: list[tuple[float, float, float]],
    max_spacing: float,
) -> list[tuple[float, float, float]]:
    if max_spacing <= 0.0 or len(points) < 2:
        return points

    interpolated = [points[0]]
    for start, end in zip(points, points[1:]):
        distance = distance2d(start, end)
        steps = max(1, int(math.ceil(distance / max_spacing)))
        for step in range(1, steps + 1):
            t = step / float(steps)
            interpolated.append(
                (
                    start[0] + (end[0] - start[0]) * t,
                    start[1] + (end[1] - start[1]) * t,
                    start[2] + (end[2] - start[2]) * t,
                )
            )
    return interpolated


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


class MissionPathFollower(Node):
    def __init__(self) -> None:
        super().__init__("mission_path_follower")
        bringup_dir = get_package_share_directory("fine_nav2d_bringup")
        self.declare_parameter("mission_file", str(Path(bringup_dir) / "config" / "uika_obstacle_mission.yaml"))
        self.declare_parameter("status_topic", "/mission_executor_status")
        self.declare_parameter("command_topic", "/mission_path_follower_command")
        self.declare_parameter("path_topic", "/mission_follow_path")
        self.declare_parameter("follow_path_action_name", "/follow_path")
        self.declare_parameter("controller_id", "FollowPath")
        self.declare_parameter("goal_checker_id", "general_goal_checker")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("base_frame", "base_link")
        self.declare_parameter("use_robot_pose_as_path_start", True)
        self.declare_parameter("auto_send_follow_path", False)
        self.declare_parameter("follow_path_wait_timeout", 2.0)
        self.declare_parameter("min_path_point_spacing", 0.02)
        self.declare_parameter("max_path_point_spacing", 0.10)
        self.declare_parameter("publish_period", 0.5)

        self.mission_file = Path(str(self.get_parameter("mission_file").value)).expanduser()
        self.frame_id = str(self.get_parameter("frame_id").value)
        self.base_frame = str(self.get_parameter("base_frame").value)
        self.controller_id = str(self.get_parameter("controller_id").value)
        self.goal_checker_id = str(self.get_parameter("goal_checker_id").value)
        self.follow_path_action_name = str(self.get_parameter("follow_path_action_name").value)
        self.use_robot_pose_as_path_start = bool(self.get_parameter("use_robot_pose_as_path_start").value)
        self.auto_send_follow_path = bool(self.get_parameter("auto_send_follow_path").value)
        self.follow_path_wait_timeout = float(self.get_parameter("follow_path_wait_timeout").value)
        self.min_path_point_spacing = float(self.get_parameter("min_path_point_spacing").value)
        self.max_path_point_spacing = float(self.get_parameter("max_path_point_spacing").value)

        self.tasks_by_id: dict[str, dict[str, Any]] = {}
        self.last_mtime: float | None = None
        self.current_status: dict[str, Any] | None = None
        self.current_task_id = ""
        self.last_sent_task_id = ""
        self.last_sent_waypoint_index = -1
        self.current_path: PathMsg | None = None
        self.active_goal_handle = None

        transient_qos = rclpy.qos.QoSProfile(depth=1)
        transient_qos.durability = rclpy.qos.DurabilityPolicy.TRANSIENT_LOCAL
        transient_qos.reliability = rclpy.qos.ReliabilityPolicy.RELIABLE

        self.path_pub = self.create_publisher(PathMsg, self.get_parameter("path_topic").value, transient_qos)
        self.status_sub = self.create_subscription(
            String,
            self.get_parameter("status_topic").value,
            self.on_status,
            10,
        )
        self.command_sub = self.create_subscription(
            String,
            self.get_parameter("command_topic").value,
            self.on_command,
            10,
        )
        self.follow_path_client = ActionClient(self, FollowPath, self.follow_path_action_name)
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.publish_timer = self.create_timer(float(self.get_parameter("publish_period").value), self.publish_current_path)

        self.reload_mission()
        self.get_logger().info(
            f"mission_path_follower ready. path_topic={self.get_parameter('path_topic').value}, "
            f"follow_path_action={self.follow_path_action_name}, auto_send_follow_path={self.auto_send_follow_path}"
        )

    def reload_mission(self) -> None:
        if not self.mission_file.exists():
            self.get_logger().warning(f"Mission file does not exist: {self.mission_file}")
            self.tasks_by_id = {}
            return
        mtime = self.mission_file.stat().st_mtime
        self.last_mtime = mtime
        with self.mission_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        self.frame_id = str(data.get("frame_id", self.frame_id))
        self.tasks_by_id = {str(task.get("id", "")): dict(task) for task in data.get("tasks", []) or []}
        self.get_logger().info(f"Loaded {len(self.tasks_by_id)} mission tasks from {self.mission_file}")

    def reload_if_needed(self) -> None:
        if not self.mission_file.exists():
            return
        mtime = self.mission_file.stat().st_mtime
        if self.last_mtime != mtime:
            self.reload_mission()
            self.rebuild_current_path(force_send=False)

    def on_command(self, msg: String) -> None:
        command = msg.data.strip().lower()
        if command == "reload":
            self.reload_mission()
            self.rebuild_current_path(force_send=False)
        elif command == "send":
            self.rebuild_current_path(force_send=True)
        elif command == "auto_on":
            self.auto_send_follow_path = True
            self.get_logger().info("auto_send_follow_path enabled")
            self.rebuild_current_path(force_send=True)
        elif command == "auto_off":
            self.auto_send_follow_path = False
            self.get_logger().info("auto_send_follow_path disabled")
        elif command in ("cancel", "stop"):
            self.cancel_active_goal()
        else:
            self.get_logger().warning(f"Unsupported mission_path_follower command: {command}")

    def on_status(self, msg: String) -> None:
        try:
            status = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warning(f"Invalid executor status JSON: {exc}")
            return

        self.current_status = status
        task = status.get("current_task") or {}
        task_id = str(task.get("id", ""))
        target = status.get("current_target") or {}
        waypoint_index = int(target.get("waypoint_index", -1)) if target else -1
        state = str(status.get("state", ""))

        if state in ("complete", "empty") or not task_id:
            self.current_task_id = ""
            self.current_path = self.make_empty_path()
            self.publish_current_path()
            return

        if task_id != self.current_task_id or waypoint_index != self.last_sent_waypoint_index:
            self.current_task_id = task_id
            self.last_sent_waypoint_index = waypoint_index
            self.rebuild_current_path(force_send=False)

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

    def rebuild_current_path(self, force_send: bool) -> None:
        self.reload_if_needed()
        if self.current_status is None:
            return

        task = (self.current_status.get("current_task") or {})
        task_id = str(task.get("id", ""))
        if not task_id:
            return

        mission_task = self.tasks_by_id.get(task_id)
        if mission_task is None:
            self.get_logger().warning(f"Task '{task_id}' not found in mission file")
            return

        current_target = self.current_status.get("current_target") or {}
        waypoint_index = int(current_target.get("waypoint_index", 0)) if current_target else 0
        robot_point = self.robot_pose_point()

        bezier_points = bezier_config_points(mission_task.get("bezier_path") or {})
        if bezier_points:
            points = bezier_points
            if robot_point is not None:
                points = points[nearest_point_index(points, robot_point) :]
        else:
            points = task_route_points(mission_task)
            if 0 < waypoint_index < len(points):
                points = points[waypoint_index:]

        if self.use_robot_pose_as_path_start and robot_point is not None:
            points = [robot_point] + points

        points = interpolate_path_points(points, self.max_path_point_spacing)
        points = dedupe_points(points, self.min_path_point_spacing)
        path = self.make_path(points)
        self.current_path = path
        self.publish_current_path()

        if len(path.poses) < 2:
            self.get_logger().warning(f"Task '{task_id}' produced a path with fewer than two poses")
            return

        if self.auto_send_follow_path or force_send:
            self.send_follow_path(path, task_id)

    def make_empty_path(self) -> PathMsg:
        path = PathMsg()
        path.header.frame_id = self.frame_id
        path.header.stamp = self.get_clock().now().to_msg()
        return path

    def make_path(self, points: list[tuple[float, float, float]]) -> PathMsg:
        path = self.make_empty_path()
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
        self.reload_if_needed()
        if self.current_path is not None:
            self.current_path.header.stamp = self.get_clock().now().to_msg()
            for pose in self.current_path.poses:
                pose.header.stamp = self.current_path.header.stamp
            self.path_pub.publish(self.current_path)

    def send_follow_path(self, path: PathMsg, task_id: str) -> None:
        if not self.follow_path_client.wait_for_server(timeout_sec=self.follow_path_wait_timeout):
            self.get_logger().warning(
                f"FollowPath action '{self.follow_path_action_name}' is not available; "
                f"published /mission_follow_path only"
            )
            return

        goal = FollowPath.Goal()
        goal.path = path
        goal.controller_id = self.controller_id
        goal.goal_checker_id = self.goal_checker_id
        self.get_logger().info(
            f"Sending FollowPath for task '{task_id}' with {len(path.poses)} poses "
            f"controller_id={self.controller_id}"
        )
        future = self.follow_path_client.send_goal_async(goal, feedback_callback=self.on_feedback)
        future.add_done_callback(self.on_goal_response)
        self.last_sent_task_id = task_id

    def on_goal_response(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning("FollowPath goal was rejected")
            return
        self.active_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.on_result)
        self.get_logger().info("FollowPath goal accepted")

    def on_feedback(self, feedback_msg) -> None:
        feedback = feedback_msg.feedback
        self.get_logger().debug(
            f"FollowPath feedback distance_to_goal={feedback.distance_to_goal:.3f}, speed={feedback.speed:.3f}"
        )

    def on_result(self, future) -> None:
        result = future.result()
        # Status 6 is preempted/replaced by a newer FollowPath goal. Do not
        # clear the latest goal handle when an older preempted result arrives.
        if result.status != 6:
            self.active_goal_handle = None
        self.get_logger().info(f"FollowPath result code={result.status}")

    def cancel_active_goal(self) -> None:
        if self.active_goal_handle is None:
            return
        self.active_goal_handle.cancel_goal_async()
        self.active_goal_handle = None
        self.get_logger().info("Cancel requested for active FollowPath goal")


def main() -> None:
    rclpy.init()
    node = MissionPathFollower()
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
