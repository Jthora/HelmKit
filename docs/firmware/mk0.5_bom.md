# Mk0.5 Bench Bill of Materials

- **Status**: `v0.1` (Track I commit 1 of 6; updated 2026-05-18 to reflect actual procurement)
- **Scope**: Parts required to bring up the Mk0.5 firmware on a real
  bench, sufficient for the G2 HRV validation. NOT a Tier 1 DIY kit BOM
  (that is downstream; this is for the operator's own first build).
- **Target budget**: under **$60** for the device-under-test (DUT).
  **Actual added cost as of 2026-05-18: $0** — every biometric sensor
  line is satisfied from inventory; see [docs/inventory.md §3.7](../inventory.md).
  The oracle device line ([Polar H10](../protocols/g2_oracle_device.md))
  is no longer required: the **on-board AD8232** (in inventory, arriving
  ~June 1 2026) supersedes it. Polar H10 remains as documented fallback only.

---

## 1. Device-under-test (DUT) — the Mk0.5

| # | Item | P/N | Primary vendor | Backup vendor | Unit | Qty | Lead time |
|---|------|-----|----------------|----------------|------|-----|-----------|
| 1 | Heltec WiFi LoRa 32 V3 (ESP32-S3FN8) | `HTIT-WB32LAF` | [Heltec store](https://heltec.org/project/wifi-lora-32-v3/) | DigiKey / Mouser (`Heltec V3`) | $22 | 1 | 3–7 d US |
| 2 | MAX30102 PPG breakout (**4-pack from inventory**) | Diitao 4-pack — see [inventory §3.7](../inventory.md) | (in inventory) | SparkFun `SEN-16474`, Adafruit `5046` if re-procuring | $0 | 1 of 4 | on hand |
| 3 | Li-Po cell 1100 mAh w/ JST-PH | PKCell `LP503562` | DigiKey | Adafruit (`258`, 1200 mAh JST-PH) | $8 | 1 | 3–7 d US |
| 4 | USB-C **data** cable (not power-only) | any reputable | Amazon | Apple Store | $6 | 1 | same-day |
| 5 | Solderless breadboard, half-size | any | Amazon | Adafruit (`64`) | $5 | 1 | same-day |
| 6 | Jumper wires F-F 20 cm, assorted | any | Amazon | Adafruit (`266`) | $3 | 1 pack | same-day |
| 7 | 4.7 kΩ 1/4 W resistors | any | from any kit | DigiKey (`CF14JT4K70CT-ND`) | $0.10 | 2 | same-day |

**DUT added cost: $44.20** (Heltec + battery + cable + breadboard +
jumpers + resistors). If the Heltec board, battery, USB-C cable, and
breadboard are also already on the bench, added cost is **$0**.

### 1bis. MAX30102 substitution caveat (Diitao vs SparkFun)

The inventory MAX30102 units are Diitao clones, not SparkFun
SEN-16474. Two things must be verified on one unit before first
power-on; both are bench-side, $0:

1. **On-board pull-up state.** Look at the breakout PCB near the
   SDA/SCL pads. If you see two ~10k SMT resistors (marked `103`)
   or 4.7k (`472`), pull-ups are present — **do not add external**.
   If absent, add external 4.7k from inventory between SDA→3V3 and
   SCL→3V3 on the breadboard, per [`mk0.5_wiring.md §3`](mk0.5_wiring.md).
2. **Supply-rail tolerance.** Diitao listings commonly say
   "VIN 1.8–5.5 V auto level-shift". Some clones cannot accept 5 V
   on VIN and only tolerate 3.3 V. Use the Heltec V3 3V3 rail (per
   the wiring doc), which is safe for both. **Do not** wire VIN to
   the 5 V USB rail until the clone is confirmed.

Notes carried forward from v0:

- **The USB-C cable must support data.** A surprising number of the
  "fast charge" cables in circulation are power-only and silently
  prevent `pio device monitor` from working. If you have a spare from
  a USB-C peripheral you trust, use that.
- **JST-PH (2-pin, 2.0 mm pitch)** is the Heltec V3 battery connector.
  Confirm the cell's connector before ordering — JST-XH is common but
  *not* what the Heltec V3 has.

---

## 1ter. Additional in-inventory sensors (deferred to Track J)

These ship with separate wiring waves (each gets its own minimum-wiring
sub-doc when bench-ready). None are required for G2 by itself, but
all are part of the Mk0.5 sensor surface and all are on hand or in
transit per [inventory §3.7](../inventory.md). They are listed here so
the BOM doc is the complete picture of what gets soldered to the DUT
over the bench-bring-up sequence.

| # | Item | Channel | Status | Wave |
|---|------|---------|--------|------|
| 8 | 2× MLX90614 (GY-906, IR temp, I²C `0x5A`) | `ir-temp` | on hand | Track J |
| 9 | 1× GSR module (analog → `kGsrAdc=4`) | `gsr` | on hand | Track J |
| 10 | 50× 3M Red Dot 2560 electrodes + 2× TENS leads | (electrode interface) | on hand | Track J |
| 11 | 2× MAX30205 (contact temp, I²C `0x48`/`0x49`) | `contact-temp` | arriving ~05-27 | Track J |
| 12 | 1× AD8232 (ECG AFE → GPIO 5/6/7) | `ecg` + `ecg-rr` | arriving ~06-01 | Track J |

---

## 2. Optional but useful

| # | Item | P/N | Vendor | Unit | Notes |
|---|------|-----|--------|------|-------|
| 13 | Multimeter (cheap is fine) | any | any | $20 | Verifies 3V3 rail before plugging in MAX30102. |
| 14 | 1× SMA-to-pigtail antenna | any 868/915 MHz | DigiKey | $4 | Heltec V3 ships with an SMA jack and the WiFi/BLE radio uses it; without an antenna the radio works at very short range only. Not required for Mk0.5 (no wireless) but the board is happier with one connected. |
| 15 | Opaque black electrical tape | any | hardware store | $2 | For the [PPG mounting](../mechanical/ppg_mounting_notes.md) ambient-light shroud. |

---

## 3. Oracle device (superseded — see protocol)

The G2 validation requires a known-good reference RR stream.

**Canonical path (post-2026-05-18)**: the on-board **AD8232** ECG
front-end (in inventory, arriving ~June 1 2026) is the oracle. The
Mk0.5 DUT emits both `ppg-rr` (PPG-derived) and `ecg-rr` (ECG-derived)
in the same NDJSON stream; the comparison is in-board, in-band,
zero-clock-skew. See [`g2_oracle_device.md`](../protocols/g2_oracle_device.md) TL;DR.

**Documented fallback**: Polar H10 chest strap, ~$80. Lead time same
as DUT items. Used only if the AD8232 path is unavailable (broken
unit, off-bench session, wearer-mobility scenario).

---

## 4. Bench tooling (assumed present)

Not purchased per build — these are operator-side prerequisites:

- A laptop **or a Pi 4 from inventory §1** with `pio` (PlatformIO Core)
  installed and python3 ≥ 3.10.
- Internet for first `pio` board-support download (~250 MB cache).
- ~~An Android phone if using Polar Sensor Logger as the oracle export
  path.~~ Not required on the canonical AD8232 path.

---

## 5. Order checklist

As of 2026-05-18 the canonical-path order checklist is **empty** —
every line in §1 except the Heltec board itself is already on the
bench, and the Heltec board is also in inventory (§1 Heltec LoRa 32,
revision pending verification). Bench session can start as soon as
the operator confirms board revision (V3 vs V2; see
[inventory §11](../inventory.md)).

If re-procuring from scratch (e.g. for a Tier 2 hand-build customer):

- [ ] Cross-checked every P/N against the vendor product page (P/Ns drift).
- [ ] Confirmed JST-PH on the battery cell.
- [ ] Confirmed USB-C cable lists "data" or "USB 2.0" in the spec.
- [ ] (Optional) Polar H10 ordered in parallel — only if the AD8232
      path will not be used.

Total cart (DUT + tape, ex-Heltec): **≈ $46.20**. With shipping, expect
$50–60 to the door in the US, parts in hand within 7 days of ordering.

---

## 6. Maintenance

- Update P/Ns the first time a vendor URL 404s.
- Add a row only if the part is actually needed for the bench session.
- Do **not** roll Mk1 stim parts into this BOM. Mk1 has its own.
