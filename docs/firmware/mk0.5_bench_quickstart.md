# Mk0.5 Bench Quickstart — Bridge A (PPG) + Bridge B (MLX + GSR)

- **Status**: `v0` (Track K commit 3)
- **Scope**: One-page operator runbook: from "I have a Heltec V3 and
  some sensors in front of me" to "I have an NDJSON capture and a
  one-page report of what it contained." Bridges A and B only; Bridge C
  (ECG / AD8232) ships in [`track-J-sensor-bring-up.md §4`](../plans/2026-tier1-launch/track-J-sensor-bring-up.md)
  Bridge C when hardware arrives.
- **Authority**: This doc cross-links into the authoritative sources;
  it does *not* duplicate them. Pin assignments live in
  [`firmware/mk0.5/src/board/pins.h`](../../firmware/mk0.5/src/board/pins.h)
  and [`firmware/mk0.5/docs/PINOUT.md`](../../firmware/mk0.5/docs/PINOUT.md);
  channel definitions live in [`firmware/mk0.5/docs/SCHEMA.md`](../../firmware/mk0.5/docs/SCHEMA.md);
  wiring photos and the ASCII layout live in [`mk0.5_wiring.md`](mk0.5_wiring.md).

---

## 1. Pre-flight checklist

Before plugging anything in:

- [ ] Heltec V3 (silkscreen `HTIT-WB32LAF`) — verified in Track J §3 #1.
- [ ] One Diitao MAX30102 breakout — pull-ups confirmed on-board
      (Track J §3 #2). Do **not** add external 4.7 kΩ.
- [ ] PlatformIO installed (`pio --version` works).
- [ ] Python 3.11+ with `pyserial` available (`pip install pyserial`
      if missing — only required for live capture, not for replay).
- [ ] USB-C cable that actually carries data (not power-only).

Optional but recommended for Bridge B:

- [ ] One MLX90614 breakout (GY-906, I²C addr `0x5A`).
- [ ] One CJMCU-6701 (or compatible) GSR board with 3.5 mm TRS leads
      and two Red Dot 2560 wet-gel electrodes.

---

## 2. Wire it

Authoritative pin table:
[`mk0.5_wiring.md`](mk0.5_wiring.md). Summary:

**Bridge A (PPG only — 5 wires):**

| Heltec V3 GPIO | MAX30102 pad |
|----------------|--------------|
| GPIO 41 (SDA)  | SDA          |
| GPIO 42 (SCL)  | SCL          |
| GPIO 38        | INT          |
| 3V3            | VIN          |
| GND            | GND          |

**Bridge B additions:**

- MLX90614 → same I²C bus (GPIO 41/42), 3V3, GND. Address `0x5A`.
- GSR module → 3V3, GND, signal to **GPIO 4** (`kGsrAdc`, ADC1_CH3).
  Electrodes go to the TRS tip (finger 1) and ring (finger 2); sleeve
  is shield/ground. See [`track-J-sensor-bring-up.md §3 #3`](../plans/2026-tier1-launch/track-J-sensor-bring-up.md).

---

## 3. Flash

From the repo root:

```bash
cd firmware/mk0.5
pio run -t upload
pio device monitor -b 115200
```

You should see, in order:

1. A human-readable boot preamble (`[main] starting MAX30102 smoke...`
   etc.).
2. An NDJSON `hello` line with `kind:"hello"`, `git`, `schema`, `boot`.
3. Three NDJSON `smoke` lines, one per Bridge-A/B driver in hand
   (`ppg-hrv`, `temp-forehead`, `gsr`). Each must report `"ok":1`
   before that sensor is bench-ready. A `smoke` line with `"ok":0`
   means do not trust that channel until the smoke passes.
4. A prompt summarising the serial commands.

If smoke fails on a channel you don't have wired (e.g. MLX without
the breakout connected), that's expected — proceed with the channels
that did pass.

---

## 4. Start the streams you want

Serial commands (lowercase = start, uppercase = stop):

| key | stream         | NDJSON channel(s)                            |
|-----|----------------|----------------------------------------------|
| `g` | PPG start      | `ppg-hrv` (100 Hz), `ppg-rr` (event)         |
| `G` | PPG stop       | —                                            |
| `t` | MLX start      | `temp-forehead`, `temp-forehead.amb` (4 Hz)  |
| `T` | MLX stop       | —                                            |
| `e` | GSR start      | `gsr` (50 Hz)                                |
| `E` | GSR stop       | —                                            |
| `p` | L0 pacer 6 bpm | (no channel; produces `cue` events)          |
| `s` | pacer stop     | —                                            |
| `?` | help           | reprints the command table                   |
| `r` | re-run smoke   | (refused if a safety-halt is sticky)         |
| `R` | ack safety-halt| only needed after a safety halt              |

