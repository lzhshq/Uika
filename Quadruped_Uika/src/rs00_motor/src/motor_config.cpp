#include "motor_ros2/motor_config.h"

#include <algorithm>

namespace rs00_motor {
namespace {

constexpr float kCalfReduction = 28.0f / 15.0f;
constexpr float kCalfReductionInv = 15.0f / 28.0f;

// 下面所有配置表都严格按 0~11 顺序排列，顺序不能随意调整：
// 0 fl_hip, 1 fl_thigh, 2 fl_calf,
// 3 fr_hip, 4 fr_thigh, 5 fr_calf,
// 6 rl_hip, 7 rl_thigh, 8 rl_calf,
// 9 rr_hip, 10 rr_thigh, 11 rr_calf。

// 电机和 CAN 总线映射。
// 每行格式：{CAN 设备名, 主站 ID, 电机 ID, 电机类型}。
// 当前 12 个电机都使用 ROBSTRIDE_02，所以电机类型都是 2。
const std::array<MotorConfig, kMotorCount> kMotorConfigs = {{
    {"can1", 0xFF, 1, 2},   // 0
    {"can1", 0xFF, 2, 2},   // 1
    {"can1", 0xFF, 3, 2},   // 2
    {"can4", 0xFF, 10, 2},  // 3
    {"can4", 0xFF, 11, 2},  // 4
    {"can4", 0xFF, 12, 2},  // 5
    {"can2", 0xFF, 4, 2},   // 6
    {"can2", 0xFF, 5, 2},   // 7
    {"can2", 0xFF, 6, 2},   // 8
    {"can3", 0xFF, 7, 2},   // 9
    {"can3", 0xFF, 8, 2},   // 10
    {"can3", 0xFF, 9, 2},   // 11
}};

// 电机位置限位，单位 rad。
// 限位按最终发给电机的角度理解：髋/大腿命令会取反，小腿命令会乘 28/15。
const std::array<JointLimit, kMotorCount> kJointLimits = {{
    {0.00f, 1.50f},     // 0
    {-0.79f, 0.79f},    // 1
    {0.187f, 2.07f},    // 2
    {-1.50f, 0.00f},    // 3
    {-0.79f, 0.79f},    // 4
    {-2.07f, -0.187f},  // 5
    {-1.50f, 0.00f},    // 6
    {-0.79f, 0.79f},    // 7
    {0.187f, 2.07f},    // 8
    {0.00f, 1.50f},     // 9
    {-0.79f, 0.79f},    // 10
    {-2.07f, -0.187f},  // 11
}};

// 命令和反馈缩放。
// 每行格式：{命令位置缩放, 反馈位置缩放, 反馈力矩缩放, 反馈速度缩放}。
// 翻转关节按实机标定：FL_hip, FL_thigh, FR_hip, FR_calf, RL_thigh, RR_calf。
// 小腿同时保留 28/15 减速比：命令到电机侧乘 28/15，反馈回关节侧乘 15/28。
const std::array<JointTransform, kMotorCount> kJointTransforms = {{
    {-1.0f, -1.0f, -1.0f, -1.0f},                                          // 0 FL_hip
    {-1.0f, -1.0f, -1.0f, -1.0f},                                          // 1 FL_thigh
    { kCalfReduction,  kCalfReductionInv,  kCalfReduction,  kCalfReductionInv},  // 2 FL_calf
    {-1.0f, -1.0f, -1.0f, -1.0f},                                          // 3 FR_hip
    { 1.0f,  1.0f,  1.0f,  1.0f},                                          // 4 FR_thigh
    {-kCalfReduction, -kCalfReductionInv, -kCalfReduction, -kCalfReductionInv},  // 5 FR_calf
    { 1.0f,  1.0f,  1.0f,  1.0f},                                          // 6 RL_hip
    {-1.0f, -1.0f, -1.0f, -1.0f},                                          // 7 RL_thigh
    { kCalfReduction,  kCalfReductionInv,  kCalfReduction,  kCalfReductionInv},  // 8 RL_calf
    { 1.0f,  1.0f,  1.0f,  1.0f},                                          // 9 RR_hip
    { 1.0f,  1.0f,  1.0f,  1.0f},                                          // 10 RR_thigh
    {-kCalfReduction, -kCalfReductionInv, -kCalfReduction, -kCalfReductionInv},  // 11 RR_calf
}};

// 默认 PD 增益，单位和 /motor_command 中的 kp/kd 一致。
// 如果上层命令里的 kp 或 kd 为 0，就使用这里对应电机的默认值。
// 当前按原 README 示例设置：髋/大腿 kp=30，小腿 kp=30，kd 都为 10。
const std::array<JointGain, kMotorCount> kJointGains = {{
    {30.0f, 10.0f},  // 0
    {30.0f, 10.0f},  // 1
    {30.0f, 10.0f},  // 2
    {30.0f, 10.0f},  // 3
    {30.0f, 10.0f},  // 4
    {30.0f, 10.0f},  // 5
    {30.0f, 10.0f},  // 6
    {30.0f, 10.0f},  // 7
    {30.0f, 10.0f},  // 8
    {30.0f, 10.0f},  // 9
    {30.0f, 10.0f},  // 10
    {30.0f, 10.0f},  // 11
}};

}  // namespace

const std::array<MotorConfig, kMotorCount> &motor_configs() {
  return kMotorConfigs;
}

const std::array<JointLimit, kMotorCount> &joint_limits() {
  return kJointLimits;
}

const std::array<JointTransform, kMotorCount> &joint_transforms() {
  return kJointTransforms;
}

const std::array<JointGain, kMotorCount> &joint_gains() {
  return kJointGains;
}

float clamp_position(std::size_t motor_index, float position) {
  const auto &limit = kJointLimits.at(motor_index);
  return std::min(std::max(position, limit.min_position), limit.max_position);
}

}  // namespace rs00_motor
