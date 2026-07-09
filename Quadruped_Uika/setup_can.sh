#!/usr/bin/env bash
set -euo pipefail

# ==========================================
# 四足机器人 CAN 总线一键配置脚本
# 配置机器人电机 CAN 口 can1 ~ can4，波特率 1Mbps
# ==========================================

if [[ ${EUID} -ne 0 ]]; then
    exec sudo "$0" "$@"
fi

BITRATE="${BITRATE:-1000000}"
TXQUEUE="${TXQUEUE:-1000}"
RESTART_MS="${RESTART_MS:-100}"

echo "正在加载 CAN 内核模块..."
modprobe can || true
modprobe can_raw || true
modprobe gs_usb || true

if [[ $# -gt 0 ]]; then
    CAN_INTERFACES=("$@")
else
    CAN_INTERFACES=(can1 can2 can3 can4)
fi

if [[ ${#CAN_INTERFACES[@]} -eq 0 ]]; then
    echo "没有发现可配置的 CAN 接口，请检查 CAN hub 是否连接。"
    exit 1
fi

failed=0

for can in "${CAN_INTERFACES[@]}"; do
    echo "--------------------------------"
    echo "正在配置 ${can}..."

    if [[ ! -e "/sys/class/net/${can}" ]]; then
        echo "${can} 不存在，跳过。"
        failed=1
        continue
    fi

    ip link set dev "${can}" down 2>/dev/null || true
    if ! ip link set dev "${can}" type can bitrate "${BITRATE}" restart-ms "${RESTART_MS}"; then
        echo "${can} 不支持 restart-ms，降级为只设置 bitrate。"
        ip link set dev "${can}" type can bitrate "${BITRATE}"
    fi
    ip link set dev "${can}" txqueuelen "${TXQUEUE}"
    ip link set dev "${can}" up

    state=$(ip -details -statistics link show dev "${can}" | sed -n '2p' | xargs)
    echo "${can} 配置成功 [bitrate=${BITRATE}, txqueuelen=${TXQUEUE}, restart-ms=${RESTART_MS}]"
    echo "${state}"
done

echo "--------------------------------"
if [[ ${failed} -ne 0 ]]; then
    echo "配置流程结束，但有 CAN 接口不存在。"
    exit 1
fi

echo "配置流程结束。"
echo "可用 'ip -details -statistics link show canX' 查看详细状态。"
