# HelmKit Mk0.5 firmware

**Target:** Heltec WiFi LoRa 32 V3 (HTIT-WB32LAF, ESP32-S3) — the single-MCU
sensor host for the vp0 helm (Track M combat trim, Track N robustness).

**Status (2026-09-11):** builds (7 % RAM, 9 % flash); 12 native tests and
the target build run in CI. Real drivers: MAX30102 PPG, MLX90614 thermopile,
GSR, battery. Header-only stubs: AD8232 ECG, MAX30205 contact temperature,
OLED. No IMU yet (stillness is reported unknown; impact cues cannot fire).
Operator interface is serial keys; the nape pod's buttons and OLED are
planned (Track N phases 1–2). No stim, no radio, no WiFi at Mk0.5.

Plans: [`docs/plans/2026-tier1-launch/track-M-combat-trim.md`](../../docs/plans/2026-tier1-launch/track-M-combat-trim.md)
(what the helm senses and cues) and
[`track-N-capability-robustness.md`](../../docs/plans/2026-tier1-launch/track-N-capability-robustness.md)
(how each capability survives motion, sweat, a yanked cable and a low battery).
The May 2026 bring-up ladder lives in `../../docs/mk0.5_firmware_bringup.md`
and `../../docs/BLACKOUT_PLAN.md` (history; the day numbers there are done).

## Quick start

```bash
cd firmware/mk0.5
pio run                    # build
pio run --target upload    # flash via CP2102
pio device monitor         # serial @ 115200
pio test -e native         # host unit tests for the Arduino-free modules (no ESP toolchain needed)
```

Serial keys (115200): `r`/`R` smoke retry, `?` last result, `h` hello, `p`/`s` plain L0 pacer,
`g`/`x` PPG stream (`ppg-rr`), `t`/`T` thermopile stream, `e`/`E` GSR stream, and the Track M
combat modes: `m`/`M` session start/end (owns the pacer), `b`/`B` round start/end, `i` prime,
`n` sanctuary, `y` intrusion tally, `N` thermopile channel `temp-forehead` <-> `temp-nose`.
Build with `-D HELMKIT_DEBUG` for the fault-injection keys (`W` spins for the watchdog).
Score a session afterwards with `tools/analyze_combat_session.py capture.ndjson`
(`--strict` fails on any malformed line, for CI).

## What the log carries (Track N phase 0)

- Every NDJSON line has `n`, a per-boot sequence number. A gap in `n` on the
  host is exactly one lost line; the writer never blocks on a full USB ring or
  a missing host, it counts instead.
- `kind:"boot"` follows `hello` with the reset reason (`poweron`, `brownout`,
  `task-wdt`, ...) so a restart mid-session is attributable.
- `ch:"hb"` every 5 s with the drop counters and free heap: a gap in `hb` is a
  link gap, not a sensor gap.
- `kind:"health"` on every driver health transition and every re-begin. A
  stream whose driver faults (no-ack, overflow, error) is re-begun on a
  5 / 10 / 20 / 60 s schedule after a 9-clock I²C bus recovery when a slave
  holds SDA. The loop task sits on a 5 s task watchdog.

See [docs/SCHEMA.md](docs/SCHEMA.md) §2.4 for the shapes, [docs/BUILD.md](docs/BUILD.md)
for toolchain notes, [docs/PINOUT.md](docs/PINOUT.md) for pin allocations, the
ADC conflict resolution and the planned button / IMU pins.

## Layout

```
firmware/mk0.5/
├── platformio.ini         # build config, board target, pinned lib versions, native test env
├── README.md              # this file
├── AGENTS.md              # working rules for AI-assisted edits
├── docs/
│   ├── BUILD.md           # toolchain, flash, debug
│   ├── PINOUT.md          # pin assignments + conflict resolution + planned pins
│   ├── SCHEMA.md          # NDJSON wire format (channels, quality flags, Track N lines)
│   └── TROUBLESHOOTING.md
├── scripts/
│   ├── inject_build_id.py # git SHA + schema version into build flags
│   ├── rr_replay.py       # Python reference of the R-peak detector (self-test + replay)
│   └── capture_ndjson.sh  # capture + schema round-trip (needs psistab-ingest)
├── src/
│   ├── main.cpp           # dispatcher: smoke tests, serial keys, streams, modes, supervisor, heartbeat
│   ├── board/             # pins, ADC1 mutex, task watchdog + reset reason, I²C bus recovery
│   ├── drivers/           # max30102, mlx90614, gsr, battery (real); ad8232, max30205 (stubs); health model
│   ├── dsp/               # r_peak (RR intervals), resp_thermal (breathing from the thermopile)
│   ├── layers/            # pacer (L0 resonance breathing), modes (combat state machine), backoff (retry schedule)
│   ├── log/               # NDJSON writer (sequence numbers, drop accounting), line helpers, boot id
│   ├── safety/            # no_stim_below_mk1.h (compile-time guard)
│   └── ui/                # status LED; OLED (stub)
└── test/test_native/      # Unity tests for the Arduino-free modules (`pio test -e native`)
```

## Bringup order (done) and what comes next

| Stage | Module | State |
|---|---|---|
| L0 | MAX30102 PPG smoke + stream, R-peak → `ppg-rr` | done |
| L0 → L1 | MLX90614, GSR, battery, NDJSON logger | done |
| Track M | thermal respiration, combat modes, pacer retune | done (firmware + host reference) |
| Track N phase 0 | sequence numbers, boot line, heartbeat, health lines, retry with backoff, bus recovery, task watchdog, CI | done |
| Track N phase 1 | IMU (`still`, `impact`), nape pod buttons, low-battery policy, session persistence, self-tests | next |
| Track N phase 2 | derived-channel buffer on flash while the link is down, OLED status, MAX30205, capture service | after |

## Discipline rules

* No WiFi / LoRa / Bluetooth at Mk0.5. Surface area stays minimal.
* No stim payload at Mk0.5 (`safety/no_stim_below_mk1.h`); the coil driver
  gets its own interlock before it exists (Track N N-F8).
* Library versions pinned. Bumping a pin requires re-running the full sensor
  smoke matrix.
* Pin assignments in `docs/PINOUT.md` are authoritative. Code that disagrees
  with the table is wrong; fix the code.
* Host reference first, firmware second: the Python implementation is the
  behavioural spec (`tools/analyze_combat_session.py`, `scripts/rr_replay.py`);
  a constant changed in one is changed in the other in the same commit.
