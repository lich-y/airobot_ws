"""
Author:小鱼
Description: Nav2 launch启动文件
"""
import os
from typing import List

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def get_package_path(package_name: str) -> str:
    """获取包_share目录路径"""
    return get_package_share_directory(package_name)


def declare_launch_arguments() -> List[DeclareLaunchArgument]:
    """声明所有可配置的启动参数"""
    return [
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(
                get_package_path('airobot_navigation2'),
                'maps',
                'airobot_map.yaml'
            ),
            description='Path to the map yaml file'
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(
                get_package_path('airobot_navigation2'),
                'param',
                'airobot_nav2.yaml'
            ),
            description='Path to the Nav2 params yaml file'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation time'
        ),
        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically start the nav2 lifecycle'
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='Robot namespace for nodes'
        ),
        DeclareLaunchArgument(
            'launch_rviz',
            default_value='true',
            description='Whether to launch rviz2'
        ),
        DeclareLaunchArgument(
            'rviz_config_file',
            default_value=os.path.join(
                get_package_path('nav2_bringup'),
                'rviz',
                'nav2_default_view.rviz'
            ),
            description='Path to rviz config file'
        ),
    ]


def generate_launch_description() -> LaunchDescription:
    """生成Nav2启动描述"""
    # 获取包路径
    airobot_navigation2_dir = get_package_path('airobot_navigation2')
    nav2_bringup_dir = get_package_path('nav2_bringup')

    # 声明启动参数
    launch_args = declare_launch_arguments()

    # 获取配置参数
    map_yaml_path = LaunchConfiguration('map')
    nav2_param_path = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    namespace = LaunchConfiguration('namespace')
    launch_rviz = LaunchConfiguration('launch_rviz')
    rviz_config_dir = LaunchConfiguration('rviz_config_file')

    # 启动nav2_bringup_launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_path,
            'use_sim_time': use_sim_time,
            'params_file': nav2_param_path,
            'autostart': autostart,
            'namespace': namespace,
        }.items(),
    )

    # 创建节点列表
    launch_nodes = [nav2_bringup_launch]

    # 可选:启动rviz2节点
    rviz_condition_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(launch_rviz),
    )

    launch_nodes.append(rviz_condition_node)

    return LaunchDescription(launch_args + launch_nodes)