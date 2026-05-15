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

---

## Error UX — three channels, three audiences

Mk0.5 emits failure information on **three independent channels**, each
sized for one consumer. Confusing them is the most common bug a future
contributor will introduce, so read this section before touching any
error-path code.

### Channel 1 — NDJSON over USB-CDC (canonical, for the Pi sink + future-AI)

Every failure produces a structured line:
- `kind:"smoke"` for smoke-test results (one per smoke run).
- `kind:"error"` for runtime errors during normal operation.
- `kind:"hello"` once at boot to anchor the `boot_id` to a specific build.

These lines carry `code` (string), `code_num` (integer), `health`, two
evidence integers, a free-text `note`, and `boot`. They are the
**only** authoritative record. The Pi log-sink and psiStabilizer
analysis pipeline both parse this channel. Wire shapes are documented in
[`src/log/ndjson.h`](src/log/ndjson.h); the code dictionary lives in
[`src/drivers/smoke_fail.h`](src/drivers/smoke_fail.h); human-readable
explanations are in [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).

**Discipline:** never add a code path that emits only to the prose
banner without also emitting an NDJSON line.

### Channel 2 — Status LED (operator, real-time, visible across a room)

Patterns are defined in [`src/ui/status_led.h`](src/ui/status_led.h):

| Pattern | Visual | Meaning |
|---|---|---|
| `kBoot` | off | Before `setup()` completes. |
| `kTesting` | solid on | Smoke test in progress. |
| `kPass` | 1 Hz square (50% duty) | Last smoke test passed. |
| `kFail` | 3×100 ms blink + 800 ms gap | Last smoke test failed (non-safety). |
| `kSafetyHalt` | **5 s solid preamble** + 5×80 ms blink + 2 s gap | Safety condition tripped. **Distinguishable from `kFail` at a glance.** |
| `kIdle` | 0.5 Hz (long off, short on) | Operational, no recent activity. |

The 5-second solid preamble on `kSafetyHalt` is a defensive-publication
claim (M10). A passing observer who sees only the preamble must read
"safety state, not transient fault." Do not shorten it without updating
the claim.

### Channel 3 — Prose banner over Serial (human at the desk)

The `[main]` prefixed lines printed at boot and on retry are for a
human reading `pio device monitor` live. They are **not parsed by
anything downstream**. They duplicate Channel 1 information in a
glanceable form. Discrepancies between Channel 1 and Channel 3 are bugs
in Channel 3 — Channel 1 wins.

### Operator-acknowledgement gate

Serial commands:
- `r` — re-run smoke. **Refused after a safety-halt** with a Channel 1
  `kStimSafetyHalt` error log.
- `R` — force-acknowledge a safety-halt and re-run. Required after any
  `kSafetyHalt` LED pattern. The case-difference is deliberate (M10):
  a reflexive single-keystroke retry cannot defeat the safety floor.
- `?` — re-emit the last `kind:"smoke"` line (useful when the Pi sink
  lost it).
- `h` — re-emit the `kind:"hello"` line (useful when the Pi sink
  attached after boot).

Do not add lower-case shortcuts for safety-bypass operations. The shape
of the grammar is part of the safety protocol.

### What is NOT a channel

The OLED display, when wired in Wave 2, will mirror Channel 2 + a one-line
summary of Channel 1 for the operator. It is not an independent error
surface. Code that emits to the OLED but not to Channels 1+2 is a bug.

---

## When a future AI reads the logs

If you are an AI session opening this directory because the operator
asked you to interpret a set of NDJSON logs, your starting point is:

1. Find the `kind:"hello"` line. Extract `git`, `dirty`, `schema`,
   `boot`. This identifies which build produced the rest of the lines.
2. Filter for `kind:"smoke"` and `kind:"error"`. The `code` field is
   the structured handle; the `note` field is the observation.
3. Cross-reference `code` against [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md).
4. If `code` is `kUnknown` (65535), the call-site has migration debt.
   The `note` is your only handle. File a Wave-2 ticket.
5. If you find a code in the 100–199 range from a Mk0.5 build, that is
   a bug — Mk0.5 has no stim hardware.

See [`docs/MANIFESTO.md`](docs/MANIFESTO.md) for why the schema is
shaped this way.
