# HelmKit Mk0.5 firmware

**Target:** Heltec WiFi LoRa 32 V3 (HTIT-WB32LAF, ESP32-S3) — the single-MCU
sensor host for the vp0 helm (Track M combat trim, Track N robustness).

**Status (2026-09-11):** builds (8 % RAM, 12 % flash); 24 native tests and
the target build run in CI. Real drivers: MAX30102 PPG, MLX90614 thermopile,
GSR, battery, MAX30205 contact temperature, IMU (register-level, MPU-6050 or
LSM6DS3 class, part not yet bought), SSD1306 OLED. Header-only stub: AD8232
ECG. Operator interface is serial keys plus the nape pod's three buttons and
slide switch (firmware done, not yet wired). No stim, no radio, no WiFi at
Mk0.5.

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
Phase 1 adds `a`/`A` for the IMU stream (`still`, `impact`, `activity`), a second `M` within 3 s to
end a session (the first emits `confirm-end`), and the nape pod buttons on GPIO 26 / 33 / 34 with the
sanctuary slide on 40: round = short press, prime = short, session start / end = long press on prime,
tally = the large cap. `vbat` goes out every 5 s; a pack under 3.5 V for 10 s ends the session and
stops the streams. A session survives a brownout, panic or watchdog reset (resumed in Tranquil with
its tally); a power-on reset discards it.
Phase 2 adds `c`/`C` for the MAX30205 contact-temperature stream (`temp-skin.L` / `.R`), `hr` /
`scr` / `sweat` lines (the host fusion and sweat rules on the helm), a flash link buffer that parks
event lines while the link is down and replays them tagged `replay:1` when it returns, the `~` host
acknowledgement byte that `tools/capture_service.py` sends after every heartbeat, and an OLED status
page (mode, HR, breaths, per-channel quality, battery, link, drops) with a fault page for low battery
and safety halts.
Build with `-D HELMKIT_DEBUG` for the fault-injection keys: `W` spins for the watchdog, `K` ends the
I²C bus (the supervisor must recover the streams), `F` floods the TX ring (drops, then raw shedding),
`V` fakes a 3.3 V pack.
Capture with `tools/capture_service.py` (one file per boot, `t_wallclock` added, acks, reconnects),
score a session with `tools/analyze_combat_session.py capture.ndjson` (`--strict` fails on any malformed
line, for CI), and check the helm's derived channels against the host references with
`tools/replay_equivalence.py capture.ndjson` (gate N-G6).

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
│   ├── drivers/           # max30102, mlx90614, gsr, battery, imu, max30205 (real); ad8232 (stub); health model
│   ├── dsp/               # r_peak (RR intervals), resp_thermal (breathing), motion (still / impact / activity), fog, eda (SCR, sweat slope)
│   ├── layers/            # pacer, modes (combat state machine), backoff (retry), power_policy (low battery), degrade (shedding), session_store
│   ├── log/               # NDJSON writer (sequence numbers, drop accounting, store hook), link buffer (LittleFS), line helpers, boot id
│   ├── safety/            # no_stim_below_mk1.h (compile-time guard)
│   └── ui/                # status LED; buttons (debounce, short / long press); OLED (SSD1306 over Wire, built-in 3x5 font)
└── test/test_native/      # Unity tests for the Arduino-free modules (`pio test -e native`)
```

## Bringup order (done) and what comes next

| Stage | Module | State |
|---|---|---|
| L0 | MAX30102 PPG smoke + stream, R-peak → `ppg-rr` | done |
| L0 → L1 | MLX90614, GSR, battery, NDJSON logger | done |
| Track M | thermal respiration, combat modes, pacer retune | done (firmware + host reference) |
| Track N phase 0 | sequence numbers, boot line, heartbeat, health lines, retry with backoff, bus recovery, task watchdog, CI | done |
| Track N phase 1 | IMU driver (MPU-6050 / LSM6DS3 auto-detect) with `still`, `impact`, `activity`; nape pod buttons; low-battery policy; session persistence; PPG window quality; thermopile fog + donning check; EDA open-circuit gap; raw shedding; fault-injection keys | done in firmware, awaiting the IMU and the switches on the bench |
| Track N phase 2 | flash link buffer with replay + host ack, OLED status / fault pages (no library), MAX30205 driver, `hr` / `scr` / `sweat` on the helm, capture service, replay-equivalence tool | done in firmware and tools; bench pending |
| Track N phase 3 | golden real captures, gate N-G6 on a real session | after the first bench capture |

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
