import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    fast_lio_dir = get_package_share_directory('fast_lio')
    config_dir = os.path.join(bringup_dir, 'config')
    launch_dir = os.path.join(bringup_dir, 'launch')
    rviz_dir = os.path.join(bringup_dir, 'rviz')
    pcd_dir = os.path.join(fast_lio_dir, 'PCD')
    default_urdf_path = os.path.join(bringup_dir, 'urdf', 'uika_lidar_mount.urdf')

    use_sim_time = LaunchConfiguration('use_sim_time')
    mission_file = LaunchConfiguration('mission_file')
    mission_initial_task_id = LaunchConfiguration('mission_initial_task_id')
    mission_initial_task_index = LaunchConfiguration('mission_initial_task_index')
    mission_initial_waypoint_index = LaunchConfiguration('mission_initial_waypoint_index')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')
    odom_topic = LaunchConfiguration('odom_topic')
    initial_x = LaunchConfiguration('initial_x')
    initial_y = LaunchConfiguration('initial_y')
    initial_z = LaunchConfiguration('initial_z')
    initial_yaw = LaunchConfiguration('initial_yaw')

    dryrun_nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(launch_dir, 'uika_nav2_mppi_dryrun.launch.py')),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'cmd_vel_topic': cmd_vel_topic,
            'odom_topic': odom_topic,
            'initial_x': initial_x,
            'initial_y': initial_y,
            'initial_z': initial_z,
            'initial_yaw': initial_yaw,
            'log_level': LaunchConfiguration('nav2_log_level'),
        }.items(),
    )

    robot_state_publisher = Node(
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
        condition=IfCondition(LaunchConfiguration('start_robot_description')),
    )

    saved_map_publisher = Node(
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
        condition=IfCondition(LaunchConfiguration('start_saved_map_publisher')),
    )

    mission_executor = Node(
        package='fine_nav2d_bringup',
        executable='terrain_mission_executor.py',
        name='terrain_mission_executor',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': mission_file,
            'frame_id': 'map',
            'base_frame': 'base_link',
            'use_tf_pose': True,
            'initial_task_id': mission_initial_task_id,
            'initial_task_index': ParameterValue(mission_initial_task_index, value_type=int),
            'initial_waypoint_index': ParameterValue(mission_initial_waypoint_index, value_type=int),
            'waypoint_reach_radius': ParameterValue(
                LaunchConfiguration('mission_executor_waypoint_reach_radius'), value_type=float),
            'dryrun_auto_play': False,
            'pose_topic': '/mission_executor_pose',
            'command_topic': '/mission_executor_command',
            'status_topic': '/mission_executor_status',
            'policy_topic': '/mission_executor_policy',
            'task_topic': '/mission_executor_task',
            'target_topic': '/mission_executor_target',
            'marker_topic': '/mission_executor_markers',
        }],
        condition=IfCondition(LaunchConfiguration('start_mission_executor')),
    )

    mission_path_follower = Node(
        package='fine_nav2d_bringup',
        executable='mission_path_follower.py',
        name='mission_path_follower',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': mission_file,
            'status_topic': '/mission_executor_status',
            'command_topic': '/mission_path_follower_command',
            'path_topic': '/mission_follow_path',
            'follow_path_action_name': '/follow_path',
            'controller_id': 'FollowPath',
            'goal_checker_id': 'general_goal_checker',
            'frame_id': 'map',
            'base_frame': 'base_link',
            'use_robot_pose_as_path_start': True,
            'auto_send_follow_path': ParameterValue(
                LaunchConfiguration('mission_path_auto_send_follow_path'), value_type=bool),
            'min_path_point_spacing': ParameterValue(
                LaunchConfiguration('mission_path_min_point_spacing'), value_type=float),
        }],
        condition=IfCondition(LaunchConfiguration('start_mission_path_follower')),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        condition=IfCondition(LaunchConfiguration('start_rviz')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'mission_file',
            default_value=os.path.join(config_dir, 'uika_obstacle_mission_stair_frame.yaml'),
        ),
        DeclareLaunchArgument('mission_initial_task_id', default_value='pole_slalom'),
        DeclareLaunchArgument('mission_initial_task_index', default_value='-1'),
        DeclareLaunchArgument('mission_initial_waypoint_index', default_value='0'),
        DeclareLaunchArgument('mission_executor_waypoint_reach_radius', default_value='0.25'),
        DeclareLaunchArgument('mission_path_auto_send_follow_path', default_value='true'),
        DeclareLaunchArgument('mission_path_min_point_spacing', default_value='0.02'),
        DeclareLaunchArgument('cmd_vel_topic', default_value='/cmd_vel_test'),
        DeclareLaunchArgument('odom_topic', default_value='/dryrun_odom'),
        DeclareLaunchArgument('initial_x', default_value='6.30'),
        DeclareLaunchArgument('initial_y', default_value='-0.175'),
        DeclareLaunchArgument('initial_z', default_value='-0.40'),
        DeclareLaunchArgument('initial_yaw', default_value='0.0'),
        DeclareLaunchArgument('nav2_log_level', default_value='info'),
        DeclareLaunchArgument('start_robot_description', default_value='true'),
        DeclareLaunchArgument('start_saved_map_publisher', default_value='false'),
        DeclareLaunchArgument('start_mission_executor', default_value='true'),
        DeclareLaunchArgument('start_mission_path_follower', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('robot_description_path', default_value=default_urdf_path),
        DeclareLaunchArgument(
            'viz_pcd_file_path',
            default_value=os.path.join(pcd_dir, 'scene_terrain_map_stair_frame_viz_stride5_cropped.pcd'),
        ),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(rviz_dir, 'complex_terrain_nav.rviz'),
        ),
        dryrun_nav2,
        robot_state_publisher,
        saved_map_publisher,
        TimerAction(period=2.0, actions=[mission_executor]),
        TimerAction(period=2.4, actions=[mission_path_follower]),
        TimerAction(period=3.0, actions=[rviz]),
    ])
