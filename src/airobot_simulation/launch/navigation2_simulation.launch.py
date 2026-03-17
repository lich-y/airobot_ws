"""
Author:小鱼
Description: 启动仿真环境并同时启动导航的launch文件
"""
import os
from typing import List

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
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
    ]


def generate_launch_description() -> LaunchDescription:
    """生成启动描述：启动仿真环境 + 导航"""
    # 获取包路径
    airobot_simulation_dir = get_package_path('airobot_simulation')
    airobot_navigation2_dir = get_package_path('airobot_navigation2')
    nav2_bringup_dir = get_package_path('nav2_bringup')

    # 声明启动参数
    launch_args = declare_launch_arguments()

    # 获取配置参数
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    namespace = LaunchConfiguration('namespace')
    launch_rviz = LaunchConfiguration('launch_rviz')

    # ============================== 1. 仿真环境启动 ==============================
    # 导入gazebo_sim.launch.py
    gazebo_sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(airobot_simulation_dir, 'launch', 'gazebo_sim.launch.py')
        ),
    )

    # ============================== 2. 导航启动 ==============================
    # 地图和参数文件路径
    map_yaml_path = os.path.join(
        airobot_navigation2_dir,
        'maps',
        'airobot_map.yaml'
    )
    nav2_param_path = os.path.join(
        airobot_navigation2_dir,
        'param',
        'airobot_nav2.yaml'
    )
    rviz_config_dir = os.path.join(
        nav2_bringup_dir,
        'rviz',
        'nav2_default_view.rviz'
    )

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

    # 可选:启动rviz2节点
    from launch.conditions import IfCondition
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen',
        condition=IfCondition(launch_rviz),
    )

    # ============================== 3. 返回启动描述 ==============================
    return LaunchDescription(
        launch_args + [gazebo_sim_launch, nav2_bringup_launch, rviz_node]
    )
