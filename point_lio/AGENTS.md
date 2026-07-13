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

Use the complete interactive mapping script on the Jetson:

```bash
cd /home/lzh/Uika/point_lio
./build_map.sh
```

Run it from the control PC. The script starts PC-side RViz with
`tf_path_only.rviz`, then opens an interactive SSH session to run the mapping
half on the Jetson. RViz uses `map` as its fixed frame and renders only a
`base_link` Axes display plus `/path`; the TF tree and dense clouds are disabled.
Running the same script directly on the Jetson is still supported, but cannot
start the PC GUI because reverse SSH is unavailable.

Enter an ASCII map name, map the course, then press `Ctrl+S`. The script calls
`/save_map`, stops Point-LIO cleanly, and writes both map representations under
`/home/nvidia/Uika/point_lio/maps/`:

```text
<name>.pcd       3D map for relocalization
<name>.yaml      Nav2 map metadata
<name>.pgm       Nav2 occupancy image
```

The default occupancy conversion uses 0.05 m cells, z=0.10..1.20 m, and no
baked-in inflation. Nav2 costmap inflation remains responsible for clearance.
The script accepts overrides through `MAP_RESOLUTION`, `MAP_Z_MIN`,
`MAP_Z_MAX`, `MAP_PADDING`, and `MAP_INFLATION`.

Formal mapping uses a conservative quality profile without changing navigation
defaults: `point_filter_num=2`, `filter_size_surf=0.20`,
`filter_size_map=0.20`, and `ivox_nearby_type=6`. Keep the MID360 frame rate at
10 Hz and verify `/aft_mapped_to_init` remains at 10 Hz. Tests on the Jetson
showed that `1 / 0.15 / 0.20 / nearby 18` dropped odometry to about 3.2 Hz and
`2 / 0.15 / 0.20 / nearby 6` reached only about 7.6 Hz, so neither should be
used for formal mapping. Navigation and live localization retain
`2 / 0.20 / 0.30 / nearby 6` for additional CPU headroom.

The mapping bringup intentionally disables `/cloud_registered`,
`/cloud_registered_body`, `/Laser_map`, and `/scan`. Its RViz configuration
subscribes only to TF and `/path`; PCD accumulation remains enabled internally.

The equivalent manual save call is:

```bash
ros2 service call /save_map std_srvs/srv/Trigger '{}'
```

The equivalent manual conversion is:

```bash
ros2 run point_lio pcd_to_occupancy.py \
  /home/nvidia/Uika/point_lio/maps/test_map.pcd \
  --output /home/nvidia/Uika/point_lio/maps/test_map.yaml \
  --resolution 0.05 \
  --z-min 0.10 \
  --z-max 1.20 \
  --inflate 0.0
```

View both saved representations from the control PC:

```bash
cd /home/lzh/Uika/point_lio
./view_map.sh <map_name>
```

The viewer syncs `<map_name>.pcd/.pgm/.yaml` from the Jetson and opens one RViz
with independently toggleable `3D PCD` and `2D Occupancy` displays.

### 4.1 PC Rosbag Offline High-Quality Mapping

For the final map, record the unmodified MID360 streams first and run Point-LIO
afterward at reduced playback speed. This decouples sensor input from estimator
compute time, so the denser `0.10 m` voxel profile does not force Point-LIO to
drop below the sensor's 10 Hz input rate while recording.

Record on the PC connected directly to MID360:

```bash
cd /home/lzh/Uika/point_lio
./record_mid360_bag_pc.sh course_raw
```

The recorder starts only the Livox driver and stores `/livox/lidar` plus
`/livox/imu` under `bags/course_raw/`. Press `Ctrl+S` to finalize and retain the
bag; `Ctrl+C` discards an incomplete recording. A successful stop also writes
`capture_report.txt` with duration, message counts, measured topic rates, and a
PASS/WARNING result, plus the complete driver/recorder output in `session.log`.
The capture passes automatically at LiDAR >= 8 Hz and IMU >= 150 Hz.

Build the high-quality map offline:

```bash
./build_map_from_bag_pc.sh course_raw course_hq
```

The default offline profile uses `PLAYBACK_RATE=0.20`, `point_filter_num=1`, and
`filter_size_surf/map=0.10/0.10 m`. It writes `course_hq.pcd`,
`course_hq.pgm`, and `course_hq.yaml` under `maps/`. If processing cannot keep
up, reduce playback speed without changing sensor timestamps:

```bash
PLAYBACK_RATE=0.15 ./build_map_from_bag_pc.sh course_raw course_hq_slow
```

