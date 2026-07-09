import os
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.substitutions import Command, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'fines_description'
    xacro_name = "finenew.xacro"


    ld = LaunchDescription()
    pkg_share = FindPackageShare(package=package_name).find(package_name) 
    #urdf_model_path = os.path.join(pkg_share, f'urdf/{urdf_name})


    # robot_state_publisher_node = Node(
    #     package='robot_state_publisher',
    #     executable='robot_state_publisher',
    #     arguments=[urdf_model_path]
    #     )

    path_to_urdf = os.path.join(pkg_share, 'urdf', xacro_name)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',  # 推荐显式命名节点
        parameters=[{
            # 关键修改：参数名应为'robot_description'而非'fines_description'
            'robot_description': Command(['xacro ', path_to_urdf]),
        }],
        output='screen'  # 可选：打印日志到屏幕
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        parameters=[{
            'robot_description': Command(['xacro ', path_to_urdf])  # 统一使用Command解析xacro
        }],
        output='screen'
    )

    rviz2_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(pkg_share, 'rviz/display_urdf.rviz')]
        )

    ld.add_action(robot_state_publisher_node)
    # ld.add_action(joint_state_publisher_node)
    ld.add_action(rviz2_node)

    return ld