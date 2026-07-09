#!/usr/bin/env python3
import math
from typing import Optional

import rclpy
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import Bool


class CmdVelSafetyBridge(Node):
    def __init__(self) -> None:
        super().__init__('cmd_vel_safety_bridge')

        self.input_topic = self.declare_parameter('input_topic', '/nav_cmd_vel_test').value
        self.output_topic = self.declare_parameter('output_topic', '/cmd_vel').value
        self.debug_topic = self.declare_parameter('debug_topic', '/nav_cmd_vel_limited_debug').value
        self.dry_run = bool(self.declare_parameter('dry_run', True).value)

        self.max_linear_x = float(self.declare_parameter('max_linear_x', 0.20).value)
        self.max_linear_y = float(self.declare_parameter('max_linear_y', 0.0).value)
        self.max_angular_z = float(self.declare_parameter('max_angular_z', 0.40).value)
        self.max_linear_accel = float(self.declare_parameter('max_linear_accel', 0.20).value)
        self.max_angular_accel = float(self.declare_parameter('max_angular_accel', 0.50).value)
        self.command_timeout = float(self.declare_parameter('command_timeout', 0.50).value)
        self.log_period = float(self.declare_parameter('log_period', 1.0).value)

        self.require_deadman = bool(self.declare_parameter('require_deadman', False).value)
        self.deadman_topic = self.declare_parameter('deadman_topic', '/cmd_vel_deadman').value
        self.e_stop_topic = self.declare_parameter('e_stop_topic', '/cmd_vel_e_stop').value

        self.last_cmd_time = self.get_clock().now()
        self.last_log_time = self.get_clock().now()
        self.last_output = Twist()
        self.deadman_ok = not self.require_deadman
        self.e_stop_active = False

        self.debug_pub = self.create_publisher(Twist, self.debug_topic, 10)
        self.output_pub = None
        if not self.dry_run:
            self.output_pub = self.create_publisher(Twist, self.output_topic, 10)

        self.create_subscription(Twist, self.input_topic, self.cmd_callback, 10)
        self.create_subscription(Bool, self.deadman_topic, self.deadman_callback, 10)
        self.create_subscription(Bool, self.e_stop_topic, self.e_stop_callback, 10)
        self.create_timer(0.05, self.timeout_callback)

        mode = 'DRY-RUN' if self.dry_run else 'LIVE'
        self.get_logger().warn(
            f'{mode}: {self.input_topic} -> {self.output_topic}, '
            f'limits vx={self.max_linear_x:.3f} m/s, vy={self.max_linear_y:.3f} m/s, '
            f'wz={self.max_angular_z:.3f} rad/s'
        )

    def deadman_callback(self, msg: Bool) -> None:
        self.deadman_ok = bool(msg.data)

    def e_stop_callback(self, msg: Bool) -> None:
        self.e_stop_active = bool(msg.data)

    def cmd_callback(self, msg: Twist) -> None:
        now = self.get_clock().now()
        dt = max((now - self.last_cmd_time).nanoseconds / 1e9, 1e-3)
        self.last_cmd_time = now

        limited = self.limit_twist(msg, dt)
        if self.e_stop_active or not self.deadman_ok:
            limited = Twist()

        self.publish_or_log(limited, now)

    def timeout_callback(self) -> None:
        now = self.get_clock().now()
        age = (now - self.last_cmd_time).nanoseconds / 1e9
        if age <= self.command_timeout:
            return
        if self.is_nonzero(self.last_output):
            self.publish_or_log(Twist(), now, force_log=True)

    def limit_twist(self, msg: Twist, dt: float) -> Twist:
        target = Twist()
        target.linear.x = self.clamp_finite(msg.linear.x, -self.max_linear_x, self.max_linear_x)
        target.linear.y = self.clamp_finite(msg.linear.y, -self.max_linear_y, self.max_linear_y)
        target.angular.z = self.clamp_finite(msg.angular.z, -self.max_angular_z, self.max_angular_z)

        limited = Twist()
        limited.linear.x = self.rate_limit(
            self.last_output.linear.x, target.linear.x, self.max_linear_accel * dt
        )
        limited.linear.y = self.rate_limit(
            self.last_output.linear.y, target.linear.y, self.max_linear_accel * dt
        )
        limited.angular.z = self.rate_limit(
            self.last_output.angular.z, target.angular.z, self.max_angular_accel * dt
        )
        return limited

    def publish_or_log(self, msg: Twist, now, force_log: bool = False) -> None:
        self.last_output = msg
        self.debug_pub.publish(msg)
        if self.output_pub is not None:
            self.output_pub.publish(msg)

        if force_log or (now - self.last_log_time).nanoseconds / 1e9 >= self.log_period:
            self.last_log_time = now
            mode = 'dry-run' if self.dry_run else 'publish'
            blocked = ''
            if self.e_stop_active:
                blocked = ' e_stop'
            elif not self.deadman_ok:
                blocked = ' deadman'
            self.get_logger().info(
                f'{mode}{blocked}: vx={msg.linear.x:.3f}, '
                f'vy={msg.linear.y:.3f}, wz={msg.angular.z:.3f}'
            )

    @staticmethod
    def clamp_finite(value: float, low: float, high: float) -> float:
        if not math.isfinite(value):
            return 0.0
        return min(max(value, low), high)

    @staticmethod
    def rate_limit(current: float, target: float, max_delta: float) -> float:
        if max_delta <= 0.0:
            return target
        return min(max(target, current - max_delta), current + max_delta)

    @staticmethod
    def is_nonzero(msg: Twist) -> bool:
        return (
            abs(msg.linear.x) > 1e-6
            or abs(msg.linear.y) > 1e-6
            or abs(msg.angular.z) > 1e-6
        )


def main(args: Optional[list] = None) -> None:
    rclpy.init(args=args)
    node = CmdVelSafetyBridge()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        try:
            node.destroy_node()
        except KeyboardInterrupt:
            pass
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
