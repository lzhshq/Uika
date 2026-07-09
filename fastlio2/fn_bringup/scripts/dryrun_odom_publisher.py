#!/usr/bin/env python3
"""Integrate cmd_vel into a fake base_link pose for offline Nav2 dry-runs."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def yaw_to_quaternion(yaw: float) -> tuple[float, float, float, float]:
    half_yaw = yaw * 0.5
    return 0.0, 0.0, math.sin(half_yaw), math.cos(half_yaw)


class DryrunOdomPublisher(Node):
    def __init__(self) -> None:
        super().__init__("dryrun_odom_publisher")
        self.declare_parameter("cmd_vel_topic", "/cmd_vel_test")
        self.declare_parameter("odom_topic", "/dryrun_odom")
        self.declare_parameter("frame_id", "map")
        self.declare_parameter("child_frame_id", "base_link")
        self.declare_parameter("publish_rate", 30.0)
        self.declare_parameter("initial_x", 0.0)
        self.declare_parameter("initial_y", 0.0)
        self.declare_parameter("initial_z", 0.0)
        self.declare_parameter("initial_yaw", 0.0)
        self.declare_parameter("cmd_vel_timeout", 0.5)
        self.declare_parameter("max_linear_x", 1.0)
        self.declare_parameter("max_angular_z", 1.0)

        self.frame_id = str(self.get_parameter("frame_id").value)
        self.child_frame_id = str(self.get_parameter("child_frame_id").value)
        self.x = float(self.get_parameter("initial_x").value)
        self.y = float(self.get_parameter("initial_y").value)
        self.z = float(self.get_parameter("initial_z").value)
        self.yaw = float(self.get_parameter("initial_yaw").value)
        self.cmd_vel_timeout = float(self.get_parameter("cmd_vel_timeout").value)
        self.max_linear_x = abs(float(self.get_parameter("max_linear_x").value))
        self.max_angular_z = abs(float(self.get_parameter("max_angular_z").value))
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.last_cmd_time = self.get_clock().now()
        self.last_update_time = self.get_clock().now()

        self.tf_broadcaster = TransformBroadcaster(self)
        self.pub = self.create_publisher(Odometry, str(self.get_parameter("odom_topic").value), 10)
        self.cmd_sub = self.create_subscription(
            Twist,
            str(self.get_parameter("cmd_vel_topic").value),
            self.on_cmd_vel,
            10,
        )

        publish_rate = max(float(self.get_parameter("publish_rate").value), 1.0)
        self.timer = self.create_timer(1.0 / publish_rate, self.on_timer)
        self.get_logger().info(
            f"Dryrun robot simulator ready. cmd_vel={self.get_parameter('cmd_vel_topic').value}, "
            f"odom={self.get_parameter('odom_topic').value}, tf={self.frame_id}->{self.child_frame_id}, "
            f"initial=({self.x:.3f}, {self.y:.3f}, {self.z:.3f}, yaw={self.yaw:.3f})"
        )

    def on_cmd_vel(self, msg: Twist) -> None:
        self.linear_x = max(-self.max_linear_x, min(self.max_linear_x, float(msg.linear.x)))
        self.angular_z = max(-self.max_angular_z, min(self.max_angular_z, float(msg.angular.z)))
        self.last_cmd_time = self.get_clock().now()

    def on_timer(self) -> None:
        now = self.get_clock().now()
        dt = (now - self.last_update_time).nanoseconds / 1.0e9
        self.last_update_time = now
        if dt < 0.0 or dt > 0.5:
            dt = 0.0

        cmd_age = (now - self.last_cmd_time).nanoseconds / 1.0e9
        vx = self.linear_x if cmd_age <= self.cmd_vel_timeout else 0.0
        wz = self.angular_z if cmd_age <= self.cmd_vel_timeout else 0.0

        self.x += vx * math.cos(self.yaw) * dt
        self.y += vx * math.sin(self.yaw) * dt
        self.yaw = math.atan2(math.sin(self.yaw + wz * dt), math.cos(self.yaw + wz * dt))

        self.publish_tf(now)
        self.publish_odom(now, vx, wz)

    def publish_tf(self, stamp: rclpy.time.Time) -> None:
        qx, qy, qz, qw = yaw_to_quaternion(self.yaw)
        transform = TransformStamped()
        transform.header.stamp = stamp.to_msg()
        transform.header.frame_id = self.frame_id
        transform.child_frame_id = self.child_frame_id
        transform.transform.translation.x = self.x
        transform.transform.translation.y = self.y
        transform.transform.translation.z = self.z
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw
        self.tf_broadcaster.sendTransform(transform)

    def publish_odom(self, stamp: rclpy.time.Time, vx: float, wz: float) -> None:
        qx, qy, qz, qw = yaw_to_quaternion(self.yaw)
        msg = Odometry()
        msg.header.stamp = stamp.to_msg()
        msg.header.frame_id = self.frame_id
        msg.child_frame_id = self.child_frame_id
        msg.pose.pose.position.x = self.x
        msg.pose.pose.position.y = self.y
        msg.pose.pose.position.z = self.z
        msg.pose.pose.orientation.x = qx
        msg.pose.pose.orientation.y = qy
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw
        msg.twist.twist.linear.x = vx
        msg.twist.twist.linear.y = 0.0
        msg.twist.twist.angular.z = wz
        self.pub.publish(msg)


def main() -> None:
    rclpy.init()
    node = DryrunOdomPublisher()
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
