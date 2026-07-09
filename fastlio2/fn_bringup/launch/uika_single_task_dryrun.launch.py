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
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    config_dir = os.path.join(bringup_dir, 'config')
    launch_dir = os.path.join(bringup_dir, 'launch')
    rviz_dir = os.path.join(bringup_dir, 'rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    task_id = LaunchConfiguration('task_id')
    mission_file = LaunchConfiguration('mission_file')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')
    odom_topic = LaunchConfiguration('odom_topic')
    initial_x = LaunchConfiguration('initial_x')
    initial_y = LaunchConfiguration('initial_y')
    initial_z = LaunchConfiguration('initial_z')
    initial_yaw = LaunchConfiguration('initial_yaw')
    start_rviz = LaunchConfiguration('start_rviz')
    start_runner = LaunchConfiguration('start_runner')

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
        }.items(),
    )

    task_runner = Node(
        package='fine_nav2d_bringup',
        executable='single_mission_task_runner.py',
        name='single_mission_task_runner',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'mission_file': mission_file,
            'task_id': task_id,
            'frame_id': 'map',
            'base_frame': 'base_link',
            'path_topic': '/mission_follow_path',
            'status_topic': '/single_task_runner_status',
            'command_topic': '/single_task_runner_command',
            'follow_path_action_name': '/follow_path',
            'controller_id': 'FollowPath',
            'goal_checker_id': 'general_goal_checker',
            'auto_start': True,
            'use_robot_pose_as_path_start': ParameterValue(
                LaunchConfiguration('use_robot_pose_as_path_start'), value_type=bool),
            'keep_alive_after_result': ParameterValue(
                LaunchConfiguration('keep_alive_after_result'), value_type=bool),
            'min_path_point_spacing': ParameterValue(
                LaunchConfiguration('min_path_point_spacing'), value_type=float),
        }],
        condition=IfCondition(start_runner),
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rviz_config')],
        condition=IfCondition(start_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('task_id', default_value='pole_slalom'),
        DeclareLaunchArgument(
            'mission_file',
            default_value=os.path.join(config_dir, 'uika_obstacle_mission_stair_frame.yaml'),
        ),
        DeclareLaunchArgument('cmd_vel_topic', default_value='/cmd_vel_test'),
        DeclareLaunchArgument('odom_topic', default_value='/dryrun_odom'),
        DeclareLaunchArgument('initial_x', default_value='6.30'),
        DeclareLaunchArgument('initial_y', default_value='-0.175'),
        DeclareLaunchArgument('initial_z', default_value='-0.40'),
        DeclareLaunchArgument('initial_yaw', default_value='0.0'),
        DeclareLaunchArgument('use_robot_pose_as_path_start', default_value='false'),
        DeclareLaunchArgument('keep_alive_after_result', default_value='true'),
        DeclareLaunchArgument('min_path_point_spacing', default_value='0.02'),
        DeclareLaunchArgument('start_runner', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(rviz_dir, 'complex_terrain_nav.rviz'),
        ),
        dryrun_nav2,
        TimerAction(period=1.0, actions=[rviz]),
        TimerAction(period=3.0, actions=[task_runner]),
    ])
