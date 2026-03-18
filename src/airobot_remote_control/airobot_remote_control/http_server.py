#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from flask import Flask, request, jsonify
import threading
import argparse


class CmdVelPublisher(Node):
    """ROS2节点，用于发布cmd_vel消息"""
    
    def __init__(self):
        super().__init__('http_cmd_vel_publisher')
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.current_linear = 0.0
        self.current_angular = 0.0
        self.get_logger().info('cmd_vel publisher initialized')
        
    def publish_velocity(self, linear_x: float, angular_z: float):
        """发布速度命令"""
        self.current_linear = linear_x
        self.current_angular = angular_z
        
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self.cmd_vel_publisher.publish(twist)
        
    def stop(self):
        """停止机器人"""
        self.publish_velocity(0.0, 0.0)


# 全局变量
ros_node = None
http_app = Flask(__name__)


@http_app.route('/cmd_vel', methods=['POST'])
def set_velocity():
    """接收HTTP POST请求设置速度"""
    try:
        data = request.get_json()
        linear = float(data.get('linear', 0))
        angular = float(data.get('angular', 0))
        
        if ros_node:
            ros_node.publish_velocity(linear, angular)
            return jsonify({'status': 'ok', 'linear': linear, 'angular': angular})
        else:
            return jsonify({'status': 'error', 'message': 'ROS2 not initialized'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@http_app.route('/stop', methods=['POST'])
def stop_robot():
    """停止机器人"""
    try:
        if ros_node:
            ros_node.stop()
            return jsonify({'status': 'ok'})
        else:
            return jsonify({'status': 'error', 'message': 'ROS2 not initialized'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@http_app.route('/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    if ros_node:
        return jsonify({
            'status': 'ok',
            'linear': ros_node.current_linear,
            'angular': ros_node.current_angular
        })
    else:
        return jsonify({'status': 'error', 'message': 'ROS2 not initialized'}), 500


@http_app.route('/')
def index():
    """主页 - 返回遥控器HTML"""
    import os
    # 查找web目录下的index.html
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', 'web', 'index.html'),
        os.path.join(os.path.dirname(__file__), '..', '..', 'web', 'index.html'),
        '/data/code/airobot_ws/src/airobot_remote_control/web/index.html',
        '/data/code/airobot_ws/install/airobot_remote_control/share/airobot_remote_control/web/index.html',
    ]
    
    for path in possible_paths:
        path = os.path.abspath(path)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/html'}
    
    return '<html><body><h1>404 - 页面未找到</h1><p>请使用 file:// 协议打开 Web 界面</p></body></html>', 404


def run_flask(port=5000):
    """运行Flask HTTP服务器"""
    http_app.run(host='0.0.0.0', port=port, debug=False)


def main(args=None):
    global ros_node
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='HTTP ROS2 Remote Control Server')
    parser.add_argument('--port', type=int, default=5000, help='HTTP server port')
    parsed_args, unknown = parser.parse_known_args(args)
    
    # 初始化ROS2
    rclpy.init(args=unknown)
    ros_node = CmdVelPublisher()
    
    # 在后台运行Flask服务器
    server_thread = threading.Thread(target=run_flask, args=(parsed_args.port,), daemon=True)
    server_thread.start()
    
    print("=" * 50)
    print("HTTP ROS2 遥控器服务已启动")
    print(f"服务地址: http://localhost:{parsed_args.port}")
    print("API 端点:")
    print("  POST /cmd_vel   - 设置线速度和角速度")
    print("  POST /stop     - 停止机器人")
    print("  GET  /status   - 获取当前状态")
    print("=" * 50)
    
    try:
        # 保持节点运行
        rclpy.spin(ros_node)
    except KeyboardInterrupt:
        pass
    finally:
        if ros_node:
            ros_node.stop()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
