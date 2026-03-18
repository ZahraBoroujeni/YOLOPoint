cmake_minimum_required(VERSION 3.8)
project(keypoint_msg)

# Default to C++14 (safe default for ROS2)
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

# Find required packages
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# Generate messages
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/KeypointArray.msg"
  DEPENDENCIES std_msgs geometry_msgs sensor_msgs
)

# Export runtime dependencies
ament_export_dependencies(rosidl_default_runtime)

# Package
ament_package()