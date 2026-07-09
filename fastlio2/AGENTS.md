# FineNav Uika 建图流程记录

这份记录用于后续继续接手 FineNav/Uika 建图、地图转换和 PCT 验证时快速恢复上下文。当前目标是完整建图验证，不走轻量化导航链路。

## 2026-07-08 Point-LIO 转换主线

当前 Uika 下的目录职责：

```text
/home/lzh/Uika/livox_ws     # MID360 Livox 驱动工作区，独立于算法包
/home/lzh/Uika/point_lio    # Point-LIO 建图、定位、PCD 转 2D map、Nav2 验证
/home/lzh/Uika/fastlio2     # 原 /home/lzh/Uika/SLAM，保留 FAST-LIO2/FineNav/PCT 基线
/home/lzh/wuer              # 只作为 Nav2、pcd2pgm、pointcloud_to_laserscan、控制桥参考
```

不要把 `livox_ws` 放进 `point_lio` 包内部。Livox 驱动是 MID360 底层依赖，Point-LIO 和 FAST-LIO2 都可能使用，应作为独立 workspace 保持边界清楚。

Jetson 通常是 `aarch64/ARM64`，本机 x86_64 的 `build/install` 不能直接搬过去运行。Jetson 上要复制源码和配置后重新编译，建议保持同样结构：

```text
/home/nvidia/Uika/livox_ws
/home/nvidia/Uika/point_lio
/home/nvidia/Uika/fastlio2
```

Jetson 编译顺序：

```bash
source /opt/ros/humble/setup.bash

cd /home/nvidia/Uika/livox_ws/src/livox_ros_driver2
./build.sh humble

source /home/nvidia/Uika/livox_ws/install/setup.bash

cd /home/nvidia/Uika/point_lio
colcon build --symlink-install --packages-select point_lio

source /home/nvidia/Uika/point_lio/install/setup.bash
ros2 pkg prefix livox_ros_driver2
ros2 pkg prefix point_lio
```

Point-LIO 跑通分阶段：

1. **目录和编译**：先确认 `livox_ros_driver2` 指向 `/home/nvidia/Uika/livox_ws/install`，`point_lio` 指向 `/home/nvidia/Uika/point_lio/install`。
2. **只跑 MID360 驱动**：`ros2 launch livox_ros_driver2 msg_MID360_launch.py`，检查 `/livox/lidar`、`/livox/imu` 频率和 `CustomMsg` 字段。
3. **只跑 Point-LIO，不开 RViz**：`ros2 launch point_lio point_lio.launch.py rviz:=false scan:=false`，检查 `/aft_mapped_to_init`、`/path`、TF 和 CPU。
4. **运动稳定性测试**：按“静止、手持慢走、装机电机不上力、电机上力不走、极慢直线走、转弯/楼梯/斜坡”的顺序测，不要跳步。
5. **保存 PCD 并转 2D**：用 `mid360_mapping_bringup.launch.py` 保存 PCD，再用 `pcd_to_occupancy.py` 生成 Nav2 `yaml/pgm`。

最小成功标准：

```text
MID360 驱动稳定
Point-LIO 静止不飘
Point-LIO 手持慢走不飞
装机电机上力不明显抖
能保存 PCD
能生成 2D map
```

当前策略判断：固定障碍赛主线优先采用 `3D LIO 定位建图 + 2D Nav2/waypoint + map trigger zones + gait/skill 策略切换`。楼梯、大斜坡等固定障碍可以在 2D 地图中当作可通行区域处理，在障碍前后用 `map` 坐标触发策略节点；PCT A* 暂时作为参考/备选，不作为第一条实机转换主线。

## 最新实机强约束：Jetson FAST-LIO 稳定链路

当前 Jetson 实机建图不要一条 launch 同时启动 Livox 驱动和 FAST-LIO。已经多次复现：即使 `/lidar` 是 10Hz、MID360 网络正常，只要 FAST-LIO 进入 `No Effective Points!` 连续刷屏，`/Odometry` 会直接发散到几十米、几百米甚至上千米，RViz 的 path 只是把这个错误轨迹画出来。

