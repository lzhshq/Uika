cmake_minimum_required(VERSION 3.22)
project(fine_nav2d_bringup)

find_package(ament_cmake_auto REQUIRED)

ament_auto_find_build_dependencies()

install(PROGRAMS
        scripts/terrain_zone_manager.py
        scripts/terrain_zone_selector.py
        scripts/terrain_mission_manager.py
        scripts/terrain_mission_executor.py
        scripts/mission_path_follower.py
        scripts/single_mission_task_runner.py
        scripts/dryrun_odom_publisher.py
        scripts/tf_path_publisher.py
        scripts/convert_lidar_odom_pcd_to_map.py
        scripts/convert_mjcf_terrain_to_pcd.py
        DESTINATION lib/${PROJECT_NAME}
)

ament_auto_package(
        INSTALL_TO_SHARE
        launch
        config
        rviz
        urdf
        maps
        behavior_tree
)
