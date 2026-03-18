#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory, get_package_prefix
from launch import LaunchDescription
from launch.actions import LogInfo, ExecuteProcess


def generate_launch_description():
    # 获取包路径
    pkg_name = 'airobot_remote_control'
    
    # 获取包前缀路径
    pkg_prefix = get_package_prefix(pkg_name)
    
    # 可执行文件路径 (ament_python 将可执行文件放在 bin 目录)
    exec_file = os.path.join(pkg_prefix, 'bin', 'remote_control_http')
    
    # Web界面路径
    web_path = os.path.join(pkg_prefix, 'share', pkg_name, 'web', 'index.html')
    
    # HTTP服务器端口
    http_port = 5000
    
    actions = []
    
    # 打印欢迎信息
    actions.append(LogInfo(msg='==========================================='))
    actions.append(LogInfo(msg='  机器人遥控器服务启动 (HTTP版)'))
    actions.append(LogInfo(msg='==========================================='))
    actions.append(LogInfo(msg=f'Web界面路径: file://{web_path}'))
    actions.append(LogInfo(msg=f'HTTP API服务器: http://localhost:{http_port}'))
    actions.append(LogInfo(msg='请在浏览器中打开 http://localhost:5000/ 访问遥控器'))
    actions.append(LogInfo(msg='==========================================='))
    
    # 使用ExecuteProcess直接执行可执行文件
    actions.append(ExecuteProcess(
        cmd=[exec_file, '--port', str(http_port)],
        output='screen',
        emulate_tty=True,
        shell=False
    ))
    
    return LaunchDescription(actions)
