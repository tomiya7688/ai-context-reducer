#!/usr/bin/env bash
set -euo pipefail

BUNDLE="$1"
GUI_HUB_SOURCE="$2"
WORK="$3"

case "$RUNNER_OS" in
  Windows) EXT=".exe" ;;
  *) EXT="" ;;
esac

SMOKE_BUNDLE="$WORK/bundle"
mkdir -p "$SMOKE_BUNDLE/gui"
cp -R "$BUNDLE"/. "$SMOKE_BUNDLE"/
cp "$GUI_HUB_SOURCE" "$SMOKE_BUNDLE/gui/acr-hub$EXT"

LOG="$WORK/acr-hub.log"
HEALTH="$WORK/health.json"
"$SMOKE_BUNDLE/gui/acr-hub$EXT" --bundle-root "$SMOKE_BUNDLE" --no-open > "$LOG" 2>&1 &
GUI_PID=$!

cleanup() {
  if [ -n "${GUI_PID:-}" ]; then
    kill "$GUI_PID" 2>/dev/null || true
    wait "$GUI_PID" 2>/dev/null || true
    GUI_PID=""
  fi
}
trap cleanup EXIT

URL=""
for _ in {1..50}; do
  URL="$(sed -n 's/^AI Context Reducer Hub: //p' "$LOG" | head -n 1)"
  if [ -n "$URL" ]; then
    break
  fi
  if ! kill -0 "$GUI_PID" 2>/dev/null; then
    cat "$LOG" >&2
    echo "acr-hub exited before announcing its URL" >&2
    exit 1
  fi
  sleep 0.1
done

case "$URL" in
  http://127.0.0.1:*/*|http://localhost:*/*|http://\[::1\]:*/*) ;;
  *)
    echo "acr-hub announced a non-loopback URL: $URL" >&2
    cat "$LOG" >&2
    exit 1
    ;;
esac

BASE_URL="${URL%/}"
curl --noproxy '*' --fail --silent --show-error "$BASE_URL/api/health" > "$HEALTH"
grep -E '"status"[[:space:]]*:[[:space:]]*"ok"' "$HEALTH" >/dev/null || {
  echo "acr-hub health endpoint returned an unexpected payload" >&2
  cat "$HEALTH" >&2
  exit 1
}

cleanup
trap - EXIT
