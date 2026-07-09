#!/usr/bin/env bash
set -euo pipefail

# Uika Jetson 一键启动 ROS bringup。
# 用法：
#   cd /home/nvidia/Uika
#   ./start_uika.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/Quadruped_Uika"
CAN_IFACES=(can1 can2 can3 can4)

echo "========================================"
echo "Uika ROS 一键启动"
echo "总目录: ${ROOT_DIR}"
echo "ROS workspace: ${WORKSPACE_DIR}"
echo "========================================"

if [[ ! -d "${WORKSPACE_DIR}" ]]; then
  echo "错误: 找不到 ROS workspace: ${WORKSPACE_DIR}"
  exit 1
fi

cd "${WORKSPACE_DIR}"

# 如果当前 shell 里有 conda，退出 conda 环境，避免影响 ROS2 Python 包路径。
if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh" || true
  conda deactivate >/dev/null 2>&1 || true
fi

if [[ -f /opt/ros/humble/setup.bash ]]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
  set -u
else
  echo "错误: 找不到 /opt/ros/humble/setup.bash"
  exit 1
fi

echo "[1/6] 获取 sudo 权限..."
sudo -v

echo "[2/6] 检查 CAN 接口..."
missing_can=0
for iface in "${CAN_IFACES[@]}"; do
  if [[ ! -e "/sys/class/net/${iface}" ]]; then
    echo "错误: 找不到 ${iface}，请检查 CAN hub 是否连接。"
    missing_can=1
  fi
done
if [[ ${missing_can} -ne 0 ]]; then
  exit 1
fi

echo "[3/6] 检查 ROS2 workspace install..."
if [[ ! -f "${WORKSPACE_DIR}/install/setup.bash" ]]; then
  echo "错误: 找不到 ${WORKSPACE_DIR}/install/setup.bash"
  echo "请先手动编译一次:"
  echo "  cd ${WORKSPACE_DIR} && colcon build"
  exit 1
fi

echo "[4/6] 加载 workspace 环境..."
set +u
# shellcheck disable=SC1091
source "${WORKSPACE_DIR}/install/setup.bash"
set -u

echo "[5/6] 配置 CAN 总线..."
chmod +x "${WORKSPACE_DIR}/setup_can.sh"
"${WORKSPACE_DIR}/setup_can.sh"

if [[ -e /dev/ttyACM0 ]]; then
  echo "[6/6] 设置 /dev/ttyACM0 权限..."
  sudo chmod 666 /dev/ttyACM0
else
  echo "[6/6] 未发现 /dev/ttyACM0，跳过串口权限设置。"
fi

echo "========================================"
echo "启动 bringup.launch.py"
echo "按 Ctrl-C 停止。"
echo "========================================"

# 仅过滤正常启动/退出时的固定噪声，保留节点状态和异常 WARN/ERROR。
ros2 launch bringup bringup.launch.py imu_type:=yesense 2>&1 | \
  grep --line-buffered -v -E '^\[INFO\] \[launch\]: (All log files can be found below|Default logging verbosity is set to INFO)' | \
  grep --line-buffered -v -E '^\[WARNING\] \[launch\]: user interrupted with ctrl-c \(SIGINT\)' | \
  grep --line-buffered -v -E '^\[[^]]+\] \[INFO\] \[[^]]+\] \[rclcpp\]: signal_handler\(signum=2\)' | \
  grep --line-buffered -v -E '^\[INFO\] \[[^]]+\]: process has finished cleanly \[pid [0-9]+\]'
