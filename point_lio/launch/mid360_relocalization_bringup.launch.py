import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    point_lio_dir = get_package_share_directory('point_lio')
    livox_dir = get_package_share_directory('livox_ros_driver2')

    driver = LaunchConfiguration('driver')
    rviz = LaunchConfiguration('rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_file = LaunchConfiguration('map')
    point_lio_cfg = LaunchConfiguration('point_lio_cfg_dir')
    relocalization_cfg = LaunchConfiguration('relocalization_params_file')
    continuous_shadow = LaunchConfiguration('continuous_shadow')

    livox_launch = os.path.join(livox_dir, 'launch_ROS2', 'msg_MID360_launch.py')
    point_lio_launch = os.path.join(point_lio_dir, 'launch', 'point_lio.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument(
            'driver', default_value='true',
            description='Start the MID360 driver.'),
        DeclareLaunchArgument(
            'rviz', default_value='false',
            description='Start Jetson-side RViz (normally keep false).'),
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(point_lio_dir, 'maps', 'sushe.pcd'),
            description='3D PCD map used for fixed-start relocalization.'),
        DeclareLaunchArgument(
            'point_lio_cfg_dir',
            default_value=os.path.join(point_lio_dir, 'config', 'avia.yaml')),
        DeclareLaunchArgument(
            'relocalization_params_file',
            default_value=os.path.join(
                point_lio_dir, 'config', 'fixed_start_relocalization.yaml')),
        DeclareLaunchArgument(
            'continuous_shadow', default_value='false',
            description='Compute periodic correction candidates without changing map->odom.'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(livox_launch),
            condition=IfCondition(driver),
        ),
        TimerAction(
            period=3.0,
            actions=[
                IncludeLaunchDescription(
                    PythonLaunchDescriptionSource(point_lio_launch),
                    launch_arguments={
                        'rviz': rviz,
                        'scan': 'false',
                        'publish_cloud': 'true',
                        'pcd_save': 'false',
                        'use_sim_time': use_sim_time,
                        'point_lio_cfg_dir': point_lio_cfg,
                        'publish_map_to_odom': 'false',
                        'lio_world_parent_frame': 'odom',
                        'path_en': 'false',
                        'point_filter_num': '3',
                        'filter_size_surf': '0.3',
                        'filter_size_map': '0.3',
                    }.items(),
                ),
            ],
        ),
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='point_lio',
                    executable='fixed_start_relocalizer',
                    name='fixed_start_relocalizer',
                    output='screen',
                    parameters=[
                        relocalization_cfg,
                        {
                            'use_sim_time': use_sim_time,
                            'map_path': map_file,
                            'continuous_shadow.enabled': ParameterValue(
                                continuous_shadow, value_type=bool),
                        },
                    ],
                ),
            ],
        ),
    ])
