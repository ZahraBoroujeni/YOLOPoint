cmake_minimum_required(VERSION 3.5)
project(object_instance_msgs)

# Find ament macros and dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Declare ROS2 messages
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ObjectInstance2D.msg"
  "msg/ObjectInstance2DArray.msg"
  "msg/ObjectInstance3D.msg"
  "msg/ObjectInstance3DArray.msg"
  DEPENDENCIES std_msgs geometry_msgs sensor_msgs
)

# Generate ament package
ament_package()