#!/usr/bin/env python3
"""Closed-loop planar simulator for the fixed-path controller."""

from __future__ import annotations

import json
import math
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped, TransformStamped, Twist
from nav_msgs.msg import Path
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import Bool, Float32, String
from std_srvs.srv import Trigger
from tf2_ros import TransformBroadcaster


def wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class FixedPathSimulator(Node):
    def __init__(self) -> None:
        super().__init__("fixed_path_simulator")

        self.map_frame = str(self.declare_parameter("map_frame", "map").value)
        self.base_frame = str(
            self.declare_parameter("base_frame", "base_footprint").value
        )
        self.route_topic = str(
            self.declare_parameter("route_topic", "/slalom_route").value
        )
        self.command_topic = str(
            self.declare_parameter(
                "command_topic", "/fixed_path_controller/cmd_debug"
            ).value
        )
        self.actual_path_topic = str(
            self.declare_parameter(
                "actual_path_topic", "/fixed_path_simulator/actual_path"
            ).value
        )
        self.pose_topic = str(
            self.declare_parameter(
                "pose_topic", "/fixed_path_simulator/pose"
            ).value
        )
        self.update_frequency = float(
            self.declare_parameter("update_frequency", 50.0).value
        )
        self.path_frequency = float(
            self.declare_parameter("path_frequency", 10.0).value
        )
        self.velocity_time_constant = float(
            self.declare_parameter("velocity_time_constant", 0.12).value
        )
        self.command_timeout = float(
            self.declare_parameter("command_timeout", 0.30).value
        )
        self.auto_start = bool(self.declare_parameter("auto_start", True).value)
        self.auto_start_delay = float(
            self.declare_parameter("auto_start_delay", 1.0).value
        )
        self.max_path_poses = int(
            self.declare_parameter("max_path_poses", 10000).value
        )

        if self.update_frequency <= 0.0 or self.path_frequency <= 0.0:
            raise ValueError("simulation frequencies must be positive")
        if self.velocity_time_constant < 0.0:
            raise ValueError("velocity_time_constant cannot be negative")

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.path_pub = self.create_publisher(Path, self.actual_path_topic, 10)
        self.pose_pub = self.create_publisher(PoseStamped, self.pose_topic, 10)
        self.localization_pub = self.create_publisher(
            Bool, "/relocalization/success", latched_qos
        )
        self.status_pub = self.create_publisher(
            String, "/fixed_path_simulator/status", latched_qos
        )
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Path, self.route_topic, self.route_callback, latched_qos)
        self.create_subscription(Twist, self.command_topic, self.command_callback, 10)
        self.create_subscription(
            Float32,
            "/fixed_path_controller/cross_track_error",
            self.cross_track_error_callback,
            10,
        )
        self.create_subscription(
            String,
            "/fixed_path_controller/status",
            self.controller_status_callback,
            latched_qos,
        )
        self.start_client = self.create_client(Trigger, "/fixed_path_controller/start")
        self.reset_service = self.create_service(Trigger, "~/reset", self.reset_callback)

        self.route: list[tuple[float, float]] = []
        self.initial_pose: tuple[float, float, float] | None = None
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.target_command = Twist()
        self.last_command_time = self.get_clock().now()
        self.last_update_time = self.get_clock().now()
        self.last_path_time = self.get_clock().now()
        self.route_received_time = None
        self.start_request_pending = False
        self.start_accepted = False
        self.controller_state = "WAITING"
        self.completed_reported = False
        self.simulation_start_time = None
        self.distance_traveled = 0.0
        self.cross_track_error_sum_sq = 0.0
        self.cross_track_error_max = 0.0
        self.cross_track_error_count = 0
        self.path_message = Path()
        self.path_message.header.frame_id = self.map_frame

        self.create_timer(1.0 / self.update_frequency, self.update)
        self.create_timer(0.2, self.try_auto_start)
        self.localization_pub.publish(Bool(data=True))
        self.publish_status("waiting for route")
        self.get_logger().info(
            f"Closed-loop simulator ready: command={self.command_topic}, "
            f"pose={self.map_frame}->{self.base_frame}"
        )

    def route_callback(self, message: Path) -> None:
        if self.route:
            return
        points = [
            (float(pose.pose.position.x), float(pose.pose.position.y))
            for pose in message.poses
            if math.isfinite(pose.pose.position.x)
            and math.isfinite(pose.pose.position.y)
        ]
        if len(points) < 2:
            self.get_logger().error("Route contains fewer than two finite points")
            return
        self.route = points
        first = points[0]
        second = next(
            (point for point in points[1:] if math.dist(first, point) > 1.0e-4),
            points[1],
        )
        heading = math.atan2(second[1] - first[1], second[0] - first[0])
        self.initial_pose = (first[0], first[1], heading)
        self.route_received_time = self.get_clock().now()
        self.reset_state()
        self.get_logger().info(
            f"Initialized at route start: x={self.x:.3f}, y={self.y:.3f}, "
            f"yaw={math.degrees(self.yaw):.1f} deg"
        )

    def command_callback(self, message: Twist) -> None:
        self.target_command = message
        self.last_command_time = self.get_clock().now()

    def cross_track_error_callback(self, message: Float32) -> None:
        error = float(message.data)
        if not math.isfinite(error) or self.controller_state != "TRACKING":
            return
        self.cross_track_error_sum_sq += error * error
        self.cross_track_error_max = max(self.cross_track_error_max, error)
        self.cross_track_error_count += 1

    def controller_status_callback(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except (json.JSONDecodeError, TypeError):
            return
        self.controller_state = str(payload.get("state", "UNKNOWN"))
        if self.controller_state == "TRACKING" and self.simulation_start_time is None:
            self.simulation_start_time = self.get_clock().now()
        if self.controller_state == "COMPLETE" and not self.completed_reported:
            self.completed_reported = True
            elapsed = 0.0
            if self.simulation_start_time is not None:
                elapsed = (
                    self.get_clock().now() - self.simulation_start_time
                ).nanoseconds / 1.0e9
            goal_error = math.dist((self.x, self.y), self.route[-1]) if self.route else 0.0
            cross_track_rms = math.sqrt(
                self.cross_track_error_sum_sq
                / max(self.cross_track_error_count, 1)
            )
            detail = (
                f"COMPLETE: time={elapsed:.1f}s, traveled={self.distance_traveled:.2f}m, "
                f"goal_error={goal_error:.3f}m, cross_track_rms={cross_track_rms:.3f}m, "
                f"cross_track_max={self.cross_track_error_max:.3f}m"
            )
            self.publish_status(detail)
            self.get_logger().info(detail)
        elif self.controller_state == "FAULT" and not self.completed_reported:
            self.publish_status(f"FAULT: {payload.get('detail', 'controller fault')}")

    def reset_callback(self, _request, response):
        if self.initial_pose is None:
            response.success = False
            response.message = "No route has been received"
            return response
        self.reset_state()
        response.success = True
        response.message = "Simulator reset to route start"
        return response

    def reset_state(self) -> None:
        if self.initial_pose is None:
            return
        self.x, self.y, self.yaw = self.initial_pose
        self.linear_velocity = 0.0
        self.angular_velocity = 0.0
        self.target_command = Twist()
        now = self.get_clock().now()
        self.last_command_time = now
        self.last_update_time = now
        self.last_path_time = now
        self.start_request_pending = False
        self.start_accepted = False
        self.completed_reported = False
        self.simulation_start_time = None
        self.distance_traveled = 0.0
        self.cross_track_error_sum_sq = 0.0
        self.cross_track_error_max = 0.0
        self.cross_track_error_count = 0
        self.path_message = Path()
        self.path_message.header.frame_id = self.map_frame
        self.append_path_pose(now)
        self.publish_pose(now)
        self.publish_status("initialized at route start")

    def try_auto_start(self) -> None:
        if (
            not self.auto_start
            or self.route_received_time is None
            or self.start_accepted
            or self.start_request_pending
        ):
            return
        age = (
            self.get_clock().now() - self.route_received_time
        ).nanoseconds / 1.0e9
        if age < self.auto_start_delay or not self.start_client.service_is_ready():
            return
        self.start_request_pending = True
        future = self.start_client.call_async(Trigger.Request())
        future.add_done_callback(self.start_response)

    def start_response(self, future) -> None:
        self.start_request_pending = False
        try:
            response = future.result()
        except Exception as error:  # rclpy service transport failure
            self.get_logger().error(f"Controller start call failed: {error}")
            return
        if response.success:
            self.start_accepted = True
            self.get_logger().info("Controller accepted automatic simulation start")
        else:
            self.get_logger().warn(f"Controller not ready: {response.message}")

    def update(self) -> None:
        if self.initial_pose is None:
            return
        now = self.get_clock().now()
        dt = min(max((now - self.last_update_time).nanoseconds / 1.0e9, 0.0), 0.10)
        self.last_update_time = now
        command_age = (now - self.last_command_time).nanoseconds / 1.0e9
        target_linear = self.target_command.linear.x if command_age <= self.command_timeout else 0.0
        target_angular = self.target_command.angular.z if command_age <= self.command_timeout else 0.0

        if self.velocity_time_constant > 0.0:
            alpha = 1.0 - math.exp(-dt / self.velocity_time_constant)
            self.linear_velocity += alpha * (target_linear - self.linear_velocity)
            self.angular_velocity += alpha * (target_angular - self.angular_velocity)
        else:
            self.linear_velocity = target_linear
            self.angular_velocity = target_angular

        previous_x = self.x
        previous_y = self.y
        middle_yaw = self.yaw + 0.5 * self.angular_velocity * dt
        self.x += self.linear_velocity * math.cos(middle_yaw) * dt
        self.y += self.linear_velocity * math.sin(middle_yaw) * dt
        self.yaw = wrap_angle(self.yaw + self.angular_velocity * dt)
        self.distance_traveled += math.hypot(self.x - previous_x, self.y - previous_y)

        self.publish_pose(now)
        path_period = 1.0 / self.path_frequency
        if (now - self.last_path_time).nanoseconds / 1.0e9 >= path_period:
            self.last_path_time = now
            self.append_path_pose(now)
            self.path_message.header.stamp = now.to_msg()
            self.path_pub.publish(self.path_message)

    def make_pose(self, now) -> PoseStamped:
        pose = PoseStamped()
        pose.header.frame_id = self.map_frame
        pose.header.stamp = now.to_msg()
        pose.pose.position.x = self.x
        pose.pose.position.y = self.y
        pose.pose.orientation.z = math.sin(0.5 * self.yaw)
        pose.pose.orientation.w = math.cos(0.5 * self.yaw)
        return pose

    def append_path_pose(self, now) -> None:
        self.path_message.poses.append(self.make_pose(now))
        if len(self.path_message.poses) > self.max_path_poses:
            self.path_message.poses = self.path_message.poses[-self.max_path_poses :]

    def publish_pose(self, now) -> None:
        pose = self.make_pose(now)
        self.pose_pub.publish(pose)
        transform = TransformStamped()
        transform.header = pose.header
        transform.child_frame_id = self.base_frame
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.rotation = pose.pose.orientation
        self.tf_broadcaster.sendTransform(transform)

    def publish_status(self, detail: str) -> None:
        payload = {
            "controller_state": self.controller_state,
            "detail": detail,
            "x": self.x,
            "y": self.y,
            "yaw": self.yaw,
            "distance_traveled": self.distance_traveled,
        }
        self.status_pub.publish(String(data=json.dumps(payload, separators=(",", ":"))))


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = FixedPathSimulator()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
