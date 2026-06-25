#!/usr/bin/env python3
"""单电机线性扫频测试节点。

流程：
  1. 等待 /motor_feedback，读取当前 12 个电机位置。
  2. 用 smoothstep 软启动到站立姿态。
  3. 只对 target_index 指定的电机叠加线性 chirp 扫频信号。
  4. 其他 11 个电机始终保持站立姿态。
  5. 扫频完成后回到站立姿态并保存 CSV。
"""

import csv
from datetime import datetime
import math
from pathlib import Path
import sys
import time

import rclpy
from rclpy.node import Node

from interfaces.msg import MotorCommand12, MotorFeedback12


DEFAULT_JOINT_FIELDS = [
    'fl_hip', 'fl_thigh', 'fl_calf',
    'fr_hip', 'fr_thigh', 'fr_calf',
    'rl_hip', 'rl_thigh', 'rl_calf',
    'rr_hip', 'rr_thigh', 'rr_calf',
]

DEFAULT_STAND_POSITIONS = [
    -0.7, 0.2, 0.7,
     0.7, -0.2, -0.7,
     0.7, 0.2, 0.7,
    -0.7, -0.2, -0.7,
]


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


class SingleMotorSweep(Node):
    def __init__(self):
        super().__init__('single_motor_sweep')

        self.declare_parameter('target_index', 2)
        self.declare_parameter('joint_fields', DEFAULT_JOINT_FIELDS)
        self.declare_parameter('stand_positions', DEFAULT_STAND_POSITIONS)
        self.declare_parameter('amplitude', 0.15)
        self.declare_parameter('start_frequency', 0.1)
        self.declare_parameter('end_frequency', 5.0)
        self.declare_parameter('duration', 40.0)
        self.declare_parameter('publish_rate', 500.0)
        self.declare_parameter('record_rate', 500.0)
        self.declare_parameter('ramp_time', 3.0)
        self.declare_parameter('hold_time', 1.0)
        self.declare_parameter('max_position_error', 0.8)
        self.declare_parameter('feedback_timeout', 0.5)
        self.declare_parameter('output_file', '')

        self.target_index = int(self.get_parameter('target_index').value)
        self.joint_fields = list(self.get_parameter('joint_fields').value)
        self.stand_positions = [float(v) for v in self.get_parameter('stand_positions').value]
        self.amplitude = float(self.get_parameter('amplitude').value)
        self.start_frequency = float(self.get_parameter('start_frequency').value)
        self.end_frequency = float(self.get_parameter('end_frequency').value)
        self.duration = max(float(self.get_parameter('duration').value), 0.1)
        self.publish_rate = max(float(self.get_parameter('publish_rate').value), 1.0)
        self.record_rate = max(float(self.get_parameter('record_rate').value), 1.0)
        self.ramp_time = max(float(self.get_parameter('ramp_time').value), 0.1)
        self.hold_time = max(float(self.get_parameter('hold_time').value), 0.0)
        self.max_position_error = max(float(self.get_parameter('max_position_error').value), 0.0)
        self.feedback_timeout = max(float(self.get_parameter('feedback_timeout').value), 0.05)
        self.output_file = str(self.get_parameter('output_file').value)

        self._validate_params()

        self.feedback = None
        self.feedback_time = None
        self.last_command = list(self.stand_positions)
        self.current_frequency = self.start_frequency
        self.current_signal = 0.0

        self.pub = self.create_publisher(MotorCommand12, '/motor_command', 10)
        self.sub = self.create_subscription(
            MotorFeedback12, '/motor_feedback', self._feedback_callback, 10)

    def _validate_params(self):
        if len(self.joint_fields) != 12:
            raise ValueError('joint_fields 必须包含 12 个字段')
        if len(self.stand_positions) != 12:
            raise ValueError('stand_positions 必须包含 12 个位置')
        if self.target_index < 0 or self.target_index >= len(self.joint_fields):
            raise ValueError(f'target_index 超出范围: {self.target_index}')
        if self.amplitude <= 0.0:
            raise ValueError('amplitude 必须大于 0')
        if self.start_frequency <= 0.0 or self.end_frequency <= 0.0:
            raise ValueError('start_frequency/end_frequency 必须大于 0')
        if self.start_frequency > self.end_frequency:
            raise ValueError('start_frequency 不能大于 end_frequency')

    def _feedback_callback(self, msg: MotorFeedback12):
        self.feedback = msg
        self.feedback_time = time.monotonic()

    def _feedback_positions(self):
        return [float(getattr(self.feedback, field).position) for field in self.joint_fields]

    def _feedback_values(self, field_name: str):
        return [float(getattr(getattr(self.feedback, field), field_name))
                for field in self.joint_fields]

    def _make_command(self, positions):
        msg = MotorCommand12()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'single_motor_sweep'
        for field, position in zip(self.joint_fields, positions):
            cmd = getattr(msg, field)
            cmd.torque = 0.0
            cmd.position = float(position)
            cmd.velocity = 0.0
            cmd.kp = 0.0
            cmd.kd = 0.0
        return msg

    def _publish_positions(self, positions):
        self.last_command = list(positions)
        self.pub.publish(self._make_command(positions))

    def _wait_feedback(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while rclpy.ok() and self.feedback is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.05)
        return self.feedback is not None

    def _feedback_is_fresh(self) -> bool:
        if self.feedback_time is None:
            return False
        return (time.monotonic() - self.feedback_time) <= self.feedback_timeout

    def _current_frequency(self, t: float) -> float:
        ratio = max(0.0, min(1.0, t / self.duration))
        return self.start_frequency + (self.end_frequency - self.start_frequency) * ratio

    def _chirp_signal(self, t: float) -> float:
        # 线性 chirp 的相位积分，单位为 cycles。
        sweep_span = self.end_frequency - self.start_frequency
        phase_cycles = self.start_frequency * t + 0.5 * sweep_span * t * t / self.duration
        return self.amplitude * math.sin(2.0 * math.pi * phase_cycles)

    def _default_output_file(self) -> str:
        log_dir = Path.home() / 'uika_sweep_logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        target_name = self.joint_fields[self.target_index]
        return str(log_dir / f'{target_name}_sweep_{stamp}.csv')

    def _open_csv(self):
        output = self.output_file.strip() or self._default_output_file()
        path = Path(output).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        f = path.open('w', newline='')
        writer = csv.writer(f)
        header = ['phase', 'time', 'current_frequency', 'sweep_signal']
        for field in self.joint_fields:
            header.extend([
                f'{field}_cmd_pos',
                f'{field}_fb_pos',
                f'{field}_fb_vel',
                f'{field}_fb_torque',
                f'{field}_fb_temp',
            ])
        writer.writerow(header)
        return path, f, writer

    def _record_row(self, writer, phase_name: str, elapsed: float):
        if self.feedback is None:
            return
        positions = self._feedback_positions()
        velocities = self._feedback_values('velocity')
        torques = self._feedback_values('torque')
        temps = self._feedback_values('temperature')
        row = [phase_name, f'{elapsed:.6f}', f'{self.current_frequency:.6f}',
               f'{self.current_signal:.6f}']
        for i in range(12):
            row.extend([
                f'{self.last_command[i]:.6f}',
                f'{positions[i]:.6f}',
                f'{velocities[i]:.6f}',
                f'{torques[i]:.6f}',
                f'{temps[i]:.6f}',
            ])
        writer.writerow(row)

    def _run_periodic(self, phase_name: str, duration: float, position_fn, writer):
        publish_period = 1.0 / self.publish_rate
        record_period = 1.0 / self.record_rate
        t0 = time.monotonic()
        next_pub = t0
        next_record = t0
        while rclpy.ok():
            now = time.monotonic()
            elapsed = now - t0
            if elapsed >= duration:
                break
            rclpy.spin_once(self, timeout_sec=0.0)
            if not self._feedback_is_fresh():
                raise RuntimeError('反馈超时，停止扫频')
            if now >= next_pub:
                self._publish_positions(position_fn(elapsed))
                next_pub += publish_period
                if now - next_pub > publish_period:
                    next_pub = now + publish_period
            if now >= next_record:
                self._record_row(writer, phase_name, elapsed)
                next_record += record_period
                if now - next_record > record_period:
                    next_record = now + record_period
            sleep_time = min(next_pub, next_record) - time.monotonic()
            if sleep_time > 0.0:
                time.sleep(sleep_time)

    def _check_target_tracking(self):
        if self.max_position_error <= 0.0 or self.feedback is None:
            return
        feedback_pos = self._feedback_positions()[self.target_index]
        target_pos = self.last_command[self.target_index]
        error = abs(target_pos - feedback_pos)
        if error > self.max_position_error:
            raise RuntimeError(
                f'目标电机位置误差过大: error={error:.3f} rad, '
                f'limit={self.max_position_error:.3f} rad')

    def run(self) -> bool:
        target_name = self.joint_fields[self.target_index]
        self.get_logger().info('等待 /motor_feedback...')
        if not self._wait_feedback(timeout=5.0):
            self.get_logger().error('5 秒内没有收到 /motor_feedback，取消扫频。')
            return False

        output_path, csv_file, writer = self._open_csv()
        self.get_logger().info(
            f'单电机扫频准备开始: target={self.target_index}({target_name}), '
            f'amp={self.amplitude:.3f}rad, freq={self.start_frequency:.2f}->{self.end_frequency:.2f}Hz, '
            f'duration={self.duration:.2f}s, output={output_path}')

        try:
            start_positions = self._feedback_positions()

            def ramp_positions(elapsed):
                alpha = smoothstep(elapsed / self.ramp_time)
                return [
                    a + (b - a) * alpha
                    for a, b in zip(start_positions, self.stand_positions)
                ]

            self.current_frequency = 0.0
            self.current_signal = 0.0
            self.get_logger().info(f'软启动到站立姿态: {self.ramp_time:.2f}s')
            self._run_periodic('ramp_to_stand', self.ramp_time, ramp_positions, writer)

            sweep_log_time = time.monotonic()

            def sweep_positions(elapsed):
                self.current_frequency = self._current_frequency(elapsed)
                self.current_signal = self._chirp_signal(elapsed)
                positions = list(self.stand_positions)
                positions[self.target_index] = (
                    self.stand_positions[self.target_index] + self.current_signal)
                return positions

            self.get_logger().info('开始线性 chirp 扫频，其他 11 个电机保持站立姿态。')
            publish_period = 1.0 / self.publish_rate
            record_period = 1.0 / self.record_rate
            t0 = time.monotonic()
            next_pub = t0
            next_record = t0
            while rclpy.ok():
                now = time.monotonic()
                elapsed = now - t0
                if elapsed >= self.duration:
                    break
                rclpy.spin_once(self, timeout_sec=0.0)
                if not self._feedback_is_fresh():
                    raise RuntimeError('反馈超时，停止扫频')
                if now >= next_pub:
                    self._publish_positions(sweep_positions(elapsed))
                    self._check_target_tracking()
                    next_pub += publish_period
                    if now - next_pub > publish_period:
                        next_pub = now + publish_period
                if now >= next_record:
                    self._record_row(writer, 'sweep', elapsed)
                    next_record += record_period
                    if now - next_record > record_period:
                        next_record = now + record_period
                if now - sweep_log_time >= 1.0:
                    progress = 100.0 * elapsed / self.duration
                    self.get_logger().info(
                        f'进度 {progress:.1f}% | t={elapsed:.2f}s | '
                        f'f={self.current_frequency:.3f}Hz | signal={self.current_signal:.4f}rad')
                    sweep_log_time = now
                sleep_time = min(next_pub, next_record) - time.monotonic()
                if sleep_time > 0.0:
                    time.sleep(sleep_time)

            self.current_frequency = 0.0
            self.current_signal = 0.0
            self.get_logger().info(f'扫频结束，保持站立姿态: {self.hold_time:.2f}s')
            self._run_periodic(
                'hold_stand', self.hold_time,
                lambda _elapsed: self.stand_positions,
                writer)
            self._publish_positions(self.stand_positions)
            self.get_logger().info(f'扫频完成，CSV 已保存: {output_path}')
            return True
        except RuntimeError as exc:
            self.get_logger().error(str(exc))
            self._publish_positions(self.stand_positions)
            return False
        finally:
            csv_file.close()


def main():
    rclpy.init()
    try:
        node = SingleMotorSweep()
    except Exception as exc:  # noqa: BLE001
        print(f'参数错误: {exc}', file=sys.stderr)
        rclpy.shutdown()
        sys.exit(2)

    try:
        ok = node.run()
    except KeyboardInterrupt:
        ok = False
        node.get_logger().warn('收到中断，发布站立姿态后退出。')
        node._publish_positions(node.stand_positions)
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
