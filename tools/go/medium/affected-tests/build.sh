#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
mkdir -p dist
go test ./...
go build -trimpath -ldflags="-s -w" -o dist/affected-tests .
echo "built: $(pwd)/dist/affected-tests"
