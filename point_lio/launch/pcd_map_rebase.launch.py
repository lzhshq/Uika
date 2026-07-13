from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    input_pcd = LaunchConfiguration('input_pcd')
    output_pcd = LaunchConfiguration('output_pcd')
    use_rviz = LaunchConfiguration('rviz')
    publish_period_ms = LaunchConfiguration('publish_period_ms')
    package_dir = get_package_share_directory('point_lio')

    pcd_publisher = Node(
        package='pcl_ros',
        executable='pcd_to_pointcloud',
        name='pcd_rebase_map_publisher',
        parameters=[{
            'file_name': input_pcd,
            'tf_frame': 'map',
            'publishing_period_ms': ParameterValue(
                publish_period_ms, value_type=int),
        }],
        remappings=[('cloud_pcd', '/cloud_registered')],
        output='screen',
    )

    selector = Node(
        package='point_lio',
        executable='pcd_map_rebase.py',
        name='pcd_map_rebase_selector',
        arguments=[
            input_pcd,
            '--output', output_pcd,
            '--interactive',
            '--topic', '/clicked_point',
            '--frame', 'map',
        ],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz_pcd_map_rebase',
        arguments=[
            '-d',
            PathJoinSubstitution([package_dir, 'rviz_cfg', 'loam_livox.rviz']),
        ],
        condition=IfCondition(use_rviz),
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'input_pcd',
            description='Original Point-LIO PCD map.'),
        DeclareLaunchArgument(
            'output_pcd',
            description='Rebased PCD output path; must not already exist.'),
        DeclareLaunchArgument(
            'rviz',
            default_value='false',
            description='Start RViz in this process.'),
        DeclareLaunchArgument(
            'publish_period_ms',
            default_value='10000',
            description='Republish interval for the full offline PCD.'),
        pcd_publisher,
        selector,
        rviz,
    ])
