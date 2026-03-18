"""
Auto SLAM Launch File with Livox Lidar
Launches Gazebo simulation, Cartographer SLAM, pointcloud to laserscan conversion,
and random exploration for automatic robot mapping.

This launch file includes:
- gazebo_sim.launch.py: Gazebo simulation with robot (using Livox 3D lidar)
- cartographer.launch.py: Cartographer SLAM nodes
- pointcloud_to_laserscan: Convert 3D pointcloud to 2D laser scan
- explore_node: Random exploration with auto-return

Usage:
    ros2 launch airobot_simulation auto_slam_livox.launch.py

Or with parameters:
    ros2 launch airobot_simulation auto_slam_livox.launch.py world_file:=/path/to/world.world
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
    sim_pkg_name = 'airobot_simulation'
    carto_pkg_name = 'airobot_cartographer'
    pc_to_laser_pkg_name = 'pc_to_laserscan'
    
    # Get package share directories
    sim_pkg_share = get_package_share_directory(sim_pkg_name)
    carto_pkg_share = get_package_share_directory(carto_pkg_name)
    pc_to_laser_pkg_share = get_package_share_directory(pc_to_laser_pkg_name)
    
    # ===================== Declare launch arguments =====================
    
    # Forward common arguments from gazebo_sim.launch.py
    world_file_arg = DeclareLaunchArgument(
        'world_file',
        default_value=os.path.join(sim_pkg_share, 'world', 'server_room.world'),
        description='Gazebo world file'
    )
    
    spawn_x_arg = DeclareLaunchArgument('spawn_x', default_value='1.0')
    spawn_y_arg = DeclareLaunchArgument('spawn_y', default_value='0.0')
    spawn_z_arg = DeclareLaunchArgument('spawn_z', default_value='0.30')
    spawn_yaw_arg = DeclareLaunchArgument('spawn_yaw', default_value='0.0')
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    # URDF arguments for Livox lidar
    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=os.path.join(sim_pkg_share, 'urdf', 'airobot', 'airobot.urdf.xacro'),
        description='URDF file path'
    )
    
    laser_type_arg = DeclareLaunchArgument(
        'laser_type',
        default_value='3d',
        description='Laser type: 2d=2D lidar, 3d=Livox 3D lidar'
    )
    
    # PointCloud to LaserScan arguments
    input_pointcloud_topic_arg = DeclareLaunchArgument(
        'input_pointcloud_topic',
        default_value='/livox/lidar',
        description='Input pointcloud topic from lidar'
    )
    
    output_scan_topic_arg = DeclareLaunchArgument(
        'output_scan_topic',
        default_value='/scan',
        description='Output laser scan topic'
    )
    
    target_frame_arg = DeclareLaunchArgument(
        'target_frame',
        default_value='laser_link',
        description='Target frame for the laser scan'
    )
    
    # Exploration parameters
    forward_speed_arg = DeclareLaunchArgument(
        'forward_speed',
        default_value='0.3',
        description='Robot forward speed for exploration'
    )
    
    turn_speed_arg = DeclareLaunchArgument(
        'turn_speed',
        default_value='0.5',
        description='Robot turn speed for exploration'
    )
    
    # SLAM completion and return parameters
    exploration_time_arg = DeclareLaunchArgument(
        'exploration_time',
        default_value='0.0',
        description='Time in seconds to explore before returning (set to 0.0 for continuous exploration)'
    )
    
    return_speed_arg = DeclareLaunchArgument(
        'return_speed',
        default_value='0.2',
        description='Robot speed when returning to start'
    )
    
    auto_return_arg = DeclareLaunchArgument(
        'auto_return',
        default_value='true',
        description='Automatically return to starting position after exploration'
    )
    
    # ===================== Include existing launch files =====================
    
    # Include Gazebo simulation launch with Livox lidar URDF
    gazebo_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(sim_pkg_share, 'launch', 'gazebo_sim.launch.py')
        ),
        launch_arguments=[
            ('world_file', LaunchConfiguration('world_file')),
            ('urdf_file', LaunchConfiguration('urdf_file')),
            ('spawn_x', LaunchConfiguration('spawn_x')),
            ('spawn_y', LaunchConfiguration('spawn_y')),
            ('spawn_z', LaunchConfiguration('spawn_z')),
            ('spawn_yaw', LaunchConfiguration('spawn_yaw')),
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('laser_type', LaunchConfiguration('laser_type')),
        ]
    )
    
    # Include Cartographer SLAM launch
    cartographer_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(carto_pkg_share, 'launch', 'cartographer.launch.py')
        ),
        launch_arguments=[
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
        ]
    )
    
    # ===================== PointCloud to LaserScan Node =====================
    
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
            'range_max': 50.0,
            'inf_epsilon': 1.0,
        }],
        remappings=[
            ('/cloud_in', LaunchConfiguration('input_pointcloud_topic')),
        ],
    )
    
    # ===================== Random Exploration Node =====================
    
    explore_node = Node(
        package='airobot_simulation',
        executable='explore_node.py',
        name='auto_slam_explorer',
        output='screen',
        parameters=[{
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'forward_speed': LaunchConfiguration('forward_speed'),
            'turn_speed': LaunchConfiguration('turn_speed'),
            'min_obstacle_distance': 0.5,
            'change_direction_interval': 3.0,
            'use_laser': True,
            'exploration_time': LaunchConfiguration('exploration_time'),
            'return_speed': LaunchConfiguration('return_speed'),
            'auto_return': LaunchConfiguration('auto_return')
        }]
    )
    
    # ===================== Create Launch Description =====================
    
    return LaunchDescription([
        # Declare arguments
        world_file_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        spawn_yaw_arg,
        use_sim_time_arg,
        urdf_file_arg,
        laser_type_arg,
        input_pointcloud_topic_arg,
        output_scan_topic_arg,
        target_frame_arg,
        forward_speed_arg,
        turn_speed_arg,
        exploration_time_arg,
        return_speed_arg,
        auto_return_arg,
        
        # Include Gazebo simulation (includes robot spawning with Livox lidar)
        gazebo_sim_launch,
        
        # Include Cartographer SLAM
        cartographer_launch,
        
        # PointCloud to LaserScan conversion node
        pc_to_scan_node,
        
        # Random exploration node with auto-return
        explore_node,
    ])
