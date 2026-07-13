#!/bin/sh
set -eu

export LANG=C

LOG_FILE=/var/log/jetson-reset-reason.log
RESET_REASON=unavailable

for reason_file in \
    /sys/devices/platform/bus@0/c360000.pmc/reset_reason \
    /sys/devices/platform/c360000.pmc/reset_reason; do
    if [ -r "$reason_file" ]; then
        RESET_REASON=$(tr -d '\r\n' < "$reason_file")
        break
    fi
done

BOOT_ID=$(cat /proc/sys/kernel/random/boot_id)
UPTIME_SECONDS=$(cut -d' ' -f1 /proc/uptime)
POWER_CYCLES=unavailable
UNSAFE_SHUTDOWNS=unavailable

if command -v nvme >/dev/null 2>&1 && [ -e /dev/nvme0 ]; then
    SMART_LOG=$(nvme smart-log /dev/nvme0 2>/dev/null || true)
    POWER_CYCLES=$(printf '%s\n' "$SMART_LOG" | awk -F: '/^power_cycles/ {gsub(/[[:space:]]/, "", $2); print $2; exit}')
    UNSAFE_SHUTDOWNS=$(printf '%s\n' "$SMART_LOG" | awk -F: '/^unsafe_shutdowns/ {gsub(/[[:space:]]/, "", $2); print $2; exit}')
    [ -n "$POWER_CYCLES" ] || POWER_CYCLES=unavailable
    [ -n "$UNSAFE_SHUTDOWNS" ] || UNSAFE_SHUTDOWNS=unavailable
fi

MESSAGE="timestamp=$(date --iso-8601=seconds) boot_id=$BOOT_ID uptime_s=$UPTIME_SECONDS reset_reason=$RESET_REASON nvme_power_cycles=$POWER_CYCLES nvme_unsafe_shutdowns=$UNSAFE_SHUTDOWNS"

touch "$LOG_FILE"
chmod 0644 "$LOG_FILE"
printf '%s\n' "$MESSAGE" >> "$LOG_FILE"
logger -t jetson-reset-reason -- "$MESSAGE"
