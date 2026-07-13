#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LIVOX_WS="${LIVOX_WS:-$(dirname "$PROJECT_DIR")/livox_ws}"
MAP_DIR="$PROJECT_DIR/maps"
PCD_DIR="$PROJECT_DIR/PCD"
ROS_LOG_DIR="${ROS_LOG_DIR:-/tmp/uika_mapping_logs}"
RESOLUTION="${MAP_RESOLUTION:-0.05}"
Z_MIN="${MAP_Z_MIN:-0.10}"
Z_MAX="${MAP_Z_MAX:-1.20}"
PADDING="${MAP_PADDING:-1.0}"
# Keep the static map geometrically faithful. Nav2 applies robot clearance in its costmap.
INFLATION="${MAP_INFLATION:-0.0}"

run_from_control_pc() {
  local jetson_host="${JETSON_HOST:-jetson}"
  local jetson_project="${JETSON_POINT_LIO_DIR:-/home/nvidia/Uika/point_lio}"
  local rviz_config="$PROJECT_DIR/rviz_cfg/tf_path_only.rviz"
  local rviz_log="/tmp/uika_mapping_rviz_$(date +%Y%m%d_%H%M%S).log"
  local remote_command rviz_pid ssh_status quoted_arg

  if [[ -z "${DISPLAY:-}" ]]; then
    echo "电脑端没有 DISPLAY，无法自动启动 RViz。请在图形桌面的终端运行。" >&2
    return 1
  fi
  if [[ ! -f "$rviz_config" ]]; then
    echo "未找到 RViz 配置: $rviz_config" >&2
    return 1
  fi
  if [[ ! -f /opt/ros/humble/setup.bash || ! -f "$PROJECT_DIR/install/setup.bash" ]]; then
    echo "电脑端 ROS 2 或 Point-LIO 环境不完整。" >&2
    return 1
  fi

  set +u
  source /opt/ros/humble/setup.bash
  source "$PROJECT_DIR/install/setup.bash"
  set -u

  rviz2 -d "$rviz_config" >"$rviz_log" 2>&1 &
  rviz_pid=$!
  cleanup_pc_rviz() {
    kill -TERM "$rviz_pid" 2>/dev/null || true
    wait "$rviz_pid" 2>/dev/null || true
  }
  trap cleanup_pc_rviz EXIT INT TERM

  sleep 1
  if ! kill -0 "$rviz_pid" 2>/dev/null; then
    echo "电脑端 RViz 启动失败，日志如下：" >&2
    tail -n 30 "$rviz_log" >&2 || true
    cleanup_pc_rviz
    trap - EXIT INT TERM
    return 1
  fi

  remote_command="cd $(printf '%q' "$jetson_project") && ./build_map.sh"
  for arg in "$@"; do
    printf -v quoted_arg '%q' "$arg"
    remote_command+=" $quoted_arg"
  done

  echo "电脑端 RViz 已启动，只显示 map、base_link 和 /path。"
  echo "正在连接 Jetson 启动建图……"
  if ssh -tt "$jetson_host" "$remote_command"; then
    ssh_status=0
  else
    ssh_status=$?
  fi
  cleanup_pc_rviz
  trap - EXIT INT TERM
  return "$ssh_status"
}

# Run this same script from the control PC to start local RViz and remote Jetson mapping.
if [[ ! -f /etc/nv_tegra_release ]]; then
  run_from_control_pc "$@"
  exit $?
fi

launch_pid=""
saved=false
old_stty=""
pcd_tmp=""

restore_terminal() {
  if [[ -n "$old_stty" && -t 0 ]]; then
    stty "$old_stty" 2>/dev/null || true
  fi
}

stop_mapping() {
  if [[ -n "$launch_pid" ]] && kill -0 "$launch_pid" 2>/dev/null; then
    kill -INT "$launch_pid" 2>/dev/null || true
    for _ in {1..50}; do
      kill -0 "$launch_pid" 2>/dev/null || break
      sleep 0.1
    done
    if kill -0 "$launch_pid" 2>/dev/null; then
      kill -TERM "$launch_pid" 2>/dev/null || true
    fi
    wait "$launch_pid" 2>/dev/null || true
  fi
  launch_pid=""
}

cleanup() {
  restore_terminal
  stop_mapping
  if [[ "$saved" != true ]]; then
    if [[ -n "$pcd_tmp" ]]; then
      rm -f -- "$pcd_tmp"
    fi
    printf '\n建图已退出，未生成地图。\n'
  fi
}
trap cleanup EXIT
trap 'exit 130' INT TERM

