"""
Livox + DLIO + Cartographer SLAM Launch File

Complete launch file for Livox Mid-360 based SLAM system with DLIO:

Flow:
  1. livox/points_raw (Livox SDK)
  2. → livox_pointcloud converter
  3. → livox/points (标准PointCloud2)
  4. → DLIO (去畸变 + 里程计)
  5. → dlio/odom_node/pointcloud/deskewed (去畸变点云)
  6. → pointcloud_to_laserscan
  7. → /scan (2D激光扫描)
  8. → Cartographer 2D SLAM

Usage:
    ros2 launch livox_pointcloud livox_dlio_slam.launch.py

Note: Requires direct_lidar_inertial_odometry package to be built
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Package names
    livox_pc_pkg = 'livox_pointcloud'
    dlio_pkg = 'direct_lidar_inertial_odometry'
    pc_to_laser_pkg = 'pc_to_laserscan'
    carto_pkg = 'airobot_cartographer'
    
    # Get package share directories
    livox_pc_share = get_package_share_directory(livox_pc_pkg)
    dlio_share = get_package_share_directory(dlio_pkg)
    pc_to_laser_share = get_package_share_directory(pc_to_laser_pkg)
    carto_share = get_package_share_directory(carto_pkg)
    
    # ===================== Declare launch arguments =====================
    
    # Common parameters
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )
    
    # Livox pointcloud topics
    input_topic_arg = DeclareLaunchArgument(
        'input_pointcloud_topic',
        default_value='/livox/points_raw',
        description='Input pointcloud topic from Livox lidar'
    )
    
    # DLIO parameters
    dlio_pointcloud_arg = DeclareLaunchArgument(
        'dlio_pointcloud_topic',
        default_value='livox/points',
        description='Pointcloud topic for DLIO'
    )
    
    dlio_imu_arg = DeclareLaunchArgument(
        'dlio_imu_topic',
        default_value='livox/imu',
        description='IMU topic for DLIO'
    )
    
    # PointCloud to LaserScan parameters
    scan_input_arg = DeclareLaunchArgument(
        'scan_input_topic',
        default_value='dlio/odom_node/pointcloud/deskewed',
        description='Input pointcloud for 3D to 2D conversion (from DLIO)'
    )
    
    scan_output_arg = DeclareLaunchArgument(
        'scan_output_topic',
        default_value='/scan',
        description='Output laser scan topic'
    )
    
    target_frame_arg = DeclareLaunchArgument(
        'target_frame',
        default_value='livox_frame',
        description='Target frame for laser scan'
    )
    
    # ===================== Include Launch Files =====================
    
    # Livox pointcloud converter
    livox_converter_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(livox_pc_share, 'launch', 'livox_pointcloud.launch.py')
        ),
        launch_arguments=[
            ('input_topic', LaunchConfiguration('input_pointcloud_topic')),
            ('output_topic', LaunchConfiguration('dlio_pointcloud_topic')),
            ('frame_id', 'livox_frame'),
        ]
    )
    
    # DLIO SLAM
    dlio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(dlio_share, 'launch', 'dlio.launch.py')
        ),
        launch_arguments=[
            ('pointcloud_topic', LaunchConfiguration('dlio_pointcloud_topic')),
            ('imu_topic', LaunchConfiguration('dlio_imu_topic')),
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('rviz', 'false'),  # Disable RViz in integrated launch
        ]
    )
    
    # Cartographer SLAM
    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(carto_share, 'launch', 'cartographer.launch.py')
        ),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
        ]
    )
    
    # ===================== Nodes =====================
    
    # PointCloud to LaserScan node
    # This converts DLIO's deskewed pointcloud to 2D laser scan for Cartographer
    pc_to_scan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[{
            'input_pointcloud_topic': LaunchConfiguration('scan_input_topic'),
            'output_scan_topic': LaunchConfiguration('scan_output_topic'),
            'target_frame': LaunchConfiguration('target_frame'),
            'transform_tolerance': 0.01,
            'min_height': -0.5,    # Include ground points
            'max_height': 2.0,     # Include higher obstacles
            'angle_min': -3.14159,  # -PI
            'angle_max': 3.14159,   # PI
            'angle_increment': 0.0087,  # ~0.5 degree
            'scan_time': 0.1,
            'range_min': 0.1,
            'range_max': 50.0,
            'inf_epsilon': 1.0,
        }],
        remappings=[
            ('/cloud_in', LaunchConfiguration('scan_input_topic')),
        ],
    )
    
    # ===================== Create Launch Description =====================
    
    return LaunchDescription([
        # Declare arguments
        use_sim_time_arg,
        input_topic_arg,
        dlio_pointcloud_arg,
        dlio_imu_arg,
        scan_input_arg,
        scan_output_arg,
        target_frame_arg,
        
        # Include launches
        livox_converter_launch,
        dlio_launch,
        cartographer_launch,
        
        # Nodes
        pc_to_scan_node,
    ])
