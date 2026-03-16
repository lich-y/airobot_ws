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

    # Get launch configuration values
    urdf_file = LaunchConfiguration('urdf_file')
    world_file = LaunchConfiguration('world_file')

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
            '-x', '0',
            '-y', '0',
            '-z', '0.1'
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

        # Robot state publisher
        robot_state_publisher_node,

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

