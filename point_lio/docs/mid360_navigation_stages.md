# MID360 Navigation Workflow

This note records the current MID360 + Point-LIO + Nav2 workflow for staged testing.

## Current Stage

Completed:

- MID360 driver publishes `/livox/lidar` and `/livox/imu`.
- Point-LIO runs with `avia.yaml` by default.
- Point-LIO publishes Nav2-compatible TF:
  - `map -> odom`
  - `odom -> base_link`
  - `map -> camera_init`
  - `camera_init -> aft_mapped`
- `cloud_registered_body` is converted to `/scan`.
- Nav2 can run in two safe modes:
  - no static map: `nav2_mid360.launch.py`
  - static map: `nav2_mid360_map.launch.py`
- Nav2 velocity output is remapped to `/nav_cmd_vel_test`.

Do not connect `/nav_cmd_vel_test` to the robot base directly.

## Stage Gate Before Real Robot

Before running on a real quadruped base, add and test a bridge node between Nav2 and the base controller.

The bridge must provide:

- topic remapping from `/nav_cmd_vel_test` to the base command topic
- linear and angular velocity limits
- acceleration limits
- command timeout
- deadman or emergency stop input
- a dry-run mode that prints commands without publishing to the base

This step is required before any real walking test.

A dry-run bridge skeleton is available:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio cmd_vel_safety_bridge.launch.py dry_run:=true
```

Default behavior:

- subscribes to `/nav_cmd_vel_test`
- does not publish to `/cmd_vel` while `dry_run:=true`
- publishes limited debug commands to `/nav_cmd_vel_limited_debug`
- limits forward speed to `0.20 m/s`
- disables lateral speed by default
- limits yaw speed to `0.40 rad/s`
- publishes zero after `0.50 s` without a new command

Only use `dry_run:=false` after the real base command topic, limits, e-stop,
deadman input, and dry-run logs have been reviewed.

## Launch Order

Unified bringup, recommended for normal dry-run testing:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio mid360_nav_bringup.launch.py
```

Default unified bringup behavior:

- starts MID360 driver
- starts optimized Point-LIO with `/scan`
- starts static-map Nav2 with `maps/stage6_test_nav2.yaml`
- starts `cmd_vel_safety_bridge` with `dry_run:=true`
- keeps Nav2 command output on `/nav_cmd_vel_test`
- does not publish real `/cmd_vel`
- keeps RViz off by default

Useful launch switches:

```bash
ros2 launch point_lio mid360_nav_bringup.launch.py driver:=false
ros2 launch point_lio mid360_nav_bringup.launch.py nav2_rviz:=true
ros2 launch point_lio mid360_nav_bringup.launch.py map:=/home/lzh/point_lio/maps/my_map.yaml
ros2 launch point_lio mid360_nav_bringup.launch.py dry_run:=true base_cmd_topic:=/cmd_vel
```

Manual launch order, useful for debugging one layer at a time:

Terminal 1, MID360 driver:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

Terminal 2, Point-LIO:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio point_lio.launch.py rviz:=false
```

Terminal 3, Nav2 without static map:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio nav2_mid360.launch.py rviz:=true
```

Terminal 3, Nav2 with static map:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio nav2_mid360_map.launch.py rviz:=true map:=/home/lzh/point_lio/maps/stage6_test_nav2.yaml
```

## Mapping Procedure

Use a separate PCD file name for every mapping run.

Recommended mapping bringup:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio mid360_mapping_bringup.launch.py \
  rviz:=false \
  pcd_save_file:=my_map.pcd
```

This starts the MID360 driver and Point-LIO only. It disables `/scan`, enables PCD saving,
and does not start Nav2.

Older manual mapping launch:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 launch point_lio point_lio.launch.py rviz:=true scan:=false pcd_save:=true pcd_save_file:=my_map.pcd
```

Walk the lidar slowly through the area, then stop with `Ctrl-C`.

The PCD will be saved under:

```bash
/home/lzh/point_lio/PCD/my_map.pcd
```

Recommended collection rules:

- Keep the lidar height close to the expected robot mounting height.
- Move slowly and smoothly; avoid fast turns.
- Start still for a few seconds before moving.
- Close loops when possible by returning near the starting area.
- Avoid mapping crowds or moving objects.
- Avoid long sessions with `pcd_save_interval: -1`; split large areas into smaller maps.

## Convert PCD To Nav2 Map

Use `--inflate 0.0`. Let Nav2 costmap handle obstacle inflation.

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/point_lio/install/setup.bash
ros2 run point_lio pcd_to_occupancy.py /home/lzh/point_lio/PCD/my_map.pcd \
  --output /home/lzh/point_lio/maps/my_map.yaml \
  --resolution 0.05 \
  --z-min 0.10 \
  --z-max 1.20 \
  --inflate 0.0
```

