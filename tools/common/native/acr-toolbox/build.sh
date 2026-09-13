#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
go test ./...
mkdir -p ../../../../bin
OUT=../../../../bin/acr-toolbox
GOOS=${GOOS:-$(go env GOOS)}
GOARCH=${GOARCH:-$(go env GOARCH)}
if [ "$GOOS" = "windows" ]; then OUT="${OUT}.exe"; fi
CGO_ENABLED=0 GOOS="$GOOS" GOARCH="$GOARCH" go build -trimpath -ldflags="-s -w" -o "$OUT" .
echo "built $OUT ($GOOS/$GOARCH)"
