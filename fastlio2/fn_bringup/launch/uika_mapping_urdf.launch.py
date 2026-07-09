# Copyright (c) 2026.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    fast_lio_dir = get_package_share_directory('fast_lio')
    livox_dir = get_package_share_directory('livox_ros_driver2')
    config_dir = os.path.join(bringup_dir, 'config')
    pcd_dir = os.path.join(fast_lio_dir, 'PCD')
    rviz_dir = os.path.join(bringup_dir, 'rviz')
    default_urdf_path = os.path.join(bringup_dir, 'urdf', 'uika_lidar_mount.urdf')
    default_raw_map_path = os.path.join(
        os.path.expanduser('~'),
        'Uika',
        'fastlio2',
        'fn_localization',
        'Fast_LIO',
        'PCD',
        'uika_real_map_pitch45_raw.pcd',
    )

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_driver = LaunchConfiguration('start_driver')
    start_fast_lio = LaunchConfiguration('start_fast_lio')
    start_localization = LaunchConfiguration('start_localization')
    start_map_manager = LaunchConfiguration('start_map_manager')
    start_saved_map_publisher = LaunchConfiguration('start_saved_map_publisher')
    start_tf_path_publisher = LaunchConfiguration('start_tf_path_publisher')
    start_pct = LaunchConfiguration('start_pct')
    start_rviz = LaunchConfiguration('start_rviz')
    global_localization_enable = LaunchConfiguration('global_localization_enable')
    global_localization_source_type = LaunchConfiguration('global_localization_source_type')
    global_localization_topic = LaunchConfiguration('global_localization_topic')
    global_localization_message_type = LaunchConfiguration('global_localization_message_type')
    robot_description_path = LaunchConfiguration('robot_description_path')
    lidar_mount_x = LaunchConfiguration('lidar_mount_x')
    lidar_mount_y = LaunchConfiguration('lidar_mount_y')
    lidar_mount_z = LaunchConfiguration('lidar_mount_z')
    lidar_mount_roll = LaunchConfiguration('lidar_mount_roll')
    lidar_mount_pitch = LaunchConfiguration('lidar_mount_pitch')
    lidar_mount_yaw = LaunchConfiguration('lidar_mount_yaw')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(Command(['cat ', robot_description_path]), value_type=str),
        }],
        condition=IfCondition(LaunchConfiguration('publish_robot_description')),
    )

    livox_driver_node = Node(
        package='livox_ros_driver2',
        executable='livox_ros_driver2_node',
        name='livox_driver_node',
        output='screen',
        parameters=[{
            'xfer_format': ParameterValue(LaunchConfiguration('xfer_format'), value_type=int),
            'multi_topic': 0,
            'data_src': 0,
            'publish_freq': ParameterValue(LaunchConfiguration('publish_freq'), value_type=float),
            'output_data_type': 0,
            'frame_id': 'base_lidar',
            'self_filtering_radius': ParameterValue(
                LaunchConfiguration('self_filtering_radius'),
                value_type=float,
            ),
            'point_max_range': ParameterValue(
                LaunchConfiguration('point_max_range'),
                value_type=float,
            ),
            'user_config_path': LaunchConfiguration('livox_config_path'),
            'cmdline_input_bd_code': 'livox0000000001',
        }],
        remappings=[
            ('/livox/lidar', '/lidar'),
            ('/livox/lidar/pointcloud', '/lidar/pointcloud'),
            ('/livox/imu', '/imu'),
        ],
        condition=IfCondition(start_driver),
    )

    fast_lio_node = Node(
        package='fast_lio',
        executable='fastlio_mapping',
        name='fast_lio',
        output='screen',
        parameters=[
            LaunchConfiguration('fast_lio_params_file'),
            {
                'use_sim_time': use_sim_time,
                'common': {
                    'lid_topic': LaunchConfiguration('lidar_topic'),
                    'imu_topic': LaunchConfiguration('imu_topic'),
                },
                'publish': {
                    'path_en': ParameterValue(
                        LaunchConfiguration('fast_lio_path_en'),
                        value_type=bool,
                    ),
                    'map_en': ParameterValue(
                        LaunchConfiguration('fast_lio_map_en'),
                        value_type=bool,
                    ),
                    'scan_publish_en': ParameterValue(
                        LaunchConfiguration('fast_lio_scan_publish_en'),
                        value_type=bool,
                    ),
                    'scan_bodyframe_pub_en': ParameterValue(
                        LaunchConfiguration('fast_lio_scan_bodyframe_pub_en'),
                        value_type=bool,
                    ),
                    'tf_en': ParameterValue(
                        LaunchConfiguration('fast_lio_tf_en'),
                        value_type=bool,
                    ),
                },
                'map_file_path': LaunchConfiguration('map_file_path'),
            },
        ],
        condition=IfCondition(start_fast_lio),
    )

    map_to_odom_node = Node(
        package='localization_manager',
        executable='localization_manager_node',
        name='global_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'source_type': ParameterValue(global_localization_source_type, value_type=int),
            'enable': ParameterValue(global_localization_enable, value_type=bool),
            'topic': global_localization_topic,
            'message_type': ParameterValue(global_localization_message_type, value_type=int),
            'map_frame': 'map',
            'odom_frame': 'odom',
            'base_link_frame': 'base_link',
        }],
        condition=IfCondition(start_localization),
    )

    odom_to_base_node = Node(
        package='localization_manager',
        executable='localization_manager_node',
        name='local_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'source_type': 0,
            'enable': True,
            'topic': '/Odometry',
            'message_type': 0,
            'map_frame': 'map',
            'odom_frame': 'odom',
            'base_link_frame': 'base_link',
            'lidar_odom_frame': 'lidar_odom',
        }],
        condition=IfCondition(start_localization),
    )

    odom_to_lidar_odom_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_lidar_odom',
        arguments=[
            '--x', lidar_mount_x, '--y', lidar_mount_y, '--z', lidar_mount_z,
            '--roll', lidar_mount_roll,
            '--pitch', lidar_mount_pitch,
            '--yaw', lidar_mount_yaw,
            '--frame-id', 'odom', '--child-frame-id', 'lidar_odom',
        ],
        condition=IfCondition(start_localization),
    )

    tf_path_publisher_node = Node(
        package='fine_nav2d_bringup',
        executable='tf_path_publisher.py',
        name='base_link_path_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'target_frame': LaunchConfiguration('path_target_frame'),
            'source_frame': LaunchConfiguration('path_source_frame'),
            'path_topic': LaunchConfiguration('base_link_path_topic'),
            'publish_rate': ParameterValue(LaunchConfiguration('path_publish_rate'), value_type=float),
            'min_distance': ParameterValue(LaunchConfiguration('path_min_distance'), value_type=float),
            'max_poses': ParameterValue(LaunchConfiguration('path_max_poses'), value_type=int),
        }],
        condition=IfCondition(start_tf_path_publisher),
    )

    map_manager_node = Node(
        package='fn_map_manager',
        executable='fn_map_manager_node',
        name='map_manager',
        output='screen',
        parameters=[
            LaunchConfiguration('map_manager_params_file'),
            {
                'use_sim_time': use_sim_time,
                'working_mode': LaunchConfiguration('working_mode'),
            },
        ],
        condition=IfCondition(start_map_manager),
    )

    saved_map_publisher_node = Node(
        package='pcl_ros',
        executable='pcd_to_pointcloud',
        name='saved_map_publisher',
        output='screen',
        parameters=[{
            'file_name': LaunchConfiguration('viz_pcd_file_path'),
            'tf_frame': 'map',
            'publishing_period_ms': 1000,
        }],
        remappings=[('cloud_pcd', '/saved_map_cloud')],
        condition=IfCondition(start_saved_map_publisher),
    )

    pct_node = Node(
        package='fn_fine_pct',
        executable='fn_global_planner_node',
        name='pct_planner',
        output='screen',
        parameters=[
            LaunchConfiguration('pct_planner_params_file'),
            {
                'use_sim_time': use_sim_time,
                'pcd_file_path_': LaunchConfiguration('pcd_file_path'),
            },
        ],
        condition=IfCondition(start_pct),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        condition=IfCondition(start_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('start_driver', default_value='true'),
        DeclareLaunchArgument('start_fast_lio', default_value='true'),
        DeclareLaunchArgument('start_localization', default_value='true'),
        DeclareLaunchArgument('start_map_manager', default_value='false'),
        DeclareLaunchArgument('start_saved_map_publisher', default_value='false'),
        DeclareLaunchArgument('start_tf_path_publisher', default_value='true'),
        DeclareLaunchArgument('start_pct', default_value='false'),
        DeclareLaunchArgument('start_rviz', default_value='false'),
        DeclareLaunchArgument('global_localization_enable', default_value='false'),
        DeclareLaunchArgument('global_localization_source_type', default_value='1'),
        DeclareLaunchArgument('global_localization_topic', default_value='/global_localization'),
        DeclareLaunchArgument('global_localization_message_type', default_value='1'),
        DeclareLaunchArgument('publish_robot_description', default_value='true'),
        DeclareLaunchArgument('lidar_topic', default_value='/lidar'),
        DeclareLaunchArgument('imu_topic', default_value='/imu'),
        DeclareLaunchArgument('xfer_format', default_value='1'),
        DeclareLaunchArgument('publish_freq', default_value='20.0'),
        DeclareLaunchArgument('fast_lio_path_en', default_value='true'),
        DeclareLaunchArgument('fast_lio_map_en', default_value='false'),
        DeclareLaunchArgument('fast_lio_scan_publish_en', default_value='false'),
        DeclareLaunchArgument('fast_lio_scan_bodyframe_pub_en', default_value='false'),
        DeclareLaunchArgument('fast_lio_tf_en', default_value='false'),
        DeclareLaunchArgument('self_filtering_radius', default_value='0.3'),
        DeclareLaunchArgument('point_max_range', default_value='5.0'),
        DeclareLaunchArgument('path_target_frame', default_value='map'),
        DeclareLaunchArgument('path_source_frame', default_value='base_link'),
        DeclareLaunchArgument('base_link_path_topic', default_value='/base_link_path'),
        DeclareLaunchArgument('path_publish_rate', default_value='10.0'),
        DeclareLaunchArgument('path_min_distance', default_value='0.02'),
        DeclareLaunchArgument('path_max_poses', default_value='20000'),
        DeclareLaunchArgument('robot_description_path', default_value=default_urdf_path),
        DeclareLaunchArgument('lidar_mount_x', default_value='0.26786'),
        DeclareLaunchArgument('lidar_mount_y', default_value='0.0'),
        DeclareLaunchArgument('lidar_mount_z', default_value='0.07286'),
        DeclareLaunchArgument('lidar_mount_roll', default_value='0.0'),
        DeclareLaunchArgument('lidar_mount_pitch', default_value='0.7853981634'),
        DeclareLaunchArgument('lidar_mount_yaw', default_value='0.0'),
        DeclareLaunchArgument('working_mode', default_value='mapping'),
        DeclareLaunchArgument(
            'map_manager_params_file',
            default_value=os.path.join(config_dir, 'map_manager.yaml'),
        ),
        DeclareLaunchArgument(
            'pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map.pcd'),
        ),
        DeclareLaunchArgument(
            'viz_pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd'),
        ),
        DeclareLaunchArgument(
            'pct_planner_params_file',
            default_value=os.path.join(config_dir, 'pct_planner.yaml'),
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(rviz_dir, 'uika_mapping_path_only.rviz'),
        ),
        DeclareLaunchArgument(
            'map_file_path',
            default_value=default_raw_map_path,
        ),
        DeclareLaunchArgument(
            'livox_config_path',
            default_value=os.path.join(livox_dir, 'config', 'MID360_config.json'),
        ),
        DeclareLaunchArgument(
            'fast_lio_params_file',
            default_value=os.path.join(config_dir, 'fastlio_mid360_config.yaml'),
        ),
        robot_state_publisher_node,
        livox_driver_node,
        fast_lio_node,
        map_to_odom_node,
        odom_to_lidar_odom_node,
        odom_to_base_node,
        tf_path_publisher_node,
        map_manager_node,
        saved_map_publisher_node,
        TimerAction(period=2.0, actions=[pct_node]),
        TimerAction(period=4.0, actions=[rviz_node]),
    ])
