# Copyright 2026 lzh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Get package share directories
    xbox_pkg_share = get_package_share_directory('xbox')
    dm_imu_pkg_share = get_package_share_directory('dm_imu')
    dm_imu_params_file = os.path.join(dm_imu_pkg_share, 'config', 'params.yaml')

    # Include xbox launch file
    xbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(xbox_pkg_share, 'launch', 'xbox.launch.py')
        )
    )

    # DM IMU node
    dm_imu_node = Node(
        package='dm_imu',
        executable='dm_imu_node',
        name='dm_imu',
        output='screen',
        parameters=[dm_imu_params_file]
    )

    # Robstride motor node
    rs_motor_node = Node(
        package='rs00_motor',
        executable='rs00_motor',
        name='rs00_motor',
        output='screen',
    )

    return LaunchDescription([
        xbox_launch,
        dm_imu_node,
        rs_motor_node,
    ])
