import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    point_lio_dir = get_package_share_directory('point_lio')
    livox_dir = get_package_share_directory('livox_ros_driver2')

    driver = LaunchConfiguration('driver')
    point_lio = LaunchConfiguration('point_lio')
    nav2 = LaunchConfiguration('nav2')
    safety_bridge = LaunchConfiguration('safety_bridge')
    rviz = LaunchConfiguration('rviz')
    nav2_rviz = LaunchConfiguration('nav2_rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    point_lio_cfg = LaunchConfiguration('point_lio_cfg_dir')
    nav2_params = LaunchConfiguration('nav2_params_file')
    bridge_params = LaunchConfiguration('bridge_params_file')
    dry_run = LaunchConfiguration('dry_run')
    base_cmd_topic = LaunchConfiguration('base_cmd_topic')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')

    livox_launch = os.path.join(livox_dir, 'launch_ROS2', 'msg_MID360_launch.py')
    point_lio_launch = os.path.join(point_lio_dir, 'launch', 'point_lio.launch.py')
    nav2_launch = os.path.join(point_lio_dir, 'launch', 'nav2_mid360_map.launch.py')
    bridge_launch = os.path.join(point_lio_dir, 'launch', 'cmd_vel_safety_bridge.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument(
            'driver',
            default_value='true',
            description='Start livox_ros_driver2 MID360 driver.',
        ),
        DeclareLaunchArgument(
            'point_lio',
            default_value='true',
            description='Start Point-LIO and pointcloud_to_laserscan.',
        ),
        DeclareLaunchArgument(
            'nav2',
            default_value='true',
            description='Start static-map Nav2.',
        ),
        DeclareLaunchArgument(
            'safety_bridge',
            default_value='false',
            description='Start cmd_vel safety bridge. Keep false until ready for real robot motion.',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Start Point-LIO RViz.',
        ),
        DeclareLaunchArgument(
            'nav2_rviz',
            default_value='false',
            description='Start Nav2 RViz.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock if true.',
        ),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(point_lio_dir, 'maps', 'stage6_test_nav2.yaml'),
            description='Static map YAML for Nav2.',
        ),
        DeclareLaunchArgument(
            'point_lio_cfg_dir',
            default_value=os.path.join(point_lio_dir, 'config', 'avia.yaml'),
            description='Point-LIO config file.',
        ),
        DeclareLaunchArgument(
            'nav2_params_file',
            default_value=os.path.join(point_lio_dir, 'config', 'nav2_mid360_map_params.yaml'),
            description='Nav2 parameter file.',
        ),
        DeclareLaunchArgument(
            'bridge_params_file',
            default_value=os.path.join(point_lio_dir, 'config', 'cmd_vel_safety_bridge.yaml'),
            description='Safety bridge parameter file.',
        ),
        DeclareLaunchArgument(
            'dry_run',
            default_value='true',
            description='Keep safety bridge from publishing to the real base topic.',
        ),
        DeclareLaunchArgument(
            'base_cmd_topic',
            default_value='/cmd_vel',
            description='Real base command topic, used only when dry_run is false.',
        ),
        DeclareLaunchArgument(
            'cmd_vel_topic',
            default_value='/nav_cmd_vel_test',
            description='Safe Nav2 output topic consumed by the safety bridge.',
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(livox_launch),
            condition=IfCondition(driver),
        ),
        TimerAction(
            period=3.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(point_lio_launch),
                    condition=IfCondition(point_lio),
                    launch_arguments={
                        'rviz': rviz,
                        'scan': 'true',
                        'use_sim_time': use_sim_time,
                        'point_lio_cfg_dir': point_lio_cfg,
                    }.items(),
                ),
            ],
        ),
        TimerAction(
            period=8.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(nav2_launch),
                    condition=IfCondition(nav2),
                    launch_arguments={
                        'rviz': nav2_rviz,
                        'use_sim_time': use_sim_time,
                        'map': map_file,
                        'params_file': nav2_params,
                        'cmd_vel_topic': cmd_vel_topic,
                    }.items(),
                ),
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(bridge_launch),
                    condition=IfCondition(safety_bridge),
                    launch_arguments={
                        'params_file': bridge_params,
                        'dry_run': dry_run,
                        'output_topic': base_cmd_topic,
                    }.items(),
                ),
            ],
        ),
    ])
