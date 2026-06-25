# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a ROS2 Humble driver for DM (达妙) IMU sensors. The package reads serial data from the IMU and publishes:
- `/imu/data` - sensor_msgs/Imu (quaternion orientation, angular velocity, linear acceleration)
- `/imu/rpy` - geometry_msgs/Vector3Stamped (roll, pitch, yaw)
- `/imu/pose` - geometry_msgs/PoseStamped (position + orientation)

## Build & Run

```bash
# Build the package
colcon build --packages-select dm_imu

# Source the workspace
source install/setup.bash

# Run with default params (port /dev/ttyACM0, 921600 baud)
ros2 launch dm_imu dm_imu.launch.py

# Or run the node directly
ros2 run dm_imu dm_imu_node

# With custom parameters
ros2 run dm_imu dm_imu_node --ros-args -p port:=/dev/ttyUSB0 -p baudrate:=921600
```

## Architecture

```
dm_imu/
├── node.py              # DmImuNode ROS2 node - publishes IMU data at 200Hz
└── modules/
    ├── dm_serial.py     # DM_Serial class - serial protocol parser with background reader thread
    └── dm_crc.py        # CRC utilities (checksum8, CRC16-CCITT)
```

### Data Flow

1. `DM_Serial` opens serial port (non-blocking) and starts a background reader thread
2. Background thread continuously reads and parses frames: `[0x55,0xAA][rid][r,p,y float32][crc16][0x0A]`
3. Main thread polls `get_latest()` at 200Hz via timer
4. `DmImuNode` converts RPY to quaternion and publishes to 3 topics

### Serial Protocol

All frames share this structure:
- Header: `0x55 0xAA`
- Byte 2: Slave ID (ignored)
- Byte 3: Frame type ID
- Payload: 3x float32 (little-endian)
- Bytes 16-17: CRC16 (CCITT 0x1021, init 0xFFFF)
- Tail: `0x0A`

| Type ID | Data | Unit |
|---------|------|------|
| 0x01 | Acceleration (x, y, z) | m/s² |
| 0x02 | Angular velocity (x, y, z) | °/s |
| 0x03 | RPY (roll, pitch, yaw) | degrees |

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `port` | `/dev/ttyACM0` | Serial device |
| `baudrate` | `921600` | Serial baud rate |
| `publish_imu_data` | `false` | Enable /imu/data |
| `publish_rpy` | `true` | Enable /imu/rpy |
| `publish_pose` | `false` | Enable /imu/pose |
| `publish_rpy_in_degree` | `true` | RPY in degrees vs radians |
| `qos_reliable` | `true` | QoS reliability |
| `verbose` | `true` | Terminal logging |
