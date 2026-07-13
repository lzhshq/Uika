import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node


def generate_launch_description():
    package_dir = get_package_share_directory("point_lio")
    params_file = LaunchConfiguration("params_file")
    map_file = LaunchConfiguration("map")
    route_file = LaunchConfiguration("route_file")
    use_sim_time = LaunchConfiguration("use_sim_time")

    return LaunchDescription([
        DeclareLaunchArgument(
            "params_file",
            default_value=os.path.join(
                package_dir, "config", "nav2_mid360_map_params.yaml"
            ),
        ),
        DeclareLaunchArgument(
            "map",
            default_value=os.path.join(package_dir, "maps", "raogan_15m.yaml"),
        ),
        DeclareLaunchArgument(
            "route_file",
            default_value=os.path.join(package_dir, "maps", "active_route.json"),
        ),
        DeclareLaunchArgument("use_sim_time", default_value="false"),
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[
                params_file,
                {"use_sim_time": use_sim_time, "yaml_filename": map_file},
            ],
        ),
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            output="screen",
            parameters=[params_file, {"use_sim_time": use_sim_time}],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_global_planning",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "autostart": True,
                "node_names": ["map_server", "planner_server"],
            }],
        ),
        Node(
            package="point_lio",
            executable="route_pose_planner.py",
            name="route_pose_planner",
            output="screen",
            parameters=[{
                "use_sim_time": use_sim_time,
                "route_file": route_file,
            }],
        ),
    ])
