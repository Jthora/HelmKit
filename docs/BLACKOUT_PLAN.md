# HelmKit Blackout Plan — Mk0.5 Dev-Complete by May 20, 2026

**Status:** Locked 2026-05-14 (Day 0). Committed and Zenodo-archivable as part of the defensive-IP record.

**Context:** Operator's paid-AI access (Claude Opus 4.x via Copilot) terminates approximately 2026-05-20. Free-tier AI (Grok, GPT-4o-class) remains available through the blackout window. Paid AI may resume on/around 2026-06-01 when independent income lands. **Sensor Wave 1 arrives 2026-05-16. Sensor Wave 2 arrives 2026-05-27 → 2026-06-15, fully inside the blackout window.**

**This document is the single source of truth for the May 14 → June 1 window.** Every other document defers to it for scheduling; it defers to [`docs/mk_ladder.md`](mk_ladder.md) and [`docs/mk0.5_firmware_bringup.md`](mk0.5_firmware_bringup.md) for architectural meaning.

---

## 1. The strategic principle

**Time-shift hard thinking into the paid-AI window. Leave only mechanical execution for the blackout.**

Most of Mk0.5 firmware can be written before Wave 1 arrives — sensor drivers, state machines, signal processing, NDJSON logging. They need a top-tier model that understands the domain, not a physical device. Bringup-day-on-hardware ("why is my I²C scan returning 0xFF?") is *exactly* what free-tier AI is fine for.

The triage:

| Opus-only (do BEFORE 2026-05-20) | Free-AI-fine (defer to blackout) |
|---|---|
| Lomb-Scargle HRV math + coherence rendering | Arduino-style sensor read loops |
| G2 ABAB pre-registration document | "Why won't this compile?" |
| Sham-arm six-channel equivalence design | Adding a new NDJSON field |
| Architectural decisions across Mk-ladder | Renaming variables |
| Tricky safety-interlock state machines | Reading datasheets aloud |
| Failure-mode anticipation + runbooks | Stepping through error messages |
| PRIOR_ART defensive writing | Wiring helper functions |
| Pinout-conflict resolution (e.g. Heltec ADC clashes) | Soldering checklists |

---

## 2. The six-day schedule

Each day is sized for ≈3–5 hours of focused work. Days are ordered so that **even if the AI window is truncated at Day 4, the load-bearing artifacts are already saved.**

### Day 0 — Tonight (2026-05-14, ~9pm)

**Goal:** Plan-only. No code. Lock decisions. Hit pillow without architectural debt.

Artifacts:
- ✅ This file (`docs/BLACKOUT_PLAN.md`).
- ✅ Repo-memory note (`/memories/repo/helmkit_blackout_strategy.md`).
- ✅ One signed commit + push (timestamps the plan to defensive-IP record).

### Day 1 — Tomorrow (2026-05-15) — Scaffold + first drivers

**Goal:** Firmware repo scaffold, pinout locked, toolchain proven, first driver (MAX30102, which is already in hand) confirmed working.

Artifacts:
- `firmware/mk0.5/platformio.ini` — Heltec WiFi LoRa 32 V3 target, libraries pinned by SHA, build flags.
- `firmware/mk0.5/README.md` — build/flash/serial-monitor instructions.
- `firmware/mk0.5/docs/PINOUT.md` — every pin assignment with conflict-check notes (GSR ADC vs battery ADC is the known Heltec gotcha).
- `firmware/mk0.5/docs/BUILD.md` — toolchain install + flash + debug.
- `firmware/mk0.5/src/main.cpp` — empty loop dispatcher.
- `firmware/mk0.5/src/drivers/max30102.{h,cpp}` — full driver + smoke-test sketch.
- All other `src/**/*.{h,cpp}` files exist as stub headers with `TODO(Day N)` markers.
- **Toolchain verified:** `pio run` compiles a hello-world for the Heltec target.
- **Bench-readiness audit:** USB-C cable, breadboard, jumpers, soldering iron, multimeter, calipers (for Wave-1 plug verification), label tape — checklist committed.

Stretch (if energy permits): begin MLX90614 driver (Wave 1, arrives tomorrow).

### Day 2 — 2026-05-16 (Wave 1 arrival day) — Drivers + pre-reg draft

