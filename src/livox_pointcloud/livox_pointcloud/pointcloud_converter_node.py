#!/usr/bin/env python3
"""
Livox PointCloud Converter Node

Converts Livox pointcloud from points_raw format to standard PointCloud2 format.
This node handles:
1. Receiving livox/points_raw (custom Livox format)
2. Converting to standard sensor_msgs/PointCloud2 (livox/points)
3. Publishing for downstream processing (DLIO, 3D to 2D conversion)
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header


class LivoxPointCloudConverter(Node):
    """Livox PointCloud Converter - converts points_raw to points"""
    
    def __init__(self, node_name='livox_pointcloud_converter'):
        super().__init__(node_name)
        
        # Declare parameters
        self.declare_parameter('input_topic', '/livox/points_raw')
        self.declare_parameter('output_topic', '/livox/points')
        self.declare_parameter('frame_id', 'livox_frame')
        
        # Get parameters
        self.input_topic = self.get_parameter('input_topic').value
        self.output_topic = self.get_parameter('output_topic').value
        self.frame_id = self.get_parameter('frame_id').value
        
        # Subscribers
        self.sub_points_raw = self.create_subscription(
            PointCloud2,
            self.input_topic,
            self.points_raw_callback,
            10
        )
        
        # Publishers
        self.pub_points = self.create_publisher(
            PointCloud2,
            self.output_topic,
            10
        )
        
        self.get_logger().info(f'Livox PointCloud Converter started')
        self.get_logger().info(f'  Input:  {self.input_topic}')
        self.get_logger().info(f'  Output: {self.output_topic}')
        
    def points_raw_callback(self, msg: PointCloud2):
        """Callback for receiving pointcloud data"""
        field_names = [f.name for f in msg.fields]
        
        # Check if already has standard x, y, z fields
        if 'x' in field_names and 'y' in field_names and 'z' in field_names:
            out_msg = PointCloud2()
            out_msg.header = Header()
            out_msg.header.stamp = self.get_clock().now().to_msg()
            out_msg.header.frame_id = self.frame_id
            out_msg.height = msg.height
            out_msg.width = msg.width
            out_msg.fields = msg.fields
            out_msg.is_bigendian = msg.is_bigendian
            out_msg.point_step = msg.point_step
            out_msg.row_step = msg.row_step
            out_msg.data = msg.data
            out_msg.is_dense = msg.is_dense
            self.pub_points.publish(out_msg)
        else:
            # Custom format - forward as-is
            out_msg = PointCloud2()
            out_msg.header = Header()
            out_msg.header.stamp = self.get_clock().now().to_msg()
            out_msg.header.frame_id = self.frame_id
            out_msg.height = msg.height
            out_msg.width = msg.width
            out_msg.fields = msg.fields
            out_msg.is_bigendian = msg.is_bigendian
            out_msg.point_step = msg.point_step
            out_msg.row_step = msg.row_step
            out_msg.data = msg.data
            out_msg.is_dense = msg.is_dense
            self.pub_points.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = LivoxPointCloudConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
