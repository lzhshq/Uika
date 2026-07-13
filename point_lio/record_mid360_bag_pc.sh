#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LIVOX_WS="${LIVOX_WS:-/home/lzh/livox_ws}"
BAG_ROOT="${BAG_ROOT:-$PROJECT_DIR/bags}"
LIDAR_IFACE="${LIDAR_IFACE:-eno1}"
LIDAR_HOST_CIDR="${LIDAR_HOST_CIDR:-192.168.3.50/24}"
LIDAR_HOST_IP="${LIDAR_HOST_IP:-192.168.3.50}"
LIDAR_IP="${LIDAR_IP:-192.168.3.168}"
LIDAR_SUBNET="${LIDAR_SUBNET:-192.168.3.0/24}"
DRIVER_CONFIG="${LIVOX_PC_CONFIG:-$PROJECT_DIR/config/MID360_pc_config.json}"
DRIVER_PUBLISH_FREQ="${DRIVER_PUBLISH_FREQ:-10.0}"
ROS_LOG_DIR="${ROS_LOG_DIR:-/tmp/uika_bag_record_logs}"

driver_pid=""
record_pid=""
bag_dir=""
bag_created=false
saved=false
old_stty=""

restore_terminal() {
  if [[ -n "$old_stty" && -t 0 ]]; then
    stty "$old_stty" 2>/dev/null || true
  fi
}

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
  restore_terminal
  stop_group "$record_pid"
  stop_group "$driver_pid"
  if [[ "$saved" != true && "$bag_created" == true && -n "$bag_dir" ]]; then
    rm -rf -- "$bag_dir"
    printf '\nRecording stopped; incomplete bag was removed.\n'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if [[ -f /etc/nv_tegra_release ]]; then
  echo "Run this script on the control PC, not the Jetson." >&2
  exit 1