**Goal:** All Wave-1 sensors driving cleanly + G2 pre-registration first draft.

Morning (Wave 1 still in transit):
- G2 ABAB pre-registration first draft (`experiments/mk0.5_g2_prereg.md`).
- Daily Likert-panel prompt schema.

Afternoon (Wave 1 arrives ~midday):
- Caliper-verify VOVOU plug diameter matches CJMCU-6701 jack (anti-precedent from cart-review discipline).
- MLX90614 driver + smoke test.
- CJMCU-6701 GSR driver + ADC smoke test.
- Audio-out driver (PWM/I2S to bone-conduction-class driver).
- OLED, button, battery drivers (all on-board Heltec; should be quick).
- **End-of-day gate:** four-sensor concurrent capture, 5-minute run, NDJSON log file readable on host.

### Day 3 — 2026-05-17 — DSP + L0/L1/L2 layers

**Goal:** The load-bearing math. **This is the day most expensive to lose.**

Artifacts:
- `dsp/rr_extract.{h,cpp}` — peak detection on PPG IR channel, RR-interval extraction, artifact rejection.
- `dsp/hrv_coherence.{h,cpp}` — 60-second sliding window, Lomb-Scargle periodogram (or RR-interpolation + FFT), LF-band (0.04–0.15 Hz) power, total spectral power, coherence ratio.
- `dsp/gsr_filter.{h,cpp}` — 10 Hz low-pass for tonic SCL; 0.5–5 Hz band-pass for phasic SCR.
- `layers/l0_breath_pacer.{h,cpp}` — 6 bpm state machine, 4 s inhale / 6 s exhale, audio + LED rendering.
- `layers/l1_hrv_coherence.{h,cpp}` — consume DSP output, render coherence as audio harmonic that consonates with breath tone when high.
- `layers/l2_session_container.{h,cpp}` — 3+2+20+2+3 minute state machine.
- `log/ndjson.{h,cpp}` — forward-compatible schema, channel names matching psiStabilizer `a01_capture`.
- `log/storage.{h,cpp}` — SPIFFS or µSD writer.
- **Unit tests** (PlatformIO host-runnable): `test_rr_extract/`, `test_hrv_coherence/` with golden-data fixtures.

### Day 4 — 2026-05-18 — Pre-reg LOCK + G2 analysis pipeline

**Goal:** Final-commit G2 pre-reg, Zenodo-DOI it, build the Python analysis pipeline that consumes NDJSON logs.

Artifacts:
- `experiments/mk0.5_g2_prereg.md` — **LOCKED, signed, tagged, and Zenodo-archived** with its own DOI. No further edits allowed.
- `experiments/mk0.5_g2_analysis.py` — consumes NDJSON, computes ΔRMSSD-morning + ΔPSS-weekly + Δsleep-onset, pre-registered weights, effect-size CIs.
- `experiments/mk0.5_g2_subjective_panel.md` — daily and weekly Likert questionnaires.
- `experiments/mk0.5_g2_sham_audio_spec.md` — what the sham control's audio bed is (matched in length / loudness / spectral character but lacking the breath-pacer envelope and the coherence rendering).
- Mk0.5 end-to-end: full 30-minute session container run, log captured, analysis script runs on it, produces a single-session report.
- **Gate:** "press button, wear helm, 30 min later, NDJSON log appears, Python script renders a session report." If this works, Mk0.5 is functionally dev-complete; remaining days are hardening.

### Day 5 — 2026-05-19 — Mk1.0 / Mk1.5 architectural spec + Wave-2 stubs

**Goal:** Lock everything needed to plumb Wave 2 (arrives during blackout) without architectural decisions.

