#!/usr/bin/env bash

set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
JETSON_HOST="${JETSON_HOST:-jetson}"
JETSON_PROJECT="${JETSON_POINT_LIO_DIR:-/home/nvidia/Uika/point_lio}"

map_name="${1:-raogan_15m}"
route_name="${2:-raogan_15m_slalom.yaml}"
mode="${MODE:-dry-run}"
auto_start="${AUTO_START:-true}"
rviz="${RVIZ:-true}"
continuous_shadow="${CONTINUOUS_SHADOW:-false}"
relocalization_timeout="${RELOCALIZATION_TIMEOUT:-180}"

is_true() {
  [[ "${1,,}" == "true" || "$1" == "1" || "${1,,}" == "yes" ]]
}

shell_quote() {
  printf '%q' "$1"
}

run_from_pc() {
  local rviz_pid=""

  cleanup_pc() {
    if [[ -n "$rviz_pid" ]] && kill -0 "$rviz_pid" 2>/dev/null; then
      kill -TERM "$rviz_pid" 2>/dev/null || true
      wait "$rviz_pid" 2>/dev/null || true
    fi
  }
  trap cleanup_pc EXIT INT TERM

  if is_true "$rviz"; then
    if [[ -z "${DISPLAY:-}" ]]; then
      echo "DISPLAY is unavailable; continuing without RViz." >&2
    else
      set +u
      source /opt/ros/humble/setup.bash
      source "$PROJECT_DIR/install/setup.bash"
      set -u
      rviz2 -d "$PROJECT_DIR/rviz_cfg/relocalization_check.rviz" \
        >/tmp/uika_navigation_rviz.log 2>&1 &
      rviz_pid=$!
      sleep 1
      if ! kill -0 "$rviz_pid" 2>/dev/null; then
        echo "RViz failed to start:" >&2
        cat /tmp/uika_navigation_rviz.log >&2
        exit 1
      fi
    fi
  fi

  echo "Starting lightweight navigation on $JETSON_HOST"
  echo "  map:   $map_name"
  echo "  route: $route_name"
  echo "  mode:  $mode"

  local remote_command
  remote_command="MODE=$(shell_quote "$mode") "
  remote_command+="AUTO_START=$(shell_quote "$auto_start") "
  remote_command+="RVIZ=false "
  remote_command+="CONTINUOUS_SHADOW=$(shell_quote "$continuous_shadow") "
  remote_command+="RELOCALIZATION_TIMEOUT=$(shell_quote "$relocalization_timeout") "
  remote_command+="CONFIRM_LIVE=$(shell_quote "${CONFIRM_LIVE:-NO}") "
  remote_command+="$(shell_quote "$JETSON_PROJECT/start_navigation.sh") "
  remote_command+="$(shell_quote "$map_name") $(shell_quote "$route_name")"
  ssh -tt "$JETSON_HOST" "$remote_command"
}

resolve_map_path() {
  local value="$1"
  if [[ "$value" == */* ]]; then
    printf '%s\n' "$value"
  else
    value="${value%.pcd}"
    printf '%s/maps/%s.pcd\n' "$PROJECT_DIR" "$value"
  fi
}

resolve_route_path() {
  local value="$1"
  if [[ "$value" == */* ]]; then
    printf '%s\n' "$value"
  else
    [[ "$value" == *.yaml ]] || value="${value}.yaml"
    printf '%s/config/%s\n' "$PROJECT_DIR" "$value"
  fi
}

