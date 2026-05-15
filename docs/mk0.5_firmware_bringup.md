# Mk0.5 Firmware Bringup Checklist

**Purpose.** Land the L0 + L1 + L2 biofeedback floor as a working closed-loop firmware on a single MCU before any Mk1.0 stim payload is added. Per [mk_ladder.md §2](mk_ladder.md), Mk0.5 is the rung where *sensing + feedback* exists; no stim.

**Target MCU:** Heltec WiFi LoRa 32 (V3) — ESP32-S3 + onboard OLED + Li-ion charger. From inventory, no additional purchase. Pi 4B / Jetson available for upstream logging but not in the live MCU loop.

**Status:** Drafted 2026-05-14 ahead of Sensor Wave 1 arrival (2026-05-16). Update as gates clear.

---

## 0. Pre-bringup — hardware staging (Wave 1, due 2026-05-16)

- [ ] MAX30102 PPG breakout — connect to I²C bus at 0x57. Verify presence with `i2cdetect` equivalent.
- [ ] MLX90614 GY-906 — connect to same I²C bus at 0x5A. Verify presence.
- [ ] CJMCU-6701 GSR — 3.5mm TRS jack → VOVOU 3.5mm-to-snap leads → 3M Red Dot 2560 pads. Verify physical fit of jack on receipt; if not 3.5mm, return + re-source.
- [ ] Bone-conduction-class 40mm drivers — wire one channel to MCU PWM pin via a low-side switch / class-D amp from inventory.
- [ ] Battery + TP4056 + 18650 cell from inventory — verify charge / discharge / fuel-gauge readback.

**Wave 2 arrives ~2026-05-27 → 2026-06-15** (AD8232 EMG + MAX30205 ×2). Not required for Mk0.5. Plumbed in at Mk1.x.

---

## 1. Sensor-level bringup (per-sensor smoke tests)

### 1.1 MAX30102 PPG
- [ ] Talk to I²C, read part ID register (`0xFF`) → expect `0x15`.
- [ ] Configure sample rate 100 Hz, pulse width 411 µs, IR + Red LED currents per [SparkFun example settings](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library).
- [ ] Stream raw IR samples to serial; verify pulsatile waveform on fingertip.
- [ ] Implement peak-detection → RR-interval extraction → HR display on OLED.
- [ ] Confirm RR jitter consistent with normal HRV (10–80 ms variation).

### 1.2 MLX90614 IR temp
- [ ] Read `T_obj` register (`0x07`) and `T_amb` register (`0x06`).
- [ ] Verify forehead reading 32–35 °C at room temp; ambient consistent with room.
- [ ] Settle time < 200 ms confirmed.

### 1.3 CJMCU-6701 GSR
- [ ] Apply electrodes to two fingertips of non-dominant hand or thenar eminence.
- [ ] Read analog output via ESP32 ADC (or PCF8591 from inventory if cleaner).
- [ ] Verify baseline reading stable for 60 s; verify response to a sharp inhalation or startle cue (should jump within 1–3 s).
- [ ] Implement 10 Hz low-pass filter for tonic SCL; reserve 0.5–5 Hz band for phasic SCR.

### 1.4 Audio out (bone-conduction-class)
- [ ] Generate test tone (440 Hz sine, ~70 dB scalp-coupled).
- [ ] Verify audibility through driver pressed to forehead.
- [ ] Build a paced-breath audio bed: 6 bpm cycle, 4 s inhale tone rising / 6 s exhale tone falling.

---

## 2. The L0 layer — Resonance breath pacer

- [ ] State machine: `idle → inhale (4 s) → hold (0 s) → exhale (6 s) → repeat` (6 bpm).
- [ ] Audio out follows the state machine.
- [ ] Optional: drive an LED at the same envelope for visual cue.
- [ ] OLED displays current phase + cycle count.

**G1-equivalent gate for L0:**
- [ ] Pacer holds 6 bpm to within ±2% over 30 minutes (no drift).
- [ ] Audio remains audible and consistent in volume over 30 minutes.

---

## 3. The L1 layer — HRV-coherence biofeedback

- [ ] 60-second sliding window of RR-intervals.
- [ ] Lomb–Scargle periodogram (or FFT after RR-interpolation) on window.
- [ ] Extract LF-band (0.04–0.15 Hz) power; total spectral power.
- [ ] Compute coherence ratio = LF / total.
- [ ] Map coherence to a continuous audio harmonic — when high, harmonic consonates with breath tone; when low, harmonic dissonates.

