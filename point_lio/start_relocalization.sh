#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
JETSON_HOST="${JETSON_HOST:-jetson}"
JETSON_PROJECT="${JETSON_POINT_LIO_DIR:-/home/nvidia/Uika/point_lio}"
rviz_pid=""

cleanup() {
  if [[ -n "$rviz_pid" ]] && kill -0 "$rviz_pid" 2>/dev/null; then
    kill -TERM "$rviz_pid" 2>/dev/null || true
    wait "$rviz_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ -f /etc/nv_tegra_release ]]; then
  echo "请在电脑端运行该脚本，RViz不会在Jetson上启动。" >&2
  exit 1
fi
if [[ -z "${DISPLAY:-}" ]]; then
  echo "电脑端没有DISPLAY，无法启动RViz。" >&2
  exit 1
fi

map_name="${1:-sushe}"
continuous_shadow="${CONTINUOUS_SHADOW:-false}"
map_name="${map_name%.pcd}"
if [[ ! "$map_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "地图名称不合法。" >&2
  exit 2
fi

echo "请把机器人放回 $map_name 的建图起点，保持建图开始时的朝向并完全静止。"
read -r -p "准备好后按Enter启动重定位；Ctrl+C取消: "

mkdir -p "$PROJECT_DIR/maps"
scp "$JETSON_HOST:$JETSON_PROJECT/maps/$map_name.pcd" "$PROJECT_DIR/maps/$map_name.pcd"

set +u
source /opt/ros/humble/setup.bash
source "$PROJECT_DIR/install/setup.bash"
set -u

rviz2 -d "$PROJECT_DIR/rviz_cfg/relocalization_check.rviz" \
  >/tmp/uika_relocalization_rviz.log 2>&1 &
rviz_pid=$!
sleep 1
if ! kill -0 "$rviz_pid" 2>/dev/null; then
  echo "RViz启动失败：" >&2
  cat /tmp/uika_relocalization_rviz.log >&2
  exit 1
fi

echo "重定位状态会显示在本终端。成功前不要移动机器人。"
if [[ "$continuous_shadow" == "true" ]]; then
  echo "持续校正影子模式已开启：只计算候选，不修改map->odom。"
fi
remote_command="source /opt/ros/humble/setup.bash; "
remote_command+="source $JETSON_PROJECT/../livox_ws/install/setup.bash; "
remote_command+="source $JETSON_PROJECT/install/setup.bash; "
remote_command+="systemctl --user stop uika-pointlio-live.service 2>/dev/null || true; "
remote_command+="exec ros2 launch point_lio mid360_relocalization_bringup.launch.py "
remote_command+="map:=$JETSON_PROJECT/maps/$map_name.pcd rviz:=false "
remote_command+="continuous_shadow:=$continuous_shadow"
ssh -tt "$JETSON_HOST" "$remote_command"