Keep the live PC mapping profile at `0.15/0.15 m`; `0.10 m` is reserved for
slow offline playback. The bag must contain the same MID360 LiDAR and IMU data
used on the Jetson, and the offline Point-LIO calibration must match the Jetson
localization calibration.

### 4.2 Fixed-Start Relocalization Validation

Run from the control PC after placing the robot at the mapping start pose:

```bash
cd /home/lzh/Uika/point_lio
./start_relocalization.sh sushe
```

This starts MID360 and Point-LIO on the Jetson without Nav2, accumulates 10
static body-frame scans, aligns them to the local PCD using yaw-seeded NDT and
ICP, and requires three consistent batches before publishing `map -> odom`.
Monitor `/relocalization/status`, `/relocalization/rmse`,
`/relocalization/overlap`, and `/relocalization/success`. Retry without restarting
the chain with `ros2 service call /relocalize std_srvs/srv/Trigger '{}'`.

Periodic correction development is isolated behind `continuous_shadow.enabled`,
which defaults to `false`. Shadow mode time-aligns each body cloud with odometry,
accumulates the clouds in `odom`, and computes low-rate candidate `map -> odom`
corrections on a worker thread. It publishes candidates on
`/relocalization/candidate_map_to_odom` but never changes TF. Enable it only for
validation with:

```bash
CONTINUOUS_SHADOW=true ./start_relocalization.sh sushe
```

Do not add correction application until shadow-mode CPU, 10 Hz Point-LIO, TF
continuity, and moving-robot candidate stability have all been measured.

Static Jetson shadow test (2026-07-11): Point-LIO held 10.00 Hz; the relocalizer
used about 18% of one CPU core; 500 `map -> odom` samples had exactly zero value
change with a mean 50 ms and maximum 66 ms TF interval. Shadow candidates varied
by about 1.2 cm X, 1.7 cm Y, 0.4 cm Z, and 0.47 degrees yaw while stationary.
This validates isolation only; correction application remains unimplemented
until a moving shadow test and full Nav2 CPU test pass.

### 5. Rebase The Final Map

Choose the competition start point as `(0, 0, 0)` and align the course with
`+X` before generating the 2D occupancy map:

```bash
ros2 launch point_lio pcd_map_rebase.launch.py \
  input_pcd:=/home/nvidia/Uika/point_lio/PCD/raw_course.pcd \
  output_pcd:=/home/nvidia/Uika/point_lio/PCD/course_rebased.pcd \
  rviz:=false
```

In a PC-side RViz with `Fixed Frame: map`, use `Publish Point` twice:

```text
first click: competition origin on the floor
second click: any point farther than 0.10 m along the desired +X direction
```

The tool writes both `course_rebased.pcd` and
`course_rebased.transform.yaml`. Generate the occupancy map from the rebased
PCD; reuse the transform YAML for waypoints and strategy trigger zones.

## Current Strategy

For the fixed obstacle course, use:

```text
3D LIO localization/mapping
2D Nav2 or waypoint following
map-frame trigger zones
gait/skill strategy switching before each obstacle
```

Treat known stairs and steep slopes as passable regions in the 2D map. Trigger gait or policy changes by `map -> base_link` position before and after each obstacle. PCT A* remains a reference or fallback, not the first real-robot conversion path.

### Fixed Route Without Nav2

For the fixed pole-slalom route, the lightweight runtime chain is:

```text
Point-LIO + fixed-start relocalization
-> map -> base_footprint
-> /slalom_route
-> fixed_path_controller (10 Hz, forward-only pure pursuit)
-> /nav_cmd_vel_test
-> cmd_vel_safety_bridge
-> /cmd_vel
```

Launch the controller in two dry-run layers by default:

```bash
ros2 launch point_lio slalom_no_nav2_tracking.launch.py
ros2 service call /fixed_path_controller/start std_srvs/srv/Trigger '{}'
```

`controller_dry_run=true` publishes only `/fixed_path_controller/cmd_debug`.
After validating TF, cross-track error, and command signs, set
`controller_dry_run=false` while keeping `bridge_dry_run=true`. Only the final
low-speed real-robot stage may set both values to `false`. The controller
requires `/relocalization/success=true`, fresh `map -> base_footprint`, a start
pose within 0.35 m of the route entry, and a manual start service call.

Use `start_navigation.sh` to gate this chain automatically. From the control PC:

```bash
cd /home/lzh/Uika/point_lio
./start_navigation.sh raogan_15m raogan_15m_slalom.yaml
```

The script starts MID360, Point-LIO, and fixed-start relocalization first. It
does not launch the route controller until `/relocalization/success=true`.
After success, Point-LIO continues to provide `odom -> base_footprint`, the
relocalizer provides `map -> odom`, and the fixed-path controller follows the
latched route. The default `MODE=dry-run` automatically starts tracking but
publishes computed commands only on the debug topic.

