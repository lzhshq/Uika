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
    controller_params = LaunchConfiguration("controller_params")
    bridge_params = LaunchConfiguration("bridge_params")
    controller_dry_run = LaunchConfiguration("controller_dry_run")
    bridge_dry_run = LaunchConfiguration("bridge_dry_run")
    enable_bridge = LaunchConfiguration("enable_bridge")
    output_topic = LaunchConfiguration("output_topic")

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
                    share_dir, "config", "fixed_path_controller.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "bridge_params",
                default_value=os.path.join(
                    share_dir, "config", "cmd_vel_safety_bridge.yaml"
                ),
            ),
            DeclareLaunchArgument("controller_dry_run", default_value="true"),
            DeclareLaunchArgument("bridge_dry_run", default_value="true"),
            DeclareLaunchArgument("enable_bridge", default_value="true"),
            DeclareLaunchArgument("output_topic", default_value="/cmd_vel"),
            Node(
                package="point_lio",
                executable="slalom_route_preview.py",
                name="fixed_route_publisher",
                output="screen",
                parameters=[
                    {
                        "route_file": route_file,
                        "route_topic": "/slalom_route",
                        "marker_topic": "/slalom_markers",
                        "publish_markers": False,
                        "publish_period_s": 0.0,
                    }
                ],
            ),
            Node(
                package="point_lio",
                executable="fixed_path_controller.py",
                name="fixed_path_controller",
                output="screen",
                parameters=[
                    controller_params,
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
                    bridge_params,
                    {
                        "dry_run": ParameterValue(bridge_dry_run, value_type=bool),
                        "input_topic": "/nav_cmd_vel_test",
                        "output_topic": output_topic,
                    },
                ],
                condition=IfCondition(enable_bridge),
            ),
        ]
    )