Output:

- `/home/lzh/point_lio/maps/my_map.yaml`
- `/home/lzh/point_lio/maps/my_map.pgm`

Tune `--z-min` and `--z-max` if the generated map misses obstacles or marks too much ground as occupied.

## Map Acceptance Checks

Check map metadata:

```bash
sed -n '1,20p' /home/lzh/point_lio/maps/my_map.yaml
```

Check occupancy ratio:

```bash
python3 - <<'PY'
from pathlib import Path
import numpy as np
p = Path('/home/lzh/point_lio/maps/my_map.pgm')
with p.open('rb') as f:
    assert f.readline().strip() == b'P5'
    line = f.readline()
    while line.startswith(b'#'):
        line = f.readline()
    w, h = map(int, line.split())
    f.readline()
    data = np.frombuffer(f.read(), dtype=np.uint8)
free = int((data > 250).sum())
occ = int((data < 10).sum())
print('size:', w, h)
print('free_ratio:', round(free / data.size, 3))
print('occupied_ratio:', round(occ / data.size, 3))
PY
```

Useful rough targets:

- Mostly open indoor maps often have more free cells than occupied cells.
- If occupied ratio is very high, the z filter is probably too broad or the map was pre-inflated.
- If occupied ratio is almost zero, the z filter is probably too narrow or too high.

## Planner Smoke Test

After launching static-map Nav2, test planning without moving the robot:

```bash
ros2 action send_goal /compute_path_to_pose nav2_msgs/action/ComputePathToPose \
  "{goal: {header: {frame_id: 'map'}, pose: {position: {x: 0.5, y: 0.0, z: 0.0}, orientation: {w: 1.0}}}, planner_id: 'GridBased'}"
```

Expected:

- `Goal accepted`
- `Goal finished with status: SUCCEEDED`
- path contains more than one pose for non-trivial goals

If it aborts:

- check whether the goal is inside an occupied or inflated area
- try a closer target
- check `global_costmap` in RViz
- regenerate the map with `--inflate 0.0`

Automated multi-goal planner smoke test:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash

ROS_LOG_DIR=/tmp/ros_logs ros2 run point_lio nav_goal_smoke_test.py \
  --goals '0.5,0.0;0.0,0.5;-0.5,0.0;0.0,-0.5;1.0,0.0' \
  --expect 'SUCCEEDED;SUCCEEDED;FAILED;FAILED;FAILED'
```

The script calls `/compute_path_to_pose` and prints CSV:

```text
goal_x,goal_y,state,path_poses,planning_time_sec
```

Use it after changing maps, Nav2 params, Point-LIO params, or Jetson runtime settings.

## Stability Baseline Test

Run this after the driver, Point-LIO, and Nav2 are all active.

Automated system check:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash

ROS_LOG_DIR=/tmp/ros_logs ros2 run point_lio mid360_system_check.py
```

The check reports:

- required nodes and topics
- `/livox/lidar`, `/livox/imu`, `/aft_mapped_to_init`, and `/scan` rates
- Nav2 lifecycle state
- `map -> base_link` TF availability
- `cmd_vel_safety_bridge.dry_run`
- whether `/cmd_vel` is unpublished in dry-run mode
- key process CPU and memory usage

Useful fast mode when the full stack is not running:

```bash
ROS_LOG_DIR=/tmp/ros_logs ros2 run point_lio mid360_system_check.py \
  --skip-hz --skip-tf --skip-cmd-vel-check
```

Topic frequency checks:

```bash
source /opt/ros/humble/setup.bash
source /home/lzh/Uika/livox_ws/install/setup.bash
source /home/lzh/point_lio/install/setup.bash

ROS_LOG_DIR=/tmp/ros_logs timeout 60 ros2 topic hz /livox/lidar
ROS_LOG_DIR=/tmp/ros_logs timeout 60 ros2 topic hz /livox/imu
ROS_LOG_DIR=/tmp/ros_logs timeout 60 ros2 topic hz /aft_mapped_to_init
ROS_LOG_DIR=/tmp/ros_logs timeout 60 ros2 topic hz /scan
ROS_LOG_DIR=/tmp/ros_logs timeout 60 ros2 topic hz /local_costmap/costmap
```

Lifecycle and TF checks:

