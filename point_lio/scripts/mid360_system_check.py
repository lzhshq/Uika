#!/usr/bin/env python3
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def run_cmd(cmd: List[str], timeout: float = 5.0) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def result(name: str, ok: bool, detail: str, warn: bool = False) -> CheckResult:
    if ok:
        status = "OK"
    elif warn:
        status = "WARN"
    else:
        status = "FAIL"
    return CheckResult(name, status, detail.strip())


def check_nodes(required_nodes: List[str], timeout: float) -> CheckResult:
    proc = run_cmd(["ros2", "node", "list"], timeout=timeout)
    if proc.returncode != 0:
        return result("nodes", False, proc.stdout)
    nodes = set(line.strip() for line in proc.stdout.splitlines() if line.strip())
    missing = [node for node in required_nodes if node not in nodes]
    if missing:
        return result("nodes", False, "missing: " + ", ".join(missing), warn=True)
    return result("nodes", True, f"found {len(required_nodes)} required nodes")


def check_topics(required_topics: List[str], timeout: float) -> CheckResult:
    proc = run_cmd(["ros2", "topic", "list"], timeout=timeout)
    if proc.returncode != 0:
        return result("topics", False, proc.stdout)
    topics = set(line.strip() for line in proc.stdout.splitlines() if line.strip())
    missing = [topic for topic in required_topics if topic not in topics]
    if missing:
        return result("topics", False, "missing: " + ", ".join(missing), warn=True)
    return result("topics", True, f"found {len(required_topics)} required topics")


def parse_hz(output: str) -> Optional[float]:
    matches = re.findall(r"average rate:\s*([0-9.]+)", output)
    if not matches:
        return None
    return float(matches[-1])


def check_topic_hz(topic: str, min_hz: float, duration: float) -> CheckResult:
    proc = run_cmd(["timeout", str(duration), "ros2", "topic", "hz", topic], timeout=duration + 3.0)
    hz = parse_hz(proc.stdout)
    if hz is None:
        return result(f"hz {topic}", False, "no rate measured", warn=True)
    ok = hz >= min_hz
    return result(f"hz {topic}", ok, f"{hz:.3f} Hz, expected >= {min_hz:.3f}", warn=not ok)


def check_lifecycle(nodes: List[str], timeout: float) -> List[CheckResult]:
    results = []
    for node in nodes:
        proc = run_cmd(["ros2", "lifecycle", "get", node], timeout=timeout)
        text = proc.stdout.strip()
        ok = proc.returncode == 0 and text.startswith("active")
        results.append(result(f"lifecycle {node}", ok, text or "unavailable", warn=not ok))
    return results


def check_tf(source: str, target: str, timeout: float) -> CheckResult:
    proc = run_cmd(
        ["timeout", str(timeout), "ros2", "run", "tf2_ros", "tf2_echo", source, target],
        timeout=timeout + 2.0,
    )
    ok = "Translation:" in proc.stdout and "Rotation:" in proc.stdout
    detail = "transform available" if ok else "transform unavailable"
    return result(f"tf {source}->{target}", ok, detail, warn=not ok)


def check_param(node: str, param: str, expected: Optional[str], timeout: float) -> CheckResult:
    proc = run_cmd(["ros2", "param", "get", node, param], timeout=timeout)
    text = proc.stdout.strip()
    if proc.returncode != 0:
        return result(f"param {node}.{param}", False, text or "unavailable", warn=True)
    if expected is None:
        return result(f"param {node}.{param}", True, text)
    ok = text.lower().endswith(expected.lower())
    return result(f"param {node}.{param}", ok, text, warn=not ok)


def check_no_cmd_vel(timeout: float) -> CheckResult:
    proc = run_cmd(["timeout", str(timeout), "ros2", "topic", "echo", "/cmd_vel", "--once"], timeout=timeout + 2.0)
    no_type = "Could not determine the type" in proc.stdout
    no_topic = "does not appear to be published" in proc.stdout
    timed_out = proc.returncode == 124
    if no_type or no_topic:
        return result("dry_run /cmd_vel", True, "/cmd_vel is not published")
    if timed_out:
        return result("dry_run /cmd_vel", True, "no /cmd_vel message observed")
    return result("dry_run /cmd_vel", False, "a /cmd_vel message may have been published", warn=True)


def check_processes(pattern: str) -> CheckResult:
    proc = run_cmd(["ps", "-eo", "pid,pcpu,pmem,comm,args"], timeout=5.0)
    if proc.returncode != 0:
        return result("process resources", False, proc.stdout, warn=True)
    regex = re.compile(pattern)
    lines = []
    for line in proc.stdout.splitlines():
        if not regex.search(line):
            continue
        if "mid360_system_check.py" in line or " ps -eo " in line:
            continue
        lines.append(line)
    if not lines:
        return result("process resources", False, "no matching processes", warn=True)
    return result("process resources", True, "\n".join(lines[:12]))


def print_results(results: List[CheckResult]) -> None:
    for item in results:
        print(f"[{item.status}] {item.name}: {item.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the running MID360 + Point-LIO + Nav2 stack.")
    parser.add_argument("--hz-duration", type=float, default=6.0)
    parser.add_argument("--skip-hz", action="store_true")
    parser.add_argument("--skip-tf", action="store_true")
    parser.add_argument("--skip-cmd-vel-check", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on WARN or FAIL.")
    args = parser.parse_args()

    results: List[CheckResult] = []
    results.append(check_nodes([
        "/livox_lidar_publisher",
        "/laserMapping",
        "/cmd_vel_safety_bridge",
        "/map_server",
        "/controller_server",
        "/planner_server",
        "/bt_navigator",
    ], timeout=5.0))
    results.append(check_topics([
        "/livox/lidar",
        "/livox/imu",
        "/aft_mapped_to_init",
        "/scan",
        "/nav_cmd_vel_test",
        "/nav_cmd_vel_limited_debug",
    ], timeout=5.0))

    if not args.skip_hz:
        results.extend([
            check_topic_hz("/livox/lidar", 8.0, args.hz_duration),
            check_topic_hz("/livox/imu", 150.0, args.hz_duration),
            check_topic_hz("/aft_mapped_to_init", 4.0, args.hz_duration),
            check_topic_hz("/scan", 4.0, args.hz_duration),
        ])

    results.extend(check_lifecycle([
        "/map_server",
        "/controller_server",
        "/planner_server",
        "/bt_navigator",
    ], timeout=5.0))

    if not args.skip_tf:
        results.append(check_tf("map", "base_link", timeout=5.0))

    results.append(check_param("/cmd_vel_safety_bridge", "dry_run", "True", timeout=5.0))

    if not args.skip_cmd_vel_check:
        results.append(check_no_cmd_vel(timeout=2.0))

    results.append(check_processes(
        "livox_ros_driver2|pointlio_mapping|controller_server|planner_server|bt_navigator|map_server|cmd_vel_safety_bridge"
    ))

    print_results(results)

    if args.strict and any(item.status != "OK" for item in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
