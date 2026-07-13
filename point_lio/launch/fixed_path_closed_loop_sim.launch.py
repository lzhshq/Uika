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
    controller_params = LaunchConfiguration("controller_params")
    start_rviz = LaunchConfiguration("start_rviz")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "route_file",
                default_value=os.path.join(
                    share_dir, "config", "raogan_15m_slalom.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "controller_params",
                default_value=os.path.join(
                    share_dir, "config", "fixed_path_sim_controller.yaml"
                ),
            ),
            DeclareLaunchArgument("start_rviz", default_value="true"),
            Node(
                package="point_lio",
                executable="slalom_route_preview.py",
                name="simulation_route_publisher",
                output="screen",
                parameters=[
                    {
                        "route_file": route_file,
                        "route_topic": "/slalom_route",
                        "marker_topic": "/slalom_markers",
                        "publish_markers": True,
                        "publish_period_s": 0.0,
                    }
                ],
            ),
            Node(
                package="point_lio",
                executable="fixed_path_controller.py",
                name="fixed_path_controller",
                output="screen",
                parameters=[controller_params, {"dry_run": True}],
            ),
            Node(
                package="point_lio",
                executable="fixed_path_simulator.py",
                name="fixed_path_simulator",
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="fixed_path_simulation_rviz",
                output="screen",
                arguments=[
                    "-d",
                    os.path.join(
                        share_dir, "rviz_cfg", "fixed_path_closed_loop_sim.rviz"
                    ),
                ],
                condition=IfCondition(start_rviz),
            ),
        ]
    )
