import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    fast_lio_dir = get_package_share_directory('fast_lio')
    pcd_dir = os.path.join(fast_lio_dir, 'PCD')
    mapping_launch = os.path.join(bringup_dir, 'launch', 'uika_mapping_urdf.launch.py')

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('start_driver', default_value='true'),
        DeclareLaunchArgument('start_fast_lio', default_value='true'),
        DeclareLaunchArgument('start_localization', default_value='true'),
        DeclareLaunchArgument('start_map_manager', default_value='true'),
        DeclareLaunchArgument('start_saved_map_publisher', default_value='false'),
        DeclareLaunchArgument('start_pct', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='false'),
        DeclareLaunchArgument('working_mode', default_value='exploration'),
        DeclareLaunchArgument('global_localization_enable', default_value='false'),
        DeclareLaunchArgument('global_localization_source_type', default_value='1'),
        DeclareLaunchArgument('global_localization_topic', default_value='/global_localization'),
        DeclareLaunchArgument('global_localization_message_type', default_value='1'),
        DeclareLaunchArgument(
            'pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map.pcd'),
        ),
        DeclareLaunchArgument(
            'viz_pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd'),
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(mapping_launch),
            launch_arguments={
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'start_driver': LaunchConfiguration('start_driver'),
                'start_fast_lio': LaunchConfiguration('start_fast_lio'),
                'start_localization': LaunchConfiguration('start_localization'),
                'start_map_manager': LaunchConfiguration('start_map_manager'),
                'start_saved_map_publisher': LaunchConfiguration('start_saved_map_publisher'),
                'start_pct': LaunchConfiguration('start_pct'),
                'start_rviz': LaunchConfiguration('start_rviz'),
                'working_mode': LaunchConfiguration('working_mode'),
                'global_localization_enable': LaunchConfiguration('global_localization_enable'),
                'global_localization_source_type': LaunchConfiguration('global_localization_source_type'),
                'global_localization_topic': LaunchConfiguration('global_localization_topic'),
                'global_localization_message_type': LaunchConfiguration('global_localization_message_type'),
                'pcd_file_path': LaunchConfiguration('pcd_file_path'),
                'viz_pcd_file_path': LaunchConfiguration('viz_pcd_file_path'),
            }.items(),
        ),
    ])
