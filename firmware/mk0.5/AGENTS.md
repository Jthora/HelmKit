# AGENTS.md — Mk0.5 firmware (Heltec WiFi LoRa 32 V3)

> Cold-start orient doc. If you are an AI session opening this directory for
> the first time (likely happening during the May 20 → June 1 blackout when
> paid-AI is unavailable to the operator), READ THIS FIRST.

---

## What this is

HelmKit Mk0.5 firmware. Single-MCU sensor smoke-test board. **No stim, no
WiFi, no LoRa, no Bluetooth.** Just sensors → NDJSON over USB-CDC → Pi
log-sink → psiStabilizer analysis.

**Mk gate definitions live in [`../../docs/mk_ladder.md`](../../docs/mk_ladder.md).**
Mk0.5 = sensing + feedback floor, before any stim payload exists at Mk1.0.

---

## Build / flash / monitor (the only three commands you need)

```bash
cd firmware/mk0.5
pio run                    # build
pio run --target upload    # flash via CP2102 (or native USB-CDC)
pio device monitor         # 115200 baud, esp32_exception_decoder filter
```

If `pio run` fails: see [`docs/BUILD.md`](docs/BUILD.md) §6 "Common failure modes."
If `upload` fails: hold BOOT (GPIO 0), tap RESET, release BOOT, retry.

---

## Canonical docs (DO NOT RE-DERIVE)

| Question | Authoritative file |
|----------|---------------------|
| What pin is what? | [`docs/PINOUT.md`](docs/PINOUT.md) — code conforms to this, not the other way around |
| What JSON format on the wire? | [`docs/SCHEMA.md`](docs/SCHEMA.md) — subordinate to `external/psiStabilizer/docs/data_schemas.md` |
| What's the bringup order? | [`README.md`](README.md) §"Bringup order" + [`../../docs/mk0.5_firmware_bringup.md`](../../docs/mk0.5_firmware_bringup.md) |
| What's the blackout schedule? | [`../../docs/BLACKOUT_PLAN.md`](../../docs/BLACKOUT_PLAN.md) |
| What defensive-IP claims must I not weaken? | [`../../PRIOR_ART.md`](../../PRIOR_ART.md) §3.11 + combination claims §4 |

---

## Codebase shape

```
src/
├── board/pins.h           # pin constants — mirrors docs/PINOUT.md §2
├── main.cpp               # banner + smoke-test dispatch + heartbeat
├── drivers/
│   ├── max30102.{h,cpp}   ✅ Day 1 — DONE
│   ├── mlx90614.h         🚧 Day 2 — stub
│   ├── gsr.h              🚧 Day 2 — stub  (ADC mutex with battery!)
│   ├── battery.h          🚧 Day 2 — stub  (ADC mutex with gsr!)
│   ├── ad8232.h           🚧 Day 4 — Wave 2
│   └── max30205.h         🚧 Day 4 — Wave 2 (dual-temple, PRIOR_ART M5)
├── dsp/dsp.h              🚧 Day 3 — empty
├── layers/layers.h        🚧 Day 3 — L0/L1/L2 state machines
├── log/ndjson.h           🚧 Day 3 — NDJSON emitter; schema = docs/SCHEMA.md
└── ui/oled.h              🚧 Day 5 — SSD1306 status display
```

✅ = compiles + has body. 🚧 = header only, `TODO(Day N)` marker.

---

## Discipline rules — DO NOT VIOLATE

1. **Library versions are pinned.** Do not edit `lib_deps` to bump to "latest"
   without re-running the full L0 smoke matrix. Each pin was deliberate.
2. **The GSR-ADC vs VBAT-ADC mutex is mandatory** (see PINOUT.md §3).
   `drivers/gsr.cpp::sample_now()` and `drivers/battery.cpp::sample_now()`
   MUST share the same `SemaphoreHandle_t`. Failure = silent data corruption.
3. **No stim payload at Mk0.5.** If you find yourself writing PWM-output to
   anything that could touch the head, STOP. That's Mk1.0 territory and gated
   by safety review.
4. **NDJSON schema conforms to psiStabilizer.** When in doubt, that repo's
   `docs/data_schemas.md` wins. Do not invent channel names.
5. **Every commit is GPG-signed.** `git commit -S`. Defensive-IP integrity.
6. **No "improvements" without tickets.** This codebase is sized to a
   blackout sprint. If a refactor isn't on `BLACKOUT_PLAN.md`'s schedule,
   defer it.

---

## Calibration constants — DO NOT TUNE

Anywhere you see `// CALIBRATION:` in a comment, that value is empirical and
tied to gate criteria. Tuning it without re-running G1 invalidates the gate.

Current calibration constants:
- `max30102.{h,cpp}`: `finger_ir_threshold = 50000`, `sample_rate_hz = 100`,
  smoke window 10s, pass threshold ≥ 950 samples.

---

## Where to look when stuck

1. Compile error → `docs/BUILD.md` §6, then `pio run --verbose 2>&1 | tail -50`.
2. No serial output → check `ARDUINO_USB_CDC_ON_BOOT=1` is set in
   `platformio.ini` build_flags. Check cable is data-capable.
3. Sensor doesn't ACK on I²C → check Wire1 init order in `main.cpp`. The
   external bus is `Wire1` on GPIO 41/42, **not** `Wire` (which is the OLED
   bus on GPIO 17/18).
4. Pinout disagreement between code and PINOUT.md → PINOUT.md wins. Fix the code.

---

## Repository memory pointer

For multi-session context that survives AI resets, see:
- `/memories/repo/helmkit_blackout_strategy.md` — locked decisions
- `/memories/repo/helmkit_anchors.md` — wiki-canonical anchors
