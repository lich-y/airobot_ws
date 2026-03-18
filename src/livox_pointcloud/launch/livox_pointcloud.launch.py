"""
Livox PointCloud Converter Launch File
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_name = 'livox_pointcloud'
    pkg_share = get_package_share_directory(pkg_name)
    
    input_topic_arg = DeclareLaunchArgument(
        'input_topic',
        default_value='/livox/points_raw',
        description='Input pointcloud topic from Livox lidar'
    )
    
    output_topic_arg = DeclareLaunchArgument(
        'output_topic',
        default_value='/livox/points',
        description='Output converted pointcloud topic'
    )
    
    frame_id_arg = DeclareLaunchArgument(
        'frame_id',
        default_value='livox_frame',
        description='PointCloud frame ID'
    )
    
    converter_node = Node(
        package=pkg_name,
        executable='pointcloud_converter_node.py',
        name='livox_pointcloud_converter',
        output='screen',
        parameters=[{
            'input_topic': LaunchConfiguration('input_topic'),
            'output_topic': LaunchConfiguration('output_topic'),
            'frame_id': LaunchConfiguration('frame_id'),
        }],
    )
    
    return LaunchDescription([
        input_topic_arg,
        output_topic_arg,
        frame_id_arg,
        converter_node,
    ])
