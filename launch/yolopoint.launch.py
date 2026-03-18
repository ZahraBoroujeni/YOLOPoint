from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        # Declare arguments
        DeclareLaunchArgument(
            'config',
            default_value='configs/campus_inference.yaml'
        ),
        DeclareLaunchArgument(
            'sensor_name',
            default_value='surround/front'
        ),
        DeclareLaunchArgument(
            'weights_path',
            default_value='weights/CampusKitti/checkpoints/CampusKitti_46_2291_ckpt.pth.tar'
        ),
        DeclareLaunchArgument(
            'filter_pts',
            default_value='false'
        ),
        DeclareLaunchArgument(
            'visualize',
            default_value='false'
        ),
        DeclareLaunchArgument(
          'node_name',
            default_value='yolopoint'
        )

        # Node
        Node(
          package='yolopoint',
          executable='ros_demo',
          name=LaunchConfiguration('node_name'),   # 🔥 important
          output='screen',
          parameters=[{
              'config': LaunchConfiguration('config'),
              'sensor_name': LaunchConfiguration('sensor_name'),
              'weights_path': LaunchConfiguration('weights_path'),
              'filter_pts': LaunchConfiguration('filter_pts'),
              'visualize': LaunchConfiguration('visualize'),
          }]
      )
    ])