已确认一个关键根因：Livox 驱动发布的 `/lidar` 和 `/imu` header 时间戳会逐渐漂移。实测纯驱动下几秒内 `lidar_stamp - imu_stamp` 从约 `-0.16s` 漂到约 `-0.65s`；FAST-LIO 日志随后会出现 `IMU and LiDAR not Synced`，例如 IMU 时间比 LiDAR header 时间落后约 11 秒，然后进入 `No Effective Points!` 并飞。当前必须开启 FAST-LIO 的 `common.time_sync_en: true`。

稳定启动顺序必须是：

```bash
# 0. Jetson 网络和接收缓存
echo nvidia | sudo -S sysctl -w net.core.rmem_max=2147483647
echo nvidia | sudo -S ip link set enxc84d44350d9c up
echo nvidia | sudo -S ip addr flush dev enxc84d44350d9c
echo nvidia | sudo -S ip addr add 192.168.3.50/24 dev enxc84d44350d9c
ping 192.168.3.168

# 1. 只启动 Livox 驱动，先不要启动 FAST-LIO
cd /home/nvidia/Uika/SLAM_fastlio_chain_20260521_224247
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py \
  start_driver:=true \
  start_fast_lio:=false \
  start_localization:=false \
  start_tf_path_publisher:=false \
  start_map_manager:=false \
  start_saved_map_publisher:=false \
  start_pct:=false \
  start_rviz:=false \
  publish_robot_description:=true

# 2. 另开终端确认 /lidar 稳定 10Hz 后，再启动 FAST-LIO/localization/path
ros2 topic hz /lidar --window 50

ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py \
  start_driver:=false \
  start_fast_lio:=true \
  start_localization:=true \
  start_tf_path_publisher:=true \
  start_map_manager:=false \
  start_saved_map_publisher:=false \
  start_pct:=false \
  start_rviz:=false \
  publish_robot_description:=false
```

启动后必须持续检查：

```bash
ros2 topic hz /lidar --window 50
ros2 topic hz /Odometry --window 50
ros2 topic echo /Odometry --once
tail -f /tmp/uika_fastlio_after_driver.log
```

正常条件：

```text
/lidar: 约 10Hz
/Odometry: 约 10Hz
/Odometry position: 应在真实运动范围内连续变化
FAST-LIO 日志：不能连续出现 No Effective Points!
```

如果出现以下任一情况，立即停止本轮建图，不要保存地图：

```text
/Odometry 突然跳到几米、几十米或更大
/Odometry 的 z 明显飞走
FAST-LIO 连续刷 No Effective Points!
/Odometry 频率明显异常并伴随轨迹跳变
```

停止坏链路：

```bash
pkill -f 'ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py'
pkill -f fastlio_mapping
pkill -f livox_ros_driver2_node
pkill -f localization_manager_node
pkill -f tf_path_publisher.py
```

当前实机安装和运行参数以这组为准：

```text
MID360 IP: 192.168.3.168
Jetson MID360 网口: enxc84d44350d9c, 192.168.3.50/24
LiDAR URDF: base_link -> base_lidar
  xyz = 0.26786 0.0 0.07286
  rpy = 0.0 0.7853981634 0.0
Livox driver:
  xfer_format = 1
  publish_freq = 10.0
  self_filtering_radius = 0.3
FAST-LIO:
  preprocess.scan_rate = 10
  preprocess.blind = 0.5
  common.time_sync_en = true
  publish.map_en = false
  publish.scan_publish_en = false
  publish.scan_bodyframe_pub_en = false
  publish.path_en = true
RViz:
  只看 /base_link_path，不发布/显示实时地图点云
```

当前已验证过的独立 Jetson 工作区：

```text
/home/nvidia/Uika/SLAM_fastlio_chain_20260521_224247
```

## 当前核心结论