run_on_jetson() {
  local map_path route_path controller_dry_run bridge_dry_run
  local relocalization_pid="" tracking_pid=""

  map_path="$(resolve_map_path "$map_name")"
  route_path="$(resolve_route_path "$route_name")"

  case "$mode" in
    dry-run)
      controller_dry_run=true
      bridge_dry_run=true
      ;;
    bridge-test)
      controller_dry_run=false
      bridge_dry_run=true
      ;;
    live)
      if [[ "${CONFIRM_LIVE:-NO}" != "YES" ]]; then
        echo "MODE=live requires CONFIRM_LIVE=YES." >&2
        exit 2
      fi
      controller_dry_run=false
      bridge_dry_run=false
      ;;
    *)
      echo "Unknown MODE=$mode; use dry-run, bridge-test, or live." >&2
      exit 2
      ;;
  esac

  [[ -f "$map_path" ]] || { echo "Map not found: $map_path" >&2; exit 2; }
  [[ -f "$route_path" ]] || { echo "Route not found: $route_path" >&2; exit 2; }
  [[ "$relocalization_timeout" =~ ^[0-9]+$ ]] || {
    echo "RELOCALIZATION_TIMEOUT must be an integer." >&2
    exit 2
  }

  local route_map route_preview route_control_enabled
  route_map="$(sed -n 's/^[[:space:]]*pcd_file:[[:space:]]*//p' "$route_path" | head -n 1)"
  route_map="${route_map##*/}"
  route_preview="$(sed -n 's/^preview_only:[[:space:]]*//p' "$route_path" | head -n 1)"
  route_control_enabled="$(sed -n 's/^control_output_enabled:[[:space:]]*//p' "$route_path" | head -n 1)"
  if [[ -n "$route_map" && "$route_map" != "$(basename "$map_path")" ]]; then
    echo "Route/map mismatch: route expects $route_map, selected $(basename "$map_path")." >&2
    exit 2
  fi
  if [[ "$mode" == "live" &&
        ( "$route_preview" == "true" || "$route_control_enabled" != "true" ) ]]; then
    echo "Live mode rejected: route is preview-only or control output is not approved." >&2
    exit 2
  fi

  set +u
  source /opt/ros/humble/setup.bash
  source "$PROJECT_DIR/../livox_ws/install/setup.bash"
  source "$PROJECT_DIR/install/setup.bash"
  set -u

  local log_dir
  log_dir="/tmp/uika_lightweight_navigation/$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$log_dir"

  cleanup_jetson() {
    local exit_code=$?
    trap - EXIT INT TERM
    set +e
    if ros2 service type /fixed_path_controller/stop >/dev/null 2>&1; then
      timeout 3 ros2 service call \
        /fixed_path_controller/stop std_srvs/srv/Trigger '{}' >/dev/null 2>&1
    fi
    if [[ -n "$tracking_pid" ]] && kill -0 "$tracking_pid" 2>/dev/null; then
      kill -INT "$tracking_pid" 2>/dev/null
      wait "$tracking_pid" 2>/dev/null
    fi
    if [[ -n "$relocalization_pid" ]] && kill -0 "$relocalization_pid" 2>/dev/null; then
      kill -INT "$relocalization_pid" 2>/dev/null
      wait "$relocalization_pid" 2>/dev/null
    fi
    echo "Navigation stopped. Logs: $log_dir"
    exit "$exit_code"
  }
  trap cleanup_jetson EXIT INT TERM

  if pgrep -f '[m]id360_relocalization_bringup.launch.py|[s]lalom_no_nav2_tracking.launch.py|[f]ixed_start_relocalizer|[f]ixed_path_controller.py' >/dev/null; then
    echo "A relocalization or fixed-path process is already running." >&2
    exit 1
  fi

  systemctl --user stop uika-pointlio-live.service 2>/dev/null || true
  sleep 1
  if pgrep -f '[p]oint_lio.launch.py|[l]ivox_lidar_publisher|[l]ivox_ros_driver2' >/dev/null; then
    echo "A manual Point-LIO or MID360 driver process is already running." >&2
    echo "Stop that process before using the one-click navigation script." >&2
    exit 1
  fi

  echo "Stage 1/3: starting MID360, Point-LIO, and relocalization"
  stdbuf -oL -eL ros2 launch point_lio mid360_relocalization_bringup.launch.py \
    "map:=$map_path" \
    rviz:=false \
    "continuous_shadow:=$continuous_shadow" \
    > >(tee -a "$log_dir/relocalization.log") 2>&1 &
  relocalization_pid=$!

  sleep 3
  if ! kill -0 "$relocalization_pid" 2>/dev/null; then
    echo "Relocalization launch exited during startup." >&2
    exit 1
  fi

  echo "Stage 2/3: waiting up to ${relocalization_timeout}s for relocalization"
  local deadline=$((SECONDS + relocalization_timeout))
  local last_status=""
  local relocalization_ok=false
  while (( SECONDS < deadline )); do
    if ! kill -0 "$relocalization_pid" 2>/dev/null; then
      echo "Relocalization launch exited before success." >&2
      exit 1
    fi

    local success_sample
    success_sample="$(timeout 2 ros2 topic echo --once \
      --qos-durability transient_local \
      /relocalization/success std_msgs/msg/Bool 2>/dev/null || true)"
    if grep -Eq 'data:[[:space:]]+true' <<<"$success_sample"; then
      echo "Relocalization accepted. map -> odom is active."
      relocalization_ok=true
      break
    fi

    local status_sample
    status_sample="$(timeout 2 ros2 topic echo --once \
      --qos-durability transient_local \
      /relocalization/status std_msgs/msg/String 2>/dev/null || true)"
    if [[ -n "$status_sample" && "$status_sample" != "$last_status" ]]; then
      last_status="$status_sample"
      sed -n 's/^data: //p' <<<"$status_sample"
    fi
    sleep 1
  done

  if [[ "$relocalization_ok" != "true" ]]; then
    echo "Relocalization timed out; path tracking was not started." >&2
    exit 1
  fi

  echo "Stage 3/3: starting fixed-route tracking ($mode)"
  stdbuf -oL -eL ros2 launch point_lio slalom_no_nav2_tracking.launch.py \
    "route_file:=$route_path" \
    "controller_dry_run:=$controller_dry_run" \
    "bridge_dry_run:=$bridge_dry_run" \
    enable_bridge:=true \
    > >(tee -a "$log_dir/tracking.log") 2>&1 &
  tracking_pid=$!

  local service_deadline=$((SECONDS + 20))
  while (( SECONDS < service_deadline )); do
    if ros2 service type /fixed_path_controller/start >/dev/null 2>&1; then
      break
    fi
    if ! kill -0 "$tracking_pid" 2>/dev/null; then
      echo "Tracking launch exited during startup." >&2
      exit 1
    fi
    sleep 1
  done
  if ! ros2 service type /fixed_path_controller/start >/dev/null 2>&1; then
    echo "Fixed-path start service did not appear." >&2
    exit 1
  fi

  if is_true "$auto_start"; then
    sleep 1
    local start_response
    start_response="$(timeout 5 ros2 service call \
      /fixed_path_controller/start std_srvs/srv/Trigger '{}')"
    echo "$start_response"
    if ! grep -Eq 'success=True|success:[[:space:]]+true' <<<"$start_response"; then
      echo "Controller rejected automatic start; no velocity output is active." >&2
      exit 1
    fi
  else
    echo "Controller is ready but idle. Start it with:"
    echo "ros2 service call /fixed_path_controller/start std_srvs/srv/Trigger '{}'"
  fi

  echo "Lightweight navigation is running. Press Ctrl+C to stop."
  echo "  mode: $mode"
  echo "  logs: $log_dir"
  while kill -0 "$relocalization_pid" 2>/dev/null && \
        kill -0 "$tracking_pid" 2>/dev/null; do
    sleep 2
  done
  echo "A launch process exited unexpectedly." >&2
  exit 1
}

if [[ -f /etc/nv_tegra_release ]]; then
  run_on_jetson
else
  run_from_pc
fi
