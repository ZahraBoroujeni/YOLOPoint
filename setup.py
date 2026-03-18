import os
from setuptools import setup, find_packages
from glob import glob

package_name = 'yolopoint'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(),  # <-- include all subfolders with __init__.py
    data_files=[
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    description='YOLOPoint ROS2 node',
    license='TODO',
    entry_points={
        'console_scripts': [
            'demo_ros2 = yolopoint.demo_ROS:main',
            'demo_ros2_listener = yolopoint.demo_ROS_listener:main',
            'yolopoint_ros = yolopoint.yolopoint_ros:main',
        ],
    },
)
