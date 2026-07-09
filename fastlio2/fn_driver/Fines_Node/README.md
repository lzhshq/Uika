# Finess_Node
在机器人上位机的视角里，机器人本体作为一个package进行封装维护，该package描述了操作机器人需要的所有信息，包括
* 机器人构型描述
* 机器人通信接口

本地部署
```shell
mkdir <your_ws>
cd <your_ws>
git clone https://gitee.com/huigg-practice/Fines_Node.git
colcon build --symlink-install
```
## Fines_Decription

```shell
source install/setup.bash

# 可视化 urdf
ros2 launch fines_description display_urdf.launch.py

# 根据 urdf 发送 robotstate
ros2 launch fines_description publish_urdf.launch.py
```

## Fines_Serial

```shell
source install/setup.bash

# 如果没有提供串口号，则默认使用 /dev/ttyUSB0
ros2 run fines_serial fines_serial -- <serial_port>
```