# Mk0.5 Bench Bill of Materials

- **Status**: `v0` (Track I commit 1 of 6)
- **Scope**: Parts required to bring up the Mk0.5 firmware on a real
  bench, sufficient for the G2 HRV validation. NOT a Tier 1 DIY kit BOM
  (that is downstream; this is for the operator's own first build).
- **Target budget**: under **$60** for the device-under-test (DUT); the
  oracle device ([Polar H10](../protocols/g2_oracle_device.md)) is a
  separate ~$80 line item budgeted independently.

---

## 1. Device-under-test (DUT) — the Mk0.5

| # | Item | P/N | Primary vendor | Backup vendor | Unit | Qty | Lead time |
|---|------|-----|----------------|----------------|------|-----|-----------|
| 1 | Heltec WiFi LoRa 32 V3 (ESP32-S3FN8) | `HTIT-WB32LAF` | [Heltec store](https://heltec.org/project/wifi-lora-32-v3/) | DigiKey / Mouser (`Heltec V3`) | $22 | 1 | 3–7 d US |
| 2 | MAX30102 PPG breakout | SparkFun `SEN-16474` | [SparkFun](https://www.sparkfun.com/products/16474) | Adafruit (`5046`) | $15 | 1 | 2–5 d US |
| 3 | Li-Po cell 1100 mAh w/ JST-PH | PKCell `LP503562` | DigiKey | Adafruit (`258`, 1200 mAh JST-PH) | $8 | 1 | 3–7 d US |
| 4 | USB-C **data** cable (not power-only) | any reputable | Amazon | Apple Store | $6 | 1 | same-day |
| 5 | Solderless breadboard, half-size | any | Amazon | Adafruit (`64`) | $5 | 1 | same-day |
| 6 | Jumper wires F-F 20 cm, assorted | any | Amazon | Adafruit (`266`) | $3 | 1 pack | same-day |
| 7 | 4.7 kΩ 1/4 W resistors | any | from any kit | DigiKey (`CF14JT4K70CT-ND`) | $0.10 | 2 | same-day |

**DUT subtotal: $59.20** (under the $60 cap).

Notes:

- **Avoid AliExpress/eBay MAX30102 clones.** A meaningful fraction of
  the cheap clones have either a different (incorrect) reflectance
  geometry or a clone IC that misreports IR amplitude. SparkFun and
  Adafruit boards both expose the real Maxim part with documented
  power management. The $5 saving is not worth a failed G2 session.
- **The USB-C cable must support data.** A surprising number of the
  "fast charge" cables in circulation are power-only and silently
  prevent `pio device monitor` from working. If you have a spare from
  a USB-C peripheral you trust, use that.
- **JST-PH (2-pin, 2.0 mm pitch)** is the Heltec V3 battery connector.
  Confirm the cell's connector before ordering — JST-XH is common but
  *not* what the Heltec V3 has.

---

## 2. Optional but useful

| # | Item | P/N | Vendor | Unit | Notes |
|---|------|-----|--------|------|-------|
| 8 | Multimeter (cheap is fine) | any | any | $20 | Verifies 3V3 rail before plugging in MAX30102. |
| 9 | 1× SMA-to-pigtail antenna | any 868/915 MHz | DigiKey | $4 | Heltec V3 ships with an SMA jack and the WiFi/BLE radio uses it; without an antenna the radio works at very short range only. Not required for Mk0.5 (no wireless) but the board is happier with one connected. |
| 10 | Opaque black electrical tape | any | hardware store | $2 | For the [PPG mounting](../mechanical/ppg_mounting_notes.md) ambient-light shroud. |

---

## 3. Oracle device (separate budget — see protocol)

The G2 validation requires a known-good reference RR stream. See
[`docs/protocols/g2_oracle_device.md`](../protocols/g2_oracle_device.md)
for the decision and BOM.

Primary: **Polar H10** chest strap, ~$80. Lead time same as DUT items.

---

## 4. Bench tooling (assumed present)

Not purchased per build — these are operator-side prerequisites:

- A laptop with `pio` (PlatformIO Core) installed and python3 ≥ 3.10.
- Internet for first `pio` board-support download (~250 MB cache).
- An Android phone if using Polar Sensor Logger as the oracle export path.

---

## 5. Order checklist

Before placing the order:

- [ ] Cross-checked every P/N against the vendor product page (P/Ns drift).
- [ ] Confirmed JST-PH on the battery cell.
- [ ] Confirmed USB-C cable lists "data" or "USB 2.0" in the spec.
- [ ] Polar H10 ordered in parallel from a separate vendor (faster total lead).

Total cart (DUT + tape): **≈ $61.20**. With shipping, expect $65–75 to
the door in the US, parts in hand within 7 days of ordering.

---

## 6. Maintenance

- Update P/Ns the first time a vendor URL 404s.
- Add a row only if the part is actually needed for the bench session.
- Do **not** roll Mk1 stim parts into this BOM. Mk1 has its own.
