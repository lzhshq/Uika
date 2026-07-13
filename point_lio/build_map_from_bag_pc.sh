#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LIVOX_WS="${LIVOX_WS:-/home/lzh/livox_ws}"
BAG_ROOT="${BAG_ROOT:-$PROJECT_DIR/bags}"
MAP_DIR="$PROJECT_DIR/maps"
PCD_DIR="$PROJECT_DIR/PCD"
ROS_LOG_DIR="${ROS_LOG_DIR:-/tmp/uika_offline_mapping_logs}"
POINT_LIO_CONFIG="${POINT_LIO_CONFIG:-$PROJECT_DIR/config/avia.yaml}"

PLAYBACK_RATE="${PLAYBACK_RATE:-0.20}"
CLOCK_HZ="${CLOCK_HZ:-100}"
DRAIN_SECONDS="${DRAIN_SECONDS:-8}"
POINT_FILTER_NUM="${POINT_FILTER_NUM:-1}"
SURF_VOXEL="${SURF_VOXEL:-0.10}"
MAP_VOXEL="${MAP_VOXEL:-0.10}"
IVOX_NEARBY_TYPE="${IVOX_NEARBY_TYPE:-6}"
OFFLINE_RVIZ="${OFFLINE_RVIZ:-false}"

RESOLUTION="${MAP_RESOLUTION:-0.05}"
Z_MIN="${MAP_Z_MIN:-0.10}"
Z_MAX="${MAP_Z_MAX:-1.20}"
PADDING="${MAP_PADDING:-1.0}"
INFLATION="${MAP_INFLATION:-0.0}"

mapping_pid=""
play_pid=""
pcd_tmp=""
pcd_owned=false
saved=false

stop_group() {
  local pid="${1:-}"
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    return
  fi
  kill -INT -- "-$pid" 2>/dev/null || true
  for _ in {1..100}; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$pid" 2>/dev/null; then
    kill -TERM -- "-$pid" 2>/dev/null || true
  fi
  wait "$pid" 2>/dev/null || true
}

