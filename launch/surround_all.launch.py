from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
import os

from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    pkg_yolopoint = get_package_share_directory('yolopoint')
    launch_file = os.path.join(pkg_yolopoint, 'launch', 'yolopoint.launch.py')

    def create_camera(ns, sensor_name, node_name):
        return [
            PushRosNamespace(ns),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(launch_file),
                launch_arguments={
                    'sensor_name': sensor_name,
                    'node_name': node_name,
                }.items(),
            )
        ]

    return LaunchDescription([

        # Global namespace: perception/yolopoint
        PushRosNamespace('perception'),
        PushRosNamespace('yolopoint'),

        # Cameras
        *create_camera('surround_front', 'surround/front', 'keypoint_front'),
        *create_camera('surround_left', 'surround/left', 'keypoint_left'),
        *create_camera('surround_back', 'surround/back', 'keypoint_back'),
        *create_camera('surround_right', 'surround/right', 'keypoint_right'),
    ])