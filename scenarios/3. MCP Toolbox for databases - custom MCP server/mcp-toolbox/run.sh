#!/bin/sh
set -e

sleep 3

MCP_PORT="${SCENARIO_3_MCP_TOOLBOX_PORT:-8093}"
UI_PORT="${SCENARIO_3_MCP_TOOLBOX_UI_PORT:-8082}"
TOOLBOX_URL="${TOOLBOX_URL:-${SCENARIO_3_MCP_TOOLBOX_URL:-http://127.0.0.1:${MCP_PORT}/mcp}}"

MCP_ARGS="--address 0.0.0.0 --port ${MCP_PORT} --toolbox-url ${TOOLBOX_URL}"
UI_ARGS="--address 0.0.0.0 --port ${UI_PORT} --ui --toolbox-url ${TOOLBOX_URL}"

start_toolbox() {
  if [ -d /app/config ]; then
    /app/toolbox --config-folder /app/config "$@" &
  else
    /app/toolbox --config tools.yaml "$@" &
  fi
}

start_toolbox $MCP_ARGS
TOOLBOX_PID=$!

start_toolbox $UI_ARGS
TOOLBOX_UI_PID=$!

trap 'kill "$TOOLBOX_PID" "$TOOLBOX_UI_PID" 2>/dev/null' INT TERM

# Coordinated shutdown of all processes if one fails
(
  wait "$TOOLBOX_UI_PID"
  kill -TERM "$TOOLBOX_PID" "$TOOLBOX_UI_PID" 2>/dev/null
) &

wait "$TOOLBOX_PID"
kill -TERM "$TOOLBOX_UI_PID" 2>/dev/null
wait "$TOOLBOX_UI_PID" 2>/dev/null || true
exit 1
