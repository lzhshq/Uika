#!/usr/bin/env python3
import argparse
import sys
from typing import List, Tuple

import rclpy
from nav2_msgs.action import ComputePathToPose
from rclpy.action import ActionClient
from rclpy.node import Node


DEFAULT_GOALS = "0.5,0.0;0.0,0.5;-0.5,0.0;0.0,-0.5;1.0,0.0"


def parse_goals(raw: str) -> List[Tuple[float, float]]:
    goals = []
    for item in raw.split(";"):
        item = item.strip()
        if not item:
            continue
        parts = [part.strip() for part in item.split(",")]
        if len(parts) != 2:
            raise ValueError(f"Invalid goal '{item}', expected x,y")
        goals.append((float(parts[0]), float(parts[1])))
    if not goals:
        raise ValueError("No goals provided")
    return goals


class NavGoalSmokeTester(Node):
    def __init__(self, action_name: str, planner_id: str, frame_id: str, timeout_sec: float):
        super().__init__("nav_goal_smoke_test")
        self.client = ActionClient(self, ComputePathToPose, action_name)
        self.planner_id = planner_id
        self.frame_id = frame_id
        self.timeout_sec = timeout_sec

    def wait_for_server(self) -> bool:
        self.get_logger().info(f"waiting for {self.client._action_name}")
        return self.client.wait_for_server(timeout_sec=self.timeout_sec)

    def test_goal(self, x: float, y: float) -> Tuple[str, int, float]:
        goal = ComputePathToPose.Goal()
        goal.goal.header.frame_id = self.frame_id
        goal.goal.pose.position.x = x
        goal.goal.pose.position.y = y
        goal.goal.pose.orientation.w = 1.0
        goal.planner_id = self.planner_id
        goal.use_start = False

        send_future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send_future, timeout_sec=self.timeout_sec)
        if not send_future.done():
            return ("TIMEOUT_SEND", 0, 0.0)

        handle = send_future.result()
        if handle is None or not handle.accepted:
            return ("REJECTED", 0, 0.0)

        result_future = handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=self.timeout_sec)
        if not result_future.done():
            return ("TIMEOUT_RESULT", 0, 0.0)

        wrapped = result_future.result()
        status = int(wrapped.status)
        result = wrapped.result
        pose_count = len(result.path.poses)
        planning_time = result.planning_time.sec + result.planning_time.nanosec / 1e9
        state = "SUCCEEDED" if status == 4 and pose_count > 0 else f"FAILED_STATUS_{status}"
        return (state, pose_count, planning_time)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run planner smoke tests against Nav2 /compute_path_to_pose."
    )
    parser.add_argument(
        "--goals",
        default=DEFAULT_GOALS,
        help="Semicolon-separated x,y goals. Example: '0.5,0.0;0.0,0.5'",
    )
    parser.add_argument("--action", default="/compute_path_to_pose")
    parser.add_argument("--planner-id", default="GridBased")
    parser.add_argument("--frame-id", default="map")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument(
        "--expect",
        default="",
        help="Optional semicolon-separated expected states, e.g. 'SUCCEEDED;SUCCEEDED;FAILED'.",
    )
    args = parser.parse_args()

    try:
        goals = parse_goals(args.goals)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    expected = [item.strip().upper() for item in args.expect.split(";") if item.strip()]
    if expected and len(expected) != len(goals):
        print("error: --expect count must match --goals count", file=sys.stderr)
        return 2

    rclpy.init()
    node = NavGoalSmokeTester(args.action, args.planner_id, args.frame_id, args.timeout)
    try:
        if not node.wait_for_server():
            print(f"ERROR action server unavailable: {args.action}", file=sys.stderr)
            return 1

        failures = 0
        print("goal_x,goal_y,state,path_poses,planning_time_sec")
        for index, (x, y) in enumerate(goals):
            state, pose_count, planning_time = node.test_goal(x, y)
            print(f"{x:.3f},{y:.3f},{state},{pose_count},{planning_time:.6f}")
            if expected:
                want = expected[index]
                ok = state == want or (want == "FAILED" and state != "SUCCEEDED")
                if not ok:
                    failures += 1

        return 1 if failures else 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
