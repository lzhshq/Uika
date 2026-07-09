import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    default_params = os.path.join(bringup_dir, 'config', 'nav2_mppi_dryrun.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')
    odom_topic = LaunchConfiguration('odom_topic')
    initial_x = LaunchConfiguration('initial_x')
    initial_y = LaunchConfiguration('initial_y')
    initial_z = LaunchConfiguration('initial_z')
    initial_yaw = LaunchConfiguration('initial_yaw')
    autostart = LaunchConfiguration('autostart')
    log_level = LaunchConfiguration('log_level')

    controller_remappings = [
        ('/tf', 'tf'),
        ('/tf_static', 'tf_static'),
        ('cmd_vel', '/cmd_vel_nav'),
    ]

    smoother_remappings = [
        ('/tf', 'tf'),
        ('/tf_static', 'tf_static'),
        ('cmd_vel', '/cmd_vel_nav'),
        ('cmd_vel_smoothed', cmd_vel_topic),
    ]

    dryrun_odom_node = Node(
        package='fine_nav2d_bringup',
        executable='dryrun_odom_publisher.py',
        name='dryrun_odom_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'odom_topic': odom_topic,
            'cmd_vel_topic': cmd_vel_topic,
            'frame_id': 'map',
            'child_frame_id': 'base_link',
            'publish_rate': 30.0,
            'initial_x': initial_x,
            'initial_y': initial_y,
            'initial_z': initial_z,
            'initial_yaw': initial_yaw,
        }],
    )

    controller_server_node = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', log_level],
        remappings=controller_remappings,
    )

    velocity_smoother_node = Node(
        package='nav2_velocity_smoother',
        executable='velocity_smoother',
        name='velocity_smoother',
        output='screen',
        parameters=[params_file, {'use_sim_time': use_sim_time}],
        arguments=['--ros-args', '--log-level', log_level],
        remappings=smoother_remappings,
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_mppi_dryrun',
        output='screen',
        arguments=['--ros-args', '--log-level', log_level],
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': autostart,
            'node_names': ['controller_server', 'velocity_smoother'],
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('cmd_vel_topic', default_value='/cmd_vel_test'),
        DeclareLaunchArgument('odom_topic', default_value='/dryrun_odom'),
        DeclareLaunchArgument('initial_x', default_value='0.0'),
        DeclareLaunchArgument('initial_y', default_value='0.0'),
        DeclareLaunchArgument('initial_z', default_value='0.0'),
        DeclareLaunchArgument('initial_yaw', default_value='0.0'),
        DeclareLaunchArgument('autostart', default_value='true'),
        DeclareLaunchArgument('log_level', default_value='info'),
        dryrun_odom_node,
        controller_server_node,
        velocity_smoother_node,
        lifecycle_manager_node,
    ])
