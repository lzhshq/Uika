#!/usr/bin/env python3
"""Publish a nav_msgs/Path from a TF frame's traveled poses."""

from __future__ import annotations

import math

import rclpy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path
from rclpy.node import Node
from tf2_ros import Buffer, TransformException, TransformListener


class TfPathPublisher(Node):
    def __init__(self) -> None:
        super().__init__("tf_path_publisher")
        self.declare_parameter("target_frame", "map")
        self.declare_parameter("source_frame", "base_link")
        self.declare_parameter("path_topic", "/base_link_path")
        self.declare_parameter("publish_rate", 10.0)
        self.declare_parameter("min_distance", 0.02)
        self.declare_parameter("max_poses", 20000)

        self.target_frame = str(self.get_parameter("target_frame").value)
        self.source_frame = str(self.get_parameter("source_frame").value)
        self.min_distance = max(float(self.get_parameter("min_distance").value), 0.0)
        self.max_poses = max(int(self.get_parameter("max_poses").value), 1)
        path_topic = str(self.get_parameter("path_topic").value)

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.path_pub = self.create_publisher(Path, path_topic, 10)
        self.path = Path()
        self.path.header.frame_id = self.target_frame
        self.last_xyz: tuple[float, float, float] | None = None

        publish_rate = max(float(self.get_parameter("publish_rate").value), 1.0)
        self.timer = self.create_timer(1.0 / publish_rate, self.on_timer)
        self.get_logger().info(
            f"Publishing {self.source_frame} trajectory as {path_topic} in {self.target_frame}"
        )

    def on_timer(self) -> None:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.target_frame,
                self.source_frame,
                rclpy.time.Time(),
            )
        except TransformException:
            return

        translation = transform.transform.translation
        xyz = (float(translation.x), float(translation.y), float(translation.z))
        if self.last_xyz is not None and self.distance(self.last_xyz, xyz) < self.min_distance:
            self.publish_existing_path(transform.header.stamp)
            return

        pose = PoseStamped()
        pose.header.stamp = transform.header.stamp
        pose.header.frame_id = self.target_frame
        pose.pose.position.x = xyz[0]
        pose.pose.position.y = xyz[1]
        pose.pose.position.z = xyz[2]
        pose.pose.orientation = transform.transform.rotation

        self.path.poses.append(pose)
        if len(self.path.poses) > self.max_poses:
            self.path.poses = self.path.poses[-self.max_poses :]
        self.last_xyz = xyz
        self.publish_existing_path(pose.header.stamp)

    def publish_existing_path(self, stamp) -> None:
        self.path.header.stamp = stamp
        self.path.header.frame_id = self.target_frame
        self.path_pub.publish(self.path)

    @staticmethod
    def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return math.sqrt(
            (a[0] - b[0]) * (a[0] - b[0])
            + (a[1] - b[1]) * (a[1] - b[1])
            + (a[2] - b[2]) * (a[2] - b[2])
        )


def main() -> None:
    rclpy.init()
    node = TfPathPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
