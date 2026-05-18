# The HelmKit platform

<!-- Source: docs/architecture.md, docs/roadmap.md, docs/mk_ladder.md
     Status: v0 (2026-05-18)
     Target length: 6-8 printed pages.
-->

The HelmKit is a *platform*, not a device. Its job is to give Psi-Tech
modules a reliable place to live — with reliable power, reliable data,
and reliable head-fit — and to enforce a small, hard set of safety
invariants regardless of which modules are mounted. This chapter
specifies what the platform contract is and what it costs.

## The four-layer model

The platform is organized in four layers. Each layer has one
responsibility, one place in the repository, and one contract with the
layer above and below it.

| Layer | What it is | Where it lives |
|-------|------------|----------------|
| **L0 — Fit** | Headband and frame ring; sets where the device sits on the head | `3D-Models/HelmKit/` head-ring and Mk1 frame parts |
| **L1 — Structure** | Forehelm, sidehelm, rearhelm, temple booms; the load-bearing skeleton | `3D-Models/HelmKit/` Mk1 modular parts |
| **L2 — Bus** | Power rails, data bus, cable raceway; carries V, GND, I²C, USB 2.0 HS, UART, audio diff pair | Printed-in channels; documented connector pinout |
| **L3 — Modules** | Sensing, stimulation, optics, comms — the actual Psi-Tech | Mount via L1 hardpoints, plug into L2 |

A module is "Mk1-compatible" if and only if it conforms to the L1
hardpoint mechanical contract and the L2 bus electrical contract. Nothing
else qualifies a module. Manufacturer, vendor, certification, and
provenance are below this line; geometry and pinout are above it. This
asymmetry is deliberate. The frame's job is to make modules
*interchangeable*, and interchangeability requires that the frame itself
not care who made the module — only whether it fits and what it asks the
bus to do.

## The hardpoint specification

Every module mounts at a **hardpoint** — a printed feature on the frame
with a fixed mechanical and electrical contract. Mk1 freezes ten
hardpoint locations:

| ID | Location | Typical occupant |
|----|----------|------------------|
| `HP-F` | Forehelm, centerline | HUD optic mount, indicator LEDs, forward sensor |
| `HP-FL`, `HP-FR` | Forehelm, left/right of centerline | Camera, ambient EM antenna, photic LED bar |
| `HP-TL`, `HP-TR` | Temple boom, left/right | EEG electrode, magnetometer boom, coil driver, PPG |
| `HP-EL`, `HP-ER` | Ear-shield, left/right | Bone-conduction transducer, in-ear audio, ear-canal sensor |
| `HP-SL`, `HP-SR` | Sidehelm, left/right | Battery bay (one side), comms radio bay (other side) |
| `HP-R` | Rearhelm | Compute node, primary battery, µSD/IO door |

The locations are not arbitrary. Temple hardpoints (`HP-T*`) sit closest
to the skin-contact line and carry the most signal-relevant mounts —
EEG, magnetometer, PPG. Forehelm hardpoints (`HP-F*`) sit closest to the
gaze axis and are reserved for HUD optics and forward-facing sensors.
Sidehelm hardpoints (`HP-S*`) host the larger volumes — battery,
comms — that cannot fit on the temple boom. The rearhelm hardpoint
(`HP-R`) hosts the compute node and primary battery, where the largest
volume and the longest cable-run can be tolerated.

The **mechanical contract** is short: a 2-bolt M3 pattern at 20 mm
centers, a captive-nut pocket on the frame side, ±0.2 mm tolerance at
print scale, a polarity rib that prevents 180° rotation on installation,
and a documented footprint envelope per hardpoint that a module is not
permitted to exceed. Every hardpoint has a 4 mm × 8 mm slot to the L2
raceway for cable pass-through.

