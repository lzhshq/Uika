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
import subprocess
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
    -0.4, 0.2, 0.7,
     0.4, -0.2, -0.7,
     0.4, 0.2, 0.7,
    -0.4, -0.2, -0.7,
]

CALF_REDUCTION = 28.0 / 15.0


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


class SingleMotorSweep(Node):
    def __init__(self):
        super().__init__('single_motor_sweep')

        self.declare_parameter('target_index', 2)
        self.declare_parameter('joint_fields', DEFAULT_JOINT_FIELDS)
        self.declare_parameter('stand_positions', DEFAULT_STAND_POSITIONS)
        self.declare_parameter('amplitude', 0.3)
        self.declare_parameter('start_frequency', 0.1)
        self.declare_parameter('end_frequency', 5.0)
        self.declare_parameter('duration', 40.0)
        self.declare_parameter('publish_rate', 200.0)
        self.declare_parameter('record_rate', 200.0)
        self.declare_parameter('ramp_time', 3.0)
        self.declare_parameter('hold_time', 1.0)
        self.declare_parameter('stand_tolerance', 0.05)
        self.declare_parameter('stand_settle_time', 0.3)
        self.declare_parameter('stand_timeout', 8.0)
        self.declare_parameter('target_kp', 30.0)
        self.declare_parameter('target_kd', 1.5)
        self.declare_parameter('hold_kp', 80.0)
        self.declare_parameter('hold_kd', 3.0)
        self.declare_parameter('generate_pdf', True)
        self.declare_parameter('max_position_error', 0.8)
        self.declare_parameter('feedback_timeout', 0.5)
        self.declare_parameter('response_check_time', 3.0)
        self.declare_parameter('min_command_motion', 0.08)
        self.declare_parameter('min_feedback_motion', 0.03)
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
        self.stand_tolerance = max(float(self.get_parameter('stand_tolerance').value), 0.0)
        self.stand_settle_time = max(float(self.get_parameter('stand_settle_time').value), 0.0)
        self.stand_timeout = max(float(self.get_parameter('stand_timeout').value), 0.1)
        self.target_kp = float(self.get_parameter('target_kp').value)
        self.target_kd = float(self.get_parameter('target_kd').value)
        self.hold_kp = float(self.get_parameter('hold_kp').value)
        self.hold_kd = float(self.get_parameter('hold_kd').value)
        self.generate_pdf = bool(self.get_parameter('generate_pdf').value)
        self.max_position_error = max(float(self.get_parameter('max_position_error').value), 0.0)
        self.feedback_timeout = max(float(self.get_parameter('feedback_timeout').value), 0.05)
        self.response_check_time = max(float(self.get_parameter('response_check_time').value), 0.0)
        self.min_command_motion = max(float(self.get_parameter('min_command_motion').value), 0.0)
        self.min_feedback_motion = max(float(self.get_parameter('min_feedback_motion').value), 0.0)
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

    def _sweep_signal_for_record(self) -> float:
        return self.current_signal

    def _target_amplitude_for_record(self) -> float:
        field = self.joint_fields[self.target_index]
        if field.endswith('_calf'):
            return self.amplitude * CALF_REDUCTION
        return self.amplitude

    def _make_command(self, positions):
        msg = MotorCommand12()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'single_motor_sweep'
        for index, (field, position) in enumerate(zip(self.joint_fields, positions)):
            cmd = getattr(msg, field)
            cmd.torque = 0.0
            cmd.position = float(position)
            cmd.velocity = 0.0
            if index == self.target_index:
                cmd.kp = self.target_kp
                cmd.kd = self.target_kd
            else:
                cmd.kp = self.hold_kp
                cmd.kd = self.hold_kd
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
        header = [
            'phase', 'time', 'current_frequency', 'sweep_signal',
            'target_index', 'target_name',
            'target_kp', 'target_kd', 'hold_kp', 'hold_kd',
        ]
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
               f'{self._sweep_signal_for_record():.6f}', self.target_index,
               self.joint_fields[self.target_index],
               f'{self.target_kp:.6f}', f'{self.target_kd:.6f}',
               f'{self.hold_kp:.6f}', f'{self.hold_kd:.6f}']
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
                if writer is not None:
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

    def _response_check_enabled(self) -> bool:
        return (
            self.response_check_time > 0.0
            and self.min_command_motion > 0.0
            and self.min_feedback_motion > 0.0
        )

    def _check_target_response(self, elapsed: float, cmd_range: float,
                               feedback_range: float) -> bool:
        if not self._response_check_enabled():
            return True
        if elapsed < self.response_check_time:
            return False
        if cmd_range < self.min_command_motion:
            return False
        if feedback_range < self.min_feedback_motion:
            raise RuntimeError(
                f'目标电机没有明显运动: command_range={cmd_range:.4f} rad, '
                f'feedback_range={feedback_range:.4f} rad, '
                f'limit={self.min_feedback_motion:.4f} rad')
        self.get_logger().info(
            f'目标电机响应确认: command_range={cmd_range:.4f}rad, '
            f'feedback_range={feedback_range:.4f}rad')
        return True

    def _max_stand_error(self) -> float:
        if self.feedback is None:
            return float('inf')
        positions = self._feedback_positions()
        return max(abs(target - feedback)
                   for target, feedback in zip(self.stand_positions, positions))

    def _wait_stand_ready(self) -> bool:
        publish_period = 1.0 / self.publish_rate
        deadline = time.monotonic() + self.stand_timeout
        next_pub = time.monotonic()
        stable_since = None
        last_log = 0.0

        while rclpy.ok() and time.monotonic() < deadline:
            now = time.monotonic()
            rclpy.spin_once(self, timeout_sec=0.0)
            if not self._feedback_is_fresh():
                raise RuntimeError('反馈超时，停止扫频')

            if now >= next_pub:
                self._publish_positions(self.stand_positions)
                next_pub += publish_period
                if now - next_pub > publish_period:
                    next_pub = now + publish_period

            max_error = self._max_stand_error()
            if max_error <= self.stand_tolerance:
                if stable_since is None:
                    stable_since = now
                if now - stable_since >= self.stand_settle_time:
                    self.get_logger().info(
                        f'站立姿态已到位: max_error={max_error:.4f}rad, '
                        f'settle={self.stand_settle_time:.2f}s')
                    return True
            else:
                stable_since = None

            if now - last_log >= 1.0:
                self.get_logger().info(
                    f'等待站立姿态到位: max_error={max_error:.4f}rad, '
                    f'limit={self.stand_tolerance:.4f}rad')
                last_log = now

            sleep_time = next_pub - time.monotonic()
            if sleep_time > 0.0:
                time.sleep(min(sleep_time, 0.01))

        self.get_logger().error(
            f'站立姿态到位超时: timeout={self.stand_timeout:.2f}s, '
            f'max_error={self._max_stand_error():.4f}rad')
        return False

    def _generate_pdf_report(self, csv_path: Path):
        if not self.generate_pdf:
            return
        output_pdf = csv_path.with_suffix('.pdf')
        cmd = [
            sys.executable,
            '-m',
            'rs00_sweep.plot_single_motor_sweep',
            str(csv_path),
            '-o',
            str(output_pdf),
        ]
        self.get_logger().info(f'正在生成 PDF 报告: {output_pdf}')
        try:
            result = subprocess.run(
                cmd,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60.0,
            )
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f'PDF 报告生成失败: {exc}')
            return
        if result.returncode == 0 and output_pdf.exists():
            self.get_logger().info(f'PDF 报告已保存: {output_pdf}')
        else:
            detail = (result.stderr or result.stdout).strip()
            self.get_logger().warn(
                f'PDF 报告生成失败，返回码={result.returncode}: {detail}')

    def run(self) -> bool:
        target_name = self.joint_fields[self.target_index]
        output_path = None
        csv_file = None
        sweep_completed = False
        self.get_logger().info('等待 /motor_feedback...')
        if not self._wait_feedback(timeout=5.0):
            self.get_logger().error('5 秒内没有收到 /motor_feedback，取消扫频。')
            return False

        self.get_logger().info(
            f'单电机扫频准备开始: target={self.target_index}({target_name}), '
            f'joint_amp={self.amplitude:.3f}rad, motor_amp={self._target_amplitude_for_record():.3f}rad, '
            f'freq={self.start_frequency:.2f}->{self.end_frequency:.2f}Hz, '
            f'duration={self.duration:.2f}s, target_gain=({self.target_kp:.1f},{self.target_kd:.1f}), '
            f'hold_gain=({self.hold_kp:.1f},{self.hold_kd:.1f})')

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
            self._run_periodic('ramp_to_stand', self.ramp_time, ramp_positions, None)

            self.get_logger().info(
                f'等待站立姿态稳定后开始采集: tolerance={self.stand_tolerance:.3f}rad, '
                f'settle={self.stand_settle_time:.2f}s, timeout={self.stand_timeout:.2f}s')
            if not self._wait_stand_ready():
                return False

            output_path, csv_file, writer = self._open_csv()

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
            target_response_confirmed = not self._response_check_enabled()
            target_cmd_min = float('inf')
            target_cmd_max = float('-inf')
            target_fb_min = float('inf')
            target_fb_max = float('-inf')
            while rclpy.ok():
                now = time.monotonic()
                elapsed = now - t0
                if elapsed >= self.duration:
                    break
                rclpy.spin_once(self, timeout_sec=0.0)
                if not self._feedback_is_fresh():
                    raise RuntimeError('反馈超时，停止扫频')
                if now >= next_pub:
                    positions = sweep_positions(elapsed)
                    self._publish_positions(positions)
                    self._check_target_tracking()
                    feedback_pos = self._feedback_positions()[self.target_index]
                    target_pos = positions[self.target_index]
                    target_cmd_min = min(target_cmd_min, target_pos)
                    target_cmd_max = max(target_cmd_max, target_pos)
                    target_fb_min = min(target_fb_min, feedback_pos)
                    target_fb_max = max(target_fb_max, feedback_pos)
                    if not target_response_confirmed:
                        target_response_confirmed = self._check_target_response(
                            elapsed,
                            target_cmd_max - target_cmd_min,
                            target_fb_max - target_fb_min)
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
                        f'f={self.current_frequency:.3f}Hz | '
                        f'joint_signal={self.current_signal:.4f}rad | '
                        f'motor_signal={self._sweep_signal_for_record():.4f}rad')
                    sweep_log_time = now
                sleep_time = min(next_pub, next_record) - time.monotonic()
                if sleep_time > 0.0:
                    time.sleep(sleep_time)

            self.current_frequency = 0.0
            self.current_signal = 0.0
            self.get_logger().info(f'扫频结束，保持站立姿态: {self.hold_time:.2f}s')
            csv_file.flush()
            csv_file.close()
            self._run_periodic(
                'hold_stand', self.hold_time,
                lambda _elapsed: self.stand_positions,
                None)
            self._publish_positions(self.stand_positions)
            self.get_logger().info(f'扫频完成，CSV 已保存: {output_path}')
            sweep_completed = True
            self._generate_pdf_report(output_path)
            return True
        except RuntimeError as exc:
            self.get_logger().error(str(exc))
            self._publish_positions(self.stand_positions)
            return False
        finally:
            if csv_file is not None and not csv_file.closed:
                csv_file.close()
            if output_path is not None and not sweep_completed:
                try:
                    output_path.unlink(missing_ok=True)
                    self.get_logger().warn(f'已删除未完成 CSV: {output_path}')
                except OSError as exc:
                    self.get_logger().warn(f'未完成 CSV 删除失败: {exc}')


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
