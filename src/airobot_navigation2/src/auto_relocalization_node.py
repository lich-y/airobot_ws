#!/usr/bin/env python3
"""
Author: 小鱼
Description: 自动重定位节点 - 监听初始位姿话题，触发AMCL重新定位
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseWithCovarianceStamped
from std_srvs.srv import Empty


class AutoRelocalizationNode(Node):
    """
    自动重定位节点
    
    功能：
    - 监听 /initialpose 话题（用户在RViz中使用2D Pose Estimate设置位姿）
    - 当收到新位姿时，触发AMCL的reinitialize_global_localization服务
    - 帮助AMCL更快地收敛到正确的位置
    """
    
    def __init__(self):
        super().__init__('auto_relocalization')
        
        # QoS配置 - 需要与initialpose话题兼容
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        # 声明参数
        self.declare_parameter('initial_pose_topic', '/initialpose')
        self.declare_parameter('amcl_service_name', '/amcl/reinitialize_global_localization')
        self.declare_parameter('delay_after_pose', 0.5)  # 设置位姿后延迟触发重定位(秒)
        
        # 获取参数
        self.initial_pose_topic = self.get_parameter('initial_pose_topic').value
        self.amcl_service_name = self.get_parameter('amcl_service_name').value
        self.delay_after_pose = self.get_parameter('delay_after_pose').value
        
        # 创建订阅者 - 监听初始位姿
        self.initial_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            self.initial_pose_topic,
            self.on_initial_pose_received,
            qos_profile
        )
        
        # 创建AMCL重新定位服务的客户端
        self.amcl_client = self.create_client(Empty, self.amcl_service_name)
        
        # 标志位 - 防止重复触发
        self.is_processing = False
        self._timer = None
        
        self.get_logger().info(f'自动重定位节点已启动')
        self.get_logger().info(f'  监听话题: {self.initial_pose_topic}')
        self.get_logger().info(f'  AMCL服务: {self.amcl_service_name}')
        self.get_logger().info(f'  延迟时间: {self.delay_after_pose}s')
        
    def on_initial_pose_received(self, msg: PoseWithCovarianceStamped):
        """收到初始位姿时的回调函数"""
        if self.is_processing:
            self.get_logger().debug('正在处理上一次位姿，跳过本次')
            return
            
        self.is_processing = True
        
        # 打印收到的位姿信息
        pose = msg.pose.pose
        self.get_logger().info(
            f'收到新位姿: x={pose.position.x:.2f}, y={pose.position.y:.2f}, '
            f'z={pose.position.z:.2f}'
        )
        
        # 创建定时器，延迟后触发AMCL重定位
        # 这样可以确保位姿已经被AMCL接收处理
        self._timer = self.create_timer(self.delay_after_pose, self.trigger_relocalization)
        
    def trigger_relocalization(self):
        """触发AMCL重新定位"""
        # 取消定时器（只触发一次）
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        
        # 等待AMCL服务可用
        if not self.amcl_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().warn('AMCL重定位服务不可用，将在下一次位姿设置时重试')
            self.is_processing = False
            return
            
        # 创建请求并调用服务
        request = Empty.Request()
        future = self.amcl_client.call_async(request)
        
        # 异步处理结果
        future.add_done_callback(self.service_callback)
        
    def service_callback(self, future):
        """服务调用的回调函数"""
        try:
            result = future.result()
            self.get_logger().info('已触发AMCL重新定位，粒子将重新收敛')
        except Exception as e:
            self.get_logger().error(f'调用AMCL服务失败: {str(e)}')
        finally:
            self.is_processing = False


def main(args=None):
    rclpy.init(args=args)
    node = AutoRelocalizationNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
