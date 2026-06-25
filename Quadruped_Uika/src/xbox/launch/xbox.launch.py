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
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Joy node - publishes joy messages from Xbox controller
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{
                'deadzone': 0.1,
                'autorepeat_rate': 20.0,
            }],
        ),
        # Xbox velocity publisher
        Node(
            package='xbox',
            executable='xbox_vel_publisher',
            name='xbox_vel_publisher',
            output='screen',
            parameters=[{
                'max_linear_speed': 1.0,
                'max_angular_speed': 0.5,
                'deadzone': 0.1,
            }],
        ),
    ])
