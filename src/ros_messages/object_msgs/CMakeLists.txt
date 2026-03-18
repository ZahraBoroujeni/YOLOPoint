cmake_minimum_required(VERSION 3.8)
project(object_msgs)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

# Find packages
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)
find_package(Eigen3 REQUIRED)

# Include directories
include_directories(
  include
  ${EIGEN3_INCLUDE_DIRS}
)

# Message generation
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MotionType.msg"
  "msg/Pose32.msg"
  "msg/Pose64.msg"
  "msg/ObjectDimension.msg"
  "msg/ObjectClass.msg"
  "msg/ObjectClassEstimate.msg"
  "msg/ObjectStateIndex.msg"
  "msg/Object.msg"
  "msg/Objects.msg"
  "msg/ReferencePointType.msg"
  DEPENDENCIES std_msgs
)

# Export dependencies
ament_export_dependencies(rosidl_default_runtime)

install(DIRECTORY include/
        DESTINATION include)
        
# Package
ament_package()