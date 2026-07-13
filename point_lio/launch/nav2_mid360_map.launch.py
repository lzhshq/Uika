import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_dir = get_package_share_directory('point_lio')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    params_file = LaunchConfiguration('params_file')
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    rviz = LaunchConfiguration('rviz')
    cmd_vel_topic = LaunchConfiguration('cmd_vel_topic')
    enable_cmd_bridge = LaunchConfiguration('enable_cmd_bridge')
    cmd_bridge_dry_run = LaunchConfiguration('cmd_bridge_dry_run')
    cmd_bridge_params_file = LaunchConfiguration('cmd_bridge_params_file')
    base_cmd_topic = LaunchConfiguration('base_cmd_topic')
    enable_route_planner = LaunchConfiguration('enable_route_planner')

    lifecycle_nodes = [
        'map_server',
        'controller_server',
        'planner_server',
        'smoother_server',
        'behavior_server',
        'bt_navigator',
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_dir, 'config', 'nav2_mid360_map_params.yaml'),
            description='Full path to the Nav2 parameters file',
        ),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_dir, 'maps', 'stage6_test.yaml'),
            description='Full path to a map YAML file',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='False',
            description='Use /clock if true',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Start RViz with the Nav2 default view',
        ),
        DeclareLaunchArgument(
            'cmd_vel_topic',
            default_value='/nav_cmd_vel_test',
            description='Safe output topic for Nav2 velocity commands',
        ),
        DeclareLaunchArgument(
            'enable_cmd_bridge',
            default_value='false',
            description='Start the limited bridge from Nav2 test cmd_vel to the real base topic.',
        ),
        DeclareLaunchArgument(
            'cmd_bridge_dry_run',
            default_value='true',
            description='If true, bridge only publishes debug output and does not publish to base_cmd_topic.',
        ),
        DeclareLaunchArgument(
            'cmd_bridge_params_file',
            default_value=os.path.join(pkg_dir, 'config', 'cmd_vel_safety_bridge.yaml'),
            description='Full path to cmd_vel safety bridge parameters',
        ),
        DeclareLaunchArgument(
            'base_cmd_topic',
            default_value='/cmd_vel',
            description='Real robot base command topic used by the bridge when dry_run is false.',
        ),
        DeclareLaunchArgument(
            'enable_route_planner',
            default_value='true',
            description='Collect RViz route poses and publish one continuous route path.',
        ),

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}, {'yaml_filename': map_file}],
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=[('/cmd_vel', cmd_vel_topic)],
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),
        Node(
            package='nav2_smoother',
            executable='smoother_server',
            name='smoother_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
            remappings=[('/cmd_vel', cmd_vel_topic)],
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[params_file, {'use_sim_time': use_sim_time}],
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart': True},
                {'node_names': lifecycle_nodes},
            ],
        ),
        Node(
            condition=IfCondition(enable_cmd_bridge),
            package='point_lio',
            executable='cmd_vel_safety_bridge.py',
            name='cmd_vel_safety_bridge',
            output='screen',
            parameters=[
                cmd_bridge_params_file,
                {
                    'input_topic': cmd_vel_topic,
                    'output_topic': base_cmd_topic,
                    'dry_run': cmd_bridge_dry_run,
                },
            ],
        ),
        Node(
            condition=IfCondition(enable_route_planner),
            package='point_lio',
            executable='route_pose_planner.py',
            name='route_pose_planner',
            output='screen',
        ),
        Node(
            condition=IfCondition(rviz),
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=[
                '-d',
                os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz'),
            ],
            parameters=[{'use_sim_time': use_sim_time}],
        ),
    ])
