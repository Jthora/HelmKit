#!/usr/bin/env bash
# build.sh — wrapper around arduino-cli that injects BUILD_ID from git.
#
# Usage:
#   ./firmware/build.sh nano_bringup            # compile only
#   ./firmware/build.sh nano_bringup /dev/cu.x  # compile + upload to port
#
# Exits 0 on success, non-zero on any failure (including dirty tree
# detection if STRICT_BUILD=1).

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <sketch_dir> [upload_port]" >&2
  echo "example: $0 nano_bringup" >&2
  exit 2
fi

SKETCH="$1"
PORT="${2:-}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKETCH_DIR="$REPO_ROOT/firmware/$SKETCH"

if [[ ! -d "$SKETCH_DIR" ]]; then
  echo "ERROR: sketch dir not found: $SKETCH_DIR" >&2
  exit 1
fi

# Pick FQBN per sketch. Add new entries as new targets are added.
case "$SKETCH" in
  nano_bringup|nano_safety)
    FQBN="arduino:avr:nano:cpu=atmega328"
    ;;
  heltec_uplink)
    FQBN="esp32:esp32:heltec_wifi_lora_32_V3"
    ;;
  *)
    echo "ERROR: unknown sketch '$SKETCH' — add an FQBN mapping in $0" >&2
    exit 1
    ;;
esac

# Build identity: short git hash + dirty flag.
cd "$REPO_ROOT"
BUILD_ID="$(git rev-parse --short HEAD 2>/dev/null || echo nogit)"
if ! git diff --quiet -- "$SKETCH_DIR" 2>/dev/null; then
  BUILD_ID="${BUILD_ID}-dirty"
fi

if [[ "${STRICT_BUILD:-0}" == "1" && "$BUILD_ID" == *-dirty ]]; then
  echo "ERROR: STRICT_BUILD=1 and tree is dirty — refusing to build" >&2
  exit 1
fi

echo "==> Building $SKETCH for $FQBN  (BUILD_ID=$BUILD_ID)"
arduino-cli compile \
  --fqbn "$FQBN" \
  --build-property "compiler.cpp.extra_flags=-DBUILD_ID=\"$BUILD_ID\"" \
  --warnings all \
  "$SKETCH_DIR"

if [[ -n "$PORT" ]]; then
  echo "==> Uploading to $PORT"
  arduino-cli upload -p "$PORT" --fqbn "$FQBN" "$SKETCH_DIR"
  echo "==> Done. Open the monitor with:"
  echo "    arduino-cli monitor -p $PORT -c baudrate=115200"
fi
