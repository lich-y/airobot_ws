import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, RegisterEventHandler, SetEnvironmentVariable
from launch.event_handlers import OnProcessStart
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    # Package name
    pkg_name = 'airobot_simulation'

    # Get package share directory
    pkg_share = get_package_share_directory(pkg_name)

    # Default URDF file path
    default_urdf_file = os.path.join(
        pkg_share, 
        'urdf', 
        'airobot', 
        'airobot.urdf.xacro'
    )

    # Default world file path
    default_world_file = os.path.join(
        pkg_share, 
        'world', 
        'apartment.world'
    )

    # Declare launch arguments
    urdf_file_arg = DeclareLaunchArgument(
        'urdf_file',
        default_value=default_urdf_file,
        description='Absolute path to the URDF file'
    )

    world_file_arg = DeclareLaunchArgument(
        'world_file',
        default_value=default_world_file,
        description='Absolute path to the Gazebo world file'
    )

    spawn_x_arg = DeclareLaunchArgument(
        'spawn_x',
        default_value='1.0',
        description='Robot initial x position in Gazebo'
    )

    spawn_y_arg = DeclareLaunchArgument(
        'spawn_y',
        default_value='0.0',
        description='Robot initial y position in Gazebo'
    )

    spawn_z_arg = DeclareLaunchArgument(
        'spawn_z',
        default_value='0.30',
        description='Robot initial z position in Gazebo; default keeps the robot above the floor for a clean drop'
    )

    spawn_roll_arg = DeclareLaunchArgument(
        'spawn_roll',
        default_value='0.0',
        description='Robot initial roll in Gazebo'
    )

    spawn_pitch_arg = DeclareLaunchArgument(
        'spawn_pitch',
        default_value='0.0',
        description='Robot initial pitch in Gazebo'
    )

    spawn_yaw_arg = DeclareLaunchArgument(
        'spawn_yaw',
        default_value='0.0',
        description='Robot initial yaw in Gazebo'
    )

    # Get launch configuration values
    urdf_file = LaunchConfiguration('urdf_file')
    world_file = LaunchConfiguration('world_file')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')
    spawn_roll = LaunchConfiguration('spawn_roll')
    spawn_pitch = LaunchConfiguration('spawn_pitch')
    spawn_yaw = LaunchConfiguration('spawn_yaw')

    # Generate robot description from xacro
    # This creates the robot_description parameter from the URDF/XACRO file
    # Wrap in ParameterValue to specify it's a string type
    robot_description_content = ParameterValue(
        Command(
            [
                FindExecutable(name='xacro'), ' ',
                urdf_file
            ]
        ),
        value_type=str
    )

    # Robot state publisher node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    # Joint state publisher node (publishes joint_states for robot joints)
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    # Gazebo launch with world
    gazebo = ExecuteProcess(
        cmd=[
            'gazebo',
            '--verbose',
            world_file,
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so'
        ],
        output='screen',
        shell=True
    )

    # Spawn robot in Gazebo
    spawn_robot_node = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'airobot',
            '-topic', 'robot_description',
            '-x', spawn_x,
            '-y', spawn_y,
            '-z', spawn_z,
            '-R', spawn_roll,
            '-P', spawn_pitch,
            '-Y', spawn_yaw
        ],
        parameters=[{
            'use_sim_time': True
        }],
        output='screen'
    )

    # Create launch description
    return LaunchDescription([
        # Declare arguments
        urdf_file_arg,
        world_file_arg,
        spawn_x_arg,
        spawn_y_arg,
        spawn_z_arg,
        spawn_roll_arg,
        spawn_pitch_arg,
        spawn_yaw_arg,

        # Robot state publisher
        robot_state_publisher_node,

        # Joint state publisher
        joint_state_publisher_node,

        # Gazebo
        gazebo,

        # Spawn robot (wait for gazebo to start)
        RegisterEventHandler(
            OnProcessStart(
                target_action=gazebo,
                on_start=spawn_robot_node
            )
        )
    ])

