#!/usr/bin/env sh
set -eu
ROOT="${1:-.}"
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
NATIVE="$SELF_DIR/common/native/acr-toolbox/dist/acr-toolbox"
PY_ANALYZE="$SELF_DIR/common/small/analyze-and-recommend/script/analyze_and_recommend.py"
PY_LANG="$SELF_DIR/common/small/language-environment-plan/script/language_environment_plan.py"

echo "[ai-context-reducer] environment"
if [ -x "$NATIVE" ]; then
  "$NATIVE" env
  echo "[ai-context-reducer] language environments"
  "$NATIVE" language-env
  echo "[ai-context-reducer] project analysis"
  "$NATIVE" analyze "$ROOT"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$PY_LANG"
  python3 "$PY_ANALYZE" "$ROOT"
elif command -v python >/dev/null 2>&1; then
  python "$PY_LANG"
  python "$PY_ANALYZE" "$ROOT"
else
  echo "No native acr-toolbox or Python runtime found." >&2
  echo "Use a prebuilt acr-toolbox binary for this OS/architecture." >&2
  exit 2
fi

echo "[ai-context-reducer] setup policy: enable only compatible language-specific tools; do not install missing runtimes automatically."
