cmake_minimum_required(VERSION 3.8)
project(estimation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find Eigen3 for matrix operations
find_package(Eigen3 REQUIRED)

# Find ROS2 dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(interfaces REQUIRED)

# Include directories
include_directories(
  include
  ${EIGEN3_INCLUDE_DIRS}
)

# Create kinematics library
add_library(estimation_kinematics
  src/leg_dynamics.cpp
)
target_link_libraries(estimation_kinematics
  ${EIGEN3_LIBRARIES}
)

# Create contact detection node executable
add_executable(contact_detection_node
  src/main.cpp
  src/contact_detection_node.cpp
  src/gm_observer.cpp
)
target_link_libraries(contact_detection_node
  estimation_kinematics
  ${EIGEN3_LIBRARIES}
)
ament_target_dependencies(contact_detection_node
  rclcpp
  std_msgs
  geometry_msgs
  interfaces
)

# Install executables
install(TARGETS contact_detection_node
  RUNTIME DESTINATION lib/estimation
)

# Install library
install(TARGETS estimation_kinematics
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
)

# Install headers
install(DIRECTORY include/estimation/
  DESTINATION include/estimation
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
