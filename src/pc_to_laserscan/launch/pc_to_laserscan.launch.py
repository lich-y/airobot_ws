"""
PointCloud to LaserScan conversion launch file

This launch file starts the pointcloud_to_laserscan node which converts
pointcloud data from lidar to laser scan for navigation.
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_name = 'pc_to_laserscan'
    
    # Launch arguments
    input_pointcloud_topic = DeclareLaunchArgument(
        'input_pointcloud_topic',
        default_value='/livox/lidar',
        description='Input pointcloud topic'
    )
    
    output_scan_topic = DeclareLaunchArgument(
        'output_scan_topic',
        default_value='/scan',
        description='Output laser scan topic'
    )
    
    target_frame = DeclareLaunchArgument(
        'target_frame',
        default_value='laser_link',
        description='Target frame for the laser scan'
    )
    
    # Get package share directory
    pkg_share = FindPackageShare(package=pkg_name).find(pkg_name)
    
    # PointCloud to LaserScan node
    pc_to_scan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[{
            'input_pointcloud_topic': LaunchConfiguration('input_pointcloud_topic'),
            'output_scan_topic': LaunchConfiguration('output_scan_topic'),
            'target_frame': LaunchConfiguration('target_frame'),
            'transform_tolerance': 0.01,
            'min_height': 0.0,
            'max_height': 1.0,
            'angle_min': -3.14159,  # -PI
            'angle_max': 3.14159,   # PI
            'angle_increment': 0.0087,  # ~0.5 degree
            'scan_time': 0.1,
            'range_min': 0.1,
            'range_max': 10.0,
            'inf_epsilon': 1.0,
        }],
        remappings=[
            ('/cloud_in', LaunchConfiguration('input_pointcloud_topic')),
        ],
    )
    
    return LaunchDescription([
        input_pointcloud_topic,
        output_scan_topic,
        target_frame,
        pc_to_scan_node,
    ])