if [[ $# -gt 1 ]]; then
  echo "用法: $0 [地图名称]" >&2
  exit 2
fi
if [[ ! -t 0 ]]; then
  echo "该脚本需要交互终端来读取地图名和 Ctrl+S；通过 SSH 运行时请分配 TTY。" >&2
  exit 1
fi

map_name="${1:-}"
while [[ -z "$map_name" ]]; do
  read -r -p "请输入地图名称（英文、数字、下划线或短横线）: " map_name
done
map_name="${map_name%.pcd}"
map_name="${map_name%.yaml}"
map_name="${map_name%.pgm}"

if [[ ! "$map_name" =~ ^[A-Za-z0-9][A-Za-z0-9_-]*$ ]]; then
  echo "地图名称不合法，只允许英文、数字、下划线和短横线，且必须以英文或数字开头。" >&2
  exit 2
fi

if [[ ! -f /opt/ros/humble/setup.bash ]]; then
  echo "未找到 /opt/ros/humble/setup.bash；请在 Jetson ROS 2 Humble 环境运行。" >&2
  exit 1
fi
if [[ ! -f "$LIVOX_WS/install/setup.bash" ]]; then
  echo "未找到 Livox 驱动环境: $LIVOX_WS/install/setup.bash" >&2
  exit 1
fi
if [[ ! -f "$PROJECT_DIR/install/setup.bash" ]]; then
  echo "未找到 Point-LIO 环境: $PROJECT_DIR/install/setup.bash" >&2
  exit 1
fi

mkdir -p "$MAP_DIR" "$PCD_DIR" "$ROS_LOG_DIR"
pcd_tmp="$PCD_DIR/$map_name.pcd"
pcd_out="$MAP_DIR/$map_name.pcd"
yaml_out="$MAP_DIR/$map_name.yaml"
pgm_out="$MAP_DIR/$map_name.pgm"
launch_log="$ROS_LOG_DIR/${map_name}_$(date +%Y%m%d_%H%M%S).log"

for output in "$pcd_tmp" "$pcd_out" "$yaml_out" "$pgm_out"; do
  if [[ -e "$output" ]]; then
    echo "目标文件已经存在，拒绝覆盖: $output" >&2
    exit 1
  fi
done

set +u
source /opt/ros/humble/setup.bash
source "$LIVOX_WS/install/setup.bash"
source "$PROJECT_DIR/install/setup.bash"
set -u

# Stop only the known visualization/test mapping service. Do not touch motor or policy nodes.
systemctl --user stop uika-pointlio-live.service 2>/dev/null || true
sleep 1
if ros2 node list 2>/dev/null | grep -qx '/laserMapping'; then
  echo "检测到已有 /laserMapping。请先停止旧建图进程，再运行本脚本。" >&2
  exit 1
fi

echo "正在启动 MID360 + Point-LIO 建图……"
echo "地图名称: $map_name"
echo "日志文件: $launch_log"
echo "建图时不发布注册点云，只发布 TF/path，以降低 Jetson 开销。"
echo "稳健建图参数: point_filter=2, surf_voxel=0.20m, map_voxel=0.20m, iVox_nearby=6"

ros2 launch point_lio mid360_mapping_bringup.launch.py \
  rviz:=false \
  pcd_save_file:="$map_name.pcd" \
  pcd_save_interval:=-1 \
  point_filter_num:=2 \
  filter_size_surf:=0.20 \
  filter_size_map:=0.20 \
  ivox_nearby_type:=6 \
  >"$launch_log" 2>&1 &
launch_pid=$!

service_ready=false
for _ in {1..40}; do
  if ! kill -0 "$launch_pid" 2>/dev/null; then
    echo "建图启动失败，最近日志如下：" >&2
    tail -n 40 "$launch_log" >&2 || true
    exit 1
  fi
  if ros2 service list 2>/dev/null | grep -qx '/save_map'; then
    service_ready=true
    break
  fi
  sleep 0.5
done
if [[ "$service_ready" != true ]]; then
  echo "等待 /save_map 服务超时，最近日志如下：" >&2
  tail -n 40 "$launch_log" >&2 || true
  exit 1
fi

echo
echo "建图已就绪。先静止 2~3 秒，再推行或慢速行走完成采集。"
echo "完成后回到这个终端，按 Ctrl+S 保存两种地图并退出。"
echo "按 Ctrl+C 可放弃本次建图。"

old_stty="$(stty -g)"
stty -ixon

while true; do
  if ! IFS= read -rsn1 key; then
    echo "终端输入已关闭，本次地图不保存。" >&2
    exit 1
  fi
  if [[ "$key" == $'\x13' ]]; then
    break
  fi
done

restore_terminal
old_stty=""
echo
echo "收到 Ctrl+S，正在保存 3D PCD……"
save_result="$(ros2 service call /save_map std_srvs/srv/Trigger '{}' 2>&1)" || {
  echo "$save_result" >&2
  echo "调用 /save_map 失败；建图仍将停止，请检查日志。" >&2
  exit 1
}
echo "$save_result"

if [[ ! -s "$pcd_tmp" ]]; then
  echo "保存服务未生成有效 PCD: $pcd_tmp" >&2
  exit 1
fi

# Stop Point-LIO cleanly so its shutdown save completes before moving the PCD.
stop_mapping
if [[ ! -s "$pcd_tmp" ]]; then
  echo "Point-LIO 退出后 PCD 无效: $pcd_tmp" >&2
  exit 1
fi
mv -- "$pcd_tmp" "$pcd_out"

echo "正在生成 Nav2 2D occupancy map……"
python3 "$PROJECT_DIR/scripts/pcd_to_occupancy.py" \
  "$pcd_out" \
  --output "$yaml_out" \
  --resolution "$RESOLUTION" \
  --padding "$PADDING" \
  --z-min "$Z_MIN" \
  --z-max "$Z_MAX" \
  --inflate "$INFLATION"

if [[ ! -s "$yaml_out" || ! -s "$pgm_out" ]]; then
  echo "2D occupancy map 生成失败。3D PCD 已保留: $pcd_out" >&2
  exit 1
fi

saved=true
echo
echo "地图保存完成："
echo "  3D 重定位地图: $pcd_out"
echo "  Nav2 地图配置: $yaml_out"
echo "  Nav2 栅格图像: $pgm_out"
echo "  建图日志: $launch_log"