- 工作仓库是 `/home/lzh/Uika/fastlio2`。
- 当前采用 FineNav 自带 FAST-LIO 建图，不使用 `/home/lzh/point_lio` 建图。
- MID360 当前物理安装外参为 `base_link -> base_lidar: xyz=(0.313, 0.0, -0.06), rpy=(0.0, 1.5707963268, 0.0)`。
- 这个安装外参不要写进 FAST-LIO 的 `mapping.extrinsic_R`。
- FAST-LIO 保存的原始 PCD 是 `lidar_odom` 坐标系下的地图。
- PCT 当前直接把 PCD 当 `map` 坐标系使用，所以导航/规划用 PCD 必须先从 `lidar_odom` 离线转换到 `map`。

## 关键文件

- Uika 建图 launch：
  - `/home/lzh/Uika/fastlio2/fn_bringup/launch/uika_mapping_urdf.launch.py`
- Uika 雷达安装 URDF：
  - `/home/lzh/Uika/fastlio2/fn_bringup/urdf/uika_lidar_mount.urdf`
- MID360 FAST-LIO 参数：
  - `/home/lzh/Uika/fastlio2/fn_bringup/config/fastlio_mid360_config.yaml`
- Map manager 参数：
  - `/home/lzh/Uika/fastlio2/fn_bringup/config/map_manager.yaml`
- PCT 参数：
  - `/home/lzh/Uika/fastlio2/fn_bringup/config/pct_planner.yaml`
- PCD 输出目录：
  - `/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD`
- 保存地图可视化 RViz：
  - `/home/lzh/Uika/fastlio2/fn_bringup/rviz/saved_pcd_map.rviz`

## 当前 TF 设计

作者原始 FineNav 的思路是：

```text
map -> odom -> lidar_odom -> base_lidar
                      \
                       base_link 由 localization_manager 根据 /Odometry 和静态 TF 算出
```

当前 Uika 链路按作者意图保留：

```text
URDF:
  base_link -> base_lidar
  xyz = 0.313 0.0 -0.06
  rpy = 0.0 1.5707963268 0.0

static TF:
  odom -> lidar_odom
  xyz = 0.313 0.0 -0.06
  rpy = 0.0 1.5707963268 0.0

FAST-LIO:
  /Odometry: lidar_odom -> base_lidar
  /cloud_registered: frame_id = lidar_odom
  /cloud_registered_body: frame_id = base_lidar
  /Laser_map: frame_id = lidar_odom
  PCD save: lidar_odom 坐标系
```

注意：修改 URDF/launch 的 z 或 pitch 后，已保存的 PCD 不会自动变化。需要从原始 `lidar_odom` PCD 重新生成一份新的 `map` PCD。

## FAST-LIO 参数原则

`fastlio_mid360_config.yaml` 中当前关键参数：

```yaml
common:
  initial_frame: "lidar_odom"
  body_frame: "base_lidar"
  use_imu_odometry: true

mapping:
  extrinsic_est_en: false
  extrinsic_T: [ -0.011, -0.02329, 0.04412 ]
  extrinsic_R: [ 1., 0., 0.,
                 0., 1., 0.,
                 0., 0., 1. ]

publish:
  tf_en: false

pcd_save:
  pcd_save_en: true
  interval: -1
```

不要把机器人上 MID360 的安装外参写进 `extrinsic_R`。这里的 `extrinsic_R/T` 是 LiDAR 和 MID360 内部 IMU 之间的外参，不是机器人 `base_link` 到 `base_lidar` 的安装关系。

## 启动建图链路

确保 MID360 已连接，然后运行：

```bash
cd /home/lzh/Uika/fastlio2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py
```

这个 launch 当前会启动：

- `robot_state_publisher`，加载 Uika URDF
- `livox_ros_driver2_node`
- `fast_lio`
- `global_localization`
- `odom_to_lidar_odom` 静态 TF
- `local_localization`
- `fn_map_manager_node`

旧的 `lightweight_bringup.launch.py` 和 `fn_lightweight_follower` 已删除；建图验证只走上面的 URDF/FAST-LIO/FineNav 链路。

## Jetson 单机运行策略

当前默认按“全部在 Jetson 上跑”整理：

