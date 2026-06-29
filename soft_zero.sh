#!/usr/bin/env bash
set -euo pipefail

# 平滑移动到 0 位置。
# 用法：
#   cd /home/nvidia/Uika
#   ./soft_zero.sh
# 可选参数会原样转发给 soft_start_zero.py，例如：
#   ./soft_zero.sh --duration 3.0 --rate 500 --hold-time 1.0

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="${ROOT_DIR}/Quadruped_Uika"

cd "${WORKSPACE_DIR}"

# 如果当前 shell 里有 conda，退出 conda 环境，避免 ros2 run 使用 conda Python。
if command -v conda >/dev/null 2>&1; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh" || true
  conda deactivate >/dev/null 2>&1 || true
fi

set +u
source /opt/ros/humble/setup.bash
source "${WORKSPACE_DIR}/install/setup.bash"
set -u

exec ros2 run rs00_motor soft_start_zero.py "$@"
