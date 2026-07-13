#!/usr/bin/env python3

import argparse
import sys
import time

import rclpy
from action_msgs.srv import CancelGoal
from geometry_msgs.msg import Twist


DEFAULT_CANCEL_SERVICES = [
    "/navigate_to_pose/_action/cancel_goal",
    "/navigate_through_poses/_action/cancel_goal",
    "/follow_path/_action/cancel_goal",
]


def cancel_service(node, service_name, timeout_sec):
    client = node.create_client(CancelGoal, service_name)
    if not client.wait_for_service(timeout_sec=timeout_sec):
        node.get_logger().warn(f"{service_name} is not available")
        return False

    request = CancelGoal.Request()
    # Zero UUID + zero timestamp means cancel all goals for this action server.
    request.goal_info.goal_id.uuid = [0] * 16
    request.goal_info.stamp.sec = 0
    request.goal_info.stamp.nanosec = 0

    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future, timeout_sec=timeout_sec)
    if not future.done() or future.result() is None:
        node.get_logger().warn(f"{service_name} cancel request timed out")
        return False

    response = future.result()
    if response.return_code == CancelGoal.Response.ERROR_NONE:
        node.get_logger().info(
            f"{service_name}: cancel accepted for {len(response.goals_canceling)} goal(s)"
        )
        return True

    if response.return_code == CancelGoal.Response.ERROR_REJECTED:
        reason = "rejected"
    elif response.return_code == CancelGoal.Response.ERROR_UNKNOWN_GOAL_ID:
        reason = "unknown goal"
    elif response.return_code == CancelGoal.Response.ERROR_GOAL_TERMINATED:
        reason = "goal already terminal"
    else:
        reason = f"return_code={response.return_code}"
    node.get_logger().warn(f"{service_name}: no active goal canceled ({reason})")
    return False


def publish_stop(node, topics, duration_sec, rate_hz):
    pubs = [
        node.create_publisher(Twist, topic, 10)
        for topic in topics
        if topic
    ]
    if not pubs:
        return

    stop = Twist()
    end_time = time.monotonic() + duration_sec
    period = 1.0 / rate_hz
    while time.monotonic() < end_time:
        for pub in pubs:
            pub.publish(stop)
        rclpy.spin_once(node, timeout_sec=0.0)
        time.sleep(period)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Cancel active Nav2 goals and publish a short zero-velocity stop command."
    )
    parser.add_argument(
        "--cancel-service",
        action="append",
        dest="cancel_services",
        default=[],
        help="CancelGoal service to call. Can be passed multiple times.",
    )
    parser.add_argument(
        "--stop-topic",
        action="append",
        dest="stop_topics",
        default=["/cmd_vel", "/nav_cmd_vel_test"],
        help="Twist topic to publish zero velocity to. Can be passed multiple times.",
    )
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--stop-duration", type=float, default=0.5)
    parser.add_argument("--stop-rate", type=float, default=20.0)
    args = parser.parse_args(argv)

    cancel_services = args.cancel_services or DEFAULT_CANCEL_SERVICES

    rclpy.init(args=argv)
    node = rclpy.create_node("cancel_nav_goal")
    try:
        canceled_any = False
        for service_name in cancel_services:
            canceled_any = cancel_service(node, service_name, args.timeout) or canceled_any
        publish_stop(node, args.stop_topics, args.stop_duration, args.stop_rate)
        return 0 if canceled_any else 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
