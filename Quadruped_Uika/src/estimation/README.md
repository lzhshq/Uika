# estimation - 四足机器人状态估计包

## 概述

本包负责四足机器人的**状态估计**，为控制层提供关键的反馈信息。

**核心功能：**
1. **足端触地检测** - 检测每条腿是否接触地面
2. **机体状态估计** - 估计机体位置、姿态、速度（规划中）

---

## 已实现功能

### 触地检测 (Contact Detection)

使用**广义动量法 (Generalized Momentum, GM)** 检测足端触地状态。

#### 原理

当脚接触地面时，地面反作用力会导致关节扭矩变化。GM观测器通过以下公式估计外部扭矩：

```
τ_K = τ_measured + C^T(q,q̇)·q̇ - g(q)
```

其中：
- `τ_measured` - 实测关节扭矩
- `C^T(q,q̇)·q̇` - Coriolis项（来自腿动力学模型）
- `g(q)` - 重力项（来自腿动力学模型）

当 `|τ_K|` 超过阈值时，判定为触地。

#### 订阅话题

| 话题 | 类型 | 频率 | 说明 |
|------|------|------|------|
| `/joint_feedback` | `interfaces::msg::MotorFeedback12` | 100Hz | 关节反馈（扭矩、位置、速度） |

#### 发布话题

| 话题 | 类型 | 说明 |
|------|------|------|
| `/contact_state` | `interfaces::msg::ContactState` | 触地状态 (fl/fr/rl/rr_contact) |

#### 可选订阅

| 话题 | 类型 | 说明 |
|------|------|------|
| `/gait_phase` | `interfaces::msg::GaitPhase` | 步态相位，用于辅助判断（SWING相强制不触地） |

#### 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `contact_threshold` | 5.0 Nm | 触地检测阈值，需根据机器人重量标定 |

---

## 规划功能

### 机体状态估计 (Base State Estimation)

使用**扩展卡尔曼滤波 (EKF)** 融合多传感器数据，估计机体在世界坐标系中的状态。

#### 估计目标

```
/base_state 内容:
  - position: (x, y, z)           # 世界坐标系位置 (m)
  - orientation: quaternion        # 姿态四元数
  - linear_velocity: (vx, vy, vz)  # 线速度 (m/s)
  - angular_velocity: (wx, wy, wz) # 角速度 (rad/s)
```

#### 融合方案

```
传感器输入:
  ├── IMU (高频 100Hz+)
  │     - 角速度 (直接测量)
  │     - 加速度 (需去除重力)
  │
  └── 足端位置 (运动学，低频)
        - 通过正运动学计算机体位置
        - 触地时提供位置修正

EKF 融合输出:
  └── 机体状态 (位置、姿态、速度)
```

#### 作用

| 状态 | 用途 |
|------|------|
| 姿态角 | 平衡控制、倾斜补偿 |
| 线速度 | 速度跟踪、制动控制 |
| 角速度 | 姿态稳定、转向控制 |
| 位置 | 导航、落脚点规划 |

#### 为什么需要融合？

IMU原始数据存在问题：
- **加速度计偏移** → 积分后速度/位置会漂移
- **陀螺仪漂移** → 姿态角长期累积误差
- **磁力计干扰** → 偏航角不稳定

足端位置修正（触地时）：
- 脚相对于地面静止 → 可修正机体位置漂移
- 提供绝对位置参考（相对于起始点）

---

## 文件结构

```
estimation/
├── CMakeLists.txt
├── package.xml
├── README.md
├── include/estimation/
│   ├── types.hpp              # 机器人物理参数
│   ├── leg_dynamics.hpp       # 单腿动力学计算
│   ├── gm_observer.hpp        # 广义动量观测器
│   └── contact_detection_node.hpp  # ROS2节点
└── src/
    ├── main.cpp               # 程序入口
    ├── contact_detection_node.cpp
    ├── gm_observer.cpp
    └── leg_dynamics.cpp
```

---

## 运行方式

```bash
# 启动触地检测节点
ros2 run estimation contact_detection_node

# 带参数运行
ros2 run estimation contact_detection_node --ros-args -p contact_threshold:=3.0
```

---

## 参数标定

### 触地阈值标定步骤

1. **准备**：机器人静止站立，4条腿都在地面上

2. **初始阈值**：从较大值开始（如 10 Nm）

3. **逐渐减小**阈值，观察 `/contact_state` 输出

4. **判断标准**：
   - 所有腿都显示触地 → 阈值合适
   - 出现误报（某腿空中显示触地）→ 阈值太小

5. **安全裕度**：记录出现误报的阈值，加 0.5-1.0 Nm 作为最终值

### 推荐阈值范围

| 机器人重量 | 推荐阈值 |
|------------|----------|
| < 10 kg | 2-4 Nm |
| 10-30 kg | 4-8 Nm |
| > 30 kg | 8-15 Nm |

---

## 接口定义

### ContactState 消息

```yaml
bool fl_contact   # 左前腿是否触地
bool fr_contact   # 右前腿是否触地
bool rl_contact   # 左后腿是否触地
bool rr_contact   # 右后腿是否触地
```

### BaseState 消息（规划中）

```yaml
geometry_msgs/Point position           # 世界坐标系位置
geometry_msgs/Quaternion orientation    # 四元数姿态
geometry_msgs/Vector3 linear_velocity  # 线速度
geometry_msgs/Vector3 angular_velocity  # 角速度
```

---

## 参考资料

- Bledt, G., et al. "Contact model fusion for event-based locomotion in unstructured terrains." ICRA 2018. (GM触地检测)
- De Luca, A., et al. "Collision detection and safe reaction with the DLR-III lightweight manipulator arm." IROS 2006. (广义动量法原始论文)
