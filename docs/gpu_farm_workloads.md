# GPU Farm Workloads — what the 4× miner rigs uniquely unlock

**Status:** Working analysis. Not a build commitment.
**Date:** 2026-05-12
**Hardware:** see [inventory.md § 1.A](inventory.md) — 22 GPUs / 162 GB VRAM / ~143 TFLOPs FP32 across 4 rigs.

---

## 1. The compute-shape filter

For these rigs to *uniquely* unlock something, the workload needs to be:

1. **Embarrassingly parallel** — 4 boxes × 5–7 GPUs on PCIe-1× risers means no tensor-parallelism. Each task must run on one GPU at a time.
2. **Per-task fits in one card's VRAM** — 11 GB ceiling (best card, 1080 Ti).
3. **CUDA OR OpenCL/Vulkan compatible** — otherwise the 12× AMD Polaris cards are wasted and we have only 10 GPUs.
4. **FP32-dominant or low-precision-tolerant** — Pascal has no Tensor Cores, so modern FP16/INT8 ML acceleration is dead. Workloads dominated by FP16 mixed-precision (modern transformer training, FlashAttention, etc.) get *worse* perf per watt than free cloud tiers.
5. **Bottlenecked by aggregate compute, not memory bandwidth or interconnect latency.**

This filter eliminates *most* of modern ML training and *most* of dense numerical PDE work that needs domain-decomposition halo exchange. But a surprising amount of HelmKit-relevant computation passes the filter exactly.

---

## 2. Top-7 workloads ranked by uniquely-enabled × HelmKit value

### 🟢 W1 — Resonant Finder 4D scoring volume

