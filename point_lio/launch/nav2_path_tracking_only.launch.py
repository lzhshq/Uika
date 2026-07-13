import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = get_package_share_directory("point_lio")
    params_file = LaunchConfiguration("params_file")
    bridge_params_file = LaunchConfiguration("bridge_params_file")
    route_file = LaunchConfiguration("route_file")
    cmd_vel_topic = LaunchConfiguration("cmd_vel_topic")
    output_topic = LaunchConfiguration("output_topic")
    enable_bridge = LaunchConfiguration("enable_bridge")
    bridge_dry_run = LaunchConfiguration("bridge_dry_run")
    use_sim_time = LaunchConfiguration("use_sim_time")

    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=os.path.join(
                package_dir, "config", "nav2_mid360_map_params.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "bridge_params_file",
            default_value=os.path.join(
                package_dir, "config", "cmd_vel_safety_bridge.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "route_file",
            default_value=os.path.join(package_dir, "maps", "active_route.json"),
        ),
        DeclareLaunchArgument("cmd_vel_topic", default_value="/nav_cmd_vel_test"),
        DeclareLaunchArgument("output_topic", default_value="/cmd_vel"),
        DeclareLaunchArgument("enable_bridge", default_value="false"),
        DeclareLaunchArgument("bridge_dry_run", default_value="true"),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="pointcloud_to_laserscan",
            executable="pointcloud_to_laserscan_node",
            name="pointcloud_to_laserscan",
            output="screen",
            remappings=[
                ("cloud_in", "/cloud_registered_body"),
                ("scan", "/scan"),
            ],
            parameters=[{
                "use_sim_time": use_sim_time,
                "target_frame": "base_link",
                "transform_tolerance": 0.5,
                "min_height": -0.18,
                "max_height": 0.35,
                "angle_min": -3.14159,
                "angle_max": 3.14159,
                "angle_increment": 0.0087,
                "scan_time": 0.1,
                "range_min": 0.4,
                "range_max": 5.0,
                "use_inf": True,
                "inf_epsilon": 1.0,
            }],
        ),
        Node(
            package="nav2_controller",
            executable="controller_server",
            name="controller_server",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}],
            remappings=[("/cmd_vel", cmd_vel_topic)],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_path_tracking",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["controller_server"],
            }],
        ),
        Node(
            package="point_lio",
            executable="route_path_follower.py",
            name="route_path_follower",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "route_file": route_file,
                "stop_topic": cmd_vel_topic,
            }],
        ),
        Node(
            condition=IfCondition(enable_bridge),
            package="point_lio",
            executable="cmd_vel_safety_bridge.py",
            name="cmd_vel_safety_bridge",
            output="screen",
            parameters=[
                bridge_params_file,
                {
                    "dry_run": bridge_dry_run,
                    "input_topic": cmd_vel_topic,
                    "output_topic": output_topic,
                },
            ],
        ),
    ])
