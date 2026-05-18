# Track E — Firmware Wave M1 (MAX30102 + R-peak + RR NDJSON)

- **Status**: `ready`
- **Effort**: ~12 hours over Wed–Fri
- **Depends on**: existing L0 paced-breathing pacer (commit `2872333`)
- **Unblocks**: honest Tier 1 DIY demo; HRV-conditioned modes in Mk0.5

---

## Goal

Add a **continuous PPG sensing + R-peak detection + RR-interval NDJSON output** stage to the Mk0.5 firmware. After this lands, the device measures something real (heart-rate variability) and emits it to the serial stream in a format downstream tools can consume.

This is Wave M1 of the Mk0.5 firmware bring-up plan ([../mk0.5_firmware_bringup.md](../mk0.5_firmware_bringup.md)).

## Hardware target

- **MCU**: ESP32-S3-DevKitC-1 (already in BOM).
- **Sensor**: MAX30102 PPG breakout, I²C, 3.3 V (already in BOM).
- **Wiring**: I²C on GPIO 8 (SDA) / 9 (SCL); INT on GPIO 10; sensor 3v3 + GND.

## Functional spec

1. **Driver**: poll MAX30102 at 100 Hz (configurable). Read IR channel. Apply 50-sample SMA detrender.
2. **R-peak detector**: streaming Pan-Tompkins (bandpass 5–15 Hz emulated on PPG → derivative → squaring → moving-window integration → adaptive threshold). Latency target < 250 ms.
3. **RR-interval emitter**: on each detected peak, compute ms since previous peak. Emit:
   ```json
   {"t":1684467890123,"ch":"rr-ms","v":872,"src":"max30102","conf":0.91}
   ```
   over USB serial at 115200 baud, one JSON object per line (NDJSON).
4. **Sanity gate**: reject RR < 250 ms (HR > 240 bpm) or > 2000 ms (HR < 30 bpm). Emit `"ch":"rr-rejected"` with reason.
5. **Heartbeat**: every 5 s emit `{"t":...,"ch":"heartbeat","fw":"wave-m1-<sha>"}`.

## Non-goals (deferred to Wave M2)

- Bluetooth/BLE transport (USB serial only for M1).
- Storage to SD card.
- HRV-derived modes (RMSSD, SDNN, pNN50). M1 just emits RR; analysis is downstream.
- Multi-sensor fusion with GSR/EEG.

## Acceptance criteria

1. With sensor on a fingertip, > 95 % of beats over 60 s yield a valid `ch:"rr-ms"` line.
2. RR-interval stream matches a reference (e.g. Polar H10 chest strap, lent or rented) within ±15 ms RMS over 60 s.
3. False-positive rate at rest: < 1 phantom RR / minute.
4. Firmware compiles clean under PlatformIO `platformio.ini` already in repo (no new toolchain deps).
5. NDJSON validates: every emitted line parses as JSON and matches schema.

## Validation protocol (pre-registered)

Run a 5-minute resting session, 5-minute paced-breathing session (using L0 pacer), and compare RMSSD between the two. Expected: paced-breathing RMSSD > resting RMSSD (well-replicated finding). If we *don't* see that, our detector is wrong, not the physiology. This becomes F-row in `docs/falsification.md`.

## File deliverables

- `firmware/wave-m1/src/main.cpp` (entry)
- `firmware/wave-m1/src/max30102.{h,cpp}` (driver)
- `firmware/wave-m1/src/pan_tompkins.{h,cpp}` (detector)
- `firmware/wave-m1/src/ndjson_emit.{h,cpp}` (serial writer)
- `firmware/wave-m1/platformio.ini`
- `firmware/wave-m1/README.md` (build + flash instructions)
- `docs/firmware/wave-m1.md` (cross-link to this plan, design rationale, validation results when run)

## What ships

A single PR titled `firmware: wave M1 — MAX30102 PPG + Pan-Tompkins + RR-NDJSON`, with the validation log attached as `firmware/wave-m1/validation/2026-05-XX_resting_vs_paced.csv`.
