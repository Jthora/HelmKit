# HelmKit

> Open, non-enclosed psionic headpiece. A 3D-printed **mounting frame** with interchangeable **Psi-Tech** modules for cognitive protection, stabilization, and enhancement.

The HelmKit itself is **not** the psi-tech. It is the **hardware platform** — a head-worn skeleton with standardized hardpoints — that lets specialized modules (Psi Stabilizer, Psi Defender, sensors, HUD optics, etc.) be swapped in and out.

This repo is the platform: frame geometry, hardpoint spec, power/data bus, fit-and-mount, and the integration plan for each module generation (Mk0 → Mk3).

---

## Quick links

| | |
|---|---|
| Roadmap (Mk0 → Mk3) | [docs/roadmap.md](docs/roadmap.md) |
| System architecture & hardpoint spec | [docs/architecture.md](docs/architecture.md) |
| Mk1 build plan (concrete, near-term) | [docs/mk1_buildplan.md](docs/mk1_buildplan.md) |
| Safety, RF, and what we will NOT do | [docs/safety.md](docs/safety.md) |
| Wiki anchors (FusionGirl research source) | [docs/wiki_anchors.md](docs/wiki_anchors.md) |
| 3D-printable parts inventory | [3D-Models/](3D-Models/) |
| Sister project: Psi Stabilizer | [external/psiStabilizer/](external/psiStabilizer/) (submodule) |
| Legacy iOS apps (not used going forward) | [iOS_oldBuild/](iOS_oldBuild/) |

---

## Sibling/sister project relationship

| | Psi Defender | Psi Stabilizer | **HelmKit** |
|---|---|---|---|
| Direction | Outward — environment | Inward — self | **Platform — head-worn frame + bus** |
| Sense | Ambient EM, RF, acoustic | EEG, HRV, GSR | **Carries either or both** |
| Act | Detect / shield / alert | Entrain / feedback / baseline | **Mount, power, integrate** |
| Repo role | Sister | Submodule under `external/` | This repo |

The HelmKit is the integration point. A Psi Stabilizer module **runs on it**. A Psi Defender module **mounts to it**. The frame, hardpoints, and bus live here.

---

## Status

- **Mk0** (cosplay-grade frame, v2 type-b iter 9) — already 3D-printed and fits well on head. Frame only. No electronics.
- **Mk1** — in planning. First version that has to actually **work** (see [docs/roadmap.md](docs/roadmap.md#mk1)).
- **Mk2 / Mk3** — scoped in roadmap; not started.

The iOS apps in [iOS_oldBuild/](iOS_oldBuild/) (an astrology event predictor, a magnetometer/IMU app) are stepping-stone work and are **not** the path forward. The HelmKit is hardware-first from Mk1 onward.

---

## Discipline (carried over from psiStabilizer)

1. Every claim is falsifiable; every measurement is logged.
2. "It looks the part" is not the same as "it works." Mk0 is cosplay. Mk1 must measure something real and modulate something real, at safe power, with documented method.
3. Anything we promise the wearer gets pre-registered before the build. Anything we cannot measure, we do not claim.
4. RF / EM emission near the head is **safety-gated** — see [docs/safety.md](docs/safety.md). High-power-RF approaches are deferred to Mk2+ behind explicit SAR and biological-effects review.

---

## Legal / Naming

"HelmKit" is also the in-world name of a fictional device in the FusionGirl wiki corpus. The wiki is used here as a **research and design source** (see [docs/wiki_anchors.md](docs/wiki_anchors.md)) — it inspires the architecture but does not substitute for real engineering or peer-reviewed neuroscience.
