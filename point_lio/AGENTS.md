# Uika Point-LIO Conversion Notes

This directory is the active Point-LIO workspace for Uika MID360 mapping, localization, PCD-to-2D-map conversion, and Nav2 validation.

## Directory Layout

```text
/home/lzh/Uika/livox_ws     # Livox MID360 driver workspace
/home/lzh/Uika/point_lio    # Point-LIO workspace
/home/lzh/Uika/fastlio2     # FAST-LIO2/FineNav/PCT baseline, formerly /home/lzh/Uika/SLAM
/home/lzh/wuer              # Reference only: Nav2 params, pcd2pgm, pointcloud_to_laserscan, control bridge
```

Keep `livox_ws` independent. Do not place it inside `point_lio`; the driver is a shared sensor dependency.

## Build On Jetson

Jetson is normally `aarch64/ARM64`; x86_64 `build/install` outputs from the development PC cannot be reused. Copy source/config only, then rebuild on Jetson.

Recommended Jetson paths:

```text
/home/nvidia/Uika/livox_ws
/home/nvidia/Uika/point_lio
/home/nvidia/Uika/fastlio2
```

Build order:

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

Expected package prefixes:

```text
/home/nvidia/Uika/livox_ws/install/livox_ros_driver2
/home/nvidia/Uika/point_lio/install/point_lio
```

## Bring-Up Stages

### 1. Driver Only

```bash
source /opt/ros/humble/setup.bash
source /home/nvidia/Uika/livox_ws/install/setup.bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

Check in another terminal:

```bash
ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic echo /livox/lidar --once
```

Expected:

```text
/livox/lidar: 10Hz or 20Hz, depending on launch config
/livox/imu: about 200Hz
/livox/lidar type: livox_ros_driver2/msg/CustomMsg
points[].offset_time and points[].line exist
```

### 2. Point-LIO Only, No RViz

```bash
source /opt/ros/humble/setup.bash
source /home/nvidia/Uika/livox_ws/install/setup.bash
source /home/nvidia/Uika/point_lio/install/setup.bash
ros2 launch point_lio point_lio.launch.py rviz:=false scan:=false
```

Check:

```bash
ros2 topic hz /aft_mapped_to_init
ros2 topic hz /path
ros2 topic list | grep -E "cloud|path|odom|aft|scan"
top
```

Expected:

```text
/aft_mapped_to_init >= 10Hz, ideally close to LiDAR publish rate
Static path does not drift obviously
CPU is not pinned long-term
No repeated buffer clear or sync errors
```

### 3. Motion Stability

Test in this order:

```text
1. MID360 static for 30s
2. Handheld slow walking for 1-2min
3. Mounted on robot, motors not powered
4. Motors powered, robot standing still
5. Very slow straight walking
6. Turns, stairs, slopes
```

Record every step:

```bash
ros2 topic hz /livox/lidar
ros2 topic hz /livox/imu
ros2 topic hz /aft_mapped_to_init
top
```

Interpretation:

```text
Handheld stable but motor-on unstable: check mount rigidity and IMU noise params.
Handheld also fails: check timestamps, LiDAR/IMU extrinsic, and driver output.
Low frequency: disable RViz/dense clouds first, then reduce range or points.
```

### 4. Save PCD And Convert To 2D Map

```bash
ros2 launch point_lio mid360_mapping_bringup.launch.py \
  rviz:=false \
  pcd_save_file:=test_map.pcd
```

Stop with `Ctrl-C`. Expected output:

```text
/home/nvidia/Uika/point_lio/PCD/test_map.pcd
```

Convert:

```bash
ros2 run point_lio pcd_to_occupancy.py \
  /home/nvidia/Uika/point_lio/PCD/test_map.pcd \
  --output /home/nvidia/Uika/point_lio/maps/test_map.yaml \
  --resolution 0.05 \
  --z-min 0.10 \
  --z-max 1.20 \
  --inflate 0.0
```

## Current Strategy

For the fixed obstacle course, use:

```text
3D LIO localization/mapping
2D Nav2 or waypoint following
map-frame trigger zones
gait/skill strategy switching before each obstacle
```

Treat known stairs and steep slopes as passable regions in the 2D map. Trigger gait or policy changes by `map -> base_link` position before and after each obstacle. PCT A* remains a reference or fallback, not the first real-robot conversion path.

## Minimum Success Criteria

```text
MID360 driver is stable
Point-LIO static test does not drift
Point-LIO handheld slow walking does not fly
Mounted motor-on standing does not shake badly
PCD saving works
2D map generation works
```
