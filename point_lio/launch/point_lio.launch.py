import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    use_rviz = LaunchConfiguration('rviz')
    use_scan = LaunchConfiguration('scan')
    publish_cloud = LaunchConfiguration('publish_cloud')
    rviz_config = LaunchConfiguration('rviz_config')
    use_sim_time = LaunchConfiguration('use_sim_time')
    pcd_save = LaunchConfiguration('pcd_save')
    pcd_save_interval = LaunchConfiguration('pcd_save_interval')
    pcd_save_file = LaunchConfiguration('pcd_save_file')
    point_lio_cfg = LaunchConfiguration('point_lio_cfg_dir')
    publish_map_to_odom = LaunchConfiguration('publish_map_to_odom')
    lio_world_parent_frame = LaunchConfiguration('lio_world_parent_frame')
    path_en = LaunchConfiguration('path_en')

    declare_namespace = DeclareLaunchArgument(
        'namespace', default_value='',
        description='Namespace for the node')

    declare_rviz = DeclareLaunchArgument(
        'rviz', default_value='true',
        description='Flag to launch RViz.')

    declare_scan = DeclareLaunchArgument(
        'scan', default_value='true',
        description='Convert Point-LIO body-frame cloud to LaserScan.')

    declare_publish_cloud = DeclareLaunchArgument(
        'publish_cloud', default_value='true',
        description='Publish registered point clouds. Disable for low-overhead mapping.')

    declare_rviz_config = DeclareLaunchArgument(
        'rviz_config',
        default_value=PathJoinSubstitution([
            get_package_share_directory('point_lio'),
            'rviz_cfg', 'loam_livox.rviz'
        ]),
        description='RViz configuration file.')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='false',
        description='Use simulation time')

    declare_pcd_save = DeclareLaunchArgument(
        'pcd_save', default_value='false',
        description='Save accumulated Point-LIO map to PCD on shutdown.')

    declare_pcd_save_interval = DeclareLaunchArgument(
        'pcd_save_interval', default_value='-1',
        description='LiDAR frames per PCD file. -1 saves one PCD on shutdown.')

    declare_pcd_save_file = DeclareLaunchArgument(
        'pcd_save_file', default_value='scans.pcd',
        description='PCD file name under the package PCD directory.')

    declare_point_lio_cfg = DeclareLaunchArgument(
        'point_lio_cfg_dir',
        default_value=PathJoinSubstitution([
            get_package_share_directory('point_lio'),
            'config', 'avia.yaml'
        ]),
        description='Path to the Point-LIO config file')

    declare_publish_map_to_odom = DeclareLaunchArgument(
        'publish_map_to_odom', default_value='true',
        description='Publish identity map->odom when no relocalizer owns that transform.')

    declare_lio_world_parent_frame = DeclareLaunchArgument(
        'lio_world_parent_frame', default_value='map',
        description='Parent of camera_init; use odom while relocalizing.')

    declare_path_en = DeclareLaunchArgument(
        'path_en', default_value='true',
        description='Publish visualization paths. Disable during headless competition runtime.')

    param_names_defaults = [
        ('use_imu_as_input', 'false'),
        ('prop_at_freq_of_imu', 'true'),
        ('check_satu', 'true'),
        ('init_map_size', '10'),
        ('point_filter_num', '2'),
        ('space_down_sample', 'true'),
        ('filter_size_surf', '0.2'),
        ('filter_size_map', '0.3'),
        ('ivox_nearby_type', '6'),
        ('cube_side_length', '1000.0'),
        ('runtime_pos_log_enable', 'false'),
    ]

    launch_params = {
        name: LaunchConfiguration(name) for name, _ in param_names_defaults
    }

    point_lio_params = [
        point_lio_cfg,
        {
            'use_sim_time': use_sim_time,
            'pcd_save.pcd_save_en': pcd_save,
            'pcd_save.interval': pcd_save_interval,
            'pcd_save.file_name': pcd_save_file,
            'publish.scan_publish_en': publish_cloud,
            'publish.scan_bodyframe_pub_en': publish_cloud,
            'publish.path_en': ParameterValue(path_en, value_type=bool),
            'robot_base_to_lio_body.x': 0.313710623,
            'robot_base_to_lio_body.y': 0.02329,
            'robot_base_to_lio_body.z': -0.080845726,
            'robot_base_to_lio_body.roll': 0.0,
            'robot_base_to_lio_body.pitch': 0.7853981634,
            'robot_base_to_lio_body.yaw': 0.0,
            **{
                key: launch_params[key]
                for key in launch_params
            },
        },
    ]

    declare_point_lio_params = [
        DeclareLaunchArgument(name, default_value=default)
        for name, default in param_names_defaults
    ]

    point_lio_node = Node(
        package='point_lio',
        executable='pointlio_mapping',
        name='laserMapping',
        namespace=namespace,
        output='screen',
        parameters=point_lio_params,
    )

    map_to_odom_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom',
        namespace=namespace,
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'map',
            '--child-frame-id', 'odom'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(publish_map_to_odom),
    )

    map_to_camera_init_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_camera_init',
        namespace=namespace,
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', lio_world_parent_frame,
            '--child-frame-id', 'camera_init'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    base_link_to_body_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_body',
        namespace=namespace,
        arguments=[
            '--x', '0.313710623', '--y', '0.02329', '--z', '-0.080845726',
            '--roll', '0.0', '--pitch', '0.7853981634', '--yaw', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'body'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    base_link_to_lidar_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_base_lidar',
        namespace=namespace,
        arguments=[
            '--x', '0.33713', '--y', '0.0', '--z', '-0.04187',
            '--roll', '0.0', '--pitch', '0.7853981634', '--yaw', '0.0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'base_lidar'
        ],
        parameters=[{'use_sim_time': use_sim_time}],
    )

    pointcloud_to_scan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        namespace=namespace,
        remappings=[
            ('cloud_in', 'cloud_registered_body'),
            ('scan', 'scan'),
        ],
        parameters=[{
            'use_sim_time': use_sim_time,
            'target_frame': 'base_footprint',
            'transform_tolerance': 0.5,
            'min_height': 0.15,
            'max_height': 0.50,
            'angle_min': -3.14159,
            'angle_max': 3.14159,
            'angle_increment': 0.0087,
            'scan_time': 0.1,
            'range_min': 0.40,
            'range_max': 5.0,
            'use_inf': True,
            'inf_epsilon': 1.0,
        }],
        output='screen',
        condition=IfCondition(use_scan),
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=[
            '-d',
            rviz_config
        ],
        condition=IfCondition(use_rviz)
    )

    ld = LaunchDescription([
        declare_namespace,
        declare_rviz,
        declare_scan,
        declare_publish_cloud,
        declare_rviz_config,
        declare_use_sim_time,
        declare_pcd_save,
        declare_pcd_save_interval,
        declare_pcd_save_file,
        declare_point_lio_cfg,
        declare_publish_map_to_odom,
        declare_lio_world_parent_frame,
        declare_path_en,
        *declare_point_lio_params,
        map_to_odom_node,
        map_to_camera_init_node,
        base_link_to_body_node,
        base_link_to_lidar_node,
        point_lio_node,
        pointcloud_to_scan_node,
        GroupAction(actions=[rviz_node], condition=IfCondition(use_rviz))
    ])

    return ld
