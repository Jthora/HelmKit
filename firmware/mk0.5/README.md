# HelmKit Mk0.5 firmware

**Target:** Heltec WiFi LoRa 32 V3 (HTIT-WB32LAF) — single-MCU sensor
smoke-test board.

**Status:** scaffold + MAX30102 driver. Wave 1 sensor drivers land Day 2.

See `../../docs/mk0.5_firmware_bringup.md` for the full L0/L1/L2 + G1/G2
bringup ladder and `../../docs/BLACKOUT_PLAN.md` for the May-14 → June-1
sprint schedule.

## Quick start

```bash
cd firmware/mk0.5
pio run                    # build
pio run --target upload    # flash via CP2102
pio device monitor         # serial @ 115200
```

See [docs/BUILD.md](docs/BUILD.md) for full toolchain notes,
[docs/PINOUT.md](docs/PINOUT.md) for pin allocations and the ADC conflict
resolution.

## Layout

```
firmware/mk0.5/
├── platformio.ini         # build config, board target, pinned lib versions
├── README.md              # this file
├── docs/
│   ├── BUILD.md           # toolchain, flash, debug
│   └── PINOUT.md          # pin assignments + conflict resolution
├── include/               # public headers (none yet)
└── src/
    ├── main.cpp           # empty dispatcher (Day 1)
    ├── drivers/           # per-sensor drivers
    │   ├── max30102.{h,cpp}    # PPG, Day 1
    │   ├── mlx90614.{h,cpp}    # IR forehead temp, Day 2 (stub)
    │   ├── gsr.{h,cpp}         # CJMCU-6701, Day 2 (stub)
    │   ├── ad8232.{h,cpp}      # ECG, Day 4 / Wave 2 (stub)
    │   ├── max30205.{h,cpp}    # high-precision contact temp, Day 4 (stub)
    │   └── battery.{h,cpp}     # VBAT monitor, Day 1 (stub)
    ├── dsp/               # signal processing (Day 3)
    ├── layers/            # L0/L1/L2 state machines (Day 3)
    ├── log/               # NDJSON serial logger (Day 3)
    └── ui/                # OLED status display (Day 2)
```

## Bringup order (intentional)

| Day | Sensor / module        | Gate   | Why first |
|-----|------------------------|--------|-----------|
| 1   | MAX30102 PPG           | L0     | In hand. I²C smoke test validates the bus + driver pattern for everything that follows. |
| 2   | MLX90614, GSR, battery | L0→L1  | Wave 1 arrival. Battery monitor closes the GSR-ADC conflict regression test. |
| 3   | NDJSON logger + DSP    | L1→L2  | Once 3 sensors stream, framing matters. |
| 4   | AD8232, MAX30205       | L2→G1  | Wave 2 arrival (during blackout — stubs land Day 4 so plumbing is mechanical). |
| 5+  | OLED status, fault FSM | G1→G2  | Last because everything must already work without it. |

## Discipline rules

* No WiFi / LoRa / Bluetooth at Mk0.5. Surface area stays minimal.
* No stim payload at Mk0.5 (BLACKOUT_PLAN §3 Decision #5).
* Every commit GPG-signed; pushed same day.
* Library versions pinned. Bumping a pin requires re-running the full sensor
  smoke matrix.
* Pin assignments in `docs/PINOUT.md` are authoritative. Code that disagrees
  with the table is wrong; fix the code.