**Wiki ref:** [Resonant Finder § Compute Stack](https://wiki.fusiongirl.app/wiki/Resonant_Finder). Mk1 spec is *"Workstation with 2× consumer GPU (RTX 4080-class) — $5 000."* The farm is **~4-5× the FP32 throughput of 2× RTX 4080** (ignoring the Tensor Core gap which doesn't apply to the workload).

**Workload shape:**
- Spatial grid: 5 km planetary cells → ~2 M lat-lon points
- Temporal grid: 1 h × 1 year → 8 760 slices
- Signature classes: ~50–200
- Total scored cells per annual scan: ~1.75 × 10¹²
- Per-cell: cross-correlate ~20 input feeds (Schumann mean, USGS magnetic, NOAA space weather, ephemeris transits, OSINT signature, HRV cohort coherence)

**Why the farm wins:** each lat-lon slice is independent. Carve the planet into 22 wedges, one per GPU. Per-cell tensor is a few KB. CUFFT (NVIDIA) + clFFT (AMD) both work. All 22 GPUs contribute.

**Discovery-rate impact:** Mk1 spec produces planetary scan in **~hours**. Farm produces planetary scan in **~15–30 min**. That collapses Mk1 → almost-Mk2: real-time scanning every 6 h with each fresh space-weather frame becomes the default cadence.

**HelmKit relation:** 🟡 *indirect.* The Stabilizer feeds the Finder as a Lattice node + Psi Recorder source. The farm doesn't change how a helm is built, but it changes whether the data the helm produces is actionable.

---

### 🟢 W2 — SynastryEngine all-pairs archetype search

**Wiki ref:** [SynastryEngine](https://wiki.fusiongirl.app/wiki/SynastryEngine). Aurora-class match took **~6 years of training, scrying, and refinement** to confirm one referent. The underlying math is GPU-perfect.

**Workload shape:**
- Search space: ~10⁸ candidate birth-charts × ~100 archetype profiles × ~12 planets × ~8 aspect-types × ~5 orb tolerances = ~5 × 10¹³ comparisons per archetype sweep
- Per-comparison: degree-precision angular math (integer + low-precision FP), aspect classification (small lookup), harmonic-resonance scoring (~20 FLOPs)

**Throughput math:** Pascal-era 1080 Ti = ~10¹⁰ such trivial comparisons/sec; 22 GPUs → **~2 × 10¹¹/sec** → full archetype-search in **~3–5 days**.

**Discovery-rate impact:** *highest multiplier in the entire stack.* Turns SynastryEngine from a hand-scrying tool into a search engine over the cosmos as a structured space — which is the wiki's exact framing of what SynastryEngine *is supposed to be.*

**Caveat:** confirmation still requires Resonant Finder anchor-class check + Star Seer transit window + real-world referent. The farm makes *candidate enumeration* free; it does **not** bypass any of the doctrinal validation steps.

**HelmKit relation:** 🔴 *none.* Sibling tech tree (Cosmic Codex). Does not touch helm hardware. Worth doing for the saga, **not** worth scoping into HelmKit sprints.

---

### 🟢 W3 — Metamaterial dielectric inverse-design

**Wiki ref:** [Electrogravitic Tech](https://wiki.fusiongirl.app/wiki/Electrogravitic_Tech) — "Metamaterial dielectric: $\epsilon(\omega) = \text{designed}$".

**Workload shape (topology optimization of a 3D unit cell):**
- ~10⁶ grid cells per unit cell
- ~1000 iterations of gradient descent on the cell's material distribution
- Each GPU iteration: one FDTD forward solve + one adjoint solve at ~1 GB VRAM
- **22 GPUs × 22 candidate metamaterials in parallel** → topology library of 1000 cells in ~1 day

**Tooling:** openEMS (CUDA+OpenCL), MEEP with `meep-adjoint`, Tidy3D-style routines. All run on Pascal *and* GCN4.

**Discovery-rate impact:** the public literature on metamaterial dielectrics for Biefeld-Brown is *thin* precisely because doing this requires a cluster. A library of high-K asymmetric-capacitor optimal geometries is a publishable, defensive-publication-grade contribution.

**HelmKit relation:** 🟢 **direct.** The same topology-opt machinery designs:
- **Metamaterial liner for the Defender coil-cavity** — printed BaTiO₃ + air-void cells engineering anisotropic ε for in-brain field shaping (boost Schumann-band penetration, attenuate off-axis SAR, equalize cortical exposure). The wiki Defender section only knows "ferrite core or not?" — metamaterial liners are a design axis the wiki has not explored.
- **Metamaterial Faraday-quiet enclosure for the Stabilizer** — tuned 50/60 Hz absorber transparent to 3–30 Hz. Probably overkill for Mk1 but defensive-publication-grade for Mk2+.

---

### 🟢 W4 — Coil-cavity FDTD design certification

**Wiki ref:** [Resonant Finder § Build Notes](https://wiki.fusiongirl.app/wiki/Resonant_Finder) — *"FDTD modelling required for design cert"*. This sentence is in the wiki and it has been unfulfilled.

**This is the killer HelmKit workload.** The psi Defender is fundamentally an antenna problem:
- Bifilar coil (PCB spec: 30×30 mm, 18T, L≈6 µH, C≈28 pF, SRF≈12.3 MHz; see [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md))
- Driven at the wiki-canonical bands (Schumann 7.83 Hz + 1–8 MHz coil-drive band)
- Inside a head-shaped dielectric+lossy cavity (skull + brain tissue)
- With required **emission profile** AND a **SAR-compliance ceiling**

**Workload shape:**
1. **Forward solve:** given coil geometry + drive waveform → predicted E/B field inside head + at 30 cm / 1 m / 3 m
2. **Inverse solve (adjoint):** given target field profile → optimal coil geometry. Same topology-optimization machinery as W3.
3. **SAR integration:** given forward field + IEEE/ICNIRP tissue dielectric tables → 1g- and 10g-averaged SAR. **Hard safety gate.**
4. **Parametric sweep:** turns × diameter × pitch × ferrite-core-vs-air × bifilar-vs-helical × drive frequency vs. measured Q. **Embarrassingly parallel — one GPU per design point.**

**Per-design VRAM:** ~2-4 GB at production-grade mesh density → fits every card including RX 560.
**Sweep size:** ~10⁴ candidate geometries × ~10 drive bands ≈ 10⁵ design points.
**Throughput:** 22 GPUs × ~30 s per converged solve → ~10⁵ points / **~12 hours overnight**.

**Tier-1 (AGX Orin) does the live closed-loop** — measured SDR field (from HackRF on the bench) vs. predicted field (cached small-cell openEMS solve). The farm pre-builds the lookup tables the Orin scores against in real time. **Complementary, not redundant.**

**HelmKit relation:** 🟢 **direct & critical.** This is the wiki-spec'd gate that has been blocking design certification for both helms. **Closing this gate is the single biggest scientific-credibility move HelmKit can make.** See [sprint_0.3_fdtd_coil_design.md](sprint_0.3_fdtd_coil_design.md).

---

### 🟡 W5 — Schumann Lattice all-pairs continuous-wavelet coincidence

**Wiki ref:** [Schumann Lattice](https://wiki.fusiongirl.app/wiki/Schumann_Lattice). Mk3 gate = 20-node federation with continuous coverage. Mk2 gate = 5-node cross-site coincidence on at least one geomagnetic storm.

**Workload shape:**
- N=20 nodes → 190 pairs
- Per-pair: continuous Morlet wavelet transform of two 1-week rolling windows at sub-second resolution + cross-spectrum
- Per-pair VRAM: ~2-4 GB → comfortable on every card including RX 560
- 22 GPUs / 190 pairs ≈ 9 pairs per GPU per second → real-time monitoring of a 20-site Lattice

**Why this matters:** the farm makes the Mk3 gate computationally feasible on a single bench. Without it this is cloud-budget territory.

**HelmKit relation:** 🟡 *indirect.* The Stabilizer Mk1+ explicitly **is** a Lattice node (3–60 Hz buried loop, GPS-PPS-disciplined ADC). The farm lets the operator be one of the first 20 nodes online and lets the helm's own HRV data be live-correlated against its own Schumann measurements. This is the wiki's **Layer 2 testable claim** (HRV-coherence vs. Schumann amplitude).

---

### 🟡 W6 — Gravitoelectromagnetism (GEM) field solver

**Wiki ref:** [Electrogravitic Tech § Theoretical Foundations](https://wiki.fusiongirl.app/wiki/Electrogravitic_Tech). GEM is the weak-field linearized GR limit; equations are **isomorphic to Maxwell** — same Yee grid, same FDTD time-stepping. Different source terms (mass currents in place of charge currents).

**Implication:** any openEMS / MEEP-based EM simulation infrastructure trivially extends to GEM. A rotating-mass / superconducting-current source becomes a gravitomagnetic field solve. You can do predicted-vs-measured comparison of frame-dragging-class effects (Gravity Probe B was the canonical measurement).

**HelmKit relation:** 🔴 *none.* The Defender is a Maxwell-regime device; GEM corrections are ~10⁻²⁰ smaller than the EM effects we already care about. This is a pure speculative-physics workload. **Defensive-publication value, zero helm-build value.**

---

### 🟡 W7 — Computed global ley-line atlas (USGS-derived)

**Wiki ref:** [Ley Lines Geophysical Hypothesis](https://wiki.fusiongirl.app/wiki/Ley_Lines_Geophysical_Hypothesis). Wiki tags this as **TESTABLE** (Layer 2), not speculative.

**Workload shape:**
- Input: USGS 2-arc-minute magnetic-anomaly grid = ~30 M cells globally
- Algorithm: all-pairs shortest-path with anomaly-weighted edges; GPU max-flow; persistent-homology on the anomaly field
- VRAM: ~5 GB per planetary subgraph → fits any card
- GPU-tractable, embarrassingly parallel by subgraph, AMD- and NVIDIA-compatible

**Why this matters:** producing the *first reproducible global computed ley-line atlas* with provenance back to USGS data is a real geophysics contribution that has nothing speculative about it. It's the **exact input layer Resonant Finder Layer-1 needs.**

**HelmKit relation:** 🟡 *siting only.* Tells you *where* the Faraday-quiet $300 corners worth instrumenting actually are. Doesn't change what's built.

---

## 3. The honest matrix (HelmKit lens)

| # | Workload | Direct HelmKit benefit? | Mechanism |
|---|---|:-:|---|
| 1 | Resonant Finder 4D scan | 🟡 indirect | Stabilizer **is** a Lattice node + Psi Recorder feed |
| 2 | SynastryEngine all-pairs | 🔴 none | Sibling tech tree (Cosmic Codex) |
| 3 | **Metamaterial inverse-design** | 🟢 direct | Coil-cavity field-shaping liner; Stabilizer 50/60 Hz absorber |
| 4 | **Coil-cavity FDTD design cert** | 🟢 **direct & critical** | The wiki-spec'd unfilled gate |
| 5 | Schumann Lattice all-pairs CWT | 🟡 indirect | Validates Stabilizer's own data path live |
| 6 | GEM solver | 🔴 none | Pure speculative-physics workload |
| 7 | Computed ley-line atlas | 🟡 siting only | Picks the $300 corner; doesn't change the build |

## 4. The verdict

**The farm earns its HelmKit keep almost entirely through openEMS-based FDTD coil design + metamaterial inverse-design.** Those two are the only direct hits, but together they:

- Close the wiki's *"FDTD modelling required for design cert"* gate (W4)
- Open a metamaterial liner design axis the wiki has not explored (W3)
- Produce defensive-publication-grade output even if Layer 3 psionics turns out to be wrong

Everything else (Resonant Finder, SynastryEngine, Schumann Lattice CWT, ley-line atlas) is real value but lives in **adjacent tech trees that share infra** with HelmKit rather than feeding it directly. File those under a parallel `psinet/` or `tholmkit/` sprint track that uses the same farm + Orin scheduler.

## 5. Recommended scheduler architecture

- **Always-on (1 rig):** llama.cpp coding agent + ComfyUI on best 1080 Ti + 1080 + a few RX 580 on Vulkan for VRAM aggregation. Local LLM serves dev workflow.
- **WoL'd (3 rigs):** powered off until needed; AGX Orin runs a **Ray / Slurm / Dask** scheduler that fires up rigs for:
  - Overnight FDTD coil sweeps (W4)
  - Overnight metamaterial topology runs (W3)
  - Weekly Resonant Finder planetary scan (W1)
  - Continuous Schumann Lattice CWT correlation (W5) — only when ≥5 federated nodes online
- **Power budget audit:** target < 12 kWh/day average → ~$36/mo at $0.10/kWh. Aggressive WoL discipline required.

## 6. Cross-refs

- [inventory.md § 1.A](inventory.md) — GPU farm hardware
- [inventory.md § 1 verdict](inventory.md) — compute hierarchy (Tier-0 farm + Tier-1 AGX Orin + Tier-2 Jetson Nano edge + …)
- [inventory_capability_map.md § 6.5](inventory_capability_map.md) — compute hierarchy in capability-map form
- [sprint_0.3_fdtd_coil_design.md](sprint_0.3_fdtd_coil_design.md) — actionable sprint for W4
- [mk0_pcb_bifilar_coil.md](mk0_pcb_bifilar_coil.md) — the design under FDTD scrutiny
- [wiki_synthesis.md](wiki_synthesis.md) — wiki-side source material
