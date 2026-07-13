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
    rviz = LaunchConfiguration('rviz')
    use_sim_time = LaunchConfiguration('use_sim_time')
    point_lio_cfg = LaunchConfiguration('point_lio_cfg_dir')
    pcd_save_file = LaunchConfiguration('pcd_save_file')
    pcd_save_interval = LaunchConfiguration('pcd_save_interval')
    point_filter_num = LaunchConfiguration('point_filter_num')
    filter_size_surf = LaunchConfiguration('filter_size_surf')
    filter_size_map = LaunchConfiguration('filter_size_map')
    ivox_nearby_type = LaunchConfiguration('ivox_nearby_type')

    livox_launch = os.path.join(livox_dir, 'launch_ROS2', 'msg_MID360_launch.py')
    point_lio_launch = os.path.join(point_lio_dir, 'launch', 'point_lio.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument(
            'driver',
            default_value='true',
            description='Start livox_ros_driver2 MID360 driver.',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Start Point-LIO RViz while mapping.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use /clock if true.',
        ),
        DeclareLaunchArgument(
            'point_lio_cfg_dir',
            default_value=os.path.join(point_lio_dir, 'config', 'avia.yaml'),
            description='Point-LIO config file.',
        ),
        DeclareLaunchArgument(
            'pcd_save_file',
            default_value='mid360_mapping.pcd',
            description='PCD file name saved under the point_lio PCD directory.',
        ),
        DeclareLaunchArgument(
            'pcd_save_interval',
            default_value='-1',
            description='LiDAR frames per PCD file. -1 saves one file on shutdown.',
        ),
        DeclareLaunchArgument(
            'point_filter_num',
            default_value='2',
            description='Mapping profile: retain every second valid MID360 point.',
        ),
        DeclareLaunchArgument(
            'filter_size_surf',
            default_value='0.20',
            description='Mapping profile: current-scan voxel size in meters.',
        ),
        DeclareLaunchArgument(
            'filter_size_map',
            default_value='0.20',
            description='Mapping profile: incremental-map voxel size in meters.',
        ),
        DeclareLaunchArgument(
            'ivox_nearby_type',
            default_value='6',
            description='Mapping profile: iVox neighboring cells searched.',
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
                    launch_arguments={
                        'rviz': rviz,
                        'rviz_config': os.path.join(
                            point_lio_dir, 'rviz_cfg', 'tf_path_only.rviz'),
                        'scan': 'false',
                        'publish_cloud': 'false',
                        'use_sim_time': use_sim_time,
                        'point_lio_cfg_dir': point_lio_cfg,
                        'pcd_save': 'true',
                        'pcd_save_interval': pcd_save_interval,
                        'pcd_save_file': pcd_save_file,
                        'point_filter_num': point_filter_num,
                        'filter_size_surf': filter_size_surf,
                        'filter_size_map': filter_size_map,
                        'ivox_nearby_type': ivox_nearby_type,
                    }.items(),
                ),
            ],
        ),
    ])
