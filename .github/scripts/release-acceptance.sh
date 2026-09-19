#!/usr/bin/env bash
set -euo pipefail

BUNDLE="$1"
VERSION="$2"
ROOT="$3"

case "$RUNNER_OS" in
  Windows) EXT=".exe" ;;
  *) EXT="" ;;
esac

BIN="$BUNDLE/acr-toolbox$EXT"
fail() { echo "release acceptance failed: $*" >&2; exit 1; }
expect_file() { [ -f "$1" ] || fail "missing file: $1"; }
expect_dir() { [ -d "$1" ] || fail "missing directory: $1"; }
expect_contains() { grep -F "$2" "$1" >/dev/null || fail "$1 does not contain: $2"; }

for name in acr-toolbox go-symbols go-import-map go-package-graph affected-tests; do
  expect_file "$BUNDLE/$name$EXT"
done
for name in README.md TOOLS_README.md LICENSE RELEASE_MANIFEST.json; do
  expect_file "$BUNDLE/$name"
done
expect_contains "$BUNDLE/RELEASE_MANIFEST.json" "\"release_version\": \"$VERSION\""

mkdir -p "$ROOT"
VERSION_JSON="$ROOT/version.json"
"$BIN" version > "$VERSION_JSON"
expect_contains "$VERSION_JSON" "\"version\": \"$VERSION\""
expect_contains "$VERSION_JSON" "\"status\": \"ok\""

rm -rf "$ROOT/project"
mkdir -p "$ROOT/project/src" "$ROOT/project/tests" "$ROOT/project/docs" "$ROOT/project/app/nested" "$ROOT/project/build"
P="$ROOT/project"

cat > "$P/README.md" <<'EOF'
# Fixture
context routing sample
EOF
cat > "$P/AI_CONTEXT.md" <<'EOF'
# Root guide
Search first.
EOF
cat > "$P/app/AI_CONTEXT.local.md" <<'EOF'
# App guide
Only applies below app.
EOF
cat > "$P/src/main.py" <<'EOF'
import os
from pathlib import Path

class Demo:
    pass

def run():
    return Path(".")
EOF
cat > "$P/src/util.go" <<'EOF'
package fixture

import "fmt"

type Widget struct{}

func Run() { fmt.Println("ok") }
EOF
cat > "$P/src/native.c" <<'EOF'
#include <stdio.h>
struct Item { int x; };
int run(void) { return 0; }
EOF
cat > "$P/tests/test_main.py" <<'EOF'
def test_demo():
    assert True
EOF
cat > "$P/docs/policy.md" <<'EOF'
# Required
MUST keep generated output out of source of truth.
EOF
cat > "$P/context.md" <<'EOF'
# Goal
Change fixture safely.
# Required
Keep output compact.
# Acceptance
Targeted validation passes.
# Source
src/main.py
# Tests
tests/test_main.py
# Deferred
Unrelated refactor.
EOF
printf 'ignored\n' > "$P/build/output.log"

git -C "$P" init -q
git -C "$P" config user.email "release-ci@example.invalid"
git -C "$P" config user.name "Release CI"
git -C "$P" add .
git -C "$P" commit -qm "fixture"
printf '# changed\n' >> "$P/src/main.py"

OUT="$ROOT/out"
mkdir -p "$OUT"

"$BIN" env > "$OUT/env.json"
"$BIN" analyze "$P" > "$OUT/analyze.json"
"$BIN" select "$P" > "$OUT/select.json"
"$BIN" stats "$P" > "$OUT/stats.json"
"$BIN" doc-index "$P" > "$OUT/doc-index.json"
"$BIN" context-budget --mode fast --top 5 "$P" > "$OUT/context-budget.json"
"$BIN" hotspot-report --limit 5 "$P" > "$OUT/hotspot.json"
"$BIN" context-manifest "$P" > "$OUT/context-manifest.json"
"$BIN" search --max-results 5 --glob '*.py' Demo "$P" > "$OUT/search.json"
"$BIN" find --type file --max-results 10 '*.py' "$P" > "$OUT/find.json"
"$BIN" tree --max-depth 2 "$P" > "$OUT/tree.json"
"$BIN" slice Demo "$P/src/main.py" > "$OUT/slice.json"
printf 'ok\nwarning: sample\nerror: sample\n' | "$BIN" compact-log > "$OUT/compact-log.json"
"$BIN" compact-diff "$P" HEAD HEAD > "$OUT/compact-diff.txt"
"$BIN" remote-delta "$P" > "$OUT/remote-delta.txt"
"$BIN" change-router "$P" > "$OUT/change-router.json"
"$BIN" validation-plan "$P/src/main.py" > "$OUT/validation-plan.json"
"$BIN" responsibility-candidates "$P" > "$OUT/responsibility.md"
"$BIN" policy-index "$P/docs" > "$OUT/policy-index.json"
"$BIN" doc-duplicate-hints "$P/docs" > "$OUT/doc-duplicate.json"
"$BIN" ignore-candidates "$P" > "$OUT/ignore-candidates.json"
"$BIN" acceptance-extractor "$P/context.md" > "$OUT/acceptance.json"
"$BIN" exploration-stop-check "$P/context.md" > "$OUT/exploration-stop.json"
"$BIN" scoped-guides "$P/app/nested" "$P" > "$OUT/scoped-guides.json"

