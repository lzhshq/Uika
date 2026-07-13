#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
MAP_DIR="$PROJECT_DIR/maps"
JETSON_HOST="${JETSON_HOST:-jetson}"
JETSON_MAP_DIR="${JETSON_MAP_DIR:-/home/nvidia/Uika/point_lio/maps}"
map_server_pid=""
lifecycle_pid=""
pcd_pid=""
rviz_pid=""

cleanup() {
  for pid in "$rviz_pid" "$lifecycle_pid" "$map_server_pid" "$pcd_pid"; do
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
      kill -TERM "$pid" 2>/dev/null || true
    fi
  done
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

if [[ -f /etc/nv_tegra_release ]]; then
  echo "离线地图查看脚本必须在带显示器的电脑端运行。" >&2
  exit 1
fi
if [[ -z "${DISPLAY:-}" ]]; then
  echo "当前终端没有 DISPLAY，无法启动 RViz。" >&2
  exit 1
fi

map_name="${1:-}"
while [[ -z "$map_name" ]]; do
  read -r -p "请输入地图名称: " map_name
done
map_name="${map_name%.pcd}"
map_name="${map_name%.yaml}"
map_name="${map_name%.pgm}"
if [[ ! "$map_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "地图名称不合法。" >&2
  exit 2
fi

mkdir -p "$MAP_DIR"
pcd_file="$MAP_DIR/$map_name.pcd"
pgm_file="$MAP_DIR/$map_name.pgm"
yaml_file="$MAP_DIR/$map_name.yaml"

if [[ "${SYNC_FROM_JETSON:-false}" == "true" || \
      ! -s "$pcd_file" || ! -s "$pgm_file" || ! -s "$yaml_file" ]]; then
  echo "本地地图不完整，正在从 Jetson 同步地图 $map_name……"
  scp "$JETSON_HOST:$JETSON_MAP_DIR/$map_name.pcd" "$pcd_file"
  scp "$JETSON_HOST:$JETSON_MAP_DIR/$map_name.pgm" "$pgm_file"
  scp "$JETSON_HOST:$JETSON_MAP_DIR/$map_name.yaml" "$yaml_file"
else
  echo "正在打开电脑本地地图 $map_name。"
fi

set +u
source /opt/ros/humble/setup.bash
source "$PROJECT_DIR/install/setup.bash"
set -u

ROS_LOG_DIR=/tmp/uika_offline_map_logs
export ROS_LOG_DIR
mkdir -p "$ROS_LOG_DIR"

ros2 run pcl_ros pcd_to_pointcloud --ros-args \
  -r cloud_pcd:=/offline_map_cloud \
  -p file_name:="$pcd_file" \
  -p tf_frame:=map \
  -p publishing_period_ms:=3000 \
  >"$ROS_LOG_DIR/pcd.log" 2>&1 &
pcd_pid=$!

ros2 run nav2_map_server map_server --ros-args \
  -r __node:=offline_map_server \
  -p yaml_filename:="$yaml_file" \
  >"$ROS_LOG_DIR/map_server.log" 2>&1 &
map_server_pid=$!

ros2 run nav2_lifecycle_manager lifecycle_manager --ros-args \
  -r __node:=offline_map_lifecycle_manager \
  -p autostart:=true \
  -p node_names:="[offline_map_server]" \
  >"$ROS_LOG_DIR/lifecycle.log" 2>&1 &
lifecycle_pid=$!

sleep 2
for pid in "$pcd_pid" "$map_server_pid" "$lifecycle_pid"; do
  if ! kill -0 "$pid" 2>/dev/null; then
    echo "离线地图发布节点启动失败，请检查 $ROS_LOG_DIR。" >&2
    exit 1
  fi
done

echo "已打开 $map_name：在 Displays 中可分别勾选 3D PCD 和 2D Occupancy。"
rviz2 -d "$PROJECT_DIR/rviz_cfg/offline_maps.rviz" &
rviz_pid=$!
wait "$rviz_pid"
