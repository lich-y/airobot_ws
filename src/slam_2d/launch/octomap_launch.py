from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取包路径
    pkg_share = get_package_share_directory('slam_2d')
    
    # 配置文件路径
    octomap_config_path = os.path.join(pkg_share, 'config', 'octomap.yaml')
    
    return LaunchDescription([
        Node(
            package='octomap_server',
            executable='octomap_server_node',
            name='octomap_server',
            parameters=[octomap_config_path],
            remappings=[
                ('cloud_in', '/dlio/odom_node/pointcloud/deskewed'),  # Now published after setting waitUntilMove=false
                # ('cloud_in', '/dlio/odom_node/pointcloud/keyframe'),  # Keyframes are less frequent
                # ('cloud_in', '/livox/lidar/pointcloud'),  # Raw lidar causes blurry maps due to motion distortion
                ('projected_map', 'map'),
            ]
        )
    ])