```bash
ROS_LOG_DIR=/tmp/ros_logs ros2 lifecycle get /map_server
ROS_LOG_DIR=/tmp/ros_logs ros2 lifecycle get /controller_server
ROS_LOG_DIR=/tmp/ros_logs ros2 lifecycle get /planner_server
ROS_LOG_DIR=/tmp/ros_logs ros2 lifecycle get /bt_navigator
ROS_LOG_DIR=/tmp/ros_logs timeout 6 ros2 run tf2_ros tf2_echo map base_link
```

Process resource check:

```bash
ps -eo pid,pcpu,pmem,comm,args | rg 'livox_ros_driver2|pointlio_mapping|controller_server|planner_server|bt_navigator|map_server'
```

Baseline observed on 2026-06-29:

- `/livox/lidar`: about 10 Hz
- `/livox/imu`: about 200 Hz
- `/aft_mapped_to_init`: about 5.8 Hz
- `/scan`: about 5.8 Hz
- `/local_costmap/costmap`: about 1.67 Hz
- Nav2 lifecycle nodes stayed `active`
- `map -> base_link` TF was queryable
- `pointlio_mapping` used about one full CPU core

After changing the launch defaults to `point_filter_num:=3` and
`space_down_sample:=true`, a short test on 2026-06-29 observed:

- `/aft_mapped_to_init`: about 10 Hz
- `/cloud_registered`: about 10 Hz
- `pointlio_mapping`: about 6.5% to 7.5% CPU on the x86 test machine
- `livox_ros_driver2_node`: about 12% to 14% CPU on the x86 test machine

No-base full-stack check on 2026-06-29:

- MID360 driver, optimized Point-LIO, `/scan`, and static-map Nav2 launched together
- `/scan`: about 10 Hz
- `map -> base_link` TF was queryable
- `/map_server`, `/controller_server`, `/planner_server`, and `/bt_navigator` stayed `active`
- `/compute_path_to_pose` to `(0.5, 0.0)` returned `SUCCEEDED`

No-base controller dry-run on 2026-06-29:

- Sent `/navigate_to_pose` goal to `(0.5, 0.0)` in `map`
- Goal was accepted by Nav2
- `/nav_cmd_vel_test` published a velocity command
- Observed sample: linear `x = 0.156 m/s`, angular `z = -0.045 rad/s`
- This only verifies controller output. It does not verify real robot motion tracking.

Safety bridge dry-run on 2026-06-29:

- Started `cmd_vel_safety_bridge.launch.py` with `dry_run:=true`
- Test input `/nav_cmd_vel_test`: linear `x = 1.0 m/s`, linear `y = 0.2 m/s`,
  angular `z = 1.5 rad/s`
- Debug output `/nav_cmd_vel_limited_debug`: linear `x = 0.2 m/s`, linear `y = 0.0 m/s`,
  angular `z = 0.4 rad/s`
- `/cmd_vel` was not published in dry-run mode

Unified bringup check on 2026-06-29:

- `mid360_nav_bringup.launch.py` started MID360 driver, Point-LIO, `/scan`, static-map Nav2,
  and `cmd_vel_safety_bridge`
- `/scan`: about 10 Hz
- `/map_server`, `/controller_server`, `/planner_server`, and `/bt_navigator` stayed `active`
- Key nodes were present: `/livox_lidar_publisher`, `/laserMapping`, `/cmd_vel_safety_bridge`,
  `/map_server`, `/controller_server`, `/planner_server`, `/bt_navigator`

Unified bringup navigation dry-run on 2026-06-29:

- Sent `/navigate_to_pose` goal to `(0.5, 0.0)` in `map`
- Goal was accepted by Nav2
- `/nav_cmd_vel_limited_debug` published safety-limited commands
- Observed sample: linear `x = 0.178 m/s`, linear `y = 0.0 m/s`,
  angular `z = 0.045 rad/s`
- `/cmd_vel` was not published while `dry_run:=true`
- Nav2 later reported `Failed to make progress` and entered recovery behavior because
  no robot base was connected and the pose could not move toward the goal

Existing-map multi-goal dry-run on 2026-06-29 with `stage6_test_nav2.yaml`:

Planner-only `/compute_path_to_pose` checks:

- `(0.5, 0.0)`: `SUCCEEDED`
- `(0.0, 0.5)`: `SUCCEEDED`
- `(-0.5, 0.0)`: `ABORTED`
- `(0.0, -0.5)`: `ABORTED`
- `(1.0, 0.0)`: `ABORTED`

