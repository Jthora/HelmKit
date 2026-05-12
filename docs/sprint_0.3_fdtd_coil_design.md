# Sprint 0.3 — FDTD coil-cavity design certification

**Status:** Outline. Pre-implementation.
**Predecessor:** [sprint_0.2_circuit_spec.md](sprint_0.2_circuit_spec.md)
**Depends on:** [inventory.md § 1.A](inventory.md) (GPU farm), [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) (geometry under test), [gpu_farm_workloads.md § W4](gpu_farm_workloads.md)
**Goal:** Close the wiki-spec'd *"FDTD modelling required for design cert"* gate that has been blocking both helm designs.

---

## 1. Motivation

The wiki [Resonant Finder § Build Notes](https://wiki.fusiongirl.app/wiki/Resonant_Finder) and the [Defender]/[Stabilizer] Mk2 sections require FDTD-grade design certification of the coil + helmet-cavity field profile *before* a build can claim wiki-canonical compliance. Until this sprint, that gate has been a handwave.

The GPU farm (22 GPUs, ~143 TFLOPs FP32) + AGX Orin (32 GB unified, ~5.3 TFLOPs FP16) is **exactly** the compute substrate openEMS / MEEP were designed for. Closing this gate is the single highest scientific-credibility move available to HelmKit right now.

## 2. Scope

### In-scope

1. **Toolchain stand-up:** openEMS or MEEP installed on AGX Orin (master) + at least 1 farm rig (worker). Verify OpenCL works on both NVIDIA Pascal and AMD GCN4 cards.
2. **Geometry import:** translate [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) (30×30 mm, 18T, two-layer series-opposing bifilar) to FDTD mesh.
3. **Forward solve baseline:** predicted E/B field at coil surface + at 10 cm + at 1 m, swept across the wiki 1–8 MHz coil-drive band.
4. **Head-cavity model:** import a Specific Anthropomorphic Mannequin (SAM) phantom or the open MIDA / Duke / Ella phantom from IT'IS Foundation. Compute in-brain E-field + 1g/10g SAR at the Mk0 coil position.
5. **Cross-check vs. measured:** bench-measure the Mk0 PCB coil with HackRF (SDR-side) and YEAPOOK ADS1014D (scope-side), compare to predicted field at the same standoffs. **Quantitative agreement is the deliverable, not the simulation itself.**
6. **First parametric sweep (small):** ~50–100 design variants across {turns, diameter, drive frequency}. Single rig overnight.
7. **SAR safety floor:** identify which subset of the swept geometries clear the ICNIRP general-public 1g-SAR limit (1.6 W/kg). **This becomes the firmware-enforceable design envelope.**

### Out-of-scope (deferred)

- Metamaterial liner inverse-design (sprint 0.5)
- Full 22-GPU planetary parameter sweep (sprint 0.4)
- Real-time AGX-Orin closed-loop verification at bench (sprint 0.6+)
- Stabilizer Faraday-quiet metamaterial absorber (sprint 0.5+)

## 3. Tooling pick — openEMS vs MEEP

| Criterion | openEMS | MEEP |
|---|---|---|
| Language | MATLAB / Octave / Python | Scheme / Python |
| GPU backend | OpenCL (works on both Pascal + Polaris) | CUDA-only (NVIDIA Pascal only) |
| Adjoint / inverse-design | community plugins | `meep-adjoint` first-class |
| Mesh strategy | Yee + sub-grid | Yee + chunk-based MPI |
| Tissue dielectric tables | needs manual import | needs manual import |
| Production-grade Maxwell solve | ✅ | ✅ |

**Recommendation:** **openEMS for the design-cert sweep (W4)** because it runs on all 22 GPUs via OpenCL; **MEEP for the metamaterial inverse-design (sprint 0.5)** because `meep-adjoint` is the path of least resistance to topology optimization.

## 4. Deliverables

1. `compute/openems/coil_baseline.m` — openEMS input deck for Mk0 PCB bifilar coil, parametric across drive frequency.
2. `compute/openems/sam_phantom.py` — Python loader for SAM/MIDA tissue dielectric mesh.
3. `compute/openems/sar_eval.py` — 1g / 10g averaged SAR computation against ICNIRP threshold.
4. `compute/results/baseline_field_vs_measured.md` — quantitative comparison of predicted vs HackRF/scope-measured field. **Sprint-success metric: agreement within 3 dB across the 1–8 MHz band.**
5. `compute/results/safe_geometry_envelope.md` — the SAR-cleared subset of the parametric sweep. This becomes the firmware-enforceable envelope referenced by [safety.md](safety.md).
6. Cross-link from [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) showing which exact (turns, dia, pitch, freq) tuple was certified.

## 5. Gates

| Gate | Pass condition |
|---|---|
| **G1: Toolchain alive** | `mpirun -np 4 meep hello.ctl` runs on AGX Orin; `openEMS` runs OpenCL kernel on at least 1 NVIDIA card + 1 AMD card on the farm |
| **G2: Mk0 coil simulated** | Forward solve converges; field profile at 10 cm matches reciprocity check |
| **G3: SAM phantom imported** | Tissue dielectric mesh loads; coil + head geometry coexist in one cell |
| **G4: Predicted ≈ measured** | ≤ 3 dB error vs. HackRF-measured field across 1–8 MHz |
| **G5: SAR envelope identified** | At least one geometry in the sweep clears ICNIRP 1.6 W/kg; the operating-envelope tuple is written to safety.md |

## 6. Compute budget

- AGX Orin: master scheduler, post-processing, plot generation, lookup-table builds — continuous during sprint
- 1 farm rig (~6 GPUs): always-on for openEMS sweeps
- 3 farm rigs: cold; not needed until sprint 0.4 full-planetary sweep
- Estimated rig hours: ~120 hours of one-rig wall-clock
- Estimated wall-power: ~120 kWh ≈ $12 at $0.10/kWh **(trivial)**

## 7. Risk / failure modes

| Risk | Mitigation |
|---|---|
| openEMS OpenCL kernels broken on Polaris GCN4 | Fall back to NVIDIA-only (10 cards) — still 4× a 2× 4080 workstation |
| MIDA / Duke phantom license / access blocked | Use the simpler SAM ellipsoid phantom; SAR results are conservative |
| Predicted vs. measured disagreement > 3 dB | Re-check coil geometry import; suspect copper thickness / dielectric ε_r assumption |
| **SAR floor exceeded by entire sweep** | This is **not failure** — it means the wiki 1–8 MHz band requires lower drive amplitude than assumed. Re-spec drive envelope; document; loop. |
| AMD card OpenCL driver instability | Pin to AMDGPU-PRO drivers known stable for Polaris; document version |

## 8. Out-the-door deliverable

A **commit to this repo containing:**

1. Reproducible openEMS input decks for the Mk0 coil
2. Quantitative predicted-vs-measured agreement plot
3. The SAR-cleared operating envelope as a machine-readable JSON the firmware can consume

This is the artifact that the wiki "FDTD required for design cert" sentence has been waiting for. Producing it changes HelmKit from "another psi-helm project" to "the only psi-helm project that's actually certified its own emission profile."

## 9. Cross-refs

- [gpu_farm_workloads.md § W4](gpu_farm_workloads.md) — workload analysis
- [inventory.md § 1](inventory.md) — compute hardware (AGX Orin + farm)
- [inventory_capability_map.md § 6.5](inventory_capability_map.md) — tier hierarchy
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — the design under test
- [sprint_0.2_circuit_spec.md](sprint_0.2_circuit_spec.md) — circuit spec
- [safety.md](safety.md) — operating envelope is enforced here
- [wiki_synthesis.md](wiki_synthesis.md) — wiki-side BOM