**G1-equivalent gate for L1:**
- [ ] Coherence ratio updates at least every 5 s.
- [ ] Manual paced-breathing for 60 s drives coherence ratio measurably upward.
- [ ] Coherence rendering is audibly distinguishable between high and low states.

---

## 4. The L2 layer — Session container

- [ ] State machine: `settling (3 min) → onboarding (2 min) → active (20 min) → closure (2 min) → reflection (3 min)`.
- [ ] L0 + L1 run continuously through all phases; their *audio mix* varies per phase (e.g., L1 coherence rendering only active during the active phase).
- [ ] Hardware button or OLED tap advances state or aborts session.
- [ ] On session end, write a session log to onboard storage (µSD or SPIFFS).

**G1-equivalent gate for L2:**
- [ ] Container completes start-to-end without crash for 5 consecutive sessions.
- [ ] Session log is recoverable and parseable post-session.

---

## 5. Logging

- [ ] NDJSON schema matches the psiStabilizer submodule's `a01_capture` format (per [roadmap.md §cross-cutting principle 8](roadmap.md#cross-cutting-principles-the-spine-of-the-whole-ladder)). Reserve EEG / EMG / EDA channels even if not populated at Mk0.5.
- [ ] Each line carries: monotonic timestamp, channel, value, units, session-id, phase.
- [ ] PPG raw samples + RR-intervals + HR + HRV-coherence ratio + GSR tonic + GSR phasic + IR-skin-temp written.
- [ ] One subjective Likert panel pre-session + one post-session, prompted via OLED.
- [ ] Logs forward-flushable to Pi 4B over USB or WiFi at end of session.

---

## 6. Mk0.5 G1 gate (engineering)

The full G1 checklist for Mk0.5:
- [ ] All four sensors deliver valid data simultaneously for 30 min uninterrupted.
- [ ] L0, L1, L2 layers all run cleanly through one 30-min session container.
- [ ] Session log is complete, parseable, and matches schema spec.
- [ ] No sensor dropout > 2 s in any session.
- [ ] Battery survives 1.5× session length (45 min) on a single charge.
- [ ] OLED + audio + button input remain functional throughout.

## 7. Mk0.5 G2 gate (wearer-benefit)

Per [mk_ladder.md §4](mk_ladder.md), Mk0.5's G2 is the **biofeedback-floor wearer-benefit** gate without any stim payload involved:

- [ ] **Pre-registration filed** in `experiments/` before first ABAB session.
- [ ] Within-subject ABAB design over 4 weeks: A = sessions, B = no-session weeks (or sham audio matched in length but without the breath pacer / coherence rendering).
- [ ] **Composite primary endpoint** per [mk1_session_protocol.md §6](mk1_session_protocol.md):
  - ΔRMSSD morning baseline (PPG-measured, post-wake before coffee).
  - ΔPSS-10 (Perceived Stress Scale, weekly).
  - ΔSleep-onset latency (subjective, daily).
- [ ] Pre-registered effect size threshold: $d \geq 0.4$ on the composite (mid-range of literature for paced-breathing alone).
- [ ] Result analyzed and **published either direction** (positive, null, or negative all count as Mk0.5 G2 clearance).

A Mk0.5 outcome of "G1✓, G2-null" is *not* failure; it is information about how much of the device's value depends on the stim payload that Mk1.0 will add. The decision to proceed to Mk1.0 is gated on G1✓ AND (G2✓ OR G2-null-with-mechanism-analysis).

---

## 8. Out of scope for Mk0.5

Deferred to Mk1.0 or later:

- ❌ Bifilar coil stim driver — Mk1.0.
- ❌ Dual-MCU safety interlock (MCU-A / MCU-B split) — Mk1.0; not needed when there is no stim output to gate.
- ❌ Sham-arm equivalence beyond audio — Mk1.0 (the six-channel sham spec activates when stim activates).
- ❌ EMG / AD8232 — Mk1.5.
- ❌ Dual-temple MAX30205 differential thermography — Mk1.0 (Wave 2 hardware).
- ❌ EEG — Mk2.0.
- ❌ State-aware closed-loop session-container branching — Mk2.0 (L4).

Wave 2's MAX30205 ×2 *can* be plumbed in during Mk0.5 if firmware bandwidth allows — they add a peripheral-vasomotor channel that the L0+L1+L2 loop does not strictly require but that improves the wearer-state model. Treat as opportunistic, not mandatory.
