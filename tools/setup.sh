#!/usr/bin/env sh
set -eu
ROOT="${1:-.}"
SELF_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ACR_ROOT=$(CDPATH= cd -- "$SELF_DIR/.." && pwd)
NATIVE="$SELF_DIR/common/native/acr-toolbox/dist/acr-toolbox"
PY_ANALYZE="$SELF_DIR/common/small/analyze-and-recommend/script/analyze_and_recommend.py"
PY_LANG="$SELF_DIR/common/small/language-environment-plan/script/language_environment_plan.py"
PY_LANG_SETUP="$SELF_DIR/common/small/language-setup/script/language_setup.py"
PY_LANG_RUN="$SELF_DIR/common/small/language-run/script/language_run.py"

echo "[ai-context-reducer] environment"
if [ -x "$NATIVE" ]; then
  "$NATIVE" env
  echo "[ai-context-reducer] language environments"
  "$NATIVE" language-env
  echo "[ai-context-reducer] project analysis"
  "$NATIVE" analyze "$ROOT"
  echo "[ai-context-reducer] language tool plan"
  "$NATIVE" language-setup "$ROOT"
  echo "[ai-context-reducer] shallow language analysis"
  "$NATIVE" language-run "$ROOT"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$PY_LANG"
  python3 "$PY_ANALYZE" "$ROOT"
  python3 "$PY_LANG_SETUP" "$ROOT"
  python3 "$PY_LANG_RUN" --acr-root "$ACR_ROOT" "$ROOT"
elif command -v python >/dev/null 2>&1; then
  python "$PY_LANG"
  python "$PY_ANALYZE" "$ROOT"
  python "$PY_LANG_SETUP" "$ROOT"
  python "$PY_LANG_RUN" --acr-root "$ACR_ROOT" "$ROOT"
else
  echo "No native acr-toolbox or Python runtime found." >&2
  echo "Use a prebuilt acr-toolbox binary for this OS/architecture." >&2
  exit 2
fi

echo "[ai-context-reducer] setup policy: run only shallow compatible language analysis automatically; do not install missing runtimes or run Medium/Large analyzers automatically."
