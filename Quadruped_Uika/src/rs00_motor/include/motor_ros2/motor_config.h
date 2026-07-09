#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <string>

namespace rs00_motor {

// 当前电机控制包固定管理 12 个电机。
constexpr std::size_t kMotorCount = 12;

// 单个电机的 CAN 通信配置。
struct MotorConfig {
  std::string can_iface;  // CAN 设备名，例如 can1/can2/can3/can4。
  uint8_t master_id;      // 主站 ID，当前 RobStride 通信使用 0xFF。
  uint8_t motor_id;       // 电机 CAN ID。
  int actuator_type;      // RobStride 电机类型，2 表示 ROBSTRIDE_02。
};

// 单个电机的位置限位，单位 rad。
struct JointLimit {
  float min_position;  // 最小允许目标位置。
  float max_position;  // 最大允许目标位置。
};

// 电机命令和反馈的缩放。
// hip/thigh 与上层方向相反；calf 通过 28/15 减速比在电机侧和关节侧间换算。
struct JointTransform {
  float command_position_scale;   // 电机目标位置缩放。
  float feedback_position_scale;  // 电机反馈位置缩放。
  float feedback_torque_scale;    // 电机反馈力矩缩放。
  float feedback_velocity_scale;  // 电机反馈速度缩放。
};

// 默认 PD 增益。上层消息没有给 kp/kd 时使用这里的值。
struct JointGain {
  float kp;  // 默认位置环增益。
  float kd;  // 默认速度环增益。
};

const std::array<MotorConfig, kMotorCount> &motor_configs();
const std::array<JointLimit, kMotorCount> &joint_limits();
const std::array<JointTransform, kMotorCount> &joint_transforms();
const std::array<JointGain, kMotorCount> &joint_gains();

float clamp_position(std::size_t motor_index, float position);

}  // namespace rs00_motor