Navigate dry-run checks for successful planner goals:

- `(0.5, 0.0)`: goal accepted, `/nav_cmd_vel_limited_debug` sample linear
  `x = 0.200 m/s`, angular `z = -0.045 rad/s`
- `(0.0, 0.5)`: goal accepted, `/nav_cmd_vel_limited_debug` sample linear
  `x = 0.022 m/s`, angular `z = 0.400 rad/s`
- `/cmd_vel` was not published while `dry_run:=true`
- Without a base, long-running navigate goals can later fail progress checks or enter recovery;
  this is expected during dry-run testing.

Automated planner smoke script check on 2026-06-29:

- Added `nav_goal_smoke_test.py`
- Command returned exit code `0` with expected results
- Output:

```text
0.500,0.000,SUCCEEDED,21,0.003864
0.000,0.500,SUCCEEDED,21,0.000434
-0.500,0.000,FAILED_STATUS_6,0,0.000000
0.000,-0.500,FAILED_STATUS_6,0,0.000000
1.000,0.000,FAILED_STATUS_6,0,0.000000
```

Mapping smoke test on 2026-06-29:

- `mid360_mapping_bringup.launch.py` saved `/home/lzh/point_lio/PCD/mapping_smoke_20260629.pcd`
- PCD size: about 2.8 MB
- PCD points: 90,134
- Converted to `/home/lzh/point_lio/maps/mapping_smoke_20260629.yaml`
- Conversion kept 18,323 points with `--z-min 0.10 --z-max 1.20 --inflate 0.0`
- Map size: 321 x 512
- Occupied ratio: 0.009
- This was a short stationary smoke test, so it validates the toolchain only. It is not a
  real navigation-quality map.

Static mapping flow check on 2026-06-29:

- MID360 was kept stationary to validate the mapping toolchain only
- Saved `/home/lzh/point_lio/PCD/static_flow_01.pcd`
- PCD size: about 11 MB
- PCD points: 332,145
- Converted to `/home/lzh/point_lio/maps/static_flow_01.yaml`
- Conversion kept 66,352 points with `--z-min -0.30 --z-max 0.80 --inflate 0.0`
- Map size: 669 x 360
- Occupied ratio: 0.009
- This confirms PCD saving and Nav2 map conversion. It is not a navigation-quality map.

For longer validation, run the same checks for 5 to 10 minutes and watch for:

- topic frequency dropping to zero
- TF lookup failures after startup
- Nav2 lifecycle nodes leaving `active`
- CPU saturation across multiple cores
- large Point-LIO drift while the sensor is stationary

## Jetson CPU Reduction

Point-LIO is CPU intensive. On 2026-06-29 the x86 test machine first showed
`pointlio_mapping` using about one full CPU core with the heavier launch defaults.
After reducing the input points, the same short test dropped to about 6.5% to 7.5%.
The first optimization is to reduce the number of points processed by Point-LIO.

Recommended default launch settings:

```bash
ros2 launch point_lio point_lio.launch.py \
  rviz:=false \
  point_filter_num:=3 \
  space_down_sample:=true
```

More conservative Jetson setting:

```bash
ros2 launch point_lio point_lio.launch.py \
  rviz:=false \
  point_filter_num:=4 \
  space_down_sample:=true \
  filter_size_surf:=0.7 \
  filter_size_map:=0.7
```

Tradeoffs:

- Higher `point_filter_num` means fewer input points and lower CPU, but less geometric detail.
- Larger `filter_size_surf` and `filter_size_map` mean stronger downsampling and lower CPU, but lower map/detail precision.
- Keep `scan:=true` when running Nav2, because `/scan` depends on `cloud_registered_body`.
- Keep `rviz:=false` on Jetson unless debugging locally.

Suggested Jetson acceptance targets:

- `/livox/lidar`: about 10 Hz
- `/livox/imu`: about 200 Hz
- `/aft_mapped_to_init`: at least 4 Hz for early testing
- `/scan`: at least 4 Hz for early testing
- `pointlio_mapping`: should not force all CPU cores near 100%

If CPU is still too high, increase `point_filter_num` first. If odometry becomes unstable,
restore the previous value and increase voxel sizes more gently.

## Known Notes

- The Livox driver may exit with code `-7` after `Ctrl-C`; this has been seen during shutdown only.
- If ROS2 CLI shows `!rclpy.ok()` or daemon errors, restart the daemon:

```bash
source /opt/ros/humble/setup.bash
ROS_LOG_DIR=/tmp/ros_logs ros2 daemon stop
```
