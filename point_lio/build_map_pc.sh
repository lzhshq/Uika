#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LIVOX_WS="${LIVOX_WS:-/home/lzh/livox_ws}"
LIDAR_IFACE="${LIDAR_IFACE:-eno1}"
LIDAR_HOST_CIDR="${LIDAR_HOST_CIDR:-192.168.3.50/24}"
LIDAR_HOST_IP="${LIDAR_HOST_IP:-192.168.3.50}"
LIDAR_IP="${LIDAR_IP:-192.168.3.168}"
LIDAR_SUBNET="${LIDAR_SUBNET:-192.168.3.0/24}"
DRIVER_CONFIG="${LIVOX_PC_CONFIG:-$PROJECT_DIR/config/MID360_pc_config.json}"
POINT_LIO_CONFIG="${POINT_LIO_CONFIG:-$PROJECT_DIR/config/avia.yaml}"

MAP_DIR="$PROJECT_DIR/maps"
PCD_DIR="$PROJECT_DIR/PCD"
ROS_LOG_DIR="${ROS_LOG_DIR:-/tmp/uika_pc_mapping_logs}"
RESOLUTION="${MAP_RESOLUTION:-0.05}"
Z_MIN="${MAP_Z_MIN:-0.10}"
Z_MAX="${MAP_Z_MAX:-1.20}"
PADDING="${MAP_PADDING:-1.0}"
INFLATION="${MAP_INFLATION:-0.0}"

# Highest-density PC profile verified to sustain the 10 Hz MID360 input.
POINT_FILTER_NUM="${POINT_FILTER_NUM:-1}"
SURF_VOXEL="${SURF_VOXEL:-0.15}"
MAP_VOXEL="${MAP_VOXEL:-0.15}"
IVOX_NEARBY_TYPE="${IVOX_NEARBY_TYPE:-6}"
DRIVER_PUBLISH_FREQ="${DRIVER_PUBLISH_FREQ:-10.0}"

mapping_pid=""
driver_pid=""
saved=false
old_stty=""
pcd_tmp=""

restore_terminal() {
  if [[ -n "$old_stty" && -t 0 ]]; then
    stty "$old_stty" 2>/dev/null || true
  fi
}

stop_pid() {
  local pid="${1:-}"
  local pgid target
  if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
    return
  fi
  pgid="$(ps -o pgid= -p "$pid" 2>/dev/null | tr -d ' ' || true)"
  if [[ -n "$pgid" && "$pgid" == "$pid" ]]; then
    target="-$pgid"
  else
    target="$pid"
  fi
  kill -INT -- "$target" 2>/dev/null || true
  for _ in {1..50}; do
    kill -0 "$pid" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$pid" 2>/dev/null; then
    kill -TERM -- "$target" 2>/dev/null || true
  fi
  wait "$pid" 2>/dev/null || true
}

stop_mapping() {
  stop_pid "$mapping_pid"
  mapping_pid=""
}

stop_driver() {
  stop_pid "$driver_pid"
  driver_pid=""
}

