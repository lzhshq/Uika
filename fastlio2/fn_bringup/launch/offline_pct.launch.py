import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    bringup_dir = get_package_share_directory('fine_nav2d_bringup')
    fast_lio_dir = get_package_share_directory('fast_lio')
    config_dir = os.path.join(bringup_dir, 'config')
    pcd_dir = os.path.join(fast_lio_dir, 'PCD')
    rviz_dir = os.path.join(bringup_dir, 'rviz')

    use_sim_time = LaunchConfiguration('use_sim_time')
    pct_planner_params_file = LaunchConfiguration('pct_planner_params_file')
    pcd_file_path = LaunchConfiguration('pcd_file_path')
    viz_pcd_file_path = LaunchConfiguration('viz_pcd_file_path')
    start_saved_map_publisher = LaunchConfiguration('start_saved_map_publisher')
    start_rviz = LaunchConfiguration('start_rviz')
    rviz_config = LaunchConfiguration('rviz_config')

    pct_node = Node(
        package='fn_fine_pct',
        executable='fn_global_planner_node',
        name='pct_planner',
        output='screen',
        parameters=[
            pct_planner_params_file,
            {
                'use_sim_time': use_sim_time,
                'pcd_file_path_': pcd_file_path,
            },
        ],
    )

    saved_map_publisher_node = Node(
        package='pcl_ros',
        executable='pcd_to_pointcloud',
        name='saved_map_publisher',
        output='screen',
        parameters=[{
            'file_name': viz_pcd_file_path,
            'tf_frame': 'map',
            'publishing_period_ms': 1000,
        }],
        remappings=[('cloud_pcd', '/saved_map_cloud')],
        condition=IfCondition(start_saved_map_publisher),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        condition=IfCondition(start_rviz),
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument(
            'pct_planner_params_file',
            default_value=os.path.join(config_dir, 'pct_planner.yaml'),
        ),
        DeclareLaunchArgument(
            'pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map.pcd'),
        ),
        DeclareLaunchArgument(
            'viz_pcd_file_path',
            default_value=os.path.join(pcd_dir, 'uika_real_map_mount_x0313_zm006_p90_map_viz_stride5.pcd'),
        ),
        DeclareLaunchArgument('start_saved_map_publisher', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument(
            'rviz_config',
            default_value=os.path.join(rviz_dir, 'complex_terrain_nav.rviz'),
        ),
        saved_map_publisher_node,
        pct_node,
        rviz_node,
    ])
