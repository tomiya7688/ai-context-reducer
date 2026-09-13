#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p dist
PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python
fi
"$PYTHON_BIN" -m zipapp . -m "affected_tests:main" -o dist/affected-tests.pyz -p "/usr/bin/env python3"
echo "built: $(pwd)/dist/affected-tests.pyz"
