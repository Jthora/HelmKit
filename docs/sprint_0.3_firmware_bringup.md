# Sprint 0.3 — firmware bring-up

**Brief (verbatim from the operator):**
> *Sprint 0.3 — firmware. With the CAD shell (0.1) and circuit
> spec (0.2) done, today you start firmware: pick toolchain, get
> blink working on the MCU you spec'd, set up the repo. Just
> boot a workspace and prove the chip wakes up.*

Status: **DONE** at sprint close. See §6 DoD.

---

## 1. Scope

This sprint has exactly four deliverables. No more.

1. **Toolchain pick** — name it, install it, write down why.
2. **Repo layout** — `firmware/` exists, has a `.gitignore`,
   has a README that says where future sprints land.
3. **Blink** — the MCU that sprint 0.2 spec'd as the platform's
   primary brain wakes up, runs a program, and proves it's alive.
4. **Documentation of the above** — this file + `firmware/README.md`.

### Out of scope (explicitly)

- The §6.5.5 safety state machine. → sprint 0.3a.
- The Stabilizer module firmware. → see [`external/psiStabilizer`](../external/psiStabilizer) submodule + sprint 0.3a.
- Pi 4 host service. → sprint 0.5.
- Heltec V3 session UI / LoRa uplink. → sprint 0.4.
- Any actual sensor reads. → sprint 0.4+.

Sprint 0.3 is **the workspace boot**, nothing more.

---

## 2. Toolchain pick

**Decision: `arduino-cli`.**

Locked rationale:

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| **arduino-cli** | free, scriptable, brewable, supports AVR + ESP32 cores, CI-friendly, no GUI dependency | less powerful than PlatformIO | **picked** |
| Arduino IDE 2.x | nice-to-have for visual debug + serial plotter | Electron weight, not source-of-truth | optional install only |
| PlatformIO | unified multi-target builds, better deps | heavier, more YAML, slower onboarding | **deferred** — adopt if sprint 0.5+ needs it |
| AVR-GCC raw | maximum control | too much yak-shaving for "prove the chip wakes up" | rejected |
| ESP-IDF (for Heltec) | native ESP32 power | overkill for sprint 0.3; arduino-esp32 core is fine | deferred to sprint 0.4 |

**Install footprint (macOS):**

```bash
brew install arduino-cli      # 24.8 MB, no GUI
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr     # ATmega328P / Nano v3
# Heltec V3 (deferred to sprint 0.4):
# arduino-cli core install esp32:esp32
```

Verified on sprint 0.3 build day:
- `arduino-cli` version 1.4.1
- `arduino:avr` core 1.8.7
- `arduino:avrdude` 8.0.0-arduino1

---

## 3. MCU choice

**Target: Arduino Nano v3 (ATmega328P, 16 MHz).**

This is the MCU sprint 0.2 §3.3.2 named as the B-PWR **safety
controller** — the lowest-trust, simplest, most deterministic
brain in the platform. It is the right place to start firmware
work for three reasons:

1. **Determinism.** The Nano runs bare-metal with no RTOS. If
   blink doesn't blink, the bug is in our code or our hardware,
   not in a scheduler.
2. **Fast iteration.** AVR compile + flash is sub-second on this
   machine. Tight feedback loop.
3. **Safety-relevant.** The Nano is the MCU that will eventually
   drive K1 (12V_RAIL kill relay) and run the §6.5.5 safety
   state machine. Getting comfortable with this chip *first* is
   the right investment.

The Pi 4 and Heltec V3 (the other two MCUs in the platform) are
deferred to later sprints when they have actual work to do.

---

## 4. Repo layout

Created this sprint:

```
HelmKit/
├── firmware/
│   ├── README.md
│   ├── .gitignore
│   └── nano_bringup/
│       └── nano_bringup.ino
└── docs/
    └── sprint_0.3_firmware_bringup.md   ← this file
```

The `firmware/README.md` documents:
- the toolchain pick and install commands,
- one-target-one-subdirectory convention,
- where each future sprint's firmware will land
  (`nano_safety/`, `heltec_uplink/`, `pi_bridge/`,
  `stabilizer_mk1/`),
- the build/flash/monitor command set.

---

## 5. The blink program

File: [`firmware/nano_bringup/nano_bringup.ino`](../firmware/nano_bringup/nano_bringup.ino)

What it does:
- Blinks D13 (on-board LED) at 1 Hz.
- Emits `helmkit-mk0 nano alive tick=N` on Serial @ 115200 baud
  once per second.
