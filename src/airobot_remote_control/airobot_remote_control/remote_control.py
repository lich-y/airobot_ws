#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys


class RemoteControlNode(Node):
    """Remote control node for sending velocity commands to the robot."""
    
    def __init__(self):
        super().__init__('remote_control')
        
        # 创建cmd_vel发布者
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.get_logger().info('Remote control node initialized')
        self.get_logger().info('Use the web interface to control the robot')
        
    def publish_velocity(self, linear_x: float, angular_z: float):
        """Publish velocity command to the robot."""
        twist = Twist()
        twist.linear.x = linear_x
        twist.angular.z = angular_z
        self.cmd_vel_publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    
    node = RemoteControlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
