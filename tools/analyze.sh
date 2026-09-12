#!/usr/bin/env sh
set -eu
ROOT=${1:-.}
BASE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ -x "$BASE/bin/acr-toolbox" ]; then
  exec "$BASE/bin/acr-toolbox" analyze "$ROOT"
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$BASE/common/small/analyze-and-recommend/script/analyze_and_recommend.py" "$ROOT"
fi
if command -v python >/dev/null 2>&1; then
  exec python "$BASE/common/small/analyze-and-recommend/script/analyze_and_recommend.py" "$ROOT"
fi
echo "No usable analyzer found. Download a prebuilt acr-toolbox binary or install Python 3." >&2
exit 2
