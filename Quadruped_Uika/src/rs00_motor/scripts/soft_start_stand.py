#!/usr/bin/env python3
"""平滑发布站立姿态命令。

用法：
  ros2 run rs00_motor soft_start_stand.py
  ros2 run rs00_motor soft_start_stand.py --duration 3.0 --rate 500

说明：
  - 脚本会先等待 /motor_feedback，读取当前 12 个关节位置。
  - 然后用 smoothstep 插值到默认站立姿态。
  - kp/kd/torque 都发 0，让 rs00_motor 使用 motor_config.cpp 中的默认 kp/kd。
"""

import argparse
import math
import sys
import time

import rclpy
from rclpy.node import Node

from interfaces.msg import MotorCommand12, MotorFeedback12


JOINT_FIELDS = [
    'fl_hip', 'fl_thigh', 'fl_calf',
    'fr_hip', 'fr_thigh', 'fr_calf',
    'rl_hip', 'rl_thigh', 'rl_calf',
    'rr_hip', 'rr_thigh', 'rr_calf',
]

# 默认站立姿态，单位 rad。顺序必须和 JOINT_FIELDS 一致。
STAND_POSITIONS = [
    -0.7, 0.2, 0.7,
     0.7, -0.2, -0.7,
     0.7, 0.2, 0.7,
    -0.7, -0.2, -0.7,
]


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


class SoftStartStand(Node):
    def __init__(self, duration: float, rate_hz: float, hold_time: float):
        super().__init__('soft_start_stand')
        self.duration = max(duration, 0.1)
        self.rate_hz = max(rate_hz, 1.0)
        self.hold_time = max(hold_time, 0.0)
        self.feedback = None
        self.sub = self.create_subscription(
            MotorFeedback12, '/motor_feedback', self.feedback_callback, 10)
        self.pub = self.create_publisher(MotorCommand12, '/motor_command', 10)

    def feedback_callback(self, msg: MotorFeedback12):
        self.feedback = msg

    def wait_feedback(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and self.feedback is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
        return self.feedback is not None

    def feedback_positions(self):
        return [float(getattr(self.feedback, field).position) for field in JOINT_FIELDS]

    def make_command(self, positions):
        msg = MotorCommand12()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'soft_start_stand'
        for field, position in zip(JOINT_FIELDS, positions):
            cmd = getattr(msg, field)
            cmd.torque = 0.0
            cmd.position = float(position)
            cmd.velocity = 0.0
            cmd.kp = 0.0
            cmd.kd = 0.0
        return msg

    def run(self) -> bool:
        self.get_logger().info('等待 /motor_feedback...')
        if not self.wait_feedback(timeout=5.0):
            self.get_logger().error('5 秒内没有收到 /motor_feedback，取消软启动。')
            return False

        start = self.feedback_positions()
        target = STAND_POSITIONS
        max_delta = max(abs(b - a) for a, b in zip(start, target))
        self.get_logger().info(
            f'开始软启动到站立姿态: duration={self.duration:.2f}s, '
            f'rate={self.rate_hz:.1f}Hz, max_delta={max_delta:.3f}rad')

        period = 1.0 / self.rate_hz
        t0 = time.monotonic()
        next_tick = t0
        while rclpy.ok():
            now = time.monotonic()
            u = (now - t0) / self.duration
            if u >= 1.0:
                break
            alpha = smoothstep(u)
            positions = [a + (b - a) * alpha for a, b in zip(start, target)]
            self.pub.publish(self.make_command(positions))
            rclpy.spin_once(self, timeout_sec=0.0)
            next_tick += period
            sleep_time = next_tick - time.monotonic()
            if sleep_time > 0.0:
                time.sleep(sleep_time)
            elif sleep_time < -period:
                next_tick = time.monotonic()

        final_msg = self.make_command(target)
        hold_end = time.monotonic() + self.hold_time
        while rclpy.ok() and time.monotonic() < hold_end:
            self.pub.publish(final_msg)
            rclpy.spin_once(self, timeout_sec=0.0)
            time.sleep(period)
        self.pub.publish(final_msg)
        self.get_logger().info('软启动完成，已发布站立姿态。')
        return True


def main():
    parser = argparse.ArgumentParser(description='平滑启动到默认站立姿态')
    parser.add_argument('--duration', type=float, default=2.0,
                        help='插值时间，单位秒，默认 2.0')
    parser.add_argument('--rate', type=float, default=500.0,
                        help='发布频率 Hz，默认 500')
    parser.add_argument('--hold-time', type=float, default=0.5,
                        help='到达目标后继续发布目标姿态的时间，单位秒，默认 0.5')
    args = parser.parse_args()

    rclpy.init()
    node = SoftStartStand(args.duration, args.rate, args.hold_time)
    try:
        ok = node.run()
    except KeyboardInterrupt:
        ok = False
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
