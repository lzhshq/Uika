# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FineNav — a ROS 2 Humble navigation framework for ground robots in unstructured 3D environments (ICRA 2026 paper implementation). The current active work targets the **Uika quadruped** running on Jetson (branch `jetson`), primarily for mapping and obstacle-course navigation.

The colcon workspace root **is this directory** (`/home/lzh/Uika/fastlio2`). Every ROS package lives directly under `fn_*/` subtrees. There is no separate `src/` layer.

## Read this first

`AGENTS.md` at the repo root is the source of truth for the current Uika mapping/navigation state — TF layout, LiDAR mount conventions, PCD conversion flow, task/policy structure for the obstacle course. **Read it before touching anything in `fn_bringup/config`, `fn_bringup/launch`, `fn_bringup/urdf`, or `fn_localization`.** It contains hard-won constraints (e.g. "don't put the robot MID360 mount transform into FAST-LIO `extrinsic_R`") that aren't visible from the code alone.

## Build & run

Standard ROS 2 colcon workflow from the workspace root:

```bash
cd /home/lzh/Uika/fastlio2
source /opt/ros/humble/setup.bash
colcon build                              # or: colcon build --packages-select <pkg>
source install/setup.bash
```

- Rebuild a single package: `colcon build --packages-select fine_nav2d_bringup`
- Symlink-install for Python iteration: `colcon build --symlink-install`
- Clean rebuild: `rm -rf build install log && colcon build`

There is no test suite wired up in this workspace; no `colcon test` targets are meaningful today.

C++ style is enforced by `.clang-format` (Google base, 120-column, 4-space indent, left pointer alignment).

## Common launches

Config lives in `fn_bringup/config/`; launch files in `fn_bringup/launch/` (package name `fine_nav2d_bringup`).

- **Full bringup** (mapping/nav modes selectable by args): `ros2 launch fine_nav2d_bringup bringup.launch.py` — see the `DeclareLaunchArgument`s at the top of the file for `mode`, `lidar_type`, `lio_type`, `working_mode`, `navigation_strategy`, `map_save/load`, etc.
- **Uika real-hardware mapping** (URDF + Livox + FAST-LIO + localization + map_manager): `ros2 launch fine_nav2d_bringup uika_mapping_urdf.launch.py`
- **Obstacle-course dryruns**: `uika_complex_nav_dryrun.launch.py`, `uika_mission_nav2_dryrun.launch.py`, `uika_nav2_mppi_dryrun.launch.py`, `uika_single_task_dryrun.launch.py`
- **Save FAST-LIO map** (writes to path in the launch's `map_file_path` param): `ros2 service call /map_save std_srvs/srv/Trigger "{}"`

The Jetson-side motor/CAN/serial bringup is a separate workspace at `/home/lzh/Uika/Quadruped_Uika` and is started by `/home/lzh/Uika/start_uika.sh`. It is **not** part of this colcon workspace.

## Workspace layout

Packages are grouped by function directory, not by build system layout:

| Directory | Purpose |
|---|---|
| `fn_bringup/` | Top-level integration: launches, configs, URDFs, RViz, behavior trees, mission/terrain scripts |
| `fn_driver/` | Hardware driver submodules — `Livox_Mid360`, `Unitree_L1`, `Fines_Node` |
| `fn_localization/` | `Fast_LIO` (submodule) + `localization_manager` (base_link ← Odometry + static TF) |
| `fn_mapping/` | `map_manager`, `GridMap`, `octomap_server`, `terrain_analysis_core`, `terrain_analyzer` — the cache-memory hierarchical map (ring-buffer local grid + global OctoMap) |
| `fn_perception/` | Ground segmentation, octomap mapping |
| `fn_fine_pct/` | PCT (Poincaré Cost Terrain) global planner over static PCD |
| `fn_behavior/` | Nav2 BT plugins |
| `fn_sim/` | Gazebo/Ignition simulator packages |
| `fn_utils/` | Shared utilities |
| `external/` | Vendored `navigation2`, `perception_pcl` sources |

`fn_driver/Livox_Mid360`, `fn_driver/Unitree_L1`, `fn_driver/Fines_Node`, and `fn_localization/Fast_LIO` are git submodules — see `.gitmodules`. After a fresh clone: `git submodule update --init --recursive`.

## Architecture notes

- **TF chain (real robot):** `map → odom → lidar_odom → base_lidar`, with `base_link` computed by `localization_manager` from `/Odometry` + the static `base_link → base_lidar` transform. FAST-LIO publishes `/Odometry` as `lidar_odom → base_lidar`; the current MID360 mount is `x=0.313, y=0.0, z=-0.06, pitch=90°` and lives in the URDF + a matching static `odom → lidar_odom` TF, **not** in FAST-LIO `mapping.extrinsic_R` (that field is the LiDAR-to-internal-IMU calibration).
- **Mapping output convention:** FAST-LIO saves PCDs in the `lidar_odom` frame. PCT and any planner treating PCD as `map` frame require an offline conversion step (`fn_bringup/scripts/convert_lidar_odom_pcd_to_map.py`). Never rename `lidar_odom` to `map` in the FAST-LIO config to shortcut this.
- **Cache-memory map:** the local ring-buffer grid (O(1) shifts, high-rate) and the global OctoMap (persistent, memory-efficient) are decoupled by design; see `fn_mapping/`. Terrain analysis is a plugin — see `fn_behavior/plugin.xml` and `fn_mapping/terrain_analyzer`.
- **Obstacle-course mission model:** the course is split into per-obstacle *tasks* with attached *policies* (`stair_policy`, `wall_climb_policy`, `slalom_policy`, `gravel_policy`, `low_bar_policy`, …). Configs in `fn_bringup/config/uika_obstacle_mission_*.yaml` and `uika_terrain_zones_*.yaml`; runtime in `fn_bringup/scripts/terrain_mission_*.py`. Manual task advance: `ros2 topic pub --once /mission_command std_msgs/msg/String "{data: 'next'}"` (also `prev`, `reset`, `set <task>`, `reload`). See AGENTS.md for the current task order and per-obstacle entry/exit points.

## Guardrails when editing configs

- Don't fold per-obstacle needs into PCT global params (`safe_margin`, `inflation`, etc.). Handle those at the policy layer.
- Don't re-point PCT at the stride-5 visualization PCD (`*_viz_stride5.pcd`); those are RViz-only downsampled copies.
- Modifying URDF/launch mount geometry does **not** update already-saved PCDs — re-run the offline conversion script from the raw `lidar_odom` PCD.