Artifacts:
- `firmware/mk1.0/docs/COIL_DRIVER_SPEC.md` — bifilar-coil driver schematic + firmware: pin assignments, PWM/DAC config, 1–8 MHz carrier with 7.83 Hz envelope, dual-MCU split (MCU-A drives, MCU-B supervises), six-channel sham gates each with named instrument + pass/fail threshold.
- `firmware/mk1.5/docs/EMG_CHAIN_SPEC.md` — AD8232 signal-conditioning chain spec, filter swap from ECG (0.5–40 Hz) to EMG (20–500 Hz), sample rate, RMS-envelope window, upper-trapezius placement.
- `firmware/mk1.5/docs/IMU_FUSION_SKETCH.md` — head-pose + sway + strike-velocity from MPU9250.
- `firmware/mk0.5/src/drivers/max30205.{h,cpp}` — written and stubbed against simulated I²C, ready to slot in when Wave 2 arrives. Dual-temple address-select (A0/A1/A2 pin scheme), differential channel derived in firmware.
- `firmware/mk0.5/src/drivers/ad8232.{h,cpp}` — same: written, stub-tested, slot-ready.

### Day 6 — 2026-05-20 (final paid-AI day) — Blackout runbook + handoff

**Goal:** Convert all the implicit context that lives in this AI conversation into explicit artifacts that future-you with only GPT-4o can use.

Artifacts:
- `docs/BLACKOUT_RUNBOOK.md` — for every sensor + every state-machine layer, a diagnostic ladder: "if X happens, check Y, then Z." Written *to* future-self-with-only-GPT-4o.
- `firmware/mk0.5/docs/PROMPTS.md` — ready-to-paste prompts for free AI:
  - "Here is my I²C scan output. Tell me what's wrong." (template)
  - "Here is my failing PlatformIO build. Walk me through it." (template)
  - "Here is the relevant section of mk0.5_firmware_bringup.md and my code. Help me wire X to Y." (template)
- `WAVE2_PLUMBING.md` — exact wiring + exact code-stub locations for AD8232 + MAX30205 ×2 plumbing on the day they arrive.
- PRIOR_ART.md update if any new inventive elements crystallized during the firmware work.
- **Hard gate:** "Read BLACKOUT_RUNBOOK.md aloud. If something I'd need is missing, write it now."

---

## 3. Decisions locked at Day 0

These are baselined as of 2026-05-14. Flipping any after Day 2 carries cost; flipping after Day 4 is expensive.

| # | Decision | Locked value | Rationale |
|---|---|---|---|
| 1 | Heltec-only for Mk0.5 | **Yes** | One MCU, one firmware, one debug surface — survivable under free-AI. Pi-host is Mk1.0+ scope. |
| 2 | Pi role for Mk0.5 | **Log-flush endpoint only** | USB-serial sink; no live-loop responsibility. NDJSON logs are forward-compatible upward. |
| 3 | Firmware lives in | `HelmKit/firmware/mk0.5/` | Not psiStabilizer submodule. psiStabilizer remains the analysis/data layer. |
| 4 | Pre-reg cadence | **Draft Day 2, lock Day 4** | Highest Opus-only artifact. Cannot be finalized later without paid AI. |
| 5 | Stim payload at Mk0.5 | **None** | G1+G2 only; no G3. Confirmed by [`mk_ladder.md`](mk_ladder.md). |
| 6 | If AI truncates at Day 4 | **Irreducible saves:** pre-reg + DSP layer | These two artifacts are most expensive to redo without paid AI. |
| 7 | If AI truncates at Day 3 | **Irreducible saves:** scaffold + DSP layer | DSP is load-bearing; scaffold gives free-AI a map. |
| 8 | Wave 2 firmware development | **Stubbed Day 5, plumbed during blackout** | Drivers written against simulated I²C; physical plumbing is free-AI work. |
| 9 | Polar H10 ECG cross-validation | **Deferred** | Mk0.5 G2-result-dependent. ~$80 future buy. |
| 10 | Pre-flight bench audit | **Day 1 morning** | USB-C cable, breadboard, jumpers, soldering iron, multimeter, calipers, label tape. |

---

## 4. Free-AI cheat sheet (for blackout-you)

When you're past 2026-05-20 and reaching for Grok or GPT-4o, **what to feed them and how:**

### 4.1 Always paste these as context

