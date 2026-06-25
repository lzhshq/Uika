#!/bin/bash

# ==========================================
# 四足机器人 CAN 总线一键配置脚本
# 配置 can1 ~ can4，波特率 1Mbps
# ==========================================

echo "正在加载 CAN 内核模块..."
sudo modprobe can
sudo modprobe can_raw
sudo modprobe candev

# 定义要配置的接口列表
CAN_INTERFACES="can1 can2 can3 can4"
# 定义波特率 (1000000 = 1Mbps, 500000 = 500Kbps)
BITRATE=1000000
# 定义发送队列长度
TXQUEUE=1000

for can in $CAN_INTERFACES; do
    echo "--------------------------------"
    echo "正在配置 $can..."
    
    # 1. 关闭接口（防止已开启报错）
    sudo ip link set $can down 2>/dev/null
    
    # 2. 设置波特率
    sudo ip link set $can type can bitrate $BITRATE
    
    # 3. 开启接口
    sudo ip link set $can up
    
    # 4. 设置发送队列长度 (注：机器人控制建议设大一点，比如 1000)
    sudo ip link set $can txqueuelen $TXQUEUE
    
    if [ $? -eq 0 ]; then
        echo "$can 配置成功 [波特率: $BITRATE, 队列: $TXQUEUE]"
    else
        echo "$can 配置失败！请检查硬件是否连接。"
    fi
done

echo "--------------------------------"
echo "配置流程结束。"
echo "使用 'ip -details link show canx' 查看状态。"