cleanup() {
  restore_terminal
  stop_mapping
  stop_driver
  if [[ "$saved" != true ]]; then
    if [[ -n "$pcd_tmp" ]]; then
      rm -f -- "$pcd_tmp"
    fi
    printf '\nPC mapping stopped without saving a map.\n'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if [[ -f /etc/nv_tegra_release ]]; then
  echo "This script is for the control PC, not the Jetson." >&2
  exit 1
fi
if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [map_name]" >&2
  exit 2
fi
if [[ ! -t 0 ]]; then
  echo "An interactive terminal is required for the map name and Ctrl+S." >&2
  exit 1
fi
if [[ -z "${DISPLAY:-}" ]]; then
  echo "DISPLAY is not set. Run this script from the PC graphical desktop." >&2
  exit 1
fi

for required in \
  /opt/ros/humble/setup.bash \
  "$LIVOX_WS/install/setup.bash" \
  "$PROJECT_DIR/install/setup.bash" \
  "$DRIVER_CONFIG" \
  "$POINT_LIO_CONFIG" \
  "$PROJECT_DIR/scripts/pcd_to_occupancy.py"; do
  if [[ ! -f "$required" ]]; then
    echo "Required file is missing: $required" >&2
    exit 1
  fi
done
if ! ip link show dev "$LIDAR_IFACE" >/dev/null 2>&1; then
  echo "LiDAR interface does not exist: $LIDAR_IFACE" >&2
  echo "Set it explicitly, for example: LIDAR_IFACE=enx... $0" >&2
  exit 1
fi

map_name="${1:-}"
while [[ -z "$map_name" ]]; do
  read -r -p "Map name (letters, numbers, underscore or dash): " map_name
done
map_name="${map_name%.pcd}"
map_name="${map_name%.yaml}"
map_name="${map_name%.pgm}"
if [[ ! "$map_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "Invalid map name: $map_name" >&2
  exit 2
fi

mkdir -p "$MAP_DIR" "$PCD_DIR" "$ROS_LOG_DIR"
pcd_tmp="$PCD_DIR/$map_name.pcd"
pcd_out="$MAP_DIR/$map_name.pcd"
yaml_out="$MAP_DIR/$map_name.yaml"
pgm_out="$MAP_DIR/$map_name.pgm"
launch_log="$ROS_LOG_DIR/${map_name}_$(date +%Y%m%d_%H%M%S).log"

for output in "$pcd_tmp" "$pcd_out" "$yaml_out" "$pgm_out"; do
  if [[ -e "$output" ]]; then
    echo "Refusing to overwrite existing output: $output" >&2
    exit 1
  fi
done

echo "Configuring $LIDAR_IFACE as $LIDAR_HOST_CIDR for MID360..."
sudo -v
sudo ip link set dev "$LIDAR_IFACE" up
if ! ip -4 -o addr show dev "$LIDAR_IFACE" | grep -Fq " $LIDAR_HOST_CIDR "; then
  sudo ip addr replace "$LIDAR_HOST_CIDR" dev "$LIDAR_IFACE"
fi
# VPN clients may install a policy-routing default that captures private subnets.
sudo ip route replace "$LIDAR_SUBNET" dev "$LIDAR_IFACE" src "$LIDAR_HOST_IP" metric 10 table main
if ! ip rule show | grep -Fq "to $LIDAR_SUBNET lookup main"; then
  sudo ip rule add priority 100 to "$LIDAR_SUBNET" lookup main
fi
if (( $(sysctl -n net.core.rmem_max) < 2147483647 )); then
  sudo sysctl -w net.core.rmem_max=2147483647 >/dev/null
fi

link_ready=false
for _ in {1..20}; do
  if [[ "$(cat "/sys/class/net/$LIDAR_IFACE/carrier" 2>/dev/null || true)" == "1" ]]; then
    link_ready=true
    break
  fi
  sleep 0.5
done
if [[ "$link_ready" != true ]]; then
  echo "No Ethernet carrier on $LIDAR_IFACE. Check the MID360 cable and power." >&2
  exit 1
fi

route_line="$(ip route get "$LIDAR_IP" 2>/dev/null || true)"
if [[ "$route_line" != *" dev $LIDAR_IFACE "* || "$route_line" != *" src $LIDAR_HOST_IP "* ]]; then
  echo "The route to $LIDAR_IP is not using $LIDAR_IFACE from $LIDAR_HOST_IP:" >&2
  echo "  $route_line" >&2
  exit 1
fi
if ! ping -c 3 -W 1 "$LIDAR_IP" >/dev/null; then
  echo "MID360 is not reachable at $LIDAR_IP." >&2
  exit 1
fi

set +u
source /opt/ros/humble/setup.bash
source "$LIVOX_WS/install/setup.bash"
source "$PROJECT_DIR/install/setup.bash"
set -u

for old_node in /livox_lidar_publisher /laserMapping; do
  if ros2 node list 2>/dev/null | grep -qx "$old_node"; then
    echo "ROS node $old_node is already running. Stop it before PC mapping." >&2
    exit 1
  fi
done

echo "Starting the PC MID360 driver..."
ROS2CLI_DISABLE_DAEMON=1 setsid ros2 run livox_ros_driver2 livox_ros_driver2_node --ros-args \
  -r __node:=livox_lidar_publisher \
  -p xfer_format:=1 \
  -p multi_topic:=0 \
  -p data_src:=0 \
  -p publish_freq:="$DRIVER_PUBLISH_FREQ" \
  -p output_data_type:=0 \
  -p frame_id:=livox_frame \
  -p lvx_file_path:=/tmp/uika_unused.lvx \
  -p user_config_path:="$DRIVER_CONFIG" \
  -p cmdline_input_bd_code:=livox0000000001 \
  >>"$launch_log" 2>&1 &
driver_pid=$!

driver_ready=false
for _ in {1..30}; do
  if ! kill -0 "$driver_pid" 2>/dev/null; then
    echo "MID360 driver exited during startup:" >&2
    tail -n 50 "$launch_log" >&2 || true
    exit 1
  fi
  if ros2 topic list 2>/dev/null | grep -qx '/livox/lidar' && \
     ros2 topic list 2>/dev/null | grep -qx '/livox/imu'; then
    driver_ready=true
    break
  fi
  sleep 0.5
done
if [[ "$driver_ready" != true ]]; then
  echo "Timed out waiting for /livox/lidar and /livox/imu." >&2
  tail -n 50 "$launch_log" >&2 || true
  exit 1
fi

echo "Starting Point-LIO mapping and RViz on this PC..."
ROS2CLI_DISABLE_DAEMON=1 setsid ros2 launch point_lio mid360_mapping_bringup.launch.py \
  driver:=false \
  rviz:=true \
  point_lio_cfg_dir:="$POINT_LIO_CONFIG" \
  pcd_save_file:="$map_name.pcd" \
  pcd_save_interval:=-1 \
  point_filter_num:="$POINT_FILTER_NUM" \
  filter_size_surf:="$SURF_VOXEL" \
  filter_size_map:="$MAP_VOXEL" \
  ivox_nearby_type:="$IVOX_NEARBY_TYPE" \
  >>"$launch_log" 2>&1 &
mapping_pid=$!

service_ready=false
for _ in {1..50}; do
  if ! kill -0 "$mapping_pid" 2>/dev/null; then
    echo "Point-LIO mapping exited during startup:" >&2
    tail -n 60 "$launch_log" >&2 || true
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
  tail -n 60 "$launch_log" >&2 || true
  exit 1
fi

echo
echo "PC mapping is ready. Keep the LiDAR still for 2-3 seconds before moving."
echo "Profile: point_filter=$POINT_FILTER_NUM, surf_voxel=${SURF_VOXEL}m, map_voxel=${MAP_VOXEL}m"
echo "Shared Point-LIO config: $POINT_LIO_CONFIG"
echo "RViz shows only TF and the base_link path; registered map clouds are not published."
echo "Press Ctrl+S here to save PCD + PGM/YAML, or Ctrl+C to discard."
echo "Log: $launch_log"

old_stty="$(stty -g)"
stty -ixon
while true; do
  if ! IFS= read -rsn1 key; then
    echo "Terminal input closed; discarding this map." >&2
    exit 1
  fi
  if [[ "$key" == $'\x13' ]]; then
    break
  fi
done

restore_terminal
old_stty=""
echo
echo "Saving 3D PCD..."
save_result="$(ros2 service call /save_map std_srvs/srv/Trigger '{}' 2>&1)" || {
  echo "$save_result" >&2
  exit 1
}
echo "$save_result"
if [[ ! -s "$pcd_tmp" ]]; then
  echo "The save service did not create a valid PCD: $pcd_tmp" >&2
  exit 1
fi

stop_mapping
stop_driver
if [[ ! -s "$pcd_tmp" ]]; then
  echo "PCD became invalid while stopping Point-LIO: $pcd_tmp" >&2
  exit 1
fi
mv -- "$pcd_tmp" "$pcd_out"

echo "Generating the 2D occupancy map..."
python3 "$PROJECT_DIR/scripts/pcd_to_occupancy.py" \
  "$pcd_out" \
  --output "$yaml_out" \
  --resolution "$RESOLUTION" \
  --padding "$PADDING" \
  --z-min "$Z_MIN" \
  --z-max "$Z_MAX" \
  --inflate "$INFLATION"

if [[ ! -s "$yaml_out" || ! -s "$pgm_out" ]]; then
  echo "2D map generation failed; the 3D PCD is preserved at $pcd_out." >&2
  exit 1
fi

saved=true
echo
echo "PC map saved:"
echo "  3D relocalization map: $pcd_out"
echo "  2D map metadata:       $yaml_out"
echo "  2D occupancy image:    $pgm_out"
echo "  Mapping log:           $launch_log"
