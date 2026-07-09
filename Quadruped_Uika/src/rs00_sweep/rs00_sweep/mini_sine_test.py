#!/usr/bin/env python3
"""Small single-motor sine test before running a full frequency sweep."""

import math
import sys
import time

import rclpy
from rclpy.node import Node

from interfaces.msg import MotorCommand12, MotorFeedback12
from rs00_sweep.single_motor_sweep import DEFAULT_JOINT_FIELDS


class MiniSineTest(Node):
    def __init__(self):
        super().__init__('mini_sine_test')

        self.declare_parameter('target_index', 2)
        self.declare_parameter('amplitude', 0.03)
        self.declare_parameter('frequency', 0.3)
        self.declare_parameter('duration', 6.0)
        self.declare_parameter('publish_rate', 100.0)
        self.declare_parameter('kp', 15.0)
        self.declare_parameter('kd', 8.0)
        self.declare_parameter('feedback_timeout', 0.5)

        self.target_index = int(self.get_parameter('target_index').value)
        self.amplitude = float(self.get_parameter('amplitude').value)
        self.frequency = float(self.get_parameter('frequency').value)
        self.duration = float(self.get_parameter('duration').value)
        self.publish_rate = float(self.get_parameter('publish_rate').value)
        self.kp = float(self.get_parameter('kp').value)
        self.kd = float(self.get_parameter('kd').value)
        self.feedback_timeout = float(self.get_parameter('feedback_timeout').value)

        self._validate_params()

        self.feedback = None
        self.feedback_time = None
        self.pub = self.create_publisher(MotorCommand12, '/motor_command', 10)
        self.sub = self.create_subscription(
            MotorFeedback12, '/motor_feedback', self._feedback_callback, 10)

    def _validate_params(self):
        if self.target_index < 0 or self.target_index >= len(DEFAULT_JOINT_FIELDS):
            raise ValueError(f'target_index out of range: {self.target_index}')
        if self.amplitude <= 0.0:
            raise ValueError('amplitude must be > 0')
        if self.frequency <= 0.0:
            raise ValueError('frequency must be > 0')
        if self.duration <= 0.0:
            raise ValueError('duration must be > 0')
        if self.publish_rate <= 0.0:
            raise ValueError('publish_rate must be > 0')
        if self.feedback_timeout <= 0.0:
            raise ValueError('feedback_timeout must be > 0')

    def _feedback_callback(self, msg: MotorFeedback12):
        self.feedback = msg
        self.feedback_time = time.monotonic()

    def _feedback_positions(self):
        return [
            float(getattr(self.feedback, field).position)
            for field in DEFAULT_JOINT_FIELDS
        ]

    def _wait_feedback(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and self.feedback is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
        return self.feedback is not None

    def _feedback_is_fresh(self) -> bool:
        if self.feedback_time is None:
            return False
        return (time.monotonic() - self.feedback_time) <= self.feedback_timeout

    def _publish_positions(self, positions):
        msg = MotorCommand12()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'mini_sine_test'
        for field, position in zip(DEFAULT_JOINT_FIELDS, positions):
            cmd = getattr(msg, field)
            cmd.torque = 0.0
            cmd.position = float(position)
            cmd.velocity = 0.0
            cmd.kp = self.kp
            cmd.kd = self.kd
        self.pub.publish(msg)

    def run(self) -> bool:
        target_name = DEFAULT_JOINT_FIELDS[self.target_index]
        self.get_logger().info('等待 /motor_feedback...')
        if not self._wait_feedback(timeout=5.0):
            self.get_logger().error('5 秒内没有收到 /motor_feedback，取消测试。')
            return False

        base_positions = self._feedback_positions()
        period = 1.0 / self.publish_rate
        t0 = time.monotonic()
        next_pub = t0
        next_log = t0
        signal = 0.0

        self.get_logger().info(
            f'开始最小正弦测试: target={self.target_index}({target_name}), '
            f'base={base_positions[self.target_index]:.4f}rad, '
            f'amp={self.amplitude:.4f}rad, freq={self.frequency:.3f}Hz, '
            f'duration={self.duration:.2f}s, kp={self.kp:.2f}, kd={self.kd:.2f}')

        try:
            while rclpy.ok():
                now = time.monotonic()
                elapsed = now - t0
                if elapsed >= self.duration:
                    break

                rclpy.spin_once(self, timeout_sec=0.0)
                if not self._feedback_is_fresh():
                    raise RuntimeError('反馈超时，停止最小测试')

                if now >= next_pub:
                    signal = self.amplitude * math.sin(
                        2.0 * math.pi * self.frequency * elapsed)
                    positions = list(base_positions)
                    positions[self.target_index] = (
                        base_positions[self.target_index] + signal)
                    self._publish_positions(positions)
                    next_pub += period
                    if now - next_pub > period:
                        next_pub = now + period

                if now >= next_log:
                    fb_pos = self._feedback_positions()[self.target_index]
                    self.get_logger().info(
                        f't={elapsed:.2f}s target_cmd='
                        f'{base_positions[self.target_index] + signal:.4f}rad '
                        f'target_fb={fb_pos:.4f}rad')
                    next_log = now + 1.0

                sleep_time = next_pub - time.monotonic()
                if sleep_time > 0.0:
                    time.sleep(sleep_time)

            self._publish_positions(base_positions)
            self.get_logger().info('最小正弦测试完成，已回到测试前反馈位置。')
            return True
        except RuntimeError as exc:
            self.get_logger().error(str(exc))
            self._publish_positions(base_positions)
            return False


def main():
    rclpy.init()
    try:
        node = MiniSineTest()
    except Exception as exc:  # noqa: BLE001
        print(f'参数错误: {exc}', file=sys.stderr)
        rclpy.shutdown()
        sys.exit(2)

    try:
        ok = node.run()
    except KeyboardInterrupt:
        ok = False
        node.get_logger().warn('收到中断，退出前发布测试前反馈位置。')
        if node.feedback is not None:
            node._publish_positions(node._feedback_positions())
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
