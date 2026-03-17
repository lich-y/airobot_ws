from setuptools import setup
import os
from glob import glob

package_name = 'airobot_simulation'

# Get the package root directory
package_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name=package_name,
    version='0.0.0',
    packages=[],
    py_modules=['src.explore_node'],
    package_dir={'': package_dir},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/urdf', glob('urdf/**/*.xacro')),
        ('share/' + package_name + '/urdf', glob('urdf/**/*.urdf')),
        ('share/' + package_name + '/world', glob('world/**/*.world')),
        ('share/' + package_name + '/plugins', glob('plugins/**/*.xacro')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='edward',
    maintainer_email='edward.li@cloudwise.com',
    description='AI Robot Simulation Package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'explore_node = src.explore_node:main',
        ],
    },
)
