from setuptools import setup
import os
from glob import glob

package_name = 'airobot_remote_control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 包含web文件夹中的所有文件
        (os.path.join('share', package_name, 'web'), 
         glob('web/*')),
        # 包含launch文件夹
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robot Team',
    maintainer_email='robot@example.com',
    description='Web-based remote controller for robot car',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'remote_control = airobot_remote_control.remote_control:main',
            'remote_control_http = airobot_remote_control.http_server:main',
        ],
    },
)