Streams are independent; running all three concurrently is the
intended Bridge B bench mode.

---

## 5. Capture

In a second terminal, while the streams are live:

```bash
# from repo root
tools/capture_ndjson.py --port /dev/tty.usbmodem* --label bench-001
```

This writes:

- `captures/YYYYMMDDTHHMMSSZ_bench-001.ndjson`  — the raw NDJSON.
- `captures/YYYYMMDDTHHMMSSZ_bench-001.meta.yaml` — session metadata.

`Ctrl-C` to stop. For a bounded capture, add `--max-lines 6000`
(≈ 60 s of PPG-only).

---

## 6. Inspect

```bash
tools/analyze_capture.py captures/YYYYMMDDTHHMMSSZ_bench-001.ndjson
```

Output (example, MLX + GSR only):

```
capture: captures/...
  total=1743  data=1740  meta=3  parse_errors=0
  boot_ids: deadbeef...
  schema: 0.1
  smoke: 2/2 passed

  channel             count   dur    obs    exp   rate%  inrng  gaps ...
  gsr                  1500  30.0  50.00  50.00  100.0% 100.0%     0 ...
  temp-forehead         120  29.8   4.00   4.00  100.0% 100.0%     0 ...
  temp-forehead.amb     120  29.8   4.00   4.00  100.0% 100.0%     0 ...
```

What to look for:

- `rate%` between roughly **80 % and 120 %** of expected per channel
  on the longer captures. Lower says the driver is throttling or the
  bus is dropping; higher says the host is timestamp-aliasing.
- `inrng` **≥ 95 %** on a sane session. A clean MLX pointed at a
  forehead should sit near 100 %; a GSR with dry electrodes will
  spike `out-of-range` because the raw rails toward 4095.
- `gaps` **= 0** on continuous channels. Each gap = an inter-sample
  interval > 2× expected period (e.g. > 20 ms for GSR @ 50 Hz).
- `smoke: N/N passed` on the meta line — this is the only place
  boot-time gate failures are surfaced after a long capture.

Pass `--json` to get a machine-readable summary for scripting.

For offline test (no Heltec attached), the same tool runs against the
committed fixtures:

```bash
tools/analyze_capture.py tests/fixtures/mlx_gsr_30s_good.ndjson
```

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `hello` then silence after `g` | MAX30102 INT line floating, but bus OK | Tug the INT jumper (GPIO 38). Polling fallback still works without it. |
| `ppg-hrv` smoke fails repeatedly | I²C wiring; check SDA/SCL not swapped | `mk0.5_wiring.md` §1 has the canonical pin table. |
| MLX smoke fails (`kNoAck`) | wrong address or VIN not 3V3 | Confirm `0x5A` on silkscreen; verify rail with multimeter. |
| GSR `rate%` < 50 % | ADC1 mutex contention with battery sampler | Acceptable transiently; check `mutex_timeouts` in the GSR smoke `ev_b` field. Persistent failure = race in firmware, not bench. |
| `inrng` very low on GSR | electrodes dry or detached | Re-wet with fresh Red Dot 2560 or use new electrodes. |
| `inrng` very low on `temp-forehead` | sensor pointed at ambient, not skin | Aim at forehead at ~5 cm; object should read 35–37 °C. |
| Multiple `boot_ids` in one capture | board reset mid-session | Look at the `boot` field per line to bisect; sessions across reboots are not analysable as one stream. |

---

## 8. What's next

Once you have one clean Bridge A capture and one clean Bridge B
capture:

- File the capture pair in `captures/` and note any surprises in
  [`docs/field-notes/volume-1/08_field_notes.md`](../field-notes/volume-1/08_field_notes.md).
- Bridge C (AD8232 / ECG / G2 closure) drops in when the AD8232
  arrives (~June 1–15). See [`track-J-sensor-bring-up.md §4`](../plans/2026-tier1-launch/track-J-sensor-bring-up.md).
- `tools/analyze_g2.py` (Track J commit 7) will reuse this analyser
  module for the G2 pass/fail computation.
