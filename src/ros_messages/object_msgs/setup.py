from setuptools import setup

package_name = 'object_msgs'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=True,
    author='Andreas Reich, Thorsten Luettel',
    author_email='andreas.reich@unibw.de, thorsten.luettel@unibw.de',
    maintainer='Andreas Reich, Thorsten Luettel',
    maintainer_email='andreas.reich@unibw.de, thorsten.luettel@unibw.de',
    description='ROS2 Python package for object messages',
    license='TODO',
    entry_points={
        'console_scripts': [
            # Add your Python node scripts here if any, e.g.:
            # 'node_name = object_msgs.node_file:main',
        ],
    },
)