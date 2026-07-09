cmake_minimum_required(VERSION 3.8)
project(fines_serial)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()


find_package(OpenMP QUIET)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}   ${OpenMP_C_FLAGS}")
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(ament_cmake REQUIRED)
find_package(fmt REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

set(dependencies
  rclcpp
  std_msgs
        geometry_msgs
)

include_directories(include)

add_library(${PROJECT_NAME}_LIB
  include/serial/serial.h
  include/serial/v8stdint.h
  src/serial/serial.cc
  src/serial/impl/unix.cc
  src/serial/impl/list_ports/list_ports_linux.cc
)

add_executable(${PROJECT_NAME}
  src/interface.cpp
        src/serial_station.cpp
)

target_link_libraries(${PROJECT_NAME} 
${PROJECT_NAME}_LIB
        rt
        pthread
        ${cpp_typesupport_target}
        fmt::fmt
)
ament_target_dependencies(${PROJECT_NAME} ${dependencies})

install(TARGETS ${PROJECT_NAME}
        DESTINATION lib/${PROJECT_NAME}
)

ament_package()