Use the staged output modes in order:

```bash
MODE=dry-run ./start_navigation.sh raogan_15m raogan_15m_slalom.yaml
MODE=bridge-test ./start_navigation.sh raogan_15m raogan_15m_slalom.yaml
MODE=live CONFIRM_LIVE=YES ./start_navigation.sh raogan_15m raogan_15m_slalom.yaml
```

`bridge-test` publishes controller output to the safety bridge while the bridge
still suppresses `/cmd_vel`. `live` is the only mode that can publish `/cmd_vel`.
Set `AUTO_START=false` to leave the controller ready but idle after successful
relocalization. Ctrl+C stops tracking first and then the localization launch.

Validate the controller itself without LiDAR, localization, Jetson, or motors:

```bash
ros2 launch point_lio fixed_path_closed_loop_sim.launch.py
```

The simulator initializes `base_footprint` at the route's first point, feeds the
controller's debug velocity through a planar unicycle model, and returns the
result as `map -> base_footprint`. RViz shows the target route in yellow, the
closed-loop trajectory in cyan, the simulated robot in green, and the lookahead
target as axes. This launch never starts the safety bridge and never publishes
`/cmd_vel`. Its simulation-only controller profile tests 0.30 m/s linear and
0.50 rad/s angular limits.

For a route relative to the robot's pose at execution time, start the lightweight
tracker after odometry is available:

```bash
ros2 launch point_lio relative_path_tracking.launch.py
ros2 service call /relative_path_executor/execute std_srvs/srv/Trigger '{}'
```

The execute call captures the current `odom -> base_footprint`, moves the route's
first point onto that pose, aligns its first segment with the robot's current
heading, and starts the controller. It does not use `map` or global
relocalization. The launch defaults to controller dry-run with no safety bridge;
therefore it only computes `/fixed_path_controller/cmd_debug` until separately
approved for hardware testing.

## Active Point-LIO Baseline

The current bringup defaults to `config/avia.yaml` even though the sensor is a
MID360. Do not silently switch to `mid360.yaml`; compare one parameter group at
a time. The active baseline is:

```text
point_filter_num: 2
filter_size_surf/map: 0.2 / 0.3 m
scan_line: 6
timestamp_unit: 1
blind: 0.5 m
imu_meas_acc_cov / imu_meas_omg_cov: 0.1 / 0.1
extrinsic_est_en: false
extrinsic_T: [-0.011, -0.02329, 0.04412]
LiDAR mounting from base_link: x=0.33713, y=0, z=-0.04187, pitch=45 degrees
LIO IMU body from base_link: x=0.313710623, y=0.02329, z=-0.080845726, pitch=45 degrees
MID360 driver / Point-LIO frame rate: 10 Hz (0.1 s frame interval)
```

Point-LIO keeps the full 6-DoF pose on `/aft_mapped_to_init` and `base_link`.
For 2D Nav2 it also publishes a gait-smoothed `/odom_planar` and the TF chain:

```text
map -> odom -> base_footprint -> base_link -> body/base_lidar
```

Nav2 uses `base_footprint`; mapping and 3D sensor geometry continue to use the
full `base_link` pose.

## Minimum Success Criteria

```text
MID360 driver is stable
Point-LIO static test does not drift
Point-LIO handheld slow walking does not fly
Mounted motor-on standing does not shake badly
PCD saving works
2D map generation works
```

## Full-Stack Frequency Gate

Do not accept navigation or competition testing based only on low-load sensor
checks. With the hardware node, policy, MID360 driver, and Point-LIO all
running, execute on the Jetson:

```bash
cd /home/nvidia/Uika
./check_runtime_frequencies.sh 10
```

The required sustained rates are:

```text
/motor_command:       target 200 Hz, minimum 190 Hz
/motor_feedback:      target 200 Hz, minimum 190 Hz
/imu/data:            target 200 Hz, minimum 190 Hz
/livox/lidar:         target  10 Hz, minimum 9.5 Hz
/livox/imu:           target 200 Hz, minimum 190 Hz
/aft_mapped_to_init:  target  10 Hz, minimum 9.0 Hz
loop_control:         about 200 Hz in the policy terminal
loop_rl:              about  50 Hz in the policy terminal
```

The policy loop reports its measured rate, maximum execution time, and deadline
overruns every five seconds. `/motor_command` alone cannot prove 50 Hz policy
inference because the 200 Hz control loop can reuse the most recent action.
Keep the USB/CAN soft-unplug reset disabled in `start_uika.sh`; device recovery
must not be part of the normal startup path.
