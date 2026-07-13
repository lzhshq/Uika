import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory("point_lio")
    config_file = LaunchConfiguration("config_file")
    map_yaml = LaunchConfiguration("map_yaml")
    start_rviz = LaunchConfiguration("start_rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "config_file",
                default_value=os.path.join(
                    share, "config", "changdi_map_origin_half_mission.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "map_yaml",
                default_value=os.path.join(share, "maps", "changdi_2_nav_h5.yaml"),
            ),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            Node(
                package="nav2_map_server",
                executable="map_server",
                name="course_map_server",
                output="screen",
                parameters=[{"yaml_filename": map_yaml}],
            ),
            Node(
                package="nav2_lifecycle_manager",
                executable="lifecycle_manager",
                name="course_map_lifecycle_manager",
                output="screen",
                parameters=[
                    {
                        "autostart": True,
                        "node_names": ["course_map_server"],
                    }
                ],
            ),
            Node(
                package="point_lio",
                executable="course_mission_preview.py",
                name="course_mission_preview",
                output="screen",
                parameters=[{"config_file": config_file}],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="course_preview_rviz",
                output="screen",
                arguments=[
                    "-d",
                    os.path.join(share, "rviz_cfg", "course_mission_preview.rviz"),
                ],
                condition=IfCondition(start_rviz),
            ),
        ]
    )
