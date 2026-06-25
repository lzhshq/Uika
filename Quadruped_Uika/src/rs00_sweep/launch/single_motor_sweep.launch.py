from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import os


def generate_launch_description():
    package_share = get_package_share_directory('rs00_sweep')
    default_config = os.path.join(package_share, 'config', 'single_motor_sweep.yaml')

    config_arg = DeclareLaunchArgument(
        'config',
        default_value=default_config,
        description='单电机扫频参数文件')

    sweep_node = Node(
        package='rs00_sweep',
        executable='single_motor_sweep',
        name='single_motor_sweep',
        output='screen',
        parameters=[LaunchConfiguration('config')])

    return LaunchDescription([
        config_arg,
        sweep_node,
    ])
