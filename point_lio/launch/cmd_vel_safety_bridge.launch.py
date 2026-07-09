from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    default_params = os.path.join(
        get_package_share_directory('point_lio'),
        'config',
        'cmd_vel_safety_bridge.yaml',
    )

    params_file = LaunchConfiguration('params_file')
    dry_run = LaunchConfiguration('dry_run')
    output_topic = LaunchConfiguration('output_topic')

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=default_params,
            description='Path to cmd_vel safety bridge parameters.',
        ),
        DeclareLaunchArgument(
            'dry_run',
            default_value='true',
            description='If true, do not publish to the real base command topic.',
        ),
        DeclareLaunchArgument(
            'output_topic',
            default_value='/cmd_vel',
            description='Robot base command topic used only when dry_run is false.',
        ),
        Node(
            package='point_lio',
            executable='cmd_vel_safety_bridge.py',
            name='cmd_vel_safety_bridge',
            output='screen',
            parameters=[
                params_file,
                {
                    'dry_run': dry_run,
                    'output_topic': output_topic,
                },
            ],
        ),
    ])
