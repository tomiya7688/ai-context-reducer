#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python
fi
exec "$PYTHON_BIN" affected_tests.py "$@"
