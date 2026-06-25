# 启动节点

```bash
conda deactivate
cd /home/nvidia/UIKA/Quadruped_Uika
sudo ip link set can1 down
sudo ip link set can2 down
sudo ip link set can3 down
sudo ip link set can4 down
colcon build 
source ./install/setup.bash
chmod +x ./setup_can.sh
./setup_can.sh
sudo chmod 666 /dev/ttyACM0
ros2 launch bringup bringup.launch.py
```


# 站立指令（没写差值）

## 另开终端2
```bash
cd /home/nvidia/UIKA/Quadruped_Uika
source ./install/setup.bash
ros2 topic pub /motor_command interfaces/msg/MotorCommand12 \
"header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: 'cmd'
fl_hip:
  torque: 0.0
  position: -0.80
  velocity: 0.0
  kp: 20.0
  kd: 8.0
fl_thigh:
  torque: 0.0
  position: 0.05
  velocity: 0.0
  kp: 20.0
  kd: 8.0
fl_calf:
  torque: 0.0
  position: 0.70
  velocity: 0.0
  kp: 20.0
  kd: 8.0
fr_hip:
  torque: 0.0
  position: 0.80
  velocity: 0.0
  kp: 20.0
  kd: 8.0
fr_thigh:
  torque: 0.0
  position: -0.05
  velocity: 0.0
  kp: 20.0
  kd: 8.0
fr_calf:
  torque: 0.0
  position: -0.70
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rl_hip:
  torque: 0.0
  position: 0.75
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rl_thigh:
  torque: 0.0
  position: 0.05
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rl_calf:
  torque: 0.0
  position: 0.70
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rr_hip:
  torque: 0.0
  position: -0.75
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rr_thigh:
  torque: 0.0
  position: -0.2
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rr_calf:
  torque: 0.0
  position: -0.70
  velocity: 0.0
  kp: 20.0
  kd: 8.0" \
--once
```
ros2 topic pub /motor_command interfaces/msg/MotorCommand12 \
"header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: 'cmd'
fl_hip:
  torque: 0.0
  position: -0.80
  velocity: 0.0
  kp: 15.0
  kd: 8.0
fl_thigh:
  torque: 0.0
  position: 0.05
  velocity: 0.0
  kp: 15.0
  kd: 8.0
fl_calf:
  torque: 0.0
  position: 0.70
  velocity: 0.0
  kp: 15.0
  kd: 8.0
fr_hip:
  torque: 0.0
  position: 0.80
  velocity: 0.0
  kp: 15.0
  kd: 8.0
fr_thigh:
  torque: 0.0
  position: -0.05
  velocity: 0.0
  kp: 15.0
  kd: 8.0
fr_calf:
  torque: 0.0
  position: -0.70
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rl_hip:
  torque: 0.0
  position: 0.75
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rl_thigh:
  torque: 0.0
  position: 0.05
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rl_calf:
  torque: 0.0
  position: 0.70
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rr_hip:
  torque: 0.0
  position: -0.75
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rr_thigh:
  torque: 0.0
  position: -0.2
  velocity: 0.0
  kp: 15.0
  kd: 8.0
rr_calf:
  torque: 0.0
  position: -0.70
  velocity: 0.0
  kp: 15.0
  kd: 8.0" \
--once
ros2 topic pub /motor_command interfaces/msg/MotorCommand12 \
"header:
  stamp:
    sec: 0
    nanosec: 0
  frame_id: 'cmd'
rr_hip:
  torque: 0.0
  position: -0.75
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rr_thigh:
  torque: 0.0
  position: -0.2
  velocity: 0.0
  kp: 20.0
  kd: 8.0
rr_calf:
  torque: 0.0
  position: -0.70
  velocity: 0.0
  kp: 20.0
  kd: 8.0" \
--once