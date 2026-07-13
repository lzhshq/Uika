import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share_dir = get_package_share_directory("point_lio")

    route_file = LaunchConfiguration("route_file")
    pcd_file = LaunchConfiguration("pcd_file")
    route_topic = LaunchConfiguration("route_topic")
    marker_topic = LaunchConfiguration("marker_topic")
    start_map_publisher = LaunchConfiguration("start_map_publisher")
    start_rviz = LaunchConfiguration("start_rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "route_file",
                default_value=os.path.join(share_dir, "config", "raogan_15m_slalom.yaml"),
            ),
            DeclareLaunchArgument(
                "pcd_file",
                default_value=os.path.join(share_dir, "maps", "raogan_15m.pcd"),
            ),
            DeclareLaunchArgument("start_map_publisher", default_value="true"),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            DeclareLaunchArgument("route_topic", default_value="/slalom_route"),
            DeclareLaunchArgument("marker_topic", default_value="/slalom_markers"),
            Node(
                package="pcl_ros",
                executable="pcd_to_pointcloud",
                name="slalom_map_publisher",
                output="screen",
                parameters=[
                    {
                        "file_name": pcd_file,
                        "tf_frame": "map",
                        "publishing_period_ms": 3000,
                    }
                ],
                remappings=[("cloud_pcd", "/offline_map_cloud")],
                condition=IfCondition(start_map_publisher),
            ),
            Node(
                package="point_lio",
                executable="slalom_route_preview.py",
                name="slalom_route_preview",
                output="screen",
                parameters=[
                    {
                        "route_file": route_file,
                        "route_topic": route_topic,
                        "marker_topic": marker_topic,
                    }
                ],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="slalom_preview_rviz",
                output="screen",
                arguments=[
                    "-d",
                    os.path.join(share_dir, "rviz_cfg", "slalom_route_preview.rviz"),
                ],
                condition=IfCondition(start_rviz),
            ),
        ]
    )
