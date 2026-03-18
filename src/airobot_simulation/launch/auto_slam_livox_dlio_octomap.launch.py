"""
Auto SLAM Launch File with Livox 3D Lidar + DLIO + OctoMap 3D
Launches Gazebo simulation, DLIO SLAM (去畸变 + 里程计), and OctoMap 3D mapping.

This launch file includes:
- gazebo_sim.launch.py: Gazebo simulation with robot (using Livox 3D lidar)
- livox_pointcloud: Pointcloud conversion (points_raw -> points)
- direct_lidar_inertial_odometry: DLIO SLAM (去畸变 + 里程计)
- octomap_server: 3D octomap mapping from pointcloud
- explore_node: Random exploration with auto-return

Usage:
    ros2 launch airobot_simulation auto_slam_livox_dlio_octomap.launch.py

Or with parameters:
    ros2 launch airobot_simulation auto_slam_livox_dlio_octomap.launch.py world_file:=/path/to/world.world
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
    livox_pc_pkg = 'livox_pointcloud'
    dlio_pkg = 'direct_lidar_inertial_odometry'
    slam_2d_pkg = 'slam_2d'
    
    # Get package share directories
    sim_pkg_share = get_package_share_directory(sim_pkg_name)
    livox_pc_share = get_package_share_directory(livox_pc_pkg)
    dlio_share = get_package_share_directory(dlio_pkg)
    slam_2d_pkg_share = get_package_share_directory(slam_2d_pkg)
    
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
    
    # OctoMap parameters
    octomap_frame_arg = DeclareLaunchArgument(
        'octomap_frame',
        default_value='odom',
        description='OctoMap frame ID (DLIO使用odom坐标系)'
    )
    
    octomap_topic_arg = DeclareLaunchArgument(
        'octomap_topic',
        default_value='dlio/odom_node/pointcloud/keyframe',
        description='Input pointcloud topic for OctoMap (使用关键帧点云)'
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
    
    # Include slam_2d OctoMap launch
    slam_2d_pkg_share = get_package_share_directory('slam_2d')
    octomap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(slam_2d_pkg_share, 'launch', 'octomap_launch.py')
        )
    )
    
    # ===================== Nodes =====================
    
    # Livox PointCloud converter node
    # 仿真中: /livox/lidar → /livox/points → DLIO
    # 实际设备: /livox/points_raw → /livox/points → DLIO
    livox_converter_node = Node(
        package=livox_pc_pkg,
        executable='pointcloud_converter_node.py',
        name='livox_pointcloud_converter',
        output='screen',
        parameters=[{
            'input_topic': '/livox/lidar',  # Gazebo仿真使用 /livox/lidar
            'output_topic': '/livox/points',
            'frame_id': 'livox_frame',
        }],
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
        octomap_frame_arg,
        octomap_topic_arg,
        forward_speed_arg,
        turn_speed_arg,
        exploration_time_arg,
        return_speed_arg,
        auto_return_arg,
        
        # Include Gazebo simulation (includes robot spawning with Livox lidar)
        gazebo_sim_launch,
        
        # Include DLIO SLAM
        dlio_launch,
        
        # Include OctoMap from slam_2d package
        octomap_launch,
        
        # Livox pointcloud converter
        livox_converter_node,
        
        # Random exploration node with auto-return
        explore_node,
    ])
