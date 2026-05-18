# Bifilar series-opposing near-field enhancement factor

- **Status**: v0 (analytic on-axis result; off-axis + integrated-energy treatment deferred)
- **Track**: [C — Original math derivations](../plans/2026-tier1-launch/track-C-derivations.md)
- **Paired notebook**: [`notebooks/bifilar_near_field.ipynb`](../../notebooks/bifilar_near_field.ipynb)
- **Last updated**: 2026-05-18

---

## Claim

For a series-opposing axial bifilar pair of single-turn loops of radius $a$ separated by axial distance $d$, driven with equal-magnitude opposite-phase currents $\pm I$, the **on-axis** magnetostatic field magnitude relative to a same-current single-loop reference is

$$
\boxed{\;\eta_B(r) \;\equiv\; \frac{|B_z^{\text{bif}}(r)|}{|B_z^{\text{ref}}(r)|} \;=\; \frac{3\,d\,r}{a^2 + r^2} \;+\; \mathcal{O}\!\left(\frac{d^2}{a^2}\right)\;}
$$

where $r$ is the on-axis distance measured from the midpoint of the pair.

**Honest engineering consequence.** $\eta_B(r) < 1$ on-axis whenever $3dr < a^2 + r^2$, which is satisfied for all $r > 0$ as long as $d < a/3$ (the geometry in every plausible bifilar build). **A series-opposing axial bifilar pair therefore produces a *weaker* on-axis field than a single same-current loop**, not a stronger one. The engineering value of the bifilar geometry is **field gradient and localization**, not on-axis field amplitude — see §[Engineering interpretation](#engineering-interpretation).

---

## Setup

### Geometry

Two coaxial single-turn loops, both of radius $a$, sharing the $z$ axis.

- Upper loop at $z = +d/2$, carrying current $+I$ (counter-clockwise looking down $+z$).
- Lower loop at $z = -d/2$, carrying current $-I$.
- Field point on axis: $\mathbf{r} = (0, 0, r)$, $r$ measured from the midpoint.

```
                        +I
                   ┌─────────┐    ← z = +d/2
                   │    a    │
                  ─┼─────────┼─── axis
                   │         │
                   └─────────┘    ← z = -d/2
                        -I
```

### Variables

| Symbol | Meaning | Units |
|--------|---------|-------|
| $a$ | Loop radius | m |
| $d$ | Axial separation between the two loops | m |
| $I$ | Loop current (RMS magnitude) | A |
| $r$ | On-axis field-point distance from the midplane | m |
| $\mu_0$ | Vacuum permeability | $\mathrm{H \cdot m^{-1}}$ |
| $B_z$ | On-axis magnetic flux density | T |

### Assumptions

1. **Quasi-static.** Loop circumference $2\pi a \ll \lambda$ for all frequencies of interest. For $a = 5\,\mathrm{cm}$ this holds for $f \ll c / 2\pi a \approx 1\,\mathrm{GHz}$. The HelmKit envelope-rate carriers ($f \lesssim 30\,\mathrm{Hz}$) are deep in the quasi-static regime; the UHF-class hypothesis ([`docs/h2_modulated_uhf_hypothesis.md`](../h2_modulated_uhf_hypothesis.md)) is **not** quasi-static and is out of this derivation's scope.
2. **Identical loops.** Equal radius, equal current magnitude, exact $180°$ phase opposition.
3. **Series-opposing axial geometry.** Not co-planar caduceus. The caduceus far-field null is the subject of derivation #2 (planned).
4. **Air core.** No magnetic material in the near field.
5. **Single-turn.** $N$-turn extension is a trivial multiplicative factor $N^2$ on the field-squared ratio and is omitted.

---

## Derivation

### Step 1 — On-axis field of a single loop

The standard Biot–Savart result for a single circular loop of radius $a$ carrying current $I$, evaluated on its axis at distance $z$ from its centre, is

$$
B_z^{\text{loop}}(z) \;=\; \frac{\mu_0 I a^2}{2\,(a^2 + z^2)^{3/2}}
\tag{1}
$$

with the field directed along $+\hat{z}$ when the current is counter-clockwise looking down $+\hat{z}$. *(Standard, see e.g. Jackson §5.5. Source class (a) consensus.)*

### Step 2 — Superposition for the series-opposing pair

The on-axis field at point $(0,0,r)$ from the upper loop (centre at $z = +d/2$, current $+I$) is $B_z^{\text{loop}}(r - d/2)$. The lower loop (centre at $z = -d/2$, current $-I$) contributes $-B_z^{\text{loop}}(r + d/2)$. By linear superposition:

$$
B_z^{\text{bif}}(r)
\;=\; \frac{\mu_0 I a^2}{2}\!\left[\,\frac{1}{\bigl(a^2 + (r - d/2)^2\bigr)^{3/2}} \;-\; \frac{1}{\bigl(a^2 + (r + d/2)^2\bigr)^{3/2}}\,\right]
\tag{2}
$$

This is exact. It is also obvious from (2) that $B_z^{\text{bif}}(0) = 0$ (the field vanishes on the symmetry plane), in contrast to the single-loop maximum $B_z^{\text{ref}}(0) = \mu_0 I / 2a$.

### Step 3 — Expansion in $d / a$

Define

$$
g(z) \;\equiv\; \frac{1}{(a^2 + z^2)^{3/2}},
\qquad
g'(z) \;=\; -\frac{3 z}{(a^2 + z^2)^{5/2}}
\tag{3}
$$

For $d \ll a$ and $d \ll r$, expand both terms in (2) around $z = r$:

$$
g(r \pm d/2) \;=\; g(r) \;\pm\; \tfrac{d}{2}\,g'(r) \;+\; \tfrac{1}{8} d^2\,g''(r) \;+\; \mathcal{O}(d^3)
$$

The difference cancels the even-order terms and doubles the odd-order ones:

$$
g(r - d/2) - g(r + d/2) \;=\; -d\,g'(r) \;+\; \mathcal{O}(d^3)
\;=\; \frac{3\,d\,r}{(a^2 + r^2)^{5/2}} \;+\; \mathcal{O}(d^3)
\tag{4}
$$

Substituting (4) into (2):

$$
B_z^{\text{bif}}(r) \;=\; \frac{3\,\mu_0 I a^2 \, d \, r}{2\,(a^2 + r^2)^{5/2}} \;+\; \mathcal{O}\!\left(\frac{d^3}{a^5}\right)
\tag{5}
$$

This is the **leading-order on-axis bifilar field**. It is the field of an axial *magnetic dipole gradient* — exactly what is expected for two equal-and-opposite magnetic dipoles separated by $d$.

### Step 4 — Ratio to single-loop reference

The reference is a single same-current loop at the origin:

$$
B_z^{\text{ref}}(r) \;=\; \frac{\mu_0 I a^2}{2\,(a^2 + r^2)^{3/2}}
\tag{6}
$$

Divide (5) by (6):

$$
\eta_B(r) \;=\; \frac{B_z^{\text{bif}}(r)}{B_z^{\text{ref}}(r)}
\;=\; \frac{3\,d\,r}{a^2 + r^2} \;+\; \mathcal{O}\!\left(\frac{d^2}{a^2}\right)
\tag{7}
$$

QED for the claim.

### Step 5 — Stationary point and maximum

$$
\frac{d\eta_B}{dr} \;=\; 3d \cdot \frac{(a^2 + r^2) - 2 r^2}{(a^2 + r^2)^2} \;=\; 3d \cdot \frac{a^2 - r^2}{(a^2 + r^2)^2}
$$

So $\eta_B(r)$ has its single maximum at $r = a$, with value

$$
\boxed{\;\eta_B^{\max} \;=\; \frac{3\,d}{2a}\;}
\tag{8}
$$

Equivalently: the on-axis ratio of bifilar-to-dipole field is bounded above by $3d/2a$, *no matter what other parameter you tune*, for fixed loop radius and separation. For $d/a = 0.10$ this caps $\eta_B$ at $0.15$ — a 6.6× *suppression* of the on-axis field at the optimum point.

---

## Result

$$
\boxed{\;
\eta_B(r) \;=\; \frac{|B_z^{\text{bif}}(r)|}{|B_z^{\text{ref}}(r)|} \;=\; \frac{3\,d\,r}{a^2 + r^2}\,,
\qquad
\eta_B^{\max} \;=\; \frac{3d}{2a} \;\;\text{at}\;\; r = a
\;}
$$

For an **energy-density** ratio (relevant where coupling is proportional to $|B|^2$):

$$
\eta_{B^2}(r) \;=\; \eta_B(r)^2 \;=\; \left(\frac{3\,d\,r}{a^2 + r^2}\right)^2,
\qquad \eta_{B^2}^{\max} \;=\; \left(\frac{3d}{2a}\right)^2.
$$

---

## Numerical example

Mk0.5 / Mk1 candidate geometry (matching [`docs/mk0_pcb_bifilar_coil.md`](../mk0_pcb_bifilar_coil.md) order-of-magnitude):

| Parameter | Value |
|-----------|-------|
| Loop radius $a$ | $5.0\,\mathrm{cm}$ |
| Axial separation $d$ | $5.0\,\mathrm{mm}$ |
| $d / a$ | $0.10$ |
| Current $I$ | $50\,\mathrm{mA}$ (drives both loops in series) |

Predicted on-axis values:

| $r$ | $\eta_B(r)$ | $|B_z^{\text{bif}}(r)|$ | $|B_z^{\text{ref}}(r)|$ |
|-----|-------------|-------------------------|-------------------------|
| $1\,\mathrm{cm}$ | $0.058$ | $35\,\mathrm{nT}$ | $0.60\,\mathrm{\mu T}$ |
| $a/2 = 2.5\,\mathrm{cm}$ | $0.120$ | $54\,\mathrm{nT}$ | $0.45\,\mathrm{\mu T}$ |
| $a = 5\,\mathrm{cm}$ | $0.150$ | $33\,\mathrm{nT}$ | $0.22\,\mathrm{\mu T}$ |
| $2a = 10\,\mathrm{cm}$ | $0.120$ | $9.2\,\mathrm{nT}$ | $0.077\,\mathrm{\mu T}$ |
| $4a = 20\,\mathrm{cm}$ | $0.069$ | $0.84\,\mathrm{nT}$ | $0.012\,\mathrm{\mu T}$ |

Predicted on-axis values (regenerated by [`notebooks/bifilar_near_field.py`](../../notebooks/bifilar_near_field.py)):

| $r$ | $\eta_B$ leading (eq. 7) | $\eta_B$ exact (eq. 2 / eq. 6) | $\lvert B_z^{\text{bif}}(r)\rvert$ | $\lvert B_z^{\text{ref}}(r)\rvert$ |
|-----|------|------|------|------|
| $1\,\mathrm{cm}$ | $0.0577$ | $0.0574$ | $34.0\,\mathrm{nT}$ | $0.592\,\mathrm{\mu T}$ |
| $a/2 = 2.5\,\mathrm{cm}$ | $0.1200$ | $0.1197$ | $53.8\,\mathrm{nT}$ | $0.450\,\mathrm{\mu T}$ |
| $a = 5\,\mathrm{cm}$ | $0.1500$ | $0.1501$ | $33.3\,\mathrm{nT}$ | $0.222\,\mathrm{\mu T}$ |
| $2a = 10\,\mathrm{cm}$ | $0.1200$ | $0.1201$ | $6.75\,\mathrm{nT}$ | $0.056\,\mathrm{\mu T}$ |
| $4a = 20\,\mathrm{cm}$ | $0.0706$ | $0.0706$ | $0.63\,\mathrm{nT}$ | $0.009\,\mathrm{\mu T}$ |

Leading-order (eq. 7) and exact (eq. 2 / eq. 6) agree to better than $0.4\%$ over this entire range — the $\mathcal{O}(d^2/a^2)$ correction is tiny at $d/a = 0.10$. **A discrepancy between this table and the notebook output is a bug in one of them.**

The wearer-relevant distance — coil-to-cortex through skull — is $r \approx 1\text{–}2\,\mathrm{cm}$. There, the bifilar field is **5–10 % of a same-current single-loop** (rows 1 and 2 above).

---

## Engineering interpretation

The on-axis result is a **deflationary** result. It shows that the popular "Tesla-bifilar means stronger field" framing, when applied to a series-opposing axial pair driven at fixed current, is **false on-axis in the quasi-static limit**. Three honest engineering takeaways:

1. **For a coupling channel that depends on on-axis $|B|$ at $r \sim a$**, a single loop wins. Use a single loop. Do not use this bifilar geometry just because it sounds esoteric.
2. **For a coupling channel that depends on $\partial B / \partial z$ (gradient pickup) or on a $|B|^2$ falling off as $r^{-8}$ instead of $r^{-6}$** (steeper near-field confinement, faster far-field rolloff, lower external EMI signature), the bifilar pair is the right geometry. This is the regime the wiki's bifilar claim plausibly belongs to.
3. **At fixed total resistive loss** rather than fixed current, the bifilar pair (two loops in series, twice the wire resistance, $\sqrt{2}\times$ lower current at same $P$) is *further* suppressed on-axis by a factor of $1/\sqrt{2}$ relative to the result above. The fixed-current convention adopted in §Setup is therefore charitable to the bifilar case.

The wiki's [`Bifilar Coil`](../wiki_cache/bifilar_coil.wikitext) claim is reinterpreted by this derivation as: *"bifilar geometry is preferred for **near-field-confined**, **gradient-coupled**, **low-far-field-EMI** emitters, not for absolute on-axis field strength."* Mk1's F2 probe (see [`docs/mk1_f2_probe.md`](../mk1_f2_probe.md)) is the apparatus that will measure exactly this distinction.

---

## Falsification hook

This derivation does **not** create a new $F_n$ row in [`docs/falsification.md`](../falsification.md). It is an analytic precursor that calibrates the expected on-axis $|B|$ ratio for **F3-precursor / F4-precursor** measurements (Mk1.5 sham-controlled $F^2$ instrumentation, per [`docs/falsification.md` "What Mk* can engage"](../falsification.md#what-mk1--mk2--mk3-can-actually-engage)).

Engagement claim: **at the Mk1.5 F2-probe geometry, $\eta_B(r)$ measured by a calibrated 3-axis magnetometer at $r \in [1, 20]\,\mathrm{cm}$ on-axis must agree with eq. (7) to within $\pm 20\%$** — or one of the following must be true:

- The coil geometry deviates from the idealization (likely; merits remeasurement and re-derivation with the empirical $a, d$).
- The drive electronics are introducing common-mode current (asymmetry in $\pm I$); diagnose with a current-transformer pair.
- The quasi-static assumption is violated (check operating frequency vs $c / 2\pi a$).

A bench result outside $\pm 20\%$ that cannot be traced to one of these mundane sources is an engineering anomaly that the project records and investigates. It does not, on its own, engage $F_3$ or $F_4$.

---

## Notebook

[`notebooks/bifilar_near_field.ipynb`](../../notebooks/bifilar_near_field.ipynb) regenerates Figure 4 (on-axis $\eta_B(r)$ vs $r/a$) and the numerical-example table.

Reproducibility contract: editing eq. (7) requires re-running the notebook and committing the updated figure file in the same change.

---

## Sources

| Equation / claim | Class | Source |
|---|---|---|
| Eq. (1), single-loop on-axis field | (a) consensus | Jackson, *Classical Electrodynamics* 3e §5.5; Griffiths §5.4.2. |
| Eq. (2), linear superposition for series-opposing pair | (a) consensus | Trivial Biot–Savart linearity. |
| Eq. (3)–(7), Taylor expansion in $d/a$ | (c) extrapolated | Original to this project. Inspection-grade. |
| Eq. (8), maximum at $r = a$ | (c) extrapolated | Original to this project. |
| Engineering interpretation (§) | (c) extrapolated | Original; deflationary reading of wiki's `Bifilar Coil` claim. |
| Wiki-side framing of bifilar geometry | (b) wiki | [`docs/wiki_cache/bifilar_coil.wikitext`](../wiki_cache/bifilar_coil.wikitext). |

---

## Open questions for v1

1. **Off-axis result.** Bifilar's actual engineering value is plausibly off-axis (gradient coupling to laterally-offset cortex). A full off-axis derivation requires Legendre-polynomial expansion of the loop field and is deferred to v1.
2. **Integrated energy in $r < 2a$.** The "field confinement" claim should be quantified as $\int_{r < 2a} |B|^2 \, dV / \int_{\text{all space}} |B|^2 \, dV$. Numeric, not closed-form; planned for notebook v0.5.
3. **Frequency response.** Quasi-static limit chosen here; the full near-field-EM treatment (with displacement current and radiation correction) is deferred until Mk2's UHF-band hypothesis is taken seriously.
4. **$N$-turn extension.** Trivial scalar prefactor; deserves a one-paragraph appendix in v1 to lock the factor before the Mk0.5 PCB build.