"$BIN" language-setup "$P" > "$OUT/language-setup.json"
"$BIN" language-run --out "$OUT/language-small" "$P" > "$OUT/language-run.json"
"$BIN" language-medium-run --out "$OUT/language-medium" "$P" > "$OUT/language-medium-run.json"
"$BIN" language-large-plan "$P" > "$OUT/language-large-plan.json"

expect_dir "$OUT/language-small"
expect_dir "$OUT/language-medium"
expect_file "$OUT/language-small/python_small_python_symbols.json"
expect_file "$OUT/language-small/go_small_go_symbols.json"
expect_file "$OUT/language-medium/python_medium_python_import_map.json"
expect_file "$OUT/language-medium/go_medium_go_import_map.json"

cat > "$ROOT/policy-pass.json" <<'EOF'
{"rules":[{"id":"REL001","paths":["src/**"],"severity":"error","forbid":"__never_present__"}]}
EOF
"$BIN" policy-check --rules "$ROOT/policy-pass.json" "$P" > "$OUT/policy-pass.json"

cat > "$ROOT/policy-fail.json" <<'EOF'
{"rules":[{"id":"REL002","paths":["src/**"],"severity":"error","forbid":"class Demo"}]}
EOF
set +e
"$BIN" policy-check --rules "$ROOT/policy-fail.json" "$P" > "$OUT/policy-fail.json"
POLICY_CODE=$?
set -e
[ "$POLICY_CODE" -eq 1 ] || fail "policy violation exit code=$POLICY_CODE, expected 1"
expect_contains "$OUT/policy-fail.json" "\"status\": \"violations\""

mkdir -p "$ROOT/template"
printf 'Hello {{name}}\n' > "$ROOT/template/input.txt"
printf '{"name":"World"}\n' > "$ROOT/template/vars.json"
"$BIN" template --template "$ROOT/template/input.txt" --vars "$ROOT/template/vars.json" --out "$ROOT/template/output.txt" --required name --template-id release-ci --template-version 1 > "$OUT/template-generate.json"
expect_contains "$ROOT/template/output.txt" "Hello World"
"$BIN" template --template "$ROOT/template/input.txt" --vars "$ROOT/template/vars.json" --out "$ROOT/template/output.txt" --required name --check > "$OUT/template-check.json"
printf '{"name":"Changed"}\n' > "$ROOT/template/vars.json"
set +e
"$BIN" template --template "$ROOT/template/input.txt" --vars "$ROOT/template/vars.json" --out "$ROOT/template/output.txt" --required name --check > "$OUT/template-drift.json"
TEMPLATE_CODE=$?
set -e
[ "$TEMPLATE_CODE" -eq 1 ] || fail "template drift exit code=$TEMPLATE_CODE, expected 1"
expect_contains "$OUT/template-drift.json" "\"status\": \"drift_detected\""

expect_contains "$OUT/search.json" "src/main.py"
expect_contains "$OUT/scoped-guides.json" "AI_CONTEXT.md"
expect_contains "$OUT/scoped-guides.json" "app/AI_CONTEXT.local.md"
expect_contains "$OUT/acceptance.json" "\"status\": \"ok\""
expect_contains "$OUT/exploration-stop.json" "\"stop_broad_exploration\": true"
expect_contains "$OUT/ignore-candidates.json" "build"
expect_contains "$OUT/policy-index.json" "MUST keep generated output"

"$BUNDLE/go-symbols$EXT" "$P" > "$OUT/go-symbols.json"
"$BUNDLE/go-import-map$EXT" "$P" > "$OUT/go-import-map.json"
"$BUNDLE/go-package-graph$EXT" "$P" > "$OUT/go-package-graph.json"

expect_contains "$OUT/go-symbols.json" "Widget"
expect_contains "$OUT/go-import-map.json" "fmt"

echo "release acceptance passed for $VERSION on $RUNNER_OS/$RUNNER_ARCH"
