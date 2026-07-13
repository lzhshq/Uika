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
    share = get_package_share_directory("point_lio")

    driver = LaunchConfiguration("driver")
    map_file = LaunchConfiguration("map")
    mission_file = LaunchConfiguration("mission_file")
    point_lio_cfg = LaunchConfiguration("point_lio_cfg_dir")
    relocalization_params = LaunchConfiguration("relocalization_params_file")
    controller_params = LaunchConfiguration("controller_params_file")
    bridge_params = LaunchConfiguration("bridge_params_file")
    controller_dry_run = LaunchConfiguration("controller_dry_run")
    enable_bridge = LaunchConfiguration("enable_bridge")
    bridge_dry_run = LaunchConfiguration("bridge_dry_run")
    output_topic = LaunchConfiguration("output_topic")

    relocalization_launch = os.path.join(
        share, "launch", "mid360_relocalization_bringup.launch.py"
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("driver", default_value="true"),
            DeclareLaunchArgument(
                "map",
                default_value=os.path.join(share, "maps", "changdi_2_hq.pcd"),
            ),
            DeclareLaunchArgument(
                "mission_file",
                default_value=os.path.join(
                    share, "config", "changdi_competition_mission.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "point_lio_cfg_dir",
                default_value=os.path.join(share, "config", "avia.yaml"),
            ),
            DeclareLaunchArgument(
                "relocalization_params_file",
                default_value=os.path.join(
                    share, "config", "fixed_start_relocalization.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "controller_params_file",
                default_value=os.path.join(
                    share, "config", "fixed_path_controller.yaml"
                ),
            ),
            DeclareLaunchArgument(
                "bridge_params_file",
                default_value=os.path.join(
                    share, "config", "cmd_vel_safety_bridge.yaml"
                ),
            ),
            DeclareLaunchArgument("controller_dry_run", default_value="true"),
            DeclareLaunchArgument("enable_bridge", default_value="true"),
            DeclareLaunchArgument("bridge_dry_run", default_value="true"),
            DeclareLaunchArgument("output_topic", default_value="/cmd_vel"),

            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(relocalization_launch),
                launch_arguments={
                    "driver": driver,
                    "rviz": "false",
                    "map": map_file,
                    "point_lio_cfg_dir": point_lio_cfg,
                    "relocalization_params_file": relocalization_params,
                    "continuous_shadow": "false",
                }.items(),
            ),
            TimerAction(
                period=6.0,
                actions=[
                    Node(
                        package="point_lio",
                        executable="course_mission_preview.py",
                        name="competition_route_publisher",
                        output="screen",
                        parameters=[
                            {
                                "config_file": mission_file,
                                "route_topic": "/competition_route",
                                "publish_markers": False,
                                "publish_period_s": 0.0,
                            }
                        ],
                    ),
                    Node(
                        package="point_lio",
                        executable="fixed_path_controller.py",
                        name="competition_path_controller",
                        output="screen",
                        parameters=[
                            controller_params,
                            {
                                "route_topic": "/competition_route",
                                "dry_run": ParameterValue(
                                    controller_dry_run, value_type=bool
                                ),
                            },
                        ],
                    ),
                    Node(
                        package="point_lio",
                        executable="cmd_vel_safety_bridge.py",
                        name="competition_cmd_vel_safety_bridge",
                        output="screen",
                        condition=IfCondition(enable_bridge),
                        parameters=[
                            bridge_params,
                            {
                                "dry_run": ParameterValue(
                                    bridge_dry_run, value_type=bool
                                ),
                                "input_topic": "/nav_cmd_vel_test",
                                "output_topic": output_topic,
                            },
                        ],
                    ),
                ],
            ),
        ]
    )