cleanup() {
  stop_group "$play_pid"
  stop_group "$mapping_pid"
  if [[ "$saved" != true && "$pcd_owned" == true && -n "$pcd_tmp" ]]; then
    rm -f -- "$pcd_tmp"
    printf '\nOffline mapping stopped without saving a map.\n'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if [[ -f /etc/nv_tegra_release ]]; then
  echo "Run this script on the control PC, not the Jetson." >&2
  exit 1
fi
if [[ $# -gt 2 || ! -t 0 ]]; then
  echo "Usage: $0 [bag_name] [map_name]" >&2
  exit 2
fi
for required in \
  /opt/ros/humble/setup.bash \
  "$LIVOX_WS/install/setup.bash" \
  "$PROJECT_DIR/install/setup.bash" \
  "$POINT_LIO_CONFIG" \
  "$PROJECT_DIR/scripts/pcd_to_occupancy.py"; do
  if [[ ! -f "$required" ]]; then
    echo "Required file is missing: $required" >&2
    exit 1
  fi
done

set +u
source /opt/ros/humble/setup.bash
source "$LIVOX_WS/install/setup.bash"
source "$PROJECT_DIR/install/setup.bash"
set -u

bag_name="${1:-}"
while [[ -z "$bag_name" ]]; do
  read -r -p "Bag name: " bag_name
done
map_name="${2:-}"
while [[ -z "$map_name" ]]; do
  read -r -p "Output map name: " map_name
done
for name in "$bag_name" "$map_name"; do
  if [[ ! "$name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
    echo "Invalid name: $name" >&2
    exit 2
  fi
done

bag_dir="$BAG_ROOT/$bag_name"
if [[ ! -s "$bag_dir/metadata.yaml" ]]; then
  echo "Bag does not exist or is incomplete: $bag_dir" >&2
  exit 1
fi
bag_info="$(ros2 bag info "$bag_dir" 2>&1)"
if [[ "$bag_info" != *"/livox/lidar"* || "$bag_info" != *"/livox/imu"* ]]; then
  echo "Bag is missing /livox/lidar or /livox/imu: $bag_dir" >&2
  exit 1
fi

mkdir -p "$MAP_DIR" "$PCD_DIR" "$ROS_LOG_DIR"
pcd_tmp="$PCD_DIR/$map_name.pcd"
pcd_out="$MAP_DIR/$map_name.pcd"
yaml_out="$MAP_DIR/$map_name.yaml"
pgm_out="$MAP_DIR/$map_name.pgm"
mapping_log="$ROS_LOG_DIR/${map_name}_$(date +%Y%m%d_%H%M%S).log"
for output in "$pcd_tmp" "$pcd_out" "$yaml_out" "$pgm_out"; do
  if [[ -e "$output" ]]; then
    echo "Refusing to overwrite existing output: $output" >&2
    exit 1
  fi
done
pcd_owned=true

if ros2 node list 2>/dev/null | grep -Eq '^/(livox_lidar_publisher|laserMapping)$'; then
  echo "A live MID360 or Point-LIO node is running. Stop it first." >&2
  exit 1
fi

echo "Starting offline Point-LIO mapping..."
echo "Bag: $bag_dir"
echo "Playback: ${PLAYBACK_RATE}x; profile: point_filter=$POINT_FILTER_NUM, voxel=$SURF_VOXEL/$MAP_VOXEL m"
ROS2CLI_DISABLE_DAEMON=1 setsid ros2 launch point_lio mid360_mapping_bringup.launch.py \
  driver:=false \
  rviz:="$OFFLINE_RVIZ" \
  use_sim_time:=true \
  point_lio_cfg_dir:="$POINT_LIO_CONFIG" \
  pcd_save_file:="$map_name.pcd" \
  pcd_save_interval:=-1 \
  point_filter_num:="$POINT_FILTER_NUM" \
  filter_size_surf:="$SURF_VOXEL" \
  filter_size_map:="$MAP_VOXEL" \
  ivox_nearby_type:="$IVOX_NEARBY_TYPE" \
  >>"$mapping_log" 2>&1 &
mapping_pid=$!

service_ready=false
for _ in {1..50}; do
  if ! kill -0 "$mapping_pid" 2>/dev/null; then
    echo "Point-LIO exited during startup." >&2
    tail -n 60 "$mapping_log" >&2 || true
    exit 1
  fi
  if ros2 service list 2>/dev/null | grep -qx '/save_map'; then
    service_ready=true
    break
  fi
  sleep 0.5
done
if [[ "$service_ready" != true ]]; then
  echo "Timed out waiting for /save_map." >&2
  exit 1
fi

echo "Playing bag. This takes approximately 1 / $PLAYBACK_RATE times the recorded duration."
ROS2CLI_DISABLE_DAEMON=1 setsid ros2 bag play "$bag_dir" \
  --rate "$PLAYBACK_RATE" \
  --clock "$CLOCK_HZ" \
  --topics /livox/lidar /livox/imu \
  --disable-keyboard-controls \
  >>"$mapping_log" 2>&1 &
play_pid=$!
set +e
wait "$play_pid"
play_status=$?
set -e
if [[ "$play_status" -ne 0 ]]; then
  play_pid=""
  echo "rosbag playback failed with status $play_status." >&2
  tail -n 60 "$mapping_log" >&2 || true
  exit 1
fi
play_pid=""

echo "Playback complete; waiting ${DRAIN_SECONDS}s for Point-LIO to drain callbacks..."
sleep "$DRAIN_SECONDS"
save_result="$(ros2 service call /save_map std_srvs/srv/Trigger '{}' 2>&1)" || {
  echo "$save_result" >&2
  exit 1
}
echo "$save_result"
if [[ ! -s "$pcd_tmp" ]]; then
  echo "The save service did not create a valid PCD: $pcd_tmp" >&2
  exit 1
fi

stop_group "$mapping_pid"
mapping_pid=""
mv -- "$pcd_tmp" "$pcd_out"

python3 "$PROJECT_DIR/scripts/pcd_to_occupancy.py" \
  "$pcd_out" \
  --output "$yaml_out" \
  --resolution "$RESOLUTION" \
  --padding "$PADDING" \
  --z-min "$Z_MIN" \
  --z-max "$Z_MAX" \
  --inflate "$INFLATION"
if [[ ! -s "$yaml_out" || ! -s "$pgm_out" ]]; then
  echo "2D map generation failed; 3D PCD remains at $pcd_out." >&2
  exit 1
fi

saved=true
echo
echo "Offline high-quality map saved:"
echo "  PCD:  $pcd_out"
echo "  YAML: $yaml_out"
echo "  PGM:  $pgm_out"
echo "  Log:  $mapping_log"
