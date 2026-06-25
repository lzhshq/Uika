# xbox - Xbox 手柄速度指令包

将 Xbox 手柄摇杆数据转换为机器人速度指令的 ROS 2 包。

## 功能特性

- 订阅 `/joy` 话题获取 Xbox 手柄原始数据
- 发布 `/xbox_vel` 话题输出速度指令
- 内置死区处理，避免摇杆漂移
- 支持通过参数动态调整最大速度和死区
- 提供 launch 文件一键启动手柄节点和速度转换节点

## 摇杆映射

| 摇杆 | 轴 | 输出 |
|------|-----|------|
| 左摇杆 Y 轴 | `axes[1]` | `linear.x`（前后速度） |
| 左摇杆 X 轴 | `axes[0]` | `linear.y`（左右速度） |
| 右摇杆 X 轴 | `axes[3]` | `angular.z`（转向角速度） |

## 话题接口

### 订阅

| 话题 | 类型 | 频率 | 说明 |
|------|------|------|------| ros2 launch bringup bringup.launch.py
| `/joy` | `sensor_msgs/Joy` | 由 joy_node 控制 | Xbox 手柄原始数据 |

### 发布

| 话题 | 类型 | 频率 | 说明 |
|------|------|------|------|
| `/xbox_vel` | `geometry_msgs/Twist` | 50 Hz | 机器人速度指令 |

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_linear_speed` | `double` | `1.0` | 最大线速度 (m/s) |
| `max_angular_speed` | `double` | `2.0` | 最大角速度 (rad/s) |
| `deadzone` | `double` | `0.1` | 死区值 (0.0-1.0) |

### 死区说明

当摇杆输入绝对值小于死区值时，输出为 0。例如死区为 0.1 时：
- 输入 0.05 → 输出 0.0
- 输入 0.5 → 输出 (0.5-0.1)/(1-0.1) ≈ 0.44

## 快速开始

### 1. 编译包

```bash
cd ~/Quadruped_Uika
colcon build --packages-select xbox
source ./install/setup.bash
```

### 2. 启动节点

同时启动 joy_node 和 xbox_vel_publisher：

```bash
ros2 launch xbox xbox.launch.py
```

### 3. 查看输出

```bash
# 查看速度指令话题
ros2 topic echo /xbox_vel

# 查看话题列表
ros2 topic list

# 查看节点连接
ros2 topic info /xbox_vel
```

## 参数配置

### 通过 launch 文件修改

编辑 `launch/xbox.launch.py`：

```python
Node(
    package='xbox',
    executable='xbox_vel_publisher',
    name='xbox_vel_publisher',
    output='screen',
    parameters=[{
        'max_linear_speed': 0.5,    # 最大线速度
        'max_angular_speed': 1.5,   # 最大角速度
        'deadzone': 0.15,          # 死区
    }],
),
```

### 通过命令行修改

```bash
# 单参数
ros2 launch xbox xbox.launch.py --ros-args -p max_linear_speed:=0.5

# 多参数
ros2 launch xbox xbox.launch.py --ros-args \
  -p max_linear_speed:=0.5 \
  -p max_angular_speed:=1.0 \
  -p deadzone:=0.15
```

### 通过运行时修改

```bash
# 查看当前参数
ros2 param list /xbox_vel_publisher

# 设置参数
ros2 param set /xbox_vel_publisher max_linear_speed 0.8

# 列出参数
ros2 param get /xbox_vel_publisher max_linear_speed
```