fi
if [[ $# -gt 1 || ! -t 0 ]]; then
  echo "Usage: $0 [bag_name]  (interactive terminal required)" >&2
  exit 2
fi
for required in /opt/ros/humble/setup.bash "$LIVOX_WS/install/setup.bash" "$DRIVER_CONFIG"; do
  if [[ ! -f "$required" ]]; then
    echo "Required file is missing: $required" >&2
    exit 1
  fi
done
if ! ip link show dev "$LIDAR_IFACE" >/dev/null 2>&1; then
  echo "LiDAR interface does not exist: $LIDAR_IFACE" >&2
  exit 1
fi

bag_name="${1:-}"
while [[ -z "$bag_name" ]]; do
  read -r -p "Bag name (letters, numbers, underscore or dash): " bag_name
done
if [[ ! "$bag_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "Invalid bag name: $bag_name" >&2
  exit 2
fi
mkdir -p "$BAG_ROOT" "$ROS_LOG_DIR"
bag_dir="$BAG_ROOT/$bag_name"
if [[ -e "$bag_dir" ]]; then
  echo "Refusing to overwrite existing bag: $bag_dir" >&2
  exit 1
fi
record_log="$ROS_LOG_DIR/${bag_name}_$(date +%Y%m%d_%H%M%S).log"

echo "Configuring $LIDAR_IFACE for MID360..."
sudo -v
sudo ip link set dev "$LIDAR_IFACE" up
sudo ip addr replace "$LIDAR_HOST_CIDR" dev "$LIDAR_IFACE"
sudo ip route replace "$LIDAR_SUBNET" dev "$LIDAR_IFACE" src "$LIDAR_HOST_IP" metric 10 table main
if ! ip rule show | grep -Fq "to $LIDAR_SUBNET lookup main"; then
  sudo ip rule add priority 100 to "$LIDAR_SUBNET" lookup main
fi
if (( $(sysctl -n net.core.rmem_max) < 2147483647 )); then
  sudo sysctl -w net.core.rmem_max=2147483647 >/dev/null
fi
if [[ "$(cat "/sys/class/net/$LIDAR_IFACE/carrier" 2>/dev/null || true)" != "1" ]]; then
  echo "No Ethernet carrier on $LIDAR_IFACE." >&2
  exit 1
fi
if ! ping -c 3 -W 1 "$LIDAR_IP" >/dev/null; then
  echo "MID360 is not reachable at $LIDAR_IP." >&2
  exit 1
fi

set +u
source /opt/ros/humble/setup.bash
source "$LIVOX_WS/install/setup.bash"
set -u
if ros2 node list 2>/dev/null | grep -Eq '^/(livox_lidar_publisher|laserMapping)$'; then
  echo "An old MID360 or Point-LIO node is running. Stop it first." >&2
  exit 1
fi

echo "Starting MID360 driver (no Point-LIO)..."
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
  >>"$record_log" 2>&1 &
driver_pid=$!

topics_ready=false
for _ in {1..40}; do
  if ! kill -0 "$driver_pid" 2>/dev/null; then
    echo "MID360 driver exited during startup." >&2
    tail -n 50 "$record_log" >&2 || true
    exit 1
  fi
  if ros2 topic list 2>/dev/null | grep -qx '/livox/lidar' && \
     ros2 topic list 2>/dev/null | grep -qx '/livox/imu'; then
    topics_ready=true
    break
  fi
  sleep 0.5
done
if [[ "$topics_ready" != true ]]; then
  echo "Timed out waiting for MID360 topics." >&2
  exit 1
fi

echo "Starting raw rosbag recording..."
ROS2CLI_DISABLE_DAEMON=1 setsid ros2 bag record \
  --storage sqlite3 \
  --max-cache-size 268435456 \
  --output "$bag_dir" \
  /livox/lidar /livox/imu \
  >>"$record_log" 2>&1 &
record_pid=$!

for _ in {1..30}; do
  if ! kill -0 "$record_pid" 2>/dev/null; then
    echo "rosbag recorder exited during startup." >&2
    tail -n 50 "$record_log" >&2 || true
    exit 1
  fi
  [[ -d "$bag_dir" ]] && break
  sleep 0.2
done
if [[ ! -d "$bag_dir" ]]; then
  echo "rosbag output directory was not created." >&2
  exit 1
fi
bag_created=true

echo
echo "Raw recording is active: $bag_dir"
echo "Move through the mapping area normally. Point-LIO is not running."
echo "Press Ctrl+S to finish and keep the bag, or Ctrl+C to discard it."
echo "Log: $record_log"

old_stty="$(stty -g)"
stty -ixon
while true; do
  IFS= read -rsn1 key || exit 1
  [[ "$key" == $'\x13' ]] && break
done
restore_terminal
old_stty=""

echo
echo "Finalizing rosbag..."
stop_group "$record_pid"
record_pid=""
stop_group "$driver_pid"
driver_pid=""
if [[ ! -s "$bag_dir/metadata.yaml" ]]; then
  echo "rosbag metadata is missing: $bag_dir/metadata.yaml" >&2
  exit 1
fi
bag_info="$(ros2 bag info "$bag_dir" 2>&1)"
if [[ "$bag_info" != *"/livox/lidar"* || "$bag_info" != *"/livox/imu"* ]]; then
  echo "$bag_info" >&2
  echo "Recorded bag does not contain both required topics." >&2
  exit 1
fi

duration_s="$(sed -nE 's/^[[:space:]]*Duration:[[:space:]]*([0-9.]+)s.*/\1/p' <<<"$bag_info" | head -n1)"
lidar_count="$(sed -nE 's/.*Topic: \/livox\/lidar .*Count: ([0-9]+).*/\1/p' <<<"$bag_info" | head -n1)"
imu_count="$(sed -nE 's/.*Topic: \/livox\/imu .*Count: ([0-9]+).*/\1/p' <<<"$bag_info" | head -n1)"
if [[ -z "$duration_s" || -z "$lidar_count" || -z "$imu_count" ]]; then
  echo "$bag_info" >&2
  echo "Could not calculate capture rates from rosbag metadata." >&2
  exit 1
fi

read -r lidar_hz imu_hz <<<"$(awk -v d="$duration_s" -v l="$lidar_count" -v i="$imu_count" \
  'BEGIN { if (d <= 0) exit 1; printf "%.2f %.2f", l / d, i / d }')"
health="PASS"
health_note="LiDAR and IMU rates are within the expected MID360 range."
if ! awk -v l="$lidar_hz" -v i="$imu_hz" 'BEGIN { exit !(l >= 8.0 && i >= 150.0) }'; then
  health="WARNING"
  health_note="Expected at least 8 Hz LiDAR and 150 Hz IMU; inspect the session log before mapping."
fi

session_log="$bag_dir/session.log"
capture_report="$bag_dir/capture_report.txt"
cp -- "$record_log" "$session_log"
{
  echo "Uika MID360 capture report"
  echo "Bag: $bag_name"
  echo "Recorded: $(date --iso-8601=seconds)"
  echo "Duration: $duration_s s"
  echo "LiDAR: $lidar_count messages, $lidar_hz Hz"
  echo "IMU: $imu_count messages, $imu_hz Hz"
  echo "Health: $health"
  echo "Note: $health_note"
  echo
  echo "ros2 bag info"
  echo "$bag_info"
} >"$capture_report"

saved=true
echo "$bag_info"
echo
echo "Capture health: $health"
echo "  LiDAR: $lidar_count messages, $lidar_hz Hz"
echo "  IMU:   $imu_count messages, $imu_hz Hz"
echo "  Report: $capture_report"
echo "  Log:    $session_log"
echo "Raw MID360 bag saved: $bag_dir"
