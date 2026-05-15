# HelmKit Mk0.5 — Troubleshooting

This table is keyed by the `SmokeFail` enum (see
[`src/drivers/smoke_fail.h`](../src/drivers/smoke_fail.h)). When a
smoke-test or runtime error emits a `code_num` over NDJSON, look it up
here.

The columns are:

- **Code**: the enum name as it appears on the wire (`code` field).
- **Num**: the integer value (`code_num` field). Stable across builds
  within an Mk-version; may renumber at an Mk-version boundary.
- **Likely cause**: the top one or two physical / wiring / software
  conditions that produce this code in practice.
- **Diagnose**: a concrete next step a human operator can take with the
  hardware in front of them.
- **Escalate**: what to do if Diagnose did not resolve it. This is
  usually a doc reference, a Pi-side script, or a Wave-2 ticket.

---

## Sensor-acquisition faults (0–99)

| Code | Num | Likely cause | Diagnose | Escalate |
|---|---|---|---|---|
| `kNoAck` | 10 | Sensor not present on the bus; pulled-up SDA/SCL line floating; sensor power rail unrouted. | `i2cdetect`-equivalent: `pio device monitor` and watch for the smoke log; verify the sensor is mounted and its INT pin (if any) is not held by a stuck pull. For Wire1 sensors (MLX90614), confirm GPIO 19/20 are wired to the breakout. | [`docs/PINOUT.md`](PINOUT.md) §I²C-routing. If the bus shows no devices at all, suspect VDD rail. |
| `kWrongPartId` | 11 | A different sensor was placed at the expected address (e.g. MAX30105 reporting where MAX30102 was expected). | Read part-ID register manually over `pio device monitor` with a short test sketch. | If a different chip is intentionally present, file a Wave-2 ticket to broaden the part-ID whitelist. |
| `kConfigFailed` | 12 | Sensor ACKed the address but failed a config register write — usually a power-state-machine race in the chip's reset path. | Power-cycle the board (not just reset). If reproducible across cold boots, suspect a damaged chip. | Log the boot-ID and `code_num` to the Pi sink, then swap the breakout. |
| `kBeginFailed` | 13 | Driver `begin()` returned false for a reason not covered by the more specific codes above. Often: the lower-level `Adafruit_*` library returned false. | Read the `note` field — it should disambiguate. | If the note is generic, instrument the driver to emit a more specific code in the next build. |
| `kLowSampleRate` | 20 | PPG / EMG / GSR sampling fell below the smoke-test floor (e.g. <8 samples in 1.5s for MAX30102). Causes: poor skin contact, FIFO not actually advancing, I²C bus contention from another peripheral. | Confirm skin contact (or finger contact for benchtop test). Watch raw counts via `?` command on serial. | If raw is OK but downstream rate calc is low, the timestamp source may be the culprit. |
| `kFifoOverflow` | 21 | FIFO filled faster than `pump()` drained it. Causes: a long blocking call elsewhere stalled the main loop; pump cadence too slow. | Check `loop()` cadence — any `delay()` > 50 ms in a sibling subsystem is suspect. | If structural, raise the FIFO depth or reduce the sensor's internal sample rate. |
| `kI2cStalled` | 22 | I²C bus appears alive (ACKs) but no sample arrived for >2 s. Often a pulled-low SDA from a half-crashed peripheral. | Power-cycle. If reproducible, isolate by disabling other I²C devices one at a time. | Hardware-reset line may be wired wrong. See [`PINOUT.md`](PINOUT.md). |
| `kOutOfRange` | 23 | Sample arrived but is outside the physiological envelope (e.g. GSR > 5 MΩ when electrodes are unstuck). | Verify electrode contact. Saline-wet pad if dry-contact failed. | If contact is verified and reading is still out of range, suspect AFE saturation — file Wave-2 calibration ticket. |
| `kMutexTimeout` | 30 | ADC1 mutex held for longer than the requesting consumer's timeout. With only two consumers (`vbat`, `gsr`), this means one held the mutex for > 50 ms. | Profile the holder. Most likely cause: a long `analogRead` retry loop. | If structural, raise the timeout — but only after measuring. Do not silently widen the safety window. |
| `kHeapExhausted` | 31 | `new (std::nothrow)` returned null. Either a real OOM, or a leak elsewhere has cumulatively drained the heap. | Check `ESP.getFreeHeap()` at boot and after smoke. If the delta is large, you have a leak. | Run a long-soak repro and instrument allocations. |
| `kNotImplemented` | 90 | This driver's smoke test is a Wave-2 stub. The `note` field disambiguates which sensor (`gsr-wave2-stub`, `vbat-wave2-stub`, `mlx-wave2-stub`). **This is not an error; it is a placeholder that confirms the driver compiled and was reached.** | None needed. Read the note. | If you are blocked on this driver being real, see [`docs/mk0.5_firmware_bringup.md`](mk0.5_firmware_bringup.md) for Wave-2 scope. |

