#!/bin/sh
# Start FalkorDB on loopback only, then the query service in the foreground.
set -eu
mkdir -p "${FALKORDB_DATA_PATH}"
# shellcheck disable=SC2086
redis-server --bind 127.0.0.1 --port "${FALKORDB_PORT}" --protected-mode yes \
  --save "" --appendonly no --dir "${FALKORDB_DATA_PATH}" \
  --loadmodule "${FALKORDB_BIN_PATH}/falkordb.so" ${FALKORDB_ARGS} &
exec /opt/graph/bin/python /opt/graph/app/service.py
