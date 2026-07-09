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
    config_dir = os.path.join(bringup_dir, 'config')
    pcd_dir = os.path.join(fast_lio_dir, 'PCD')
    rviz_dir = os.path.join(bringup_dir, 'rviz')
    default_urdf_path = os.path.join(bringup_dir, 'urdf', 'uika_lidar_mount.urdf')

    use_sim_time = LaunchConfiguration('use_sim_time')
    start_static_pose = LaunchConfiguration('start_static_pose')
    start_robot_description = LaunchConfiguration('start_robot_description')
    start_saved_map_publisher = LaunchConfiguration('start_saved_map_publisher')
    start_pct = LaunchConfiguration('start_pct')
    start_click_selector = LaunchConfiguration('start_click_selector')
    start_zone_manager = LaunchConfiguration('start_zone_manager')
    start_zone_selector = LaunchConfiguration('start_zone_selector')
    start_mission_manager = LaunchConfiguration('start_mission_manager')
    start_mission_executor = LaunchConfiguration('start_mission_executor')
    start_mission_path_follower = LaunchConfiguration('start_mission_path_follower')
    start_rviz = LaunchConfiguration('start_rviz')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'robot_description': ParameterValue(
                Command(['cat ', LaunchConfiguration('robot_description_path')]),
                value_type=str,
            ),
        }],
        condition=IfCondition(start_robot_description),
    )

    static_pose_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='dryrun_map_to_base_link',
        arguments=[
            '--x', LaunchConfiguration('start_x'),
            '--y', LaunchConfiguration('start_y'),
            '--z', LaunchConfiguration('start_z'),
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', LaunchConfiguration('start_yaw'),
            '--frame-id', 'map',
            '--child-frame-id', 'base_link',
        ],
        condition=IfCondition(start_static_pose),
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

    click_selector_node = Node(
        package='fn_fine_pct',
        executable='rviz_pct_goal_selector_node',
        name='rviz_pct_goal_selector',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'clicked_topic': '/clicked_point',
            'marker_topic': '/selection_markers',
            'start_topic': '/pct_start_point',
            'goal_topic': '/pct_goal_point',
            'action_name': '/compute_path_to_pose',
            'default_frame': 'map',
        }],
        condition=IfCondition(start_click_selector),
    )

    zone_manager_node = Node(
        package='fine_nav2d_bringup',
        executable='terrain_zone_manager.py',
        name='terrain_zone_manager',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'zones_file': LaunchConfiguration('terrain_zones_file'),
            'planned_path_topic': '/planned_path',
            'zone_marker_topic': '/terrain_zones',
            'segment_marker_topic': '/terrain_path_segments',
            'segments_topic': '/terrain_segments',
            'current_terrain_topic': '/current_terrain',
        }],
        condition=IfCondition(start_zone_manager),
    )

    zone_selector_node = Node(
        package='fine_nav2d_bringup',
        executable='terrain_zone_selector.py',
        name='terrain_zone_selector',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'zones_file': LaunchConfiguration('terrain_zones_file'),
            'frame_id': 'map',
            'clicked_topic': '/zone_clicked_point',
            'command_topic': '/zone_selector_command',
            'marker_topic': '/terrain_zone_selector_markers',
            'draft_marker_topic': '/terrain_zone_draft',
        }],
        condition=IfCondition(start_zone_selector),
    )

    mission_manager_node = Node(
        package='fine_nav2d_bringup',
        executable='terrain_mission_manager.py',
        name='terrain_mission_manager',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': LaunchConfiguration('mission_file'),
            'base_frame': 'base_link',
            'mission_marker_topic': '/mission_markers',
            'mission_route_topic': '/mission_route',
            'mission_plan_topic': '/mission_plan',
            'current_task_topic': '/current_task',
            'current_policy_topic': '/current_policy',
            'mission_status_topic': '/mission_status',
            'command_topic': '/mission_command',
            'auto_advance': ParameterValue(LaunchConfiguration('mission_auto_advance'), value_type=bool),
            'task_reach_radius': ParameterValue(LaunchConfiguration('mission_task_reach_radius'), value_type=float),
            'publish_full_route_line': False,
            'publish_connector_lines': True,
        }],
        condition=IfCondition(start_mission_manager),
    )

    mission_executor_node = Node(
        package='fine_nav2d_bringup',
        executable='terrain_mission_executor.py',
        name='terrain_mission_executor',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': LaunchConfiguration('mission_file'),
            'frame_id': 'map',
            'base_frame': 'base_link',
            'use_tf_pose': ParameterValue(LaunchConfiguration('mission_executor_use_tf_pose'), value_type=bool),
            'waypoint_reach_radius': ParameterValue(LaunchConfiguration('mission_executor_waypoint_reach_radius'), value_type=float),
            'dryrun_auto_play': ParameterValue(LaunchConfiguration('mission_executor_dryrun_auto_play'), value_type=bool),
            'dryrun_step_period': ParameterValue(LaunchConfiguration('mission_executor_dryrun_step_period'), value_type=float),
            'pose_topic': '/mission_executor_pose',
            'command_topic': '/mission_executor_command',
            'status_topic': '/mission_executor_status',
            'policy_topic': '/mission_executor_policy',
            'task_topic': '/mission_executor_task',
            'target_topic': '/mission_executor_target',
            'marker_topic': '/mission_executor_markers',
        }],
        condition=IfCondition(start_mission_executor),
    )

    mission_path_follower_node = Node(
        package='fine_nav2d_bringup',
        executable='mission_path_follower.py',
        name='mission_path_follower',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': LaunchConfiguration('mission_file'),
            'status_topic': '/mission_executor_status',
            'command_topic': '/mission_path_follower_command',
            'path_topic': '/mission_follow_path',
            'follow_path_action_name': '/follow_path',
            'controller_id': 'FollowPath',
            'goal_checker_id': 'general_goal_checker',
            'frame_id': 'map',
            'base_frame': 'base_link',
            'use_robot_pose_as_path_start': ParameterValue(
                LaunchConfiguration('mission_path_use_robot_pose_as_start'), value_type=bool),
            'auto_send_follow_path': ParameterValue(
                LaunchConfiguration('mission_path_auto_send_follow_path'), value_type=bool),
            'min_path_point_spacing': ParameterValue(
                LaunchConfiguration('mission_path_min_point_spacing'), value_type=float),
        }],
        condition=IfCondition(start_mission_path_follower),
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
        DeclareLaunchArgument('start_static_pose', default_value='true'),
        DeclareLaunchArgument('start_robot_description', default_value='true'),
        DeclareLaunchArgument('start_saved_map_publisher', default_value='true'),
        DeclareLaunchArgument('start_pct', default_value='true'),
        DeclareLaunchArgument('start_click_selector', default_value='true'),
        DeclareLaunchArgument('start_zone_manager', default_value='true'),
        DeclareLaunchArgument('start_zone_selector', default_value='true'),
        DeclareLaunchArgument('start_mission_manager', default_value='true'),
        DeclareLaunchArgument('start_mission_executor', default_value='true'),
        DeclareLaunchArgument('start_mission_path_follower', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('start_x', default_value='0.0'),
        DeclareLaunchArgument('start_y', default_value='0.0'),
        DeclareLaunchArgument('start_z', default_value='0.0'),
        DeclareLaunchArgument('start_yaw', default_value='0.0'),
        DeclareLaunchArgument('robot_description_path', default_value=default_urdf_path),
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
            'terrain_zones_file',
            default_value=os.path.join(config_dir, 'uika_terrain_zones.yaml'),
        ),
        DeclareLaunchArgument(
            'mission_file',
            default_value=os.path.join(config_dir, 'uika_obstacle_mission.yaml'),
        ),
        DeclareLaunchArgument('mission_auto_advance', default_value='false'),
        DeclareLaunchArgument('mission_task_reach_radius', default_value='0.45'),
        DeclareLaunchArgument('mission_executor_use_tf_pose', default_value='true'),
        DeclareLaunchArgument('mission_executor_waypoint_reach_radius', default_value='0.25'),
        DeclareLaunchArgument('mission_executor_dryrun_auto_play', default_value='false'),
        DeclareLaunchArgument('mission_executor_dryrun_step_period', default_value='0.35'),
        DeclareLaunchArgument('mission_path_use_robot_pose_as_start', default_value='true'),
        DeclareLaunchArgument('mission_path_auto_send_follow_path', default_value='false'),
        DeclareLaunchArgument('mission_path_min_point_spacing', default_value='0.02'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(rviz_dir, 'complex_terrain_nav.rviz'),
        ),
        robot_state_publisher_node,
        static_pose_node,
        saved_map_publisher_node,
        TimerAction(period=1.0, actions=[pct_node]),
        TimerAction(period=1.5, actions=[click_selector_node]),
        TimerAction(period=1.7, actions=[zone_manager_node]),
        TimerAction(period=1.9, actions=[zone_selector_node]),
        TimerAction(period=2.1, actions=[mission_manager_node]),
        TimerAction(period=2.3, actions=[mission_executor_node]),
        TimerAction(period=2.5, actions=[mission_path_follower_node]),
        TimerAction(period=3.0, actions=[rviz_node]),
    ])