- Jetson 板载有线口 `enP8p1s0` 保留给笔记本 SSH：`192.168.1.1/24`。
- Jetson USB 转网口 `enxc84d44350d9c` 专门给 MID360：`192.168.3.50/24`。
- MID360 本体 IP 已改为 `192.168.3.168`，SLAM/Livox 配置里的 host IP 应为 `192.168.3.50`，lidar IP 应为 `192.168.3.168`。
- 建图用 `uika_mapping_urdf.launch.py`：默认启动 Livox、FAST-LIO、localization、map_manager；默认不启动 RViz、PCT、保存地图点云发布器。
- 导航/规划用 `uika_live_navigation.launch.py`：默认启动 Livox、FAST-LIO、localization、map_manager、PCT；默认不启动 RViz、保存地图点云发布器，`working_mode` 默认为 `exploration`。
- PC 只建议用 SSH/远程 RViz 调试，不作为必需运行节点。

Jetson 上建图：

```bash
cd /home/lzh/Uika/fastlio2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py
```

Jetson 上保存原始 FAST-LIO PCD 后，直接在 Jetson 上转换成 map 坐标 PCD：

```bash
ros2 run fine_nav2d_bringup convert_lidar_odom_pcd_to_map.py \
  --input /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_raw.pcd \
  --output /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map.pcd

ros2 run fine_nav2d_bringup convert_lidar_odom_pcd_to_map.py \
  --input /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_raw.pcd \
  --output /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd \
  --stride 5
```

Jetson 上导航/规划：

```bash
ros2 launch fine_nav2d_bringup uika_live_navigation.launch.py
```

如果只是跑定位和局部地图、不跑 PCT，可加：

```bash
ros2 launch fine_nav2d_bringup uika_live_navigation.launch.py start_pct:=false
```

## 建图时检查项

启动后检查：

```bash
ros2 topic hz /lidar
ros2 topic hz /imu
ros2 topic hz /cloud_registered_body
ros2 topic hz /Odometry
ros2 topic hz /local_map
ros2 topic hz /ground
ros2 topic echo --once /tf_static
```

当前期望值：

```text
/lidar: 约 20 Hz
/imu: 约 200 Hz
/cloud_registered_body: 约 20 Hz
/Odometry: use_imu_odometry=true 时约 200 Hz
/local_map, /ground, /local_cost_map: 有输出
```

TF 中应能看到：

```text
map -> odom
odom -> lidar_odom: x=0.313, z=-0.06, pitch=90deg
base_link -> base_lidar: x=0.313, z=-0.06, pitch=90deg
```

## 保存原始 FAST-LIO 地图

FAST-LIO 提供 `/map_save` 服务。保存前确认当前参数：

```bash
ros2 param get /fast_lio map_file_path
```

当前 launch 默认保存到：

```text
/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_raw.pcd
```

保存命令：

```bash
ros2 service call /map_save std_srvs/srv/Trigger "{}"
```

这个文件是原始 `lidar_odom` 坐标系 PCD，不直接给 PCT 当 `map` 用。

## 生成 map 坐标系地图

当前已有历史原始 `lidar_odom` PCD：

```text
/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_45deg_01.pcd
```

这个文件名带 `45deg` 是旧命名；它仍然是 FAST-LIO 保存的原始 `lidar_odom` 坐标 PCD。重新实机建图时，launch 默认保存到：

```text
/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_raw.pcd
```

生成出的导航用完整 map PCD：

```text
/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map.pcd
```

生成出的 RViz 可视化降采样 PCD：

```text
/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd
```

当前 `x=0.313, z=-0.06, pitch=90deg` 版本转换结果：

```text
完整点数: 1498589
最低 z: 约 -1.623618
最高 z: 约 5.270564
可视化点数: 299718
```

转换逻辑：

```text
p_map = R_y(90deg) * p_lidar_odom + [0.313, 0, -0.06]
normal_map = R_y(90deg) * normal_lidar_odom
```

这一步只是坐标变换，不抽点、不滤波、不删点。只有 `_viz_stride5.pcd` 是为了 RViz 稳定显示而额外做的 stride=5 降采样副本。

## PCT 使用的地图

