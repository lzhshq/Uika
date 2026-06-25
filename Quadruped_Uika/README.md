# 12自由度串腿狗vmc部署

本文档用于整理一个基于 **ROS 2** 的 **12 自由度四足机器人 VMC 控制系统** 的软件架构，目标是支持：

- 支撑相：基于 **VMC** 的足端力 / 关节力矩控制
- 摆动相：基于轨迹跟踪的位控或阻抗控
- 状态估计：获取 `base pose / base vel / joint state / contact state`
- 后续可扩展到：
  - 更完整的接触力分配
  - 基于 QP 的 WBC
  - MPC + WBC 架构

---

## 1. 总体架构

推荐工程分为以下几个包：

1. `description`
2. `interfaces`
3. `estimation`
4. `gait`
5. `control`
6. `bringup`

如需后续接实机，可再增加：

7. `hardware`

---

## 2. Pinocchio 放在哪个包中

推荐把 **Pinocchio** 放在：

## `quadruped_control`

更准确地说：

- 在 `quadruped_control` 包中实现一个 `robot_model` 模块
- 用它统一封装：
  - URDF 读取
  - 前向运动学
  - 足端位置计算
  - 足端 Jacobian 计算
  - 支撑腿 `J^T f` 映射
  - 后续可扩展重力补偿、RNEA、CRBA 等

### 为什么放在 `quadruped_control`

因为你当前最直接使用 Pinocchio 的地方就是控制器内部，主要需求是：

- 主控制节点每周期更新模型
- 查询四个足端位置
- 查询四个足端 Jacobian
- 将接触力映射到关节力矩

这类操作频率高、耦合紧，不适合独立做成 ROS 节点后通过话题通信。  
更适合做成 **控制包内部的库类**，由 `main_controller` 直接调用。

### 推荐结构

在 `quadruped_control` 中增加：

- `include/quadruped_control/robot_model.hpp`
- `src/robot_model.cpp`

内部封装一个类，例如：

- `RobotModel`
- 或 `PinocchioModel`

它不单独起节点，只作为 `main_controller` 的成员对象使用。

---

## 3. 各个包要实现的功能

---

## 3.1 `description`

### 功能

该包用于保存机器人模型与描述文件，主要包括：

- URDF / xacro
- mesh 模型
- 关节命名
- link / frame 命名
- ros2_control 配置所需的关节信息

### 需要实现的内容

- 机器人机身、四条腿的结构描述
- 12 个关节命名规范
- 足端 frame 命名规范
- `base_link`、`imu_link`、`foot_link` 等 frame 定义

### 建议命名

关节建议统一按腿划分，例如：

- `fl_hip_roll_joint`
- `fl_hip_pitch_joint`
- `fl_knee_joint`
- `fr_hip_roll_joint`
- `fr_hip_pitch_joint`
- `fr_knee_joint`
- `rl_hip_roll_joint`
- `rl_hip_pitch_joint`
- `rl_knee_joint`
- `rr_hip_roll_joint`
- `rr_hip_pitch_joint`
- `rr_knee_joint`

足端 frame 建议：

- `fl_foot`
- `fr_foot`
- `rl_foot`
- `rr_foot`

### 本包运行节点

本包通常不自己实现算法节点，但启动时会配合运行：

#### 节点

- `robot_state_publisher`

### 节点订阅话题

- `/joint_states`

### 节点发布话题

- `/tf`
- `/tf_static`
- `/robot_description`（参数形式提供，不一定是显式 topic）

---

## 3.2 `interfaces`

### 功能

该包用于定义系统内部通信的消息接口。

### 需要实现的内容

建议自定义以下消息：

#### `BaseState.msg`

包含：

- `geometry_msgs/Pose pose`
- `geometry_msgs/Twist twist`

或拆成更明确字段：

- position
- orientation
- linear_velocity
- angular_velocity

#### `ContactState.msg`

包含四条腿接触状态，例如：

- `bool fl_contact`
- `bool fr_contact`
- `bool rl_contact`
- `bool rr_contact`

#### `GaitPhase.msg`

包含四条腿当前相位，例如：

- `uint8 fl_phase`
- `uint8 fr_phase`
- `uint8 rl_phase`
- `uint8 rr_phase`

可约定：

- `0`：stance
- `1`：swing

#### `MotionCommand.msg`

包含：

- `float64 vx`
- `float64 vy`
- `float64 wz`
- `float64 body_height`

#### `FootState.msg`（可选）

包含每条腿足端状态：

- position
- velocity
- force（可选）

### 本包运行节点

- 无运行节点

该包只提供消息定义。

---

## 3.3 `estimation`

### 功能

该包用于状态估计，负责根据 IMU、关节状态和接触状态估计：

- `base pose`
- `base linear velocity`
- `base angular velocity`
- `base height`
- 足端接触状态

### 需要实现的内容

- IMU 数据读取与预处理
- base orientation 获取
- base angular velocity 获取
- 基于支撑腿约束的 base linear velocity 估计
- 基于足端运动学的 base z 高度估计
- 接触状态判断或融合

### 本包运行节点

#### 节点 1：`base_state_estimator`

负责输出机身状态。

#### 订阅话题

- `/imu`
- `/joint_states`
- `/contact_state_raw`（如果接触状态由硬件层给出）
- `/tf`（可选，调试用）

#### 发布话题

- `/base_state`

---

#### 节点 2：`contact_estimator`（可选）

如果你想把接触判断单独做一层，可以增加该节点。

#### 订阅话题

- `/joint_states`
- `/imu`
- `/foot_force_raw`（如果有足端力传感器）
- `/motor_state`（可选）

#### 发布话题

- `/contact_state`

> 第一版也可以不单独做 `contact_estimator`，而是在 `base_state_estimator` 内部一起完成。

---

## 3.4 `quadruped_gait`

### 功能

该包用于管理步态调度，确定四条腿在当前控制周期下是：

- 支撑相（stance）
- 摆动相（swing）

并提供：

- 步态相位
- 支撑腿集合
- 摆动腿集合
- 摆动腿相位进度

### 需要实现的内容

- stand 模式下四腿全支撑
- trot 模式下对角腿交替支撑
- phase timer
- gait phase 输出
- 可选：名义落脚点生成

### 本包运行节点

#### 节点：`gait_scheduler`

#### 订阅话题

- `/motion_command`
- `/base_state`
- `/control_mode`（可选）

#### 发布话题

- `/gait_phase`
- `/support_state`（可选）

---

## 3.5 `quadruped_control`

### 功能

该包是整个系统的核心，负责：

- VMC 生成机身 wrench
- 支撑腿接触力分配
- 支撑腿 `J^T f` 映射为关节力矩
- 摆动腿轨迹生成与位控 / 阻抗控
- 合成最终 12 维关节力矩命令
- 发布到 `ros2_control`

### 需要实现的内容

#### 1）主控制节点

- 读取状态估计结果
- 读取步态相位
- 读取运动指令
- 更新 Pinocchio 模型
- 对支撑腿执行 VMC
- 对摆动腿执行位控
- 输出最终力矩

#### 2）VMC 模块

根据机身状态误差生成：

```math
W_{body} =
\begin{bmatrix}
F_{body}\\
M_{body}
\end{bmatrix}