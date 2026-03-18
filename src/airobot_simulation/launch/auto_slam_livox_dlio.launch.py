"""
Auto SLAM Launch File with Livox 3D Lidar + DLIO
Launches Gazebo simulation, DLIO SLAM (去畸变 + 里程计), pointcloud to laserscan conversion,
and Cartographer 2D SLAM for automatic robot mapping.

This launch file includes:
- gazebo_sim.launch.py: Gazebo simulation with robot (using Livox 3D lidar)
- livox_pointcloud: Pointcloud conversion (points_raw -> points)
- direct_lidar_inertial_odometry: DLIO SLAM (去畸变 + 里程计)
- pointcloud_to_laserscan: Convert 3D pointcloud to 2D laser scan
- cartographer: Cartographer 2D SLAM
- explore_node: Random exploration with auto-return

Usage:
    ros2 launch airobot_simulation auto_slam_livox_dlio.launch.py

Or with parameters:
    ros2 launch airobot_simulation auto_slam_livox_dlio.launch.py world_file:=/path/to/world.world
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
    livox_pc_pkg = 'livox_pointcloud'
    dlio_pkg = 'direct_lidar_inertial_odometry'
    
    # Get package share directories
    sim_pkg_share = get_package_share_directory(sim_pkg_name)
    carto_pkg_share = get_package_share_directory(carto_pkg_name)
    livox_pc_share = get_package_share_directory(livox_pc_pkg)
    dlio_share = get_package_share_directory(dlio_pkg)
    
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
    
    # DLIO parameters
    dlio_rviz_arg = DeclareLaunchArgument(
        'dlio_rviz',
        default_value='false',
        description='Launch DLIO RViz'
    )
    
    # PointCloud to LaserScan arguments
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
    
    # Include DLIO launch
    dlio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(dlio_share, 'launch', 'dlio.launch.py')
        ),
        launch_arguments=[
            ('pointcloud_topic', 'livox/points'),
            ('imu_topic', 'livox/imu'),
            ('use_sim_time', LaunchConfiguration('use_sim_time')),
            ('rviz', LaunchConfiguration('dlio_rviz')),
        ]
    )
    
    # ===================== Nodes =====================
    
    # Livox PointCloud converter node
    # 数据流: /livox/points_raw (Gazebo/Livox原始) → /livox/points (标准格式) → DLIO
    # 注意: Gazebo仿真中使用 livox/lidar (通过URDF配置)，实际Livox设备使用 livox/points_raw
    livox_converter_node = Node(
        package=livox_pc_pkg,
        executable='pointcloud_converter_node.py',
        name='livox_pointcloud_converter',
        output='screen',
        parameters=[{
            'input_topic': '/livox/points_raw',   # Livox原始点云话题
            'output_topic': '/livox/points',       # 转换后标准PointCloud2
            'frame_id': 'livox_frame',
        }],
    )
    
    # PointCloud to LaserScan node
    # Converts DLIO's deskewed pointcloud to 2D laser scan for Cartographer
    pc_to_scan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[{
            'input_pointcloud_topic': 'dlio/odom_node/pointcloud/deskewed',
            'output_scan_topic': LaunchConfiguration('scan_output_topic'),
            'target_frame': LaunchConfiguration('target_frame'),
            'transform_tolerance': 0.01,
            'min_height': -0.5,      # Include ground points
            'max_height': 2.0,        # Include higher obstacles  
            'angle_min': -3.14159,    # -PI
            'angle_max': 3.14159,     # PI
            'angle_increment': 0.0087,  # ~0.5 degree
            'scan_time': 0.1,
            'range_min': 0.1,
            'range_max': 50.0,
            'inf_epsilon': 1.0,
        }],
        remappings=[
            ('/cloud_in', 'dlio/odom_node/pointcloud/deskewed'),
        ],
    )
    
    # Random Exploration Node
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
        dlio_rviz_arg,
        scan_output_arg,
        target_frame_arg,
        forward_speed_arg,
        turn_speed_arg,
        exploration_time_arg,
        return_speed_arg,
        auto_return_arg,
        
        # Include Gazebo simulation (includes robot spawning with Livox lidar)
        gazebo_sim_launch,
        
        # Include DLIO SLAM
        dlio_launch,
        
        # Include Cartographer SLAM
        cartographer_launch,
        
        # Livox pointcloud converter
        livox_converter_node,
        
        # PointCloud to LaserScan conversion node
        pc_to_scan_node,
        
        # Random exploration node with auto-return
        explore_node,
    ])