`/home/lzh/Uika/fastlio2/fn_bringup/config/pct_planner.yaml` 当前应指向完整 map 坐标地图：

```yaml
pcd_file_path_: "/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map.pcd"
```

不要把 PCT 指到 `_viz_stride5.pcd`，那只是为了 RViz 看整体效果。

当前 `ground_h`：

```yaml
ground_h: -1.65
```

因为当前 p90 转换地图最低 z 约 `-1.623618m`，这个基准先作为首轮验证值。实机规划前要在 RViz/PCT 里检查地面层是否合理；如果地面实际不在最低 z 附近，需要重新校准 `ground_h`。

## 可视化 map 坐标 PCD

直接显示完整 150 万点 PCD 时 RViz 可能退出，所以默认看降采样可视化副本：

```bash
cd /home/lzh/Uika/fastlio2
source /opt/ros/humble/setup.bash
source install/setup.bash
rviz2 -d /home/lzh/Uika/fastlio2/fn_bringup/rviz/saved_pcd_map.rviz
```

RViz 打开后，在另一个终端发布点云：

```bash
cd /home/lzh/Uika/fastlio2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run pcl_ros pcd_to_pointcloud --ros-args \
  -p file_name:=/home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd \
  -p tf_frame:=map \
  -r cloud_pcd:=/saved_map_cloud
```

RViz 配置：

```text
Fixed Frame: map
Topic: /saved_map_cloud
Color Transformer: AxisColor
Axis: Z
```

这里的颜色是高度颜色，不是 PCT 代价颜色。

## 自动获得 base_link 在 map 中的位置

要得到 `base_link` 在 `map` 中的位置，本质上需要维护正确的 `map -> odom`，然后 TF 链会自动给出：

```text
map -> odom -> base_link
```

当前 `localization_manager` 只负责两件事：

- 根据 FAST-LIO 的 `/Odometry` 和静态 `odom -> lidar_odom`，发布 `odom -> base_link`。
- 如果外部节点发布 `/global_localization`（`base_link` 在 `map` 中的位姿），它再计算并发布 `map -> odom`。

它不会自己把当前点云和历史 PCD 地图做全局匹配，所以不能单独靠 `localization_manager` 自动发现机器人在旧地图里的初始位置。

当前 launch 已预留全局定位输入接口，默认关闭：

```bash
ros2 launch fine_nav2d_bringup uika_live_navigation.launch.py \
  global_localization_enable:=true \
  global_localization_topic:=/global_localization \
  global_localization_message_type:=1
```

要做到“开机后自动找到位置”，需要再接一个全局重定位节点：加载已保存的 map PCD，取当前 LiDAR/FAST-LIO 点云，先做粗配准，再用 ICP/NDT/GICP 精配准，最后发布 `geometry_msgs/PoseWithCovarianceStamped` 到 `/global_localization`。`localization_manager` 收到后会发布 `map -> odom`，此后用下面命令即可查看自动得到的机器人位姿：

```bash
ros2 run tf2_ros tf2_echo map base_link
```

第一版建议先做“有粗初值的 ICP/NDT”：从已知起点、AprilTag/标记点、或 RViz `/initialpose` 给粗初值，再局部匹配。完全无初值全局搜索需要 Scan Context/FPFH-RANSAC 等粗定位，会更复杂，也更容易在走廊/重复结构里误匹配。

## PCT 代价颜色说明

如果后面启动 PCT 的 `/tomography_layers`：

- 低 cost 是蓝色
- 高 cost 是红色
- 黄色不是当前 PCT 代码定义的低代价颜色

当前 `/saved_map_cloud` 中看到的黄色只是 `AxisColor` 按 z 高度着色。

## 常见问题

### 为什么不直接把 FAST-LIO 的 `initial_frame` 改成 `map`？

只改名字不会让 FAST-LIO 保存时自动应用 ROS TF。这样会造成“文件名义上是 map，实际坐标还是 lidar_odom”的问题。正确做法是保留原始 `lidar_odom` PCD，再明确离线转换到 `map` PCD。

### 为什么需要保留原始 PCD？