Before asking any question, paste:
1. The relevant section of [`mk0.5_firmware_bringup.md`](mk0.5_firmware_bringup.md) (or the equivalent for whatever you're working on).
2. The relevant code file (whole file if < 200 lines; relevant function + 20 lines context otherwise).
3. The error / unexpected behavior verbatim.
4. What you've already tried.

### 4.2 What free-AI is genuinely good at

- "Why won't this compile? Here's the error and the source line."
- "Walk me through what this Arduino library function does."
- "What's the I²C address of [chip]?"
- "Help me write a Python script that reads my NDJSON log and plots channel X over time."
- "Translate this datasheet section into plain English."
- "I'm seeing 0xFF on the I²C bus where I expect 0x57 — what are the usual causes?"

### 4.3 What free-AI is bad at — DO NOT ASK during blackout

- "Should I change my Mk-ladder?" → No. The ladder is locked. See [`mk_ladder.md`](mk_ladder.md).
- "Is my G2 design statistically valid?" → No. The pre-reg is locked at Day 4. Do not re-litigate.
- "Should I add EEG?" → No. EEG is Mk2.0 capex.
- "Should I change my NDJSON schema?" → No. Forward-compat policy. Add channels, never rename or repurpose.
- "Should I rewrite this firmware in Rust / Zephyr / FreeRTOS?" → No. Heltec + Arduino-core is locked.
- "Should I order more sensors?" → No until paid AI returns and budget is reviewed.

### 4.4 If free-AI gives you a confident-sounding architectural opinion

**Reject it.** The architecture is locked. The pre-reg is locked. The Mk-ladder is locked. Free models drift on long-horizon coherence. Their job during blackout is *executing* the plan, not *revising* it.

If something genuinely seems broken architecturally, **wait until paid-AI returns ~2026-06-01.** Do not silently flip a locked decision.

---

## 5. Recovery contract (for paid-AI when it returns ~2026-06-01)

When paid AI resumes, the resumption prompt should be:

> "Resuming HelmKit work. Read `docs/BLACKOUT_PLAN.md` and `/memories/repo/helmkit_blackout_strategy.md` first. Then read `docs/BLACKOUT_RUNBOOK.md`. Then `git log --since=2026-05-20`. Then ask me what's blocking, not what to do next."

The repo memory note + the blackout plan + the git log are sufficient to fully re-context any future Opus session within one read pass.

---

## 6. Wave-2 plumbing (during blackout, no paid-AI required)

When AD8232 + MAX30205 ×2 arrive (2026-05-27 → 2026-06-15):

1. Open `WAVE2_PLUMBING.md` (written Day 6).
2. Wire AD8232 per pinout: VCC, GND, OUT → GPIO 2 (ADC), LO+ → GPIO 3, LO− → GPIO 4. Bias/REF as datasheet.
3. Wire MAX30205 ×2 onto the existing I²C bus. Set address-select pins: temple-A = 0x48, temple-B = 0x49.
4. Uncomment the `#define WAVE2_PRESENT` line in `firmware/mk0.5/src/main.cpp`.
5. Rebuild + flash.
6. Run the four-sensor smoke test (now six-sensor).
7. Capture a 5-minute log. Verify the new channels appear in the NDJSON.

If any step fails, free-AI is fine for diagnostics. If the architecture seems wrong, **wait for paid AI**.

---

## 7. Discipline rules (post-Day 6, during blackout)

1. **Do not flip locked decisions.** See §3.
2. **Do not collect any session data before the pre-reg is locked.** (Day 4 gates this.)
3. **Sign every commit.** GPG is set up; the muscle memory exists.
4. **Push every commit the same day.** Defensive-IP timestamping continues during blackout.
5. **One Zenodo deposit per Mk-step gate cleared.** Mk0.5 G1 = one DOI. Mk0.5 G2 = another DOI.
6. **If in doubt, defer.** A deferred decision is recoverable. A wrong locked-in decision under free-AI is not.

---

## 8. What this plan does NOT cover

- **Mk1.0 build:** requires bifilar PCB coil fabrication (PCB-house lead time). Out of scope for May 14–June 1 window.
- **Mk1.5 build:** requires Mk1.0 complete + Combat firmware. Out of scope.
- **G3 RCT recruitment:** all Mk1.0+ scope.
- **Polar H10 G1 cross-validation:** deferred per Decision #9.
- **EEG-based modes (Focus, Creative, Vigilance, Social, Recovery):** all Mk2.0 scope, $250+ capex.

These are *correctly* out of scope. The Mk0.5 dev-complete deliverable is the load-bearing milestone for the next 3 weeks of paid-AI-free work. Reaching past it is greedy.