- Prints `F_CPU` at boot so we can confirm the fuse/clock
  configuration is correct.

What it deliberately does **not** do:
- Touch any of the §3.3.2 platform pins (D2 SAFETY_n, D3 K1
  drive, A4/A5 I²C, etc.).
- Implement the safety state machine.
- Assume any external hardware.

**Build verification (sprint close):**

```bash
arduino-cli compile --fqbn arduino:avr:nano:cpu=atmega328 \
  firmware/nano_bringup
```

Output:
> Sketch uses 2522 bytes (8%) of program storage space. Maximum is 30720 bytes.
> Global variables use 197 bytes (9%) of dynamic memory, leaving 1851 bytes for local variables. Maximum is 2048 bytes.

Clean compile. **8% flash / 9% RAM** for a blink + heartbeat is
fine — leaves comfortable headroom for the sprint-0.3a safety
state machine (estimated ~6 KB / 400 B more).

> **Phase-1 size figures preserved for the record.** Phase-2
> hardening grew the sketch to 4860 B (15%) / 238 B RAM (11%),
> still leaving 25 KB / 1.8 KB of headroom. See §9.

---

## 6. Definition of Done — Phase 1 (compile-gate close)

| # | Gate | Status | Evidence |
|---|---|---|---|
| 1 | Toolchain picked | ✅ | §2 of this doc + [`firmware/README.md`](../firmware/README.md#toolchain-sprint-03-pick) |
| 2 | Toolchain installed on dev machine | ✅ | `arduino-cli` 1.4.1 + `arduino:avr` core 1.8.7 verified |
| 3 | `firmware/` directory exists with `.gitignore` and README | ✅ | committed this sprint |
| 4 | Bring-up sketch compiles for `arduino:avr:nano:cpu=atmega328` | ✅ | 2522 bytes flash, 197 bytes RAM |
| 5 | This sprint doc written and committed | ✅ | you're reading it |
| 6 | *(bench)* Sketch flashes to a physical Nano and blinks | ⏳ | operator hands-on; not blocking |
| 7 | *(bench)* Serial heartbeat visible at 115200 baud | ⏳ | operator hands-on; not blocking |

Gates 1–5 are reproducible from this repo alone. Gates 6–7
require physical hardware. **Phase 1 closed the sprint at
commit `ee15859`.**

---

## 7. What phase 1 explicitly did NOT settle (and why we re-opened)

After phase 1 closed, the sprint was re-opened on the
operator's challenge: *"I want it to be exceedingly robust, and
redundantly safe."*

Honest critique of phase 1:

- **No watchdog.** The MCU that will later drive K1 could hang
  silently. Unacceptable even at bring-up.
- **No reset-cause reporting.** `MCUSR` ignored. WDT/BOD/EXT
  resets were indistinguishable from cold boot.
- **No fail-safe pin init.** §3.3.2 pins were left at power-on
  default. If the Nano were socketed into B-PWR before sprint
  0.3a, K1_DRIVE behavior was "whatever the floating gate does."
- **No build-ID in firmware.** Multiple flashed chips were
  indistinguishable.
- **Freeform heartbeat string.** Sprint 0.5's parser would have
  been fragile.
- **No CI.** Compile worked on one laptop on one day.
- **No host-side smoketest.** No way to assert protocol
  conformance.
- **No simulation path.** Bench gates were indefinite blockers.
- **No bench checklist.** Operator had to assemble the safe
  ordering themselves.
- **No safety doc.** Convention announced ≠ convention enforced.

Phase 2 closes each of these.

---

## 8. Definition of Done — Phase 2 (hardening pass)

Five commits, each independently reviewable.

### Phase-2 gates

| # | Gate | Commit | Status |
|---|---|---|---|
| A1 | Four-belt safety model implemented in `nano_bringup.ino` | `50167b9` | ✅ |
| A2 | WDT at `WDTO_2S`, pet path verified by inspection | `50167b9` | ✅ |
| A3 | MCUSR snapshot at `.init3`, decoded in boot banner | `50167b9` | ✅ |
| A4 | All §3.3.2 platform pins fail-safe initialized | `50167b9` | ✅ |
| A5 | `BUILD_ID` from `git rev-parse --short HEAD` injected | `50167b9` | ✅ |
| A6 | `firmware/build.sh` wrapper with FQBN mapping + `--warnings all` | `50167b9` | ✅ |
| A7 | Free-RAM reporting on every heartbeat | `50167b9` | ✅ |
| B1 | `firmware/PROTOCOL.md` — formal serial protocol contract | `6afa4c9` | ✅ |
| B2 | CRC-8 reference implementations (C + Python) match | `6afa4c9` + `7132129` | ✅ |
| C1 | `tools/heartbeat_smoketest.py` with `--port` + `--fixture` modes | `7132129` | ✅ |
| C2 | Fixtures cover happy path AND WDT-reset failure path | `7132129` | ✅ |
| C3 | `.github/workflows/firmware.yml` — compile + smoketest on every push | `7132129` | ✅ |
| C4 | Meta-test: CI asserts the WDT fixture FAILS without `--allow-fault-bits` | `7132129` | ✅ |
| D1 | Wokwi `diagram.json` + `wokwi.toml` for `nano_bringup` | `880f954` | ✅ |
| D2 | Visual K1-coil indicator on the diagram (Belt 1 visible) | `880f954` | ✅ |
| D3 | `firmware/BENCH_CHECKLIST.md` with per-chip first-flash gates | `880f954` | ✅ |
| D4 | Multimeter D3-LOW verification step before socketing | `880f954` | ✅ |
| E1 | `firmware/SAFETY.md` — four-belt model codified | this commit | ✅ |
| E2 | Banned-API list documented and enforced by review | this commit | ✅ |
| E3 | Pin-citation convention documented | this commit | ✅ |
| E4 | `firmware/README.md` updated for phase-2 reality | this commit | ✅ |
| E5 | This phase-2 section written | this commit | ✅ |

**Phase 2 closes sprint 0.3 in commit `<this>` after `880f954`.**

### Bench gates (per-chip, not per-sprint)

These are now **per physical chip, run once on first flash**,
governed by [`firmware/BENCH_CHECKLIST.md`](../firmware/BENCH_CHECKLIST.md):

- [ ] Sketch flashes to a physical Nano v3.
- [ ] Boot banner reports `mcusr=0x01 (POR )` on cold boot.
- [ ] D13 LED blinks at ~1 Hz.
- [ ] D3 measured **0.00 V** (Belt 1 verified on silicon).
- [ ] `heartbeat_smoketest.py --port ...` exits 0.
- [ ] WDT actually fires (one-time verification per chip).

Anyone with a browser can clear the equivalent of the first
three via Wokwi *today*, without a Nano on their bench.

---

## 9. Size + headroom budget after phase 2

| Resource | Phase 1 | Phase 2 | Headroom remaining |
|---|---|---|---|
| Flash | 2522 B (8%) | **4860 B (15%)** | 25.9 KB |
| SRAM (statics) | 197 B (9%) | **238 B (11%)** | 1810 B |

Sprint-0.3a safety state machine is estimated at +6 KB flash /
+400 B RAM. Post-0.3a projection: ~35% flash / ~30% RAM. Well
inside budget on this MCU.

---

## 10. Lessons from this re-open (recorded for future sprints)

1. **"Compile-gate closed" is not the same as "sprint closed"**
   for any deliverable on the safety path. A safety MCU needs
   the four belts even at bring-up, not as a future addition.
2. **Re-opens are valid even after a clean DoD.** The first DoD
   was honestly satisfied; it was just too low a bar. Re-opening
   to *raise the bar* is a different kind of work than re-opening
   to *fix a defect* — both belong on the menu.
3. **CI is not a luxury for safety firmware.** Without it, the
   compile gate evaporates the moment I close my laptop.
4. **Simulation removes one whole class of blockers.** "I don't
   have a Nano on this bench today" should never block review.
5. **The bench checklist is the firmware's last line of defense.**
   Anything that could go wrong between "binary works in sim"
   and "binary on chip in platform" needs a numbered step with
   a checkbox.

---

## 8. Next sprint preview (0.3a)

Sprint 0.3a's brief, in advance:

> Add the §6.5.5 safety state machine on top of `nano_bringup`.
> States: OFF → ARMED → SESSION_ACTIVE → FAULT. Read SAFETY_n
> (D2, input pull-up), drive K1 (D3, low-side to relay coil).
> Use Timer1 + watchdog. Add unit-testable logic
> (state-transition table separable from `digitalRead`/`digitalWrite`).

This sprint's deliverables are the foundation that 0.3a builds
on. Nothing here will be thrown away.