---

## Stim-path faults (100–199) — RESERVED

These codes exist in the enum but **cannot be raised by Mk0.5** because
no stim hardware is present. They are reserved per claim M9 in
[`PRIOR_ART.md`](../../../PRIOR_ART.md) so that downstream parsers,
schema validators, and field-report tooling compile against the final
shape today, before Mk1.0 ships.

| Code | Num | Reserved for | Will be raised by |
|---|---|---|---|
| `kStimCurrentExcursion` | 100 | Measured stim current exceeded its commanded envelope. | Mk1.0+ bifilar driver. |
| `kStimImpedanceLow` | 101 | Inter-electrode impedance dropped below the operator-safe floor. | Mk1.0+ AFE. |
| `kStimElectrodeFloat` | 102 | Electrode contact lost mid-session; stim path opened. | Mk1.0+ AFE. |
| `kStimPatientDisconnect` | 103 | Patient-cable continuity check failed at session start. | Mk1.0+ pre-session gate. |
| `kStimSafetyHalt` | 104 | Composite safety condition tripped; stim driver disabled by supervisor. | Mk1.0+ supervisor MCU. |

**If you see one of these codes from a Mk0.5 build, that is a bug** —
either an enum mis-use or a mis-aimed test harness.

---

## Host-platform faults (200+)

| Code | Num | Likely cause | Diagnose | Escalate |
|---|---|---|---|---|
| `kHostTimeSyncFailed` | 200 | RTC drifted past tolerance or NTP/Pi-sync failed at boot. Mk0.5: NTP not yet wired, so this code is a placeholder. | Mk0.5 should not raise this; Mk1.0+ Pi-sync will. | n/a at Mk0.5. |
| `kHostBacklogOverflow` | 201 | NDJSON emit was called faster than the serial path could drain. Reserved for the Pi-side sink. | Inspect Pi-side log-sink throughput. | n/a in firmware. |

---

## Sentinel

| Code | Num | Meaning |
|---|---|---|
| `kUnknown` | 65535 | A legacy code path used the back-compat 3-arg `SmokeResult::fail()` factory without supplying a `SmokeFail` value. The free-text `note` is your only clue. **This is a migration debt marker** — file a ticket to migrate the call-site to the 5-arg factory. |

---

## Reading NDJSON in the wild

A single NDJSON `kind:"smoke"` line looks like:

```json
{"t":12345,"kind":"smoke","source":"ppg-hrv","ok":false,"code":"kLowSampleRate","code_num":20,"health":"low_signal","ev_a":3,"ev_b":1500,"note":"max30102: only 3 samples in 1500ms","boot":"a1b2c3d4e5f60718"}
```

- `t`: millis() at emission.
- `source`: which driver / subsystem produced the event.
- `ok`: convenience boolean.
- `code` + `code_num`: the SmokeFail in both string and integer form.
- `health`: the driver's terminal Health enum, as a snake_case string.
- `ev_a` / `ev_b`: two evidence integers; their meaning is per-code,
  documented in the driver source.
- `note`: free-text observation. Sanitized (quotes and backslashes
  replaced with `_`) but otherwise verbatim from the driver.
- `boot`: 16-char hex of the 64-bit per-boot nonce. Different on every
  cold boot; same across all lines of a single boot session.

The companion `kind:"hello"` line emitted at boot carries the
`schema`, `git`, `dirty`, and `mk` fields — together with the `boot`
field, those let any future parser identify exactly which build
produced the rest of the lines in the file.

---

## When in doubt

Re-read [`MANIFESTO.md`](MANIFESTO.md) §2: a failure that does not
produce a witness is worse than one that never happened. If you found
yourself reading this file because *nothing* was emitted, that is the
bug — not the underlying sensor.