The **electrical contract** — the L2 bus — was the placeholder in early
project iterations and is now wiki-canonical (re-read 2026-05-12; see
[`docs/architecture.md` §3.6](../../architecture.md#36-inter-module-bus-and-connector-spec-wiki-canonical-added-2026-05-12)
for the source citation). It specifies:

- **Connector:** USB-C Power Delivery, 5 V at up to 3 A, carrying power
  *and* data on the same cable. Keyed module-bay shells guarantee
  orientation; a mechanical index pin blocks insertion in the wrong slot.
  A GoPro / Picatinny rail segment carries the mechanical load — the
  USB-C connector is strain-relieved and explicitly *not* load-bearing.
- **Power lanes:** 3.3 V at up to 500 mA per hardpoint, 5 V at up to 1 A
  per hardpoint, with a per-hardpoint poly-fuse. PMIC enforces a hard
  3 A total cap on the 5 V bus.
- **Data lanes:** I²C at 100 kHz (sensor reads, config writes, low-rate
  telemetry, ~10 kB/s per module); USB 2.0 high-speed at 480 Mbit/s
  (HUD framebuffer, EEG and PPG streams, firmware updates); UART at
  115 200 baud (NavCom radio, debug console, ~11 kB/s).
- **Audio:** dedicated differential pair between `HP-EL`, `HP-ER`, and
  the compute node — not on the I²C/SPI bus, to keep audio out of the
  digital noise floor.
- **Stim:** dedicated isolated pair from compute → stim driver →
  temple hardpoint. Hardware interlock between stim-enable and
  recording-active. **No stim without recording.** This is enforced in
  hardware and in firmware. It is the single hardest interlock in the
  device, and it cannot be relaxed by configuration.
- **Safety line:** an open-drain GPIO with an MCU-B pull-up. Each module
  signals "ready to emit" on this line; MCU-B can force-disable any
  module by pulling the line low. Latency is under 1 ms.

Every module exposes an I²C identity register at address `0x00`
containing a 16-bit vendor-plus-class code. On hot-plug, the PMIC
asserts power-good after seeing the new load, MCU-A reads the identity
register and looks up the module's safety profile, MCU-A forwards the
profile to MCU-B for blacklist cross-check, and only after MCU-B
acknowledges does MCU-A enable the module's data lane and RF-enable
GPIO. Hot-swap during a session is supported and logged with timestamp,
module ID, and the operator's then-current HRV / EEG baseline.

## The dual-MCU safety architecture

The platform's safety story is one sentence: **no single software fault
may cause an overexposure event.** Everything in this section is
machinery for keeping that sentence true.

The platform from Mk1 onward adopts the **checker-doer pattern**
specified in the wiki's `HelmKit Architecture` page, which is in turn
inherited from RTCA DO-178C DAL-A (avionics) and IEC 61508 SIL-3
(industrial functional safety). HelmKit does not target medical or
avionics certification — we are an open research and educational
platform, not a regulated device — but the architectural pattern is
imported wholesale because the invariant it preserves is exactly the
invariant our wearer cares about.

```
            +--------------+         +--------------+
            |   MCU-A      |         |   MCU-B      |
            |  ("doer")    |         |  ("checker") |
            |              |         |              |
            |  RF / coil   |         |  Sensors     |
            |  modulation  |         |  Blacklist   |
            |  UI / BLE    |         |  RF cutoff   |
            |  Capture     |         |  Watchdog    |
            +--------------+         +--------------+
                  |                          |
                  | drive                    | opto-isolated cutoff
                  v                          v
            +------------------------------------------+
            | Stim driver (H-bridge / PA / matching)   |
            +------------------------------------------+
```

**MCU-A** is the *doer*. It generates the drive waveform (Mk1: sub-MHz
pulsed coil drive; Mk2+: optional Class-E PA and matching network), runs
the capture loop (PPG, optional EEG, magnetometer — the same pipeline
the Psi Stabilizer project's `psistabilizer.capture.a01_capture` defines),
handles UI, BLE telemetry, and session logging. Reference part: ESP32-S3
or RP2040; standard firmware-update path.

**MCU-B** is the *checker*. It runs from an independent LDO off the
battery, with an independent crystal, independent firmware, and an
independent reviewer. It has read-only authority over an opto-isolated
cutoff on the stim drive path — meaning MCU-A cannot bypass it, only
plead with it. It continuously measures drive forward/reflected power
via a directional coupler, coil temperature via a thermistor,
body-proximity via a capacitive sensor on the headband, and ambient
field via an independent E/B probe. It enforces the safety blacklist at
the hardware layer. Heartbeat watchdog: if MCU-A misses a heartbeat for
more than 100 ms, MCU-B cuts drive. Reference part: an ARM Cortex-M0+
class device (STM32G0, or the second core of an RP2040 in isolated
configuration). Target firmware size is under 5 kLOC, with no dynamic
allocation, and the safety logic is formally reviewed (Frama-C, SPARK,
TLA+, or peer audit equivalent) by a reviewer not on the MCU-A team.

On any MCU-B alert — blacklist hit, watchdog timeout, sensor out of
envelope, body-proximity lost — the system enters a **non-resettable
lockout**. RF and coil drive are cut immediately via the opto-isolated
relay. The event is logged in tamper-evident memory with a sequence
number, cause code, and timestamp. Recovery requires a physical reset
action: a manual switch inside the helmet. There is no software-only
recovery from a lockout. This is intentional, and it is the second-
hardest interlock in the device after the no-stim-without-recording line.

The **safety blacklist** is the heart of the checker. It is hardcoded in
MCU-B firmware and ships with twelve rows at Mk1 (see
[`docs/architecture.md` §3.3](../../architecture.md#33-safety-blacklist-mk1-minimum)
for the full table). Examples: DC pulses with rise time under 1 ms
targeted near thorax-coupled hardpoints (cardiac stimulation risk);
3–8 Hz photic-frequency RF at over 100 V/m head-field (seizure risk);
modulation envelope matching cardiac (0.8–3 Hz) or respiratory
(0.1–0.5 Hz) rates at over 5 % depth (cardiac/respiratory coupling);
continuous-wave near-field over 50 V/m rms at the head (ICNIRP
exceedance); any drive while the recording-active GPIO is low
(stim-without-recording forbidden); any drive while body-proximity reads
"off" (no drive into open air); any drive while coil temperature exceeds
45 °C (burn risk); drive duty cycle over 60 % averaged over 10 s
(defense-in-depth rate control).

The blacklist is **factory-set**. There is no field-modifiable path to
change it. Modifying it requires reflashing MCU-B with physical access
to the helmet, on a signed firmware image authenticated against a
hardware-fused public key. MCU-B has no remote update path. This is the
third-hardest interlock and it exists because the checker's value
depends entirely on its independence from the doer's update path.

## The generational ladder

The platform is shipped in generations — Mk0 through Mk3, with optional
intermediate revisions (Mk0.5, Mk1.5) used to land specific
sub-capabilities before the next major generation freezes.

- **Mk0 (current)** is the cosplay-grade frame. v2 type-b iteration 9 is
  already 3D-printed and fits well on a representative head. Frame only,
  no electronics, no instrumentation. Mk0 exists to establish L0 fit and
  L1 structure under wear conditions.
- **Mk0.5** is the firmware bring-up generation. The Psi Stabilizer A01
  capture pipeline runs end-to-end on representative compute hardware,
  with the platform's reference sensor stack and the dual-MCU safety
  architecture in checker-only mode (no drive). Mk0.5 produces the first
  real session data and the first calibrated ambient electromagnetic
  log.
- **Mk1** is the first generation that has to *work*. It freezes the
  hardpoint specification, the L2 bus pinout, and the BOM. It carries
  a single sub-MHz bifilar coil driver (the geometry derived in
  Chapter 5), a wearer-facing biofeedback loop (HRV, breath pacing,
  optional audio entrainment), and the full dual-MCU safety
  architecture in active mode. Mk1's wearer-benefit floor is mainstream-
  physics-defensible. Mk1's three-arm precursor protocol engages the
  $F_3$ and $F_4$ precursors named in `docs/falsification.md`.
- **Mk1.5** is the bifilar-vs-UHF calibration generation. It adds a
  Frey-class pulsed UHF channel for comparison against the Mk1 sub-MHz
  bifilar channel at matched $F^2$ envelope, in a three-arm RCT against
  sham. Mk1.5 does not adjudicate $F_3$ — that requires Mk2's resonance
  scan — but produces the baseline data Mk2 inherits.
- **Mk2** adds the resonance scan (envelope frequency swept across the
  6.5–9.5 Hz Schumann band at matched $F^2$), the calibrated FDTD SAR
  map, body-aware operation (capacitive proximity plus reflectometry-
  tracked match drift, with tuneable matching network), and the
  optional haloscope adapter for $F_{11}$ engagement. Mk2 is a
  Q4 2026 / 2027 problem and is named in the roadmap but not in this
  volume's product scope.
- **Mk3** is the precision generation. It would attempt the matched
  device-emission and AC-detection measurement that engages $F_7$.
  Two Mk3 pairs in independent setups is the wiki-stated minimum for an
  $F_7$ result. Mk3 is far enough out that planning it in detail now
  would be speculation.

A module is "MkN-compatible" if and only if it builds against the MkN
tag's frozen specification. The frame, the hardpoint table, the bus
pinout, the BOM, and the firmware tag are frozen together. Versioning
the platform any other way would let modules and frame drift, and the
whole point of the platform is that they do not.

## Coordinate system

For completeness: the platform's origin is the midpoint between the
tragi (ear-canal openings), projected to the headband plane. **+X** is
right, **+Y** is forward, **+Z** is up, in standard anatomical
convention. Module placement and EEG-electrode positions reference the
international 10-20 system; the Fp1, Fp2, Cz, T7, and T8 positions are
the primary Mk1 and Mk2 positions of interest, and all of them are
reachable from the existing frame's forehelm and temple hardpoints.

## Relationship to the Psi Stabilizer software stack

This repository does not duplicate any of the Psi Stabilizer
submodule's contents. The sensor data schema, the capture pipeline, the
HRV and ambient-anomaly analysis library, the pre-registration template,
and the A01 sensor-stack BOM all live in `external/psiStabilizer/` and
are consumed as-is. The frame geometry, the hardpoint specification, the
module bus, and the stimulation drivers live in this repository. The
wearer-facing safety document is here, citing the Psi Stabilizer
project's `safety_guidelines.md` and extending it for head-mounted
hardware. The division is not aesthetic; it is a maintainability
contract. The Psi Stabilizer project is measurement-first and lives
without HelmKit. HelmKit is where stimulation hardware lives, and it
imports the measurement stack rather than reinventing it.

The next chapter introduces the two sister-module families — Psi
Defender (outward) and Psi Stabilizer (inward) — and shows where each
mounts on the platform and which bus channels it consumes.
