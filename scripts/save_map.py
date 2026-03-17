#!/usr/bin/env python3
"""
ROS2 地图保存脚本
使用 nav2_map_server 保存地图
"""

import argparse
import os
import subprocess
import sys


def save_map(topic: str = 'map', output_path: str = '.', map_name: str = 'saved_map'):
    """
    保存 ROS2 地图
    
    Args:
        topic: 地图话题名称 (默认: 'map')
        output_path: 输出目录路径 (默认: 当前目录)
        map_name: 生成的地图文件名前缀 (默认: 'saved_map')
    """
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    # 完整输出路径
    full_path = os.path.join(output_path, map_name)
    
    # 构建命令
    cmd = [
        'ros2', 'run', 'nav2_map_server', 'map_saver_cli',
        '-t', topic,
        '-f', full_path
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    print(f"保存地图到: {full_path}.pgm 和 {full_path}.yaml")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("地图保存成功!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 地图保存失败", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("错误: 未找到 ros2 命令，请确保已安装 ROS2 并 source 环境", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='保存 ROS2 导航地图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 保存到当前目录，地图名为 my_map
  python3 save_map.py -n my_map
  
  # 保存到指定目录
  python3 save_map.py -o ~/maps -n office_map
  
  # 指定地图话题
  python3 save_map.py -t /scan_map -n laser_map
        '''
    )
    
    parser.add_argument(
        '-t', '--topic',
        type=str,
        default='map',
        help='地图话题名称 (默认: map)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='.',
        help='输出目录路径 (默认: 当前目录)'
    )
    
    parser.add_argument(
        '-n', '--name',
        type=str,
        default='saved_map',
        help='生成的地图文件名前缀 (默认: saved_map)'
    )
    
    args = parser.parse_args()
    
    success = save_map(
        topic=args.topic,
        output_path=args.output,
        map_name=args.name
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
