import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    share_dir = get_package_share_directory("point_lio")
    route_file = LaunchConfiguration("route_file")
    controller_dry_run = LaunchConfiguration("controller_dry_run")
    bridge_dry_run = LaunchConfiguration("bridge_dry_run")
    enable_bridge = LaunchConfiguration("enable_bridge")

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "route_file",
                default_value=os.path.join(
                    share_dir, "config", "raogan_15m_slalom.yaml"
                ),
            ),
            DeclareLaunchArgument("controller_dry_run", default_value="true"),
            DeclareLaunchArgument("bridge_dry_run", default_value="true"),
            DeclareLaunchArgument("enable_bridge", default_value="false"),
            Node(
                package="point_lio",
                executable="slalom_route_preview.py",
                name="relative_path_template_publisher",
                output="screen",
                parameters=[
                    {
                        "route_file": route_file,
                        "route_topic": "/relative_path/template",
                        "publish_markers": False,
                        "publish_period_s": 0.0,
                    }
                ],
            ),
            Node(
                package="point_lio",
                executable="relative_path_executor.py",
                name="relative_path_executor",
                output="screen",
            ),
            Node(
                package="point_lio",
                executable="fixed_path_controller.py",
                name="fixed_path_controller",
                output="screen",
                parameters=[
                    os.path.join(
                        share_dir, "config", "relative_path_controller.yaml"
                    ),
                    {
                        "dry_run": ParameterValue(
                            controller_dry_run, value_type=bool
                        )
                    },
                ],
            ),
            Node(
                package="point_lio",
                executable="cmd_vel_safety_bridge.py",
                name="cmd_vel_safety_bridge",
                output="screen",
                parameters=[
                    os.path.join(
                        share_dir, "config", "cmd_vel_safety_bridge.yaml"
                    ),
                    {
                        "dry_run": ParameterValue(bridge_dry_run, value_type=bool),
                        "input_topic": "/nav_cmd_vel_test",
                        "output_topic": "/cmd_vel",
                    },
                ],
                condition=IfCondition(enable_bridge),
            ),
        ]
    )