原始 PCD 是 FAST-LIO 的可回溯建图结果。之后如果 `base_link -> base_lidar` 高度、pitch 或 map 对齐策略调整，可以从原始 PCD 重新生成新的 map 坐标 PCD，不必重新采集。

### 改了 URDF/launch 后需要做什么？

需要重启建图 launch 才会更新运行中的 TF。已经保存过的 PCD 不会自动更新，需要重新执行离线转换。

### 当前最新推荐文件

```text
原始 FAST-LIO 地图:
  新建图默认:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_raw.pcd

  当前转换来源历史原始 PCD:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_45deg_01.pcd

导航/PCT 用 map 地图:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map.pcd

RViz 可视化 map 地图:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd
```

# Uika 障碍赛全局规划记录

这部分只记录障碍赛全局规划、任务路径和策略切换思路。当前目标不是让 PCT 直接求一条最短路穿过所有障碍，而是按比赛规则把赛道拆成普通连接段和障碍策略段。

## 当前坐标和地图

当前 dryrun 使用 stair-frame cropped 地图：

```text
map 原点：T 字形台阶最高平台中心
+x：朝高墙方向
+y：朝大斜坡方向
z=0：最高平台中心高度
主地面：约 z=-0.40
```

当前主要文件：

```text
PCT 参数:
  /home/lzh/Uika/fastlio2/fn_bringup/config/pct_scene_terrain_stair_frame_cropped.yaml

语义区域:
  /home/lzh/Uika/fastlio2/fn_bringup/config/uika_terrain_zones_stair_frame.yaml

任务序列:
  /home/lzh/Uika/fastlio2/fn_bringup/config/uika_obstacle_mission_stair_frame.yaml

RViz/PCT 可视地图:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/scene_terrain_map_stair_frame_viz_stride5_cropped.pcd

PCT 规划地图:
  /home/lzh/Uika/fastlio2/fn_localization/Fast_LIO/PCD/scene_terrain_map_stair_frame_lowbar_highwall_passable_cropped.pcd
```

当前 PCT 关键参数原则：

```yaml
ground_h: -0.4
resolution: 0.05
slice_dh: 0.05
interval_min: 0.05
max_step_height: 0.15
safe_margin: 0.05
inflation: 0.0
path_smoothing_enabled: false
```

PCT 只负责基础可通行性和普通连接段，不为单个障碍调大全局 `safe_margin/inflation`。障碍专用逻辑放在 mission 和 policy 里。

## 当前任务顺序

当前任务顺序：

```text
start_down_stairs
-> high_wall
-> pole_slalom
-> gravel_wood_pit
-> low_bar
-> big_slope
-> bridge_b
-> bridge_a
-> t_stairs
```

其中 `big_slope`、`bridge_b`、`bridge_a` 的具体路径暂不细化，后续单独设计。当前只保留任务节点、入口出口和对应 policy。

当前启动任务：

```text
current_task = start_down_stairs
current_policy = stair_policy
```

## 线的含义

RViz 中不要混淆三类线：

```text
mission_task_route:
  彩色线，表示障碍内部策略段。

mission_connector_route:
  白色线，表示障碍之间的普通连接段。
  只连接 start -> 第一个任务 entry，以及上一个任务 exit -> 下一个任务 entry。

mission_route / mission_full_route:
  当前禁用。不要用一整条白线串所有点，否则会把高墙、台阶、桥等误看成普通行走路径。
```

## 已细化障碍路径和策略

### 起始下台阶 start_down_stairs

策略：

```text
stair_policy
```

含义：从最高平台启动，先沿高墙一侧下台阶，再进入高墙前普通连接段。

当前路径：

```text
entry:    [0.00, 0.00,  0.00]
required: [0.65, 0.00, -0.10]
required: [0.95, 0.00, -0.20]
required: [1.25, 0.00, -0.30]
exit:     [1.80, 0.00, -0.40]
```

这些点是台阶顶面接触/经过参考点，不是普通 PCT 平地路径。

### 高墙 high_wall

策略：

```text
wall_climb_policy
```

