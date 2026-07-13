#!/usr/bin/env python3

import json

import rclpy
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseStamped, Twist
from nav2_msgs.action import FollowPath
from nav_msgs.msg import Path
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from std_srvs.srv import Trigger


class RoutePathFollower(Node):
    def __init__(self):
        super().__init__("route_path_follower")
        self.route_file = self.declare_parameter(
            "route_file", "/tmp/uika_active_route.json"
        ).value
        self.action_name = self.declare_parameter("action_name", "/follow_path").value
        self.controller_id = self.declare_parameter(
            "controller_id", "FollowPath"
        ).value
        self.goal_checker_id = self.declare_parameter(
            "goal_checker_id", "general_goal_checker"
        ).value
        self.stop_topic = self.declare_parameter(
            "stop_topic", "/nav_cmd_vel_test"
        ).value

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.path_pub = self.create_publisher(
            Path, "/execution_route", latched_qos
        )
        self.status_pub = self.create_publisher(
            String, "/route_follow_status", latched_qos
        )
        self.stop_pub = self.create_publisher(Twist, self.stop_topic, 10)
        self.action_client = ActionClient(self, FollowPath, self.action_name)
        self.goal_handle = None
        self.start_pending = False

        self.create_service(Trigger, "~/start", self.start_callback)
        self.create_service(Trigger, "~/stop", self.stop_callback)
        self.create_service(Trigger, "~/reload", self.reload_callback)
        self.create_timer(0.2, self.maybe_start)
        self.publish_status("IDLE")

    def load_route(self):
        try:
            with open(self.route_file, "r", encoding="utf-8") as stream:
                data = json.load(stream)
        except (OSError, ValueError) as error:
            raise RuntimeError(f"Cannot load route {self.route_file}: {error}") from error

        poses = data.get("poses", [])
        if len(poses) < 2:
            raise RuntimeError("Saved route contains fewer than two path points")

        now = self.get_clock().now().to_msg()
        path = Path()
        path.header.frame_id = data.get("frame_id", "map")
        path.header.stamp = now
        for item in poses:
            pose = PoseStamped()
            pose.header.frame_id = path.header.frame_id
            pose.header.stamp = now
            position = item["position"]
            orientation = item["orientation"]
            pose.pose.position.x = float(position["x"])
            pose.pose.position.y = float(position["y"])
            pose.pose.position.z = float(position.get("z", 0.0))
            pose.pose.orientation.x = float(orientation.get("x", 0.0))
            pose.pose.orientation.y = float(orientation.get("y", 0.0))
            pose.pose.orientation.z = float(orientation.get("z", 0.0))
            pose.pose.orientation.w = float(orientation.get("w", 1.0))
            path.poses.append(pose)
        return path

    def start_callback(self, _request, response):
        if self.goal_handle is not None:
            response.success = False
            response.message = "A route is already active"
            return response
        try:
            path = self.load_route()
        except RuntimeError as error:
            response.success = False
            response.message = str(error)
            return response
        if not self.action_client.server_is_ready():
            response.success = False
            response.message = "FollowPath action server is not active"
            return response
        self.pending_path = path
        self.path_pub.publish(path)
        self.start_pending = True
        response.success = True
        response.message = f"Starting route with {len(path.poses)} path points"
        return response

    def maybe_start(self):
        if not self.start_pending:
            return
        self.start_pending = False
        goal = FollowPath.Goal()
        goal.path = self.pending_path
        goal.controller_id = self.controller_id
        goal.goal_checker_id = self.goal_checker_id
        self.publish_status("STARTING")
        future = self.action_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as error:
            self.publish_status(f"FAILED: {error}")
            return
        if not goal_handle.accepted:
            self.publish_status("FAILED: controller rejected route")
            return
        self.goal_handle = goal_handle
        self.publish_status("FOLLOWING")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        try:
            status = future.result().status
        except Exception as error:
            self.publish_status(f"FAILED: {error}")
            self.goal_handle = None
            return
        if status == GoalStatus.STATUS_SUCCEEDED:
            self.publish_status("SUCCEEDED")
        elif status == GoalStatus.STATUS_CANCELED:
            self.publish_status("CANCELED")
        else:
            self.publish_status(f"FAILED: action status {status}")
        self.goal_handle = None
        self.stop_pub.publish(Twist())

    def stop_callback(self, _request, response):
        self.start_pending = False
        self.stop_pub.publish(Twist())
        if self.goal_handle is None:
            response.success = True
            response.message = "No active route; zero velocity published"
            self.publish_status("IDLE")
            return response
        self.goal_handle.cancel_goal_async()
        response.success = True
        response.message = "Route cancel requested; zero velocity published"
        self.publish_status("CANCELING")
        return response

    def reload_callback(self, _request, response):
        try:
            path = self.load_route()
        except RuntimeError as error:
            response.success = False
            response.message = str(error)
            return response
        self.path_pub.publish(path)
        response.success = True
        response.message = f"Loaded {len(path.poses)} path points"
        return response

    def publish_status(self, status):
        message = String()
        message.data = status
        self.status_pub.publish(message)
        self.get_logger().info(status)


def main(args=None):
    rclpy.init(args=args)
    node = RoutePathFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_pub.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
