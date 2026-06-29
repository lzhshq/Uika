#!/usr/bin/env bash
set -euo pipefail

# Uika RL 推理节点一键启动脚本。
# 用法：
#   cd /home/nvidia/Uika
#   ./start_rl.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RL_DIR="${ROOT_DIR}/rl_sar-main"
WORKSPACE_DIR="${ROOT_DIR}/Quadruped_Uika"
ONNXRUNTIME_LIB_DIR="${RL_DIR}/library/inference_runtime/onnxruntime/lib"
RL_BIN="${RL_DIR}/cmake_build/bin/uika"

echo "========================================"
echo "Uika RL 推理节点启动"
echo "总目录: ${ROOT_DIR}"
echo "RL 目录: ${RL_DIR}"
echo "ROS workspace: ${WORKSPACE_DIR}"
echo "========================================"

if [[ ! -d "${RL_DIR}" ]]; then
  echo "错误: 找不到 RL 目录: ${RL_DIR}"
  exit 1
fi

if [[ ! -d "${WORKSPACE_DIR}" ]]; then
  echo "错误: 找不到 ROS workspace: ${WORKSPACE_DIR}"
  exit 1
fi

if [[ ! -x "${RL_BIN}" ]]; then
  echo "错误: 找不到可执行文件或没有执行权限: ${RL_BIN}"
  echo "请先确认 rl_sar-main/cmake_build/bin/uika 已编译完成。"
  exit 1
fi

# 如果当前 shell 里有 conda，退出 conda 环境，避免影响 ROS2 动态库和 Python 包路径。
if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh" || true
  conda deactivate >/dev/null 2>&1 || true
fi

if [[ -f /opt/ros/humble/setup.bash ]]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/humble/setup.bash
  if [[ -f "${WORKSPACE_DIR}/install/setup.bash" ]]; then
    # shellcheck disable=SC1091
    source "${WORKSPACE_DIR}/install/setup.bash"
  else
    echo "错误: 找不到 workspace 环境: ${WORKSPACE_DIR}/install/setup.bash"
    echo "请先运行 ./start_uika.sh 或在 Quadruped_Uika 下 colcon build。"
    exit 1
  fi
  set -u
else
  echo "错误: 找不到 /opt/ros/humble/setup.bash"
  exit 1
fi


if [[ -d "${ONNXRUNTIME_LIB_DIR}" ]]; then
  export LD_LIBRARY_PATH="${ONNXRUNTIME_LIB_DIR}:${LD_LIBRARY_PATH:-}"
else
  echo "错误: 找不到 ONNX Runtime 库目录: ${ONNXRUNTIME_LIB_DIR}"
  exit 1
fi

cd "${RL_DIR}"

echo "启动 RL 推理程序: ${RL_BIN}"
echo "按 Ctrl-C 停止。"
echo "========================================"

exec "${RL_BIN}"
