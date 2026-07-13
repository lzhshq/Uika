#!/usr/bin/env python3

import copy
import json
import os

import rclpy
from action_msgs.msg import GoalStatus
from nav2_msgs.action import ComputePathThroughPoses
from nav_msgs.msg import Path
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from geometry_msgs.msg import PoseStamped
from std_srvs.srv import Empty, Trigger
from visualization_msgs.msg import Marker, MarkerArray


class RoutePosePlanner(Node):
    def __init__(self):
        super().__init__("route_pose_planner")

        self.map_frame = self.declare_parameter("map_frame", "map").value
        self.pose_topic = self.declare_parameter("pose_topic", "/route_pose").value
        self.path_topic = self.declare_parameter("path_topic", "/route_plan").value
        self.marker_topic = self.declare_parameter(
            "marker_topic", "/route_waypoints"
        ).value
        self.action_name = self.declare_parameter(
            "action_name", "/compute_path_through_poses"
        ).value
        self.planner_id = self.declare_parameter("planner_id", "GridBased").value
        self.route_file = self.declare_parameter(
            "route_file", "/tmp/uika_active_route.json"
        ).value

        latched_qos = QoSProfile(depth=1)
        latched_qos.reliability = ReliabilityPolicy.RELIABLE
        latched_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.path_pub = self.create_publisher(Path, self.path_topic, latched_qos)
        self.marker_pub = self.create_publisher(
            MarkerArray, self.marker_topic, latched_qos
        )
        self.create_subscription(PoseStamped, self.pose_topic, self.pose_callback, 10)
        self.create_service(Empty, "~/clear", self.clear_callback)
        self.create_service(Empty, "~/remove_last", self.remove_last_callback)
        self.create_service(Trigger, "~/replan", self.replan_callback)

        self.action_client = ActionClient(
            self, ComputePathThroughPoses, self.action_name
        )
        self.waypoints = []
        self.revision = 0
        self.plan_requested = False
        self.planning = False
        self.create_timer(0.25, self.maybe_plan)
        self.publish_markers()
        self.publish_empty_path()

        self.get_logger().info(
            f"Add route poses on {self.pose_topic}; continuous path is {self.path_topic}"
        )

    def pose_callback(self, message):
        if message.header.frame_id and message.header.frame_id != self.map_frame:
            self.get_logger().error(
                f"Expected pose frame {self.map_frame}, got {message.header.frame_id}"
            )
            return

        pose = copy.deepcopy(message)
        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        self.waypoints.append(pose)
        self.revision += 1
        self.plan_requested = True
        self.invalidate_saved_route()
        self.publish_markers()
        self.get_logger().info(
            f"Added route pose {len(self.waypoints)}: "
            f"x={pose.pose.position.x:.3f}, y={pose.pose.position.y:.3f}"
        )

    def maybe_plan(self):
        if self.planning or not self.plan_requested or not self.waypoints:
            return
        if not self.action_client.server_is_ready():
            return

        goal = ComputePathThroughPoses.Goal()
        goal.goals = copy.deepcopy(self.waypoints)
        goal.planner_id = self.planner_id
        goal.use_start = False

        request_revision = self.revision
        self.plan_requested = False
        self.planning = True
        future = self.action_client.send_goal_async(goal)
        future.add_done_callback(
            lambda result: self.goal_response_callback(result, request_revision)
        )

    def goal_response_callback(self, future, request_revision):
        try:
            goal_handle = future.result()
        except Exception as error:
            self.finish_failed_plan(f"Goal request failed: {error}")
            return

        if not goal_handle.accepted:
            self.finish_failed_plan("Planner rejected the route request")
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(
            lambda result: self.plan_result_callback(result, request_revision)
        )

    def plan_result_callback(self, future, request_revision):
        self.planning = False
        try:
            wrapped_result = future.result()
        except Exception as error:
            self.finish_failed_plan(f"Planner result failed: {error}")
            return

        if request_revision != self.revision:
            self.plan_requested = bool(self.waypoints)
            return

        path = wrapped_result.result.path
        if (
            wrapped_result.status != GoalStatus.STATUS_SUCCEEDED
            or not path.poses
        ):
            self.get_logger().warn(
                "No continuous path found through all selected route poses"
            )
            return

        path.header.frame_id = self.map_frame
        path.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(path)
        self.save_route(path)
        self.get_logger().info(
            f"Published continuous route through {len(self.waypoints)} pose(s), "
            f"{len(path.poses)} path points"
        )

    def finish_failed_plan(self, message):
        self.planning = False
        self.get_logger().warn(message)
        if self.waypoints:
            self.plan_requested = True

    def clear_callback(self, _request, response):
        self.waypoints.clear()
        self.revision += 1
        self.plan_requested = False
        self.publish_markers()
        self.invalidate_saved_route()
        self.get_logger().info("Cleared all route poses")
        return response

    def remove_last_callback(self, _request, response):
        if self.waypoints:
            self.waypoints.pop()
            self.revision += 1
        self.plan_requested = bool(self.waypoints)
        self.publish_markers()
        self.invalidate_saved_route()
        self.get_logger().info(f"Route now contains {len(self.waypoints)} pose(s)")
        return response

    def replan_callback(self, _request, response):
        if not self.waypoints:
            response.success = False
            response.message = "No route poses have been selected"
            return response
        self.plan_requested = True
        response.success = True
        response.message = f"Planning through {len(self.waypoints)} pose(s)"
        return response

    def publish_empty_path(self):
        path = Path()
        path.header.frame_id = self.map_frame
        path.header.stamp = self.get_clock().now().to_msg()
        self.path_pub.publish(path)

    def invalidate_saved_route(self):
        self.publish_empty_path()
        try:
            os.unlink(self.route_file)
        except FileNotFoundError:
            pass
        except OSError as error:
            self.get_logger().warn(f"Could not remove stale route file: {error}")

    def save_route(self, path):
        route = {
            "frame_id": self.map_frame,
            "poses": [
                {
                    "position": {
                        "x": pose.pose.position.x,
                        "y": pose.pose.position.y,
                        "z": pose.pose.position.z,
                    },
                    "orientation": {
                        "x": pose.pose.orientation.x,
                        "y": pose.pose.orientation.y,
                        "z": pose.pose.orientation.z,
                        "w": pose.pose.orientation.w,
                    },
                }
                for pose in path.poses
            ],
        }
        directory = os.path.dirname(self.route_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        temporary = self.route_file + ".tmp"
        try:
            with open(temporary, "w", encoding="utf-8") as stream:
                json.dump(route, stream, indent=2)
                stream.write("\n")
            os.replace(temporary, self.route_file)
        except OSError as error:
            self.get_logger().error(f"Could not save route: {error}")
            try:
                os.unlink(temporary)
            except OSError:
                pass

    def publish_markers(self):
        now = self.get_clock().now().to_msg()
        markers = MarkerArray()
        delete_all = Marker()
        delete_all.action = Marker.DELETEALL
        markers.markers.append(delete_all)

        line = Marker()
        line.header.frame_id = self.map_frame
        line.header.stamp = now
        line.ns = "route_waypoint_line"
        line.id = 0
        line.type = Marker.LINE_STRIP
        line.action = Marker.ADD
        line.scale.x = 0.035
        line.color.r = 1.0
        line.color.g = 0.55
        line.color.b = 0.05
        line.color.a = 0.9

        for index, waypoint in enumerate(self.waypoints, start=1):
            line.points.append(copy.deepcopy(waypoint.pose.position))

            arrow = Marker()
            arrow.header.frame_id = self.map_frame
            arrow.header.stamp = now
            arrow.ns = "route_waypoint_arrows"
            arrow.id = index
            arrow.type = Marker.ARROW
            arrow.action = Marker.ADD
            arrow.pose = copy.deepcopy(waypoint.pose)
            arrow.pose.position.z = 0.08
            arrow.scale.x = 0.30
            arrow.scale.y = 0.07
            arrow.scale.z = 0.07
            arrow.color.r = 0.1
            arrow.color.g = 0.85
            arrow.color.b = 1.0
            arrow.color.a = 1.0
            markers.markers.append(arrow)

            label = Marker()
            label.header.frame_id = self.map_frame
            label.header.stamp = now
            label.ns = "route_waypoint_labels"
            label.id = index
            label.type = Marker.TEXT_VIEW_FACING
            label.action = Marker.ADD
            label.pose.position = copy.deepcopy(waypoint.pose.position)
            label.pose.position.z = 0.30
            label.scale.z = 0.20
            label.color.r = 1.0
            label.color.g = 1.0
            label.color.b = 1.0
            label.color.a = 1.0
            label.text = str(index)
            markers.markers.append(label)

        if self.waypoints:
            markers.markers.append(line)
        self.marker_pub.publish(markers)


def main(args=None):
    rclpy.init(args=args)
    node = RoutePosePlanner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
