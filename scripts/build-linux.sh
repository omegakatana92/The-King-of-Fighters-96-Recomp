#!/usr/bin/env bash
# Build the Linux x86_64 player (Release). No packaging, no downloads.
#
# Usage: ./scripts/build-linux.sh [ROM_DIR]
# Default ROM_DIR is <repo>/roms. The generated C is written into
# build-linux/generated and is never committed or distributed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROMS="${1:-$ROOT/roms}"
BUILD="$ROOT/build-linux"
JOBS="${JOBS:-4}"

echo "== KOF '96: Linux x86_64 build =="
echo "repo: $ROOT"
echo "roms: $ROMS"
cmake -S "$ROOT" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release "-DKOF96_ROM_DIR=$ROMS"
cmake --build "$BUILD" --parallel "$JOBS" --target kof96
echo "built $BUILD/kof 96"