语义：高墙是可通过障碍段，但不是普通平地。PCT 规划地图中高墙本体已做 passable 处理；真实执行时应切到跃过/攀爬策略。

当前路径：

```text
entry:    [2.95, 0.00, -0.40]
required: [3.50, 0.00, -0.10]
exit:     [4.05, 0.00, -0.40]
```

`required` 表示墙上方/墙中心动作参考点，不表示普通底盘中心必须贴地经过。

### 直角绕杆 pole_slalom

策略：

```text
slalom_policy
```

绕杆区使用局部安全边距，不改 PCT 全局参数：

```yaml
safe_margin: 0.20
mandatory_zone_radius: 0.175
```

当前含义：

```text
mandatory_zones:
  比赛规则中的 3 个红色圆形必达区。

pole_centers:
  4 根竖杆中心，只用于语义和避障参考。

bezier_path:
  绕杆实际显示/跟踪的平滑曲线路径，减少转向突变。
```

当前入口和出口：

```text
entry: [6.60, -0.175, -0.40]
exit:  [8.825, 1.40, -0.40]
```

后续策略层应读取 `safe_margin=0.20`，只在绕杆区按局部更大安全距离处理。

### 砂砾碎木坑 gravel_wood_pit

策略：

```text
gravel_policy
```

规则重点：必须从 1m 短边进入或离开；如果 1/2 以上足端或身体支撑到地面，则该障碍失败。

当前路径使用贝塞尔曲线，入口靠近绕杆出口，出口接限高杆入口：

```text
entry: [8.825, 2.45, -0.25]
exit:  [6.35, 3.90, -0.40]
```

任务层记录：

```yaml
entry_rule: short_edge_only
```

后续策略层需要补：短边进出校验、足端接触/机身接触判定、失败后重新进入该障碍。

### 限高杆 low_bar

策略：

```text
low_bar_policy
```

语义：中间通道可通行，两根立柱为不可通行 obstacle；横杆上方点已从规划 PCD 中处理掉，避免 PCT 把低杆中心误判为不可通行。

当前路径：

```text
entry:    [6.35, 3.90, -0.40]
required: [5.50, 3.90, -0.40]
exit:     [4.65, 3.90, -0.40]
```

执行时应切低姿态/低身策略，通过后恢复正常姿态；不能碰倒限高杆。

### 终点台阶 t_stairs

策略：

```text
stair_policy
```

当前保留最终通过台阶的任务段，用于后续从桥 A 返回台阶时接入。台阶路径沿同一直线的两段台阶，要求至少每一级顶面有一次足底接触。

当前入口和出口：

```text
entry: [1.55, 0.00, -0.40]
exit:  [1.80, 0.00, -0.40]
```

中间 required_points 是每一级台阶顶面参考点。不要把台阶简化为普通 PCT 直线。

## 暂不细化的障碍

以下任务节点保留，但具体全局路径/策略细节暂不定稿：

```text
big_slope: slope_policy
bridge_b:  bridge_policy
bridge_a:  bridge_policy
```

后续再分别决定大斜坡的进入方向、长边行走距离校验，以及桥 A/B 的身体中心线和足端策略。

## 任务切换接口

当前第一版任务管理仍是手动推进：

```bash
ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'next'}"
ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'prev'}"
ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'reset'}"
ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'set pole_slalom'}"
ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'reload'}"
```

策略管理器后续应订阅：

```text
/current_task
/current_policy
/mission_status
/terrain_segments
```

任务层只发布当前 policy 和任务结构，不直接发布真实 `/cmd_vel`。

## 容易犯的错误

- 不要把 MID360 的机器人安装角写进 FAST-LIO 的 `extrinsic_R`。
- 不要把 FAST-LIO 保存的 `lidar_odom` PCD 直接当 `map` PCD 给 PCT。
- 不要为了绕杆把 PCT 全局 `safe_margin` 改大。
- 不要启用 `mission_route` / `mission_full_route` 作为主显示。
- 不要把高墙、限高杆、碎木坑、台阶这类规则障碍只当作普通全局路径问题。
- 当前大斜坡和桥 A/B 的路径还未定稿，不要在 AGENTS 中把它们写死。
