#!/usr/bin/env bash
# capture_ndjson.sh — capture raw NDJSON from a connected HelmKit Mk0.5
# board and pipe it through the schema validator.
#
# Usage:
#   scripts/capture_ndjson.sh [PORT] [SECONDS]
#
# Defaults: auto-detect first /dev/cu.usbmodem* port; 15 second window.
#
# Requires:
#   - HelmKit board flashed with current firmware (HELMKIT_SCHEMA_VERSION
#     must match psistabilizer.ingest.schemas.SCHEMA_VERSION)
#   - psistab-ingest installed (pip install -e external/psiStabilizer/software)
#
# Exit code 0 = round-trip OK. Non-zero = a wire-format regression.
set -euo pipefail

PORT="${1:-}"
SECS="${2:-15}"

if [[ -z "$PORT" ]]; then
    PORT="$(ls /dev/cu.usbmodem* /dev/cu.SLAB_USBtoUART 2>/dev/null | head -1 || true)"
fi
if [[ -z "$PORT" || ! -e "$PORT" ]]; then
    echo "no USB port found; pass one explicitly (e.g. /dev/cu.usbmodem1101)" >&2
    exit 2
fi

OUT="/tmp/helmkit_capture_$(date +%Y%m%d_%H%M%S).ndjson"
echo "capturing from $PORT for ${SECS}s -> $OUT"

# Open serial at 115200 (8N1, raw), drain for SECS, save.
stty -f "$PORT" 115200 raw -echo
( cat "$PORT" & CATPID=$!
  sleep "$SECS"
  kill "$CATPID" 2>/dev/null || true
) > "$OUT"

LINES=$(wc -l < "$OUT" | tr -d ' ')
echo "captured $LINES lines"

if (( LINES == 0 )); then
    echo "ERROR: no data captured. Check that the board is running and" >&2
    echo "       that emit_hello() runs at boot. Try resetting the board" >&2
    echo "       before running this script." >&2
    exit 3
fi

echo "--- first 3 lines ---"
head -3 "$OUT"
echo "--- validation ---"
psistab-ingest validate --strict-mk 50 "$OUT"
