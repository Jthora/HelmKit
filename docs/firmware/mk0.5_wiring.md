# Mk0.5 Bench Wiring — Heltec V3 ↔ MAX30102

- **Status**: `v0` (Track I commit 2 of 6)
- **Scope**: Minimum wiring to bring the Mk0.5 firmware up against a
  single MAX30102 PPG sensor on a breadboard. **GSR, ECG, and thermal
  sensors are out of scope here** — they ship in later waves and use
  pins documented in [`firmware/mk0.5/docs/PINOUT.md`](../../firmware/mk0.5/docs/PINOUT.md).
- **Authority**: The pin assignments below mirror the constants in
  [`firmware/mk0.5/src/board/pins.h`](../../firmware/mk0.5/src/board/pins.h),
  which in turn conforms to PINOUT.md. If this doc and PINOUT.md
  disagree, **PINOUT.md wins** — fix this doc.

---

## 1. Pin table (canonical)

| Heltec V3 GPIO | Heltec V3 silkscreen | MAX30102 pad | `pins.h` constant | Jumper colour (suggested) | Notes |
|----------------|----------------------|--------------|-------------------|---------------------------|-------|
| GPIO 41 | `41` | `SDA` | `kExtI2cSda` | yellow | External I²C bus 1, 400 kHz. |
| GPIO 42 | `42` | `SCL` | `kExtI2cScl` | green  | (paired with SDA) |
| GPIO 38 | `38` | `INT` | `kMax30102Int` | blue   | Active-LOW, FIFO almost-full. Optional but recommended — without it the driver polls. |
| 3V3 rail (any 3V3 pin) | `3V3` | `VIN` | — | red    | Heltec V3 3V3 LDO output, 600 mA capable. |
| GND rail (any GND pin) | `GND` | `GND` | — | black  | Common ground. |

That's it. Five wires. Anything more belongs to a later wave.

---

## 2. ASCII sketch

```
              ┌──────────────────────────┐
              │      Heltec V3           │
              │   (ESP32-S3FN8 + LoRa)   │
              │                          │
              │  USB-C ──────── host PC  │
              │                          │
              │  3V3 ──────┐             │
              │  GND ───┐  │             │
              │         │  │             │
              │  GPIO41 │  │  SDA        │
              │  GPIO42 │  │  SCL        │
              │  GPIO38 │  │  INT        │
              └─────────┼──┼─────────────┘
                        │  │
                  black │  │ red
                        │  │
                ┌───────▼──▼───────────────┐
                │     half-size            │
                │     breadboard           │
                │                          │
                │   ─── 4.7kΩ ── 3V3 ──    │   (SDA pull-up, if not on breakout)
                │   ─── 4.7kΩ ── 3V3 ──    │   (SCL pull-up, if not on breakout)
                │                          │
                └─────┬──┬──┬──────────────┘
                      │  │  │
            yellow ── │  │  │ ── green   (SDA / SCL to MAX30102)
                blue ─────────┘          (INT to MAX30102)
                      │  │
                ┌─────▼──▼────────────────┐
                │    MAX30102 breakout    │
                │   (SparkFun SEN-16474)  │
                │                         │
                │   VIN  GND  SDA  SCL  INT
                └─────────────────────────┘
```

---

## 3. Pull-ups

The SparkFun SEN-16474 already has on-board 4.7 kΩ pull-ups on SDA and
SCL. **If you are using that board, do not add external pull-ups** —
parallel pull-ups halve the effective resistance and degrade the I²C
rise time at 400 kHz.

If you are using a different breakout (e.g. a generic clone), check
for SMD resistors near the SDA/SCL traces. If absent, add 4.7 kΩ from
each line to 3V3 on the breadboard, as drawn above.

### 3.1 Diitao 4-pack (the in-inventory units, 2026-05-18)

The inventory MAX30102 units are Diitao clones, not SparkFun. Pull-up
state is not guaranteed and varies by batch.

**Verified on the in-hand units (2026-05-18):** SMT resistors near the
I²C lines are marked `472` → **4.7 kΩ pull-ups present on SDA and
SCL**. Do **not** add external pull-ups on the breadboard for these
units — parallel pull-ups would halve effective resistance and degrade
the rise time at 400 kHz, same caveat as §3 (SparkFun).

If you ever receive a Diitao batch from a different production run,
re-verify before wiring:

1. Look at the breakout PCB near the SDA and SCL pads. Two small
   SMT resistors marked `103` (= 10 kΩ) or `472` (= 4.7 kΩ) means
   pull-ups are present; do **not** add external ones.
2. If no SMT resistors are visible on the I²C lines, add 4.7 kΩ
   external pull-ups from SDA→3V3 and SCL→3V3 on the breadboard
   (from the inventory resistor stock).
3. Diitao listings commonly say "VIN 1.8–5.5 V auto level-shift".
   Some clones cannot tolerate 5 V on VIN. Wire VIN to the Heltec V3
   **3V3** rail only — it is safe for any MAX30102 clone in any state.
   Do **not** experiment with 5 V on a brand-new unit. This is the
   standing policy until a per-batch data-sheet confirms otherwise.

---

## 4. First-power-on sanity sequence

Before flashing the firmware:

1. **Wire everything with the USB cable unplugged.** Double-check VIN
   and GND. A reversed power connection on the MAX30102 will release
   the magic smoke.
2. **Multimeter check the 3V3 rail at the MAX30102 VIN pad** — should
   read 3.25–3.35 V with USB plugged in. If it's significantly low,
   the Heltec V3 LDO is unhappy (usually a brownout from a flaky USB-C
   cable).
3. **Bus continuity**: with USB unplugged, beep-test SDA from GPIO 41 to
   the MAX30102 SDA pad. Same for SCL.

After flashing, the firmware's boot smoke test should report the
MAX30102 at I²C address `0x57` (the only address the part responds to;
not configurable). If the smoke test fails with `no-ack`:

- Verify pull-ups (see §3).
- Verify VIN voltage (see §4 step 2).
- Power-cycle (USB unplug, re-plug). The MAX30102 latches occasionally
  if the rails come up out of order.

---

## 5. What is **not** wired at this stage

These are documented in [PINOUT.md](../../firmware/mk0.5/docs/PINOUT.md) §2 and
are reserved silicon but **not** populated on the bench until later
waves:

- GSR (CJMCU-6701 → GPIO 4).
- ECG (AD8232 → GPIO 5/6/7).
- Forehead IR temp (MLX90614 → external I²C, address `0x5A`).
- Skin temp L/R (MAX30205 → external I²C, addresses `0x48`/`0x49`).
- Status LED (GPIO 35) — optional, not required for G2.

Each wave adds its own minimum-wiring sub-doc when it's time. Keeping
the bench at one sensor for G2 isolates the variable being validated.

---

## 6. Maintenance

- If `pins.h` constants change, this doc's pin-table column 4 must
  change in the same commit.
- If PINOUT.md adds a new bench-relevant sensor wave, a new section
  (`§5` body) gets added here, not a new doc.
