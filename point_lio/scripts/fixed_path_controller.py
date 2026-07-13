#!/usr/bin/env python3
"""Lightweight forward-only path tracker for fixed map-frame routes."""

from __future__ import annotations

import bisect
import json
import math
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Path
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from std_msgs.msg import Bool, Float32, String
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformException, TransformListener


def clamp(value: float, low: float, high: float) -> float:
    return min(max(value, low), high)


def wrap_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def quaternion_yaw(x: float, y: float, z: float, w: float) -> float:
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class FixedPathController(Node):
    def __init__(self) -> None:
        super().__init__("fixed_path_controller")

        self.map_frame = str(self.declare_parameter("map_frame", "map").value)
        self.base_frame = str(
            self.declare_parameter("base_frame", "base_footprint").value
        )
        self.route_topic = str(
            self.declare_parameter("route_topic", "/slalom_route").value
        )
        self.command_topic = str(
            self.declare_parameter("command_topic", "/nav_cmd_vel_test").value
        )
        self.debug_topic = str(
            self.declare_parameter(
                "debug_topic", "/fixed_path_controller/cmd_debug"
            ).value
        )
        self.status_topic = str(
            self.declare_parameter(
                "status_topic", "/fixed_path_controller/status"
            ).value
        )
        self.localization_topic = str(
            self.declare_parameter(
                "localization_success_topic", "/relocalization/success"
            ).value
        )
        self.e_stop_topic = str(
            self.declare_parameter("e_stop_topic", "/cmd_vel_e_stop").value
        )

        self.dry_run = bool(self.declare_parameter("dry_run", True).value)
        self.require_localization_success = bool(
            self.declare_parameter("require_localization_success", True).value
        )
        self.control_frequency = float(
            self.declare_parameter("control_frequency", 10.0).value
        )
        self.lookahead_distance = float(
            self.declare_parameter("lookahead_distance", 0.30).value
        )
        self.nominal_linear_speed = float(
            self.declare_parameter("nominal_linear_speed", 0.05).value
        )
        self.minimum_linear_speed = float(
            self.declare_parameter("minimum_linear_speed", 0.02).value
        )
        self.maximum_linear_speed = float(
            self.declare_parameter("maximum_linear_speed", 0.08).value
        )
        self.maximum_angular_speed = float(
            self.declare_parameter("maximum_angular_speed", 0.20).value
        )
        self.maximum_linear_accel = float(
            self.declare_parameter("maximum_linear_accel", 0.10).value
        )
        self.maximum_angular_accel = float(
            self.declare_parameter("maximum_angular_accel", 0.25).value
        )
        self.heading_gain = float(self.declare_parameter("heading_gain", 0.20).value)
        self.rotate_gain = float(self.declare_parameter("rotate_gain", 0.80).value)
        self.rotate_in_place_threshold = float(
            self.declare_parameter("rotate_in_place_threshold", 0.65).value
        )
        self.goal_position_tolerance = float(
            self.declare_parameter("goal_position_tolerance", 0.12).value
        )
        self.goal_yaw_tolerance = float(
            self.declare_parameter("goal_yaw_tolerance", 0.25).value
        )
        self.goal_slowdown_distance = float(
            self.declare_parameter("goal_slowdown_distance", 0.50).value
        )
        self.maximum_cross_track_error = float(
            self.declare_parameter("maximum_cross_track_error", 0.35).value
        )
        self.start_position_tolerance = float(
            self.declare_parameter("start_position_tolerance", 0.35).value
        )
        self.start_heading_tolerance = float(
            self.declare_parameter("start_heading_tolerance", 0.80).value
        )
        self.pose_timeout = float(self.declare_parameter("pose_timeout", 0.25).value)
        self.search_behind_points = int(
            self.declare_parameter("search_behind_points", 4).value
        )
        self.search_ahead_points = int(
            self.declare_parameter("search_ahead_points", 30).value
        )
        self.maximum_index_advance = int(
            self.declare_parameter("maximum_index_advance", 8).value
        )

        if self.control_frequency <= 0.0:
            raise ValueError("control_frequency must be positive")
        if self.lookahead_distance <= 0.0:
            raise ValueError("lookahead_distance must be positive")
        if not (0.0 <= self.minimum_linear_speed <= self.maximum_linear_speed):
            raise ValueError("linear speed limits are inconsistent")

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.debug_pub = self.create_publisher(Twist, self.debug_topic, 10)
        self.command_pub = None
        if not self.dry_run:
            self.command_pub = self.create_publisher(Twist, self.command_topic, 10)
        self.status_pub = self.create_publisher(String, self.status_topic, latched_qos)
        self.error_pub = self.create_publisher(
            Float32, "/fixed_path_controller/cross_track_error", 10
        )
        self.progress_pub = self.create_publisher(
            Float32, "/fixed_path_controller/progress", 10
        )
        self.target_pub = self.create_publisher(
            PoseStamped, "/fixed_path_controller/lookahead_target", 10
        )

        self.create_subscription(Path, self.route_topic, self.route_callback, latched_qos)
        self.create_subscription(
            Bool, self.localization_topic, self.localization_callback, latched_qos
        )
        self.create_subscription(Bool, self.e_stop_topic, self.e_stop_callback, 10)
        self.create_service(Trigger, "~/start", self.start_callback)
        self.create_service(Trigger, "~/stop", self.stop_callback)
        self.create_service(Trigger, "~/reset", self.reset_callback)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

        self.route: list[tuple[float, float]] = []
        self.route_headings: list[float] = []
        self.route_distances: list[float] = []
        self.route_signature: tuple[tuple[float, float], ...] = ()
        self.localization_ok = not self.require_localization_success
        self.e_stop_active = False
        self.active = False
        self.state = "IDLE"
        self.state_detail = "waiting for route"
        self.progress_index = 0
        self.last_cross_track_error = math.nan
        self.last_command = Twist()
        self.last_control_time = self.get_clock().now()

        self.create_timer(1.0 / self.control_frequency, self.control_tick)
        self.create_timer(1.0, self.publish_status)
        self.publish_status()
        mode = "DRY-RUN" if self.dry_run else "COMMAND-OUTPUT"
        self.get_logger().warn(
            f"{mode}: fixed path controller, route={self.route_topic}, "
            f"command={self.command_topic}, base={self.base_frame}"
        )

    def route_callback(self, message: Path) -> None:
        frame_id = message.header.frame_id or self.map_frame
        if frame_id != self.map_frame:
            self.get_logger().error(
                f"Rejected route in frame {frame_id}; expected {self.map_frame}"
            )
            return

        points = []
        for pose in message.poses:
            x = float(pose.pose.position.x)
            y = float(pose.pose.position.y)
            if math.isfinite(x) and math.isfinite(y):
                points.append((x, y))
        if len(points) < 2:
            self.get_logger().error("Rejected route with fewer than two finite points")
            return

        signature = tuple((round(x, 4), round(y, 4)) for x, y in points)
        if signature == self.route_signature:
            return
        if self.route_signature and signature != self.route_signature and self.active:
            self.fault("route changed while tracking")
            return
        self.route = points
        self.route_signature = signature
        self.route_distances = [0.0]
        for first, second in zip(points, points[1:]):
            self.route_distances.append(
                self.route_distances[-1] + math.dist(first, second)
            )
        self.route_headings = []
        for index in range(len(points)):
            before = points[max(index - 1, 0)]
            after = points[min(index + 1, len(points) - 1)]
            self.route_headings.append(
                math.atan2(after[1] - before[1], after[0] - before[0])
            )
        if not self.active and self.state in ("IDLE", "READY"):
            self.state = "READY"
            self.state_detail = f"route loaded: {len(points)} points"
        self.get_logger().info(
            f"Loaded fixed route: {len(points)} points, "
            f"length={self.route_distances[-1]:.2f} m"
        )
        self.publish_status()

    def localization_callback(self, message: Bool) -> None:
        self.localization_ok = bool(message.data)
        if self.active and not self.localization_ok:
            self.fault("relocalization success became false")

    def e_stop_callback(self, message: Bool) -> None:
        self.e_stop_active = bool(message.data)
        if self.active and self.e_stop_active:
            self.fault("emergency stop active")

    def lookup_pose(self) -> tuple[float, float, float] | None:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                self.base_frame,
                Time(),
                timeout=Duration(seconds=0.03),
            )
        except TransformException:
            return None

        stamp = Time.from_msg(transform.header.stamp)
        if stamp.nanoseconds > 0:
            age = (self.get_clock().now() - stamp).nanoseconds / 1.0e9
            if age < -0.05 or age > self.pose_timeout:
                return None
        translation = transform.transform.translation
        rotation = transform.transform.rotation
        yaw = quaternion_yaw(rotation.x, rotation.y, rotation.z, rotation.w)
        return float(translation.x), float(translation.y), yaw

    def start_callback(self, _request, response):
        if self.active:
            response.success = False
            response.message = "Controller is already tracking"
            return response
        if self.e_stop_active:
            response.success = False
            response.message = "Emergency stop is active"
            return response
        if self.require_localization_success and not self.localization_ok:
            response.success = False
            response.message = "Relocalization has not succeeded"
            return response
        if len(self.route) < 2:
            response.success = False
            response.message = "No valid fixed route is loaded"
            return response
        pose = self.lookup_pose()
        if pose is None:
            response.success = False
            response.message = "Fresh map->base_footprint TF is unavailable"
            return response
        start_distance = math.dist(pose[:2], self.route[0])
        if start_distance > self.start_position_tolerance:
            response.success = False
            response.message = (
                f"Robot is {start_distance:.3f} m from route start; "
                f"limit is {self.start_position_tolerance:.3f} m"
            )
            return response
        heading_error = wrap_angle(self.route_headings[0] - pose[2])
        if abs(heading_error) > self.start_heading_tolerance:
            response.success = False
            response.message = (
                f"Start heading error is {math.degrees(heading_error):.1f} deg; "
                f"limit is {math.degrees(self.start_heading_tolerance):.1f} deg"
            )
            return response

        self.progress_index = 0
        self.last_control_time = self.get_clock().now()
        self.last_command = Twist()
        self.active = True
        self.state = "TRACKING"
        self.state_detail = "manual start accepted"
        self.publish_status()
        response.success = True
        response.message = "Fixed route tracking started"
        return response

    def stop_callback(self, _request, response):
        was_active = self.active
        self.active = False
        self.state = "STOPPED"
        self.state_detail = "manual stop"
        self.publish_zero()
        self.publish_status()
        response.success = True
        response.message = "Tracking stopped" if was_active else "Controller was idle"
        return response

    def reset_callback(self, _request, response):
        self.active = False
        self.progress_index = 0
        self.last_cross_track_error = math.nan
        self.state = "READY" if self.route else "IDLE"
        self.state_detail = "progress reset"
        self.publish_zero()
        self.publish_status()
        response.success = True
        response.message = "Controller progress reset"
        return response

    def control_tick(self) -> None:
        if not self.active:
            return
        if self.e_stop_active:
            self.fault("emergency stop active")
            return
        if self.require_localization_success and not self.localization_ok:
            self.fault("relocalization is not valid")
            return
        pose = self.lookup_pose()
        if pose is None:
            self.fault("map->base_footprint TF missing or stale")
            return

        x, y, yaw = pose
        search_start = max(self.progress_index - self.search_behind_points, 0)
        search_end = min(
            self.progress_index + self.search_ahead_points + 1, len(self.route)
        )
        closest = min(
            range(search_start, search_end),
            key=lambda index: math.hypot(
                self.route[index][0] - x, self.route[index][1] - y
            ),
        )
        closest = min(closest, self.progress_index + self.maximum_index_advance)
        self.progress_index = max(self.progress_index, closest)
        cross_track_error = math.hypot(
            self.route[self.progress_index][0] - x,
            self.route[self.progress_index][1] - y,
        )
        self.last_cross_track_error = cross_track_error
        self.error_pub.publish(Float32(data=float(cross_track_error)))
        if cross_track_error > self.maximum_cross_track_error:
            self.fault(
                f"cross-track error {cross_track_error:.3f} m exceeds "
                f"{self.maximum_cross_track_error:.3f} m"
            )
            return

        final_x, final_y = self.route[-1]
        final_distance = math.hypot(final_x - x, final_y - y)
        final_heading_error = wrap_angle(self.route_headings[-1] - yaw)
        if final_distance <= self.goal_position_tolerance:
            if abs(final_heading_error) <= self.goal_yaw_tolerance:
                self.complete()
                return
            command = Twist()
            command.angular.z = clamp(
                self.rotate_gain * final_heading_error,
                -self.maximum_angular_speed,
                self.maximum_angular_speed,
            )
            self.publish_limited(command)
            return

        target_distance = self.route_distances[self.progress_index] + self.lookahead_distance
        target_index = min(
            bisect.bisect_left(self.route_distances, target_distance),
            len(self.route) - 1,
        )
        target_x, target_y = self.route[target_index]
        dx = target_x - x
        dy = target_y - y
        cos_yaw = math.cos(yaw)
        sin_yaw = math.sin(yaw)
        body_x = cos_yaw * dx + sin_yaw * dy
        body_y = -sin_yaw * dx + cos_yaw * dy
        lookahead_actual = max(math.hypot(body_x, body_y), 1.0e-3)
        target_angle = math.atan2(body_y, body_x)
        path_heading_error = wrap_angle(self.route_headings[self.progress_index] - yaw)

        command = Twist()
        if body_x <= 0.02 or abs(target_angle) >= self.rotate_in_place_threshold:
            command.angular.z = clamp(
                self.rotate_gain * target_angle,
                -self.maximum_angular_speed,
                self.maximum_angular_speed,
            )
        else:
            speed = clamp(
                self.nominal_linear_speed,
                self.minimum_linear_speed,
                self.maximum_linear_speed,
            )
            angle_scale = clamp(
                1.0 - 0.65 * abs(target_angle) / self.rotate_in_place_threshold,
                self.minimum_linear_speed / max(speed, 1.0e-3),
                1.0,
            )
            remaining = self.route_distances[-1] - self.route_distances[self.progress_index]
            if remaining < self.goal_slowdown_distance:
                angle_scale = min(
                    angle_scale,
                    clamp(
                        remaining / max(self.goal_slowdown_distance, 1.0e-3),
                        self.minimum_linear_speed / max(speed, 1.0e-3),
                        1.0,
                    ),
                )
            command.linear.x = speed * angle_scale
            curvature = 2.0 * body_y / (lookahead_actual * lookahead_actual)
            command.angular.z = clamp(
                command.linear.x * curvature + self.heading_gain * path_heading_error,
                -self.maximum_angular_speed,
                self.maximum_angular_speed,
            )

        target = PoseStamped()
        target.header.frame_id = self.map_frame
        target.header.stamp = self.get_clock().now().to_msg()
        target.pose.position.x = target_x
        target.pose.position.y = target_y
        target.pose.orientation.z = math.sin(0.5 * self.route_headings[target_index])
        target.pose.orientation.w = math.cos(0.5 * self.route_headings[target_index])
        self.target_pub.publish(target)
        progress = self.route_distances[self.progress_index] / max(
            self.route_distances[-1], 1.0e-6
        )
        self.progress_pub.publish(Float32(data=float(progress)))
        self.publish_limited(command)

    def publish_limited(self, target: Twist) -> None:
        now = self.get_clock().now()
        dt = clamp((now - self.last_control_time).nanoseconds / 1.0e9, 1.0e-3, 0.5)
        self.last_control_time = now
        command = Twist()
        command.linear.x = clamp(
            target.linear.x,
            max(0.0, self.last_command.linear.x - self.maximum_linear_accel * dt),
            min(
                self.maximum_linear_speed,
                self.last_command.linear.x + self.maximum_linear_accel * dt,
            ),
        )
        command.angular.z = clamp(
            target.angular.z,
            self.last_command.angular.z - self.maximum_angular_accel * dt,
            self.last_command.angular.z + self.maximum_angular_accel * dt,
        )
        self.last_command = command
        self.debug_pub.publish(command)
        if self.command_pub is not None:
            self.command_pub.publish(command)

    def publish_zero(self) -> None:
        self.last_command = Twist()
        self.last_control_time = self.get_clock().now()
        self.debug_pub.publish(self.last_command)
        if self.command_pub is not None:
            self.command_pub.publish(self.last_command)

    def fault(self, detail: str) -> None:
        self.active = False
        self.state = "FAULT"
        self.state_detail = detail
        self.publish_zero()
        self.publish_status()
        self.get_logger().error(detail)

    def complete(self) -> None:
        self.active = False
        self.progress_index = len(self.route) - 1
        self.state = "COMPLETE"
        self.state_detail = "goal position and yaw reached"
        self.publish_zero()
        self.publish_status()
        self.get_logger().info("Fixed route complete")

    def publish_status(self) -> None:
        total = self.route_distances[-1] if self.route_distances else 0.0
        traveled = (
            self.route_distances[min(self.progress_index, len(self.route_distances) - 1)]
            if self.route_distances
            else 0.0
        )
        payload = {
            "state": self.state,
            "detail": self.state_detail,
            "active": self.active,
            "dry_run": self.dry_run,
            "localization_ok": self.localization_ok,
            "e_stop": self.e_stop_active,
            "route_points": len(self.route),
            "progress_index": self.progress_index,
            "progress": traveled / total if total > 0.0 else 0.0,
            "cross_track_error": (
                self.last_cross_track_error
                if math.isfinite(self.last_cross_track_error)
                else None
            ),
        }
        self.status_pub.publish(String(data=json.dumps(payload, separators=(",", ":"))))


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = FixedPathController()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        if rclpy.ok():
            node.publish_zero()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
