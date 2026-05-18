# Firmware — feature plans

This directory holds **per-wave feature plans** for the Mk0.5 firmware bring-up and beyond.

The firmware code itself lives at `firmware/`. This directory documents wave-by-wave intent, hardware targets, acceptance criteria, and validation logs.

For the overall bring-up arc, see [`../mk0.5_firmware_bringup.md`](../mk0.5_firmware_bringup.md) and [`../sprint_0.3_firmware_bringup.md`](../sprint_0.3_firmware_bringup.md).

## Waves

| Wave | Title | Plan | Status |
|------|-------|------|--------|
| L0 | Paced-breathing pacer | (shipped, commit `2872333`) | done |
| M1 | MAX30102 PPG + Pan-Tompkins + RR NDJSON | [`../plans/2026-tier1-launch/track-E-firmware-wave-m1.md`](../plans/2026-tier1-launch/track-E-firmware-wave-m1.md) | planned |
| M2 | BLE transport + HRV metrics (RMSSD, SDNN, pNN50) | not planned yet | future |
| M3 | GSR fusion + state classifier | not planned yet | future |
| M4 | Bifilar emitter driver + safety interlock | not planned yet | future |

## Convention

When a wave ships:

1. Add a `wave-<id>.md` doc here with: hardware target, build instructions, validation results, known issues.
2. Update the table above with the commit SHA and status `done`.
3. Cross-link from the corresponding `../plans/2026-tier1-launch/track-*.md` doc.
