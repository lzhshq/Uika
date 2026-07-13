#!/usr/bin/env python3
"""Anchor a route template at the robot's current odometry pose and execute it."""

from __future__ import annotations

import json
import math
from typing import Optional

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.duration import Duration
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from std_msgs.msg import String
from std_srvs.srv import Trigger
from tf2_ros import Buffer, TransformException, TransformListener


def quaternion_yaw(x: float, y: float, z: float, w: float) -> float:
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


class RelativePathExecutor(Node):
    def __init__(self) -> None:
        super().__init__("relative_path_executor")

        self.tracking_frame = str(
            self.declare_parameter("tracking_frame", "odom").value
        )
        self.base_frame = str(
            self.declare_parameter("base_frame", "base_footprint").value
        )
        self.template_topic = str(
            self.declare_parameter(
                "template_topic", "/relative_path/template"
            ).value
        )
        self.output_topic = str(
            self.declare_parameter("output_topic", "/relative_path/route").value
        )
        self.pose_timeout = float(self.declare_parameter("pose_timeout", 0.25).value)
        self.start_delay = float(self.declare_parameter("start_delay", 0.30).value)

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.route_pub = self.create_publisher(Path, self.output_topic, latched_qos)
        self.status_pub = self.create_publisher(
            String, "/relative_path_executor/status", latched_qos
        )
        self.create_subscription(
            Path, self.template_topic, self.template_callback, latched_qos
        )
        self.create_subscription(
            String,
            "/fixed_path_controller/status",
            self.controller_status_callback,
            latched_qos,
        )
        self.create_service(Trigger, "~/execute", self.execute_callback)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.controller_start = self.create_client(
            Trigger, "/fixed_path_controller/start"
        )

        self.template: Path | None = None
        self.controller_active = False
        self.pending_start_time = None
        self.start_call_pending = False
        self.create_timer(0.05, self.try_start_controller)
        self.publish_status("WAITING", "waiting for route template")

    def template_callback(self, message: Path) -> None:
        finite_poses = [
            pose
            for pose in message.poses
            if math.isfinite(pose.pose.position.x)
            and math.isfinite(pose.pose.position.y)
        ]
        if len(finite_poses) < 2:
            self.get_logger().error("Rejected relative route template with <2 points")
            return
        copied = Path()
        copied.header = message.header
        copied.poses = finite_poses
        self.template = copied
        self.publish_status(
            "READY", f"template loaded: {len(finite_poses)} points"
        )

    def controller_status_callback(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except (json.JSONDecodeError, TypeError):
            return
        self.controller_active = bool(payload.get("active", False))

    def execute_callback(self, _request, response):
        if self.controller_active or self.pending_start_time is not None:
            response.success = False
            response.message = "Relative path execution is already active or starting"
            return response
        if self.template is None:
            response.success = False
            response.message = "No relative route template has been received"
            return response

        try:
            transform = self.tf_buffer.lookup_transform(
                self.tracking_frame,
                self.base_frame,
                Time(),
                timeout=Duration(seconds=0.10),
            )
        except TransformException as error:
            response.success = False
            response.message = (
                f"Missing {self.tracking_frame}->{self.base_frame} TF: {error}"
            )
            return response

        stamp = Time.from_msg(transform.header.stamp)
        if stamp.nanoseconds > 0:
            age = (self.get_clock().now() - stamp).nanoseconds / 1.0e9
            if age < -0.05 or age > self.pose_timeout:
                response.success = False
                response.message = f"Odometry pose is stale ({age:.3f} s)"
                return response

        translation = transform.transform.translation
        rotation = transform.transform.rotation
        current_yaw = quaternion_yaw(
            rotation.x, rotation.y, rotation.z, rotation.w
        )
        anchored = self.anchor_template(
            float(translation.x), float(translation.y), current_yaw
        )
        self.route_pub.publish(anchored)
        self.pending_start_time = self.get_clock().now() + Duration(
            seconds=self.start_delay
        )
        self.publish_status(
            "STARTING",
            f"anchored at x={translation.x:.3f}, y={translation.y:.3f}, "
            f"yaw={math.degrees(current_yaw):.1f} deg",
        )
        response.success = True
        response.message = "Relative route anchored; controller start is scheduled"
        return response

    def anchor_template(self, start_x: float, start_y: float, start_yaw: float) -> Path:
        assert self.template is not None
        first = self.template.poses[0].pose
        template_yaw = quaternion_yaw(
            first.orientation.x,
            first.orientation.y,
            first.orientation.z,
            first.orientation.w,
        )
        rotation = start_yaw - template_yaw
        cos_rotation = math.cos(rotation)
        sin_rotation = math.sin(rotation)

        route = Path()
        route.header.frame_id = self.tracking_frame
        route.header.stamp = self.get_clock().now().to_msg()
        for template_pose in self.template.poses:
            dx = template_pose.pose.position.x - first.position.x
            dy = template_pose.pose.position.y - first.position.y
            yaw = quaternion_yaw(
                template_pose.pose.orientation.x,
                template_pose.pose.orientation.y,
                template_pose.pose.orientation.z,
                template_pose.pose.orientation.w,
            )
            pose = PoseStamped()
            pose.header = route.header
            pose.pose.position.x = start_x + cos_rotation * dx - sin_rotation * dy
            pose.pose.position.y = start_y + sin_rotation * dx + cos_rotation * dy
            anchored_yaw = yaw + rotation
            pose.pose.orientation.z = math.sin(0.5 * anchored_yaw)
            pose.pose.orientation.w = math.cos(0.5 * anchored_yaw)
            route.poses.append(pose)
        return route

    def try_start_controller(self) -> None:
        if (
            self.pending_start_time is None
            or self.start_call_pending
            or self.get_clock().now() < self.pending_start_time
            or not self.controller_start.service_is_ready()
        ):
            return
        self.pending_start_time = None
        self.start_call_pending = True
        future = self.controller_start.call_async(Trigger.Request())
        future.add_done_callback(self.start_response)

    def start_response(self, future) -> None:
        self.start_call_pending = False
        try:
            response = future.result()
        except Exception as error:  # rclpy service transport failure
            self.publish_status("FAULT", f"controller start call failed: {error}")
            return
        if response.success:
            self.publish_status("TRACKING", response.message)
            self.get_logger().info(response.message)
        else:
            self.publish_status("FAULT", response.message)
            self.get_logger().error(f"Controller rejected relative route: {response.message}")

    def publish_status(self, state: str, detail: str) -> None:
        self.status_pub.publish(
            String(
                data=json.dumps(
                    {"state": state, "detail": detail}, separators=(",", ":")
                )
            )
        )


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = RelativePathExecutor()
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
