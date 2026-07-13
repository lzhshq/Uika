#!/usr/bin/env bash

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DURATION="${1:-10}"
LOG_DIR="/tmp/uika_rate_check/$(date +%Y%m%d_%H%M%S)"

if ! [[ "${DURATION}" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Usage: $0 [seconds_per_topic]" >&2
  exit 2
fi

set +u
source /opt/ros/humble/setup.bash
[[ -f "${ROOT_DIR}/Quadruped_Uika/install/setup.bash" ]] && \
  source "${ROOT_DIR}/Quadruped_Uika/install/setup.bash"
[[ -f "${ROOT_DIR}/point_lio/install/setup.bash" ]] && \
  source "${ROOT_DIR}/point_lio/install/setup.bash"
set -u

mkdir -p "${LOG_DIR}"

topics=(
  /motor_command
  /motor_feedback
  /imu/data
  /livox/lidar
  /livox/imu
  /aft_mapped_to_init
)
labels=(
  "control command"
  "motor feedback"
  "body IMU"
  "MID360 LiDAR"
  "MID360 IMU"
  "Point-LIO odometry"
)
targets=(200 200 200 10 200 10)
minimums=(190 190 190 9.5 190 9.0)

echo "Uika full-stack frequency check"
echo "Each topic: ${DURATION}s; logs: ${LOG_DIR}"
echo "The strategy, hardware driver, MID360 driver and Point-LIO must already be running."
echo

failed=0
for i in "${!topics[@]}"; do
  topic="${topics[$i]}"
  label="${labels[$i]}"
  log="${LOG_DIR}/$(echo "${topic#/}" | tr '/' '_').log"

  if ! timeout 3 ros2 topic info "${topic}" 2>/dev/null | grep -q "Publisher count: [1-9]"; then
    printf "FAIL  %-22s %-24s no publisher\n" "${label}" "${topic}"
    failed=1
    continue
  fi

  timeout "${DURATION}" ros2 topic hz "${topic}" --window 2000 >"${log}" 2>&1 || true
  rate="$(awk '/average rate:/ {value=$3} END {print value}' "${log}")"
  if [[ -z "${rate}" ]]; then
    printf "FAIL  %-22s %-24s no samples\n" "${label}" "${topic}"
    failed=1
    continue
  fi

  if awk -v value="${rate}" -v minimum="${minimums[$i]}" 'BEGIN {exit !(value >= minimum)}'; then
    printf "PASS  %-22s %-24s %7.2f Hz  target=%g\n" \
      "${label}" "${topic}" "${rate}" "${targets[$i]}"
  else
    printf "FAIL  %-22s %-24s %7.2f Hz  minimum=%g target=%g\n" \
      "${label}" "${topic}" "${rate}" "${minimums[$i]}" "${targets[$i]}"
    failed=1
  fi
done

echo
echo "Process CPU snapshot:"
ps -eo pid,psr,pcpu,pmem,comm,args --sort=-pcpu | \
  grep -E 'pointlio_mapping|livox_ros_driver2|rl_real_uika|rs00_motor|yesense_node' | \
  grep -v grep | head -20 || true

echo
echo "Check the strategy terminal for both lines every 5 seconds:"
echo "  [Loop] Rate - name: loop_control, avg_hz: about 200"
echo "  [Loop] Rate - name: loop_rl,      avg_hz: about 50"

if [[ "${failed}" -ne 0 ]]; then
  echo "RESULT: FAIL"
  exit 1
fi

echo "RESULT: PASS"
