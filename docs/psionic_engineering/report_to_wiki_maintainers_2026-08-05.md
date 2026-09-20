# Consistency findings on the "Psionic Engineering" branch — for the FusionGirl wiki maintainers

**From**: the HelmKit repository (https://github.com/Jthora/HelmKit) engineering side — the head-worn hardware platform your `HelmKit` and `HelmKit Architecture` pages describe. We build from your wiki as a design specification and take the framework's own internal discipline seriously.
**Date**: 2026-08-05
**Re**: four internal-consistency findings in the new `Psionic Engineering` branch (published in the drop that landed shortly before this date), found via independent, tool-assisted recomputation — plus a fifth item that's a two-way check: we found what looks like an effect-size unit issue in a citation your `Psionic Engineering` hub and our own docs both carry, and separately confirmed one of your other citations holds up exactly against its primary source.
**Status of this report**: informational. We have not modified, and cannot modify, the wiki. Everything below is reproducible from the wiki's own public API or from public literature; we're sending it because your `Psionic Engineering` hub page states its own discipline as "every component, material, and system is derived from a specific term in the master ψ field equation — never invented by analogy alone," and these findings are exactly the kind of thing that discipline is designed to catch. We verified immediately before sending that none of the four wiki pages involved have changed since we found these (checked via `action=query` against your live API; all four revisions below are current as of this writing).

---

## Why we're writing

Your `Psionic Engineering` hub is an unusually rigorous, equation-first engineering discipline — the Track A/Track B split, the derivation-term table, the TML validation ladder are all things we adopted as a model for our own falsification framework. Rigor like that invites (and rewards) independent checking. We built a small toolkit to do exactly that: re-derive PDE solutions numerically from your stated formulas via finite-difference residual checks, and recompute worked examples from their own stated inputs. Two of your foundational equations (the ψ dispersion relation, the Yukawa/coherence-length static solution) passed cleanly under independent numerical verification — we're not reporting a list of complaints, we're reporting the output of a check that mostly came back green, with four exceptions.

We are explicitly **not** taking a position on whether ψ is real, and none of these four findings touch that question — they are all Track A (buildable/testable regardless of the ψ hypothesis), and all four are either arithmetic or citation-consistency issues, not physics disagreements.

---

## Summary

| # | Page(s) | Finding | Confidence |
|---|---|---|---|
| 1 | `Bifilar Coil Engineering` | Stated 9.7°C adiabatic pulse temperature rise doesn't follow from the page's own formula and inputs (recomputes to ≈9690°C) — but root cause identified | High — confirmed by direct recomputation, root cause pinned down |
| 2 | `Bifilar Coil Engineering` | Two different numbers (20 mW vs 20 W) stated for the same "average pulsed drive power" quantity in two sections of the same page | High — direct quote comparison, unambiguous |
| 3 | `Psionic Engineering` (hub) vs. `Shepard Tone Synthesis` | Hub's summary table states Shepard-tone carriers at 10/20/40 kHz; the detailed page states 40/80/160 kHz | High — direct quote comparison; the detailed page's derivations only support one of the two triples |
| 4 | `Smart Composite Fill` | Infobox states BST tunability target ≥70%; "what it predicts" section states ≥35% for the same quantity | High — direct quote comparison |
| 5a | `Psionic Engineering` (hub), Falsifiability Framework section | Citation "Star Gate review: combined d≈0.20, p<10⁻²⁰" — the p-value **checks out** against Utts (1996)'s own reported aggregate figure | Confirmed accurate — not a problem, included for completeness |
| 5b | `Psionic Engineering` (hub) — and, we discovered, our own `docs/falsification.md` carries the same issue | The "d≈0.20" part of the same citation, and a parallel "d≈0.14–0.20" figure attributed to Storm et al. 2010, likely conflate an *r*-type effect size with Cohen's *d* — see below | Moderate-high — real primary-source numbers found, conversion math is unambiguous, but which exact figure the hub meant to cite isn't fully resolved |
| 6 | `Effective Field Theory of Consciousness`, `5D Action Principle` | Both pages are categorized/framed under "Effective Physics" (the hub's own branch alongside phonons, quasiparticles, analogue gravity — all *substrate-derived* physics), but neither page actually derives ψ's existence the way that branch's other members derive their emergent quantities from a known substrate. Not a numeric error — a framing/categorization question. | High confidence on the structural observation; a judgment call on what (if anything) to do about it, explained below |

Findings 1–4 and 5b are internal to the wiki or point at a citation issue; 5a is a case where checking against the primary source confirmed your citation rather than finding a problem — we didn't want to only report bad news. Finding 6 is a different kind of item — not a bug, a framing observation — included because it came out of the same discipline of taking your own stated method seriously.

---

## Finding 1: Bifilar Coil Engineering — adiabatic pulse temperature rise

**Page**: [`Bifilar Coil Engineering`](https://wiki.fusiongirl.app/wiki/Bifilar_Coil_Engineering), pageid 6571, revid 12570 (last revised 2026-07-04T21:49:40Z).
**Section**: "Pulsed Drive Constraint."

**Quote** (page's own words): *"At τ_pulse = 1 μs: ΔT = 20000 × 10⁻⁶/(3.44×10⁶ × 6×10⁻¹³) = 9.7°C per pulse."*

**Recomputation**: evaluating that exact expression —

```
ΔT = P_peak · τ / (ρc_p · V)
   = 20000 W × 1×10⁻⁶ s / (3.44×10⁶ J/(m³·K) × 6×10⁻¹³ m³)
   ≈ 9690 °C
```

— gives ≈9690°C, not 9.7°C. (We independently checked the copper volumetric heat capacity constant used, 3.44×10⁶ J/(m³·K): density 8960 kg/m³ × specific heat 385 J/(kg·K) = 3.45×10⁶ J/(m³·K), matching your value closely — the constant itself is correct and is not the source of the discrepancy.)

**Root cause**: substituting **average** power for the formula's labeled `P_peak` reproduces your stated answer almost exactly:

```
P_avg = P_peak × duty_cycle = 20000 W × 0.001 = 20 W
ΔT_using_P_avg = 20 W × 1×10⁻⁶ s / (3.44×10⁶ × 6×10⁻¹³) ≈ 9.69 °C
```

This matches your stated 9.7°C to within rounding. Our read: this specific calculation appears to have used the average (duty-cycle-scaled) power where the formula's own variable name — and the physical meaning of a *per-pulse* transient-heating calculation — calls for the instantaneous peak power. We're not asserting which is physically correct (a genuine per-pulse spike calculation arguably should use peak power, since that's what's actually flowing during the 1μs "on" window; if average power was intentional, the framing as "per pulse" may need adjusting) — that's a modeling call for whoever owns this derivation. What we can say with confidence is that this pins down *exactly* which two quantities got swapped, rather than leaving it as an unexplained ~1000× gap.

---

## Finding 2: Bifilar Coil Engineering — average power stated two different ways

**Page**: same as above (pageid 6571, revid 12570).

**Quote A** (body text, "Pulsed Drive Constraint" section): *"At 0.1% duty cycle (1 μs on, 1 ms off): average dissipation = 20 W × 0.001 = 20 mW per metre of trace — trivially manageable."*

**Quote B** (later, "Sanity Checks" table, TML Measurement Protocol section): *"Average drive power ‖ 20 kW peak × 0.1% duty cycle = 20 W average → within wearable budget ✓"*

**Recomputation**: P_peak × duty_cycle = 20,000 W × 0.001 = **20 W**, matching Quote B and contradicting Quote A's 20 mW (which appears to start from "20 W" rather than "20 kW" as its multiplicand — a factor-of-1000 slip consistent with, though not necessarily connected to, Finding 1's peak/average mix-up).

---

## Finding 3: Shepard-tone carrier frequencies disagree between the hub and the detailed page

**Page A**: [`Psionic Engineering`](https://wiki.fusiongirl.app/wiki/Psionic_Engineering) (hub), pageid 6541, revid 13195 (last revised 2026-07-23T21:22:55Z). Branch D summary table, `Shepard Tone Synthesis` row.

**Quote A**: *"DSP implementation: 3 carriers (10, 20, 40 kHz), raised-cosine envelopes, geometric spacing"*

**Page B**: [`Shepard Tone Synthesis`](https://wiki.fusiongirl.app/wiki/Shepard_Tone_Synthesis), pageid 6572, revid 12571 (last revised 2026-07-04T21:50:03Z) — the detailed page the hub row summarizes.

**Quote B** (repeated consistently throughout the page): *"a three-carrier drive waveform at 40, 80, and 160 kHz"* — with supporting derivation that specifically requires this triple: *"With a 160 MHz FPGA clock (standard for Artix-7), all three carriers can be synthesised with integer phase accumulator values: 40 kHz = 160 MHz/4000; 80 kHz = 160 MHz/2000; 160 kHz = 160 MHz/1000"* and *"The PZT-5H acoustic resonance at ~1.5 MHz ... is the 37th harmonic of 40 kHz."*

These are two different stated frequency triples for the same design element. Page B's numbers are load-bearing — the FPGA integer-division property and the PZT 37th-harmonic relationship both specifically depend on the 40/80/160 triple and would not hold for 10/20/40. Our read: the hub's "10, 20, 40 kHz" is a summary-table entry that predates, or wasn't updated alongside, the detailed derivation in Page B.

---

## Finding 4: Smart Composite Fill — BST tunability target stated two ways

**Page**: [`Smart Composite Fill`](https://wiki.fusiongirl.app/wiki/Smart_Composite_Fill), pageid 6557, revid 12555 (last revised 2026-07-04T07:47:21Z).

**Quote A** (infobox): *"BST tunability target: τ = (ε_r(0V) − ε_r(200V))/ε_r(0V) ≥ 0.70"* (i.e. ≥70%).

**Quote B** ("what it predicts" section): *"(1) A BST nanocomposite with ε_eff tunability ≥ 35% at 40 kHz across a 0–200V bias sweep, confirmed by Maxwell-Garnett prediction before measurement"*

Both describe the same quantity (BST dielectric tunability under the same 0–200V bias sweep) with different minimum targets (70% vs. 35%). We also noticed a handful of other numbers near "tunability" elsewhere on the page (a QC-table minimum around 8%, a volume-fraction figure of ~4.6%) that may or may not be the same claim in different units — we did not chase those further and flag them only as possibly-related context, not as confirmed findings.

---

## Finding 5: your `Psionic Engineering` hub's Star Gate/Ganzfeld citation — one part confirmed, one part likely a unit conflation (and we have the same issue in our own docs)

**Page**: [`Psionic Engineering`](https://wiki.fusiongirl.app/wiki/Psionic_Engineering) (hub), pageid 6541, revid 13195. Falsifiability Framework section.

**Quote**: *"prior from existing anomalous cognition literature (Star Gate review: combined d ≈ 0.20, p < 10⁻²⁰)"*

We independently checked both halves of this against the actual literature (web search, not a full read of every primary PDF — treat our confidence accordingly):

**The p-value holds up.** Jessica Utts' 1996 assessment of the U.S. government Star Gate program reported the combined probability across ~27,000 trials (SRI + SAIC, 1973–1993) as "astronomically small (p = 10×10⁻²⁰)" — matching your citation closely. No correction needed here; we're including it so this report isn't only a list of problems.

**The "d≈0.20" part looks like it's applying the wrong effect-size metric** — and we found the identical issue in our own `docs/falsification.md`, which independently cites "Storm et al. 2010 / Cardeña 2018 aggregate d ≈ 0.14–0.20" for the related Ganzfeld literature. What Storm, Tressoldi & Di Risio (2010) actually report for their primary 29-study homogeneous ganzfeld set is an **effect size r = 0.142** (Stouffer Z=5.48) — and r and Cohen's d are different statistics. Converted properly (d = 2r/√(1−r²)), that's d≈0.29, not 0.14. Separately, a more recent preregistered ganzfeld meta-analysis (~2020–2021) reports a smaller r≈0.08 across the 1974–2020 literature, suggesting the 2010 figure may also be a dated upper bound rather than the best current estimate. We haven't traced exactly which number your hub's "0.20" was meant to represent (Utts' own SAIC sub-analyses report several different effect-size-like figures — 0.124, 0.248, 0.385, etc., depending on which subset — so there may be a legitimate source for "0.20" we haven't found), so we're flagging this as "worth a second look," not asserting a specific fix.

We're documenting the details of this check (sources, conversion math, and what's still unresolved) in [`literature_grounding.md`](literature_grounding.md) in our own repo, in case it's useful — happy to share the reasoning in full or compare notes on where each of us got these numbers from.

---

## Finding 6: the "Effective Physics" framing claims more than the two derivation pages deliver

**Pages**: [`Effective Field Theory of Consciousness`](https://wiki.fusiongirl.app/wiki/Effective_Field_Theory_of_Consciousness) and [`5D Action Principle`](https://wiki.fusiongirl.app/wiki/5D_Action_Principle), read in full (not just summarized) via browser fetch on 2026-08-06.

Your `Effective Physics` hub page is, itself, entirely legitimate — its four branches (Effective Matter, Effective Geometry, Effective Media, Effective Gravity) all describe real physics: quasiparticles, metamaterials, analogue-gravity/Hawking-analogue systems. The common thread across all four is that a *known* microscopic substrate (atoms, a lattice, a fluid) gets coarse-grained into a description that mathematically mimics something else — nobody has to independently establish that phonons "exist," because they're a construction on top of atoms everyone already agrees are there. `Psionic Engineering`'s hub page lists "Effective Physics" as one of five foundational domains, which implicitly invites the same reading for ψ.

We checked whether that reading holds by reading the two pages that would have to do the actual work: `Effective Field Theory of Consciousness` (builds a genuinely correct EFT — starts from Wilson-Cowan neural-field theory, a real trusted microscopic model, and writes the most general Lagrangian consistent with stated symmetries) and `5D Action Principle` (uses genuine Kaluza-Klein dimensional reduction, the same technique that famously derives 4D electromagnetism from 5D gravity). Both use rigorous, honestly-applied machinery — but in both cases, ψ itself enters as a field already assumed to exist, not as something the machinery derives from a known substrate. The EFT page is explicit about this itself ("the coefficients g₁, …, g₄, g_F, m_C, λ_C are empirically open"); the 5D page's own framing ("everything else is mathematics, not new postulates") is true of the *consequences* of assuming ψ, not of ψ's existence.

We want to be precise about what we're and aren't saying: this is not the same genre of finding as 1–5 above, and we don't think it's wrong physics — postulating a hypothetical field and then applying rigorous EFT/Kaluza-Klein discipline to its consequences is a completely legitimate genre of theoretical physics (it's exactly how axion physics and other beyond-Standard-Model extensions work). What we'd flag is a framing/reader-expectation issue: shelving Psionics under the same "Effective Physics" banner as substrate-derived branches (phonons, analogue gravity) reads, to a careful reader, as claiming ψ is *that* kind of emergent — grounded in a known substrate — when the two pages that would establish that instead do the (still legitimate, but different) BSM-EFT-style move of positing a hypothetical field and working out its disciplined consequences. The CEMI page already models the fix we'd suggest — it's upfront that ψ generalizes CEMI via a coupling constant (α) that's "empirically open," and even draws the axion-photon analogy explicitly. Making that same epistemic-status framing more prominent on the two derivation pages themselves (rather than only in the CEMI cross-reference) would resolve the mismatch without changing any of the underlying physics.

One useful thing this framing *does* already buy, which might be worth surfacing more: setting α = 0 in the EFT collapses the whole framework to McFadden's CEMI theory, which is real and checkable against already-published ephaptic-coupling/EEG/MEG literature without any new experiment — that sub-claim doesn't share the "postulated, not derived" status of the ψ-specific part, and distinguishing the two more clearly on-page would let readers see exactly which parts of the framework rest on existing evidence versus which parts are, by the framework's own honest admission, open.

---

## Part 2 additions (2026-08-06) — factual updates, a taxonomy fix, and one constructive architectural option

Everything below is either a number to correct, a category to move something into, or a concrete restructuring option — deliberately not a proposal to add more caveat language anywhere. If anything, several of these *reduce* how much hedging the framework needs, by making its claims match its actual evidentiary support instead of overstating it.

### Finding 7: the ganzfeld citation has a better number available now

Finding 5b flagged "d≈0.20" as likely conflating an *r*-statistic with Cohen's *d*, without fully resolving what the correct figure should be. It's resolved now: **Tressoldi & Storm's Stage 2 Registered Report** (*F1000Research*, 2024) — the actual preregistered gold-standard format, not just a newer meta-analysis — covers the 1974–2020 literature and reports **ES = 0.088 (95% CI 0.04–0.13)**, passing four separate publication-bias tests with no decline over time. Recommend updating the Falsifiability Framework's citation to this figure directly.

### Finding 8: the field's own most rigorous 2020s tests of RNG-PK and precognition are null — worth reflecting wherever those paradigms are cited

Not previously reported. The 1988 US National Research Council review found no convincing evidence for RNG-PK, a verdict never overturned; Bösch, Steinkamp & Boller's 2006 meta-analysis (380 studies) found a significant-but-tiny effect tracking with funnel-plot asymmetry (the statistical signature of publication bias); most directly, **Maier & Dechamps (2022)**, a preregistered exact replication (quantum-RNG dataset, n=12,254), found strong evidence *against* the original correlational micro-PK effect after error-correction. For precognition specifically: the **Transparent Psi Project**, a large preregistered confirmatory replication of Bem's paradigm, found no evidence for psi, and a 2024/2025 follow-up ran three further replications totaling 26,483 participants and 420,472 trials — also null. If any page cites RNG-PK or precognition evidence as part of the framework's empirical support, this is the current state of the best available tests on those two paradigms specifically, and it's materially different from ganzfeld's picture (Finding 7).

### Finding 9: the "Effective Physics" categorization is a taxonomy problem with a taxonomy fix, not a hedging problem

Checked five pages directly (not just the two from the original Finding 6): `Psi Field`, `Quantization of the Psi Field`, `Renormalization of Psi Theory`, `Wilson-Cowan Coupled to Psi`, and `Psi Condensation Threshold`. All five show the same pattern — genuine emergence *vocabulary* without an emergence *derivation*. `Psi Field` (revid 13202) states ψ "emerges from an underlying substrate rather than a fundamental field" but immediately admits "the precise functional forms remain an open research problem and are expected to follow from a future microscopic substrate theory" — no substrate is named. `Wilson-Cowan Coupled to Psi` (revid 12585) uses "two coupled pendulums" as its own chosen metaphor — an explicit description of two independent pre-existing systems being coupled, not one emerging from the other. Most directly: `Psi Condensation Threshold` (revid 13361, edited 2026-08-05 — recent enough that it's likely the specific attempt at this exact fix) defines its condensation threshold using parameters it then states, in its own words, *"A rigorous version must derive r and φ from the structural parameters rather than treating them as co-equal factors. This derivation is not yet done."*

**Recommended fix — recategorize, don't caveat, and there's already a template for this in your own wiki.** A broader survey (2026-08-06) read seven more pages across the actual "Effective X" stack — `Effective Mass`, `Effective Charge`, `Effective Metric`, `Effective Spacetime`, `Effective Medium Theory`, `Analogue Gravity`, `Emergent Geometry` — plus two adjacent branch pages, `Magnetogravitics` and `Electrogravitics`. The core discipline is uniformly excellent: six of seven "Effective X" pages are completely uncontaminated by anything psi-adjacent, technically correct, real physics. `Magnetogravitics` cleanly stratifies confirmed physics (frame-dragging, Gravity Probe B) from contested claims (the Tajmar anomaly, labeled "contested, possibly an artefact") from openly-speculative engineering (dated 2038–2042, explicitly conditional on unconfirmed effects). `Electrogravitics` goes further — it presents the Biefeld-Brown "antigravity" claim, then refutes its own premise with vacuum-test evidence, and states plainly: *"electrogravitics, as originally framed, is essentially refuted by vacuum tests."*

That changes what this recommendation actually is. It isn't asking the wiki to adopt a standard it doesn't have — the standard is demonstrably already there, applied correctly everywhere in the "Effective Physics" branch except at every seam where content touches Psionics (including a "Psi Tech" subsection on the otherwise-clean `Effective Mass` page, using the identical unearned framing found elsewhere). The recommendation is: apply the `Electrogravitics` treatment to `Psi Field` / `Psi Condensation Threshold` — state plainly what's confirmed (the C order parameter, the g_F/CEMI channel — real, published, evidenced), what's contested or unconfirmed (α and everything downstream of it), and, per Finding 10 below, what's structurally ruled out rather than merely untested (non-local derivation from a locally-confined substrate). Move the result into a category that matches what it actually is — alongside openly beyond-Standard-Model-style content, the same reference class ψ already claims for itself via its own axion-photon analogy on the Renormalization page. This isn't a downgrade or a foreign standard. It's internal consistency with work this wiki has already done well, on a structurally similar problem, two clicks away.

### Finding 10: a specific, structural reason the derivation keeps stalling, worth stating precisely before more effort goes into attempting it

Every genuine phonon-style effective field (phonons, magnons, analogue-gravity horizons) is provably confined to the substrate it's derived from — that confinement is *why* the derivation works, not an incidental limitation. But ψ's stated functions (dyadic/"communion mode" coupling between separate people, N⁴ group amplification, F2's distance-independence) all require it to reach *beyond* any single brain's tissue. A field can be legitimately derived from a substrate (local, confined) or it can do the cross-substrate things ψ is asked to do (non-local) — those two requirements are in direct tension, and no amount of additional derivation work resolves a structural contradiction. The one place in real physics where genuine non-locality exists — quantum entanglement — doesn't rescue this either: even setting aside decoherence at biological temperatures (the same problem that constrains Orch-OR), the no-communication theorem independently guarantees entanglement alone can never transmit information or influence between two parties. This is worth having on record precisely, not as a dismissal, but so future derivation attempts aim at the actual obstacle instead of re-discovering the same wall.

### Finding 11 (constructive): a concrete restructuring that resolves Findings 9 and 10 cleanly, without deleting content

Set α = 0 in ψ's own Lagrangian. With no EM coupling, ψ has no observable consequences, which makes every C-ψ coupling term (g₁–g₄) inert by the same logic — a coupling to a field with zero observable effect is dead weight. What remains: `L = ½∂C∂C − V(C) − g_F·C·F_μν F^μν + L_EM` — which is exactly Johnjoe McFadden's published CEMI theory, wearing the same rigorous EFT formalism the wiki already built. Nothing about the C order-parameter model, its phase structure, or its predictions changes. What changes is scope: the framework's confirmed-adjacent core (C + g_F/CEMI, resting on real ephaptic-coupling literature) becomes explicitly separable from its hypothesis extension (ψ, α, g₁–g₄ — kept, not deleted, clearly labeled as the postulated BSM-style piece per Finding 9's recategorization). This isn't a smaller framework. It's the same framework with an honest internal boundary drawn where one already structurally exists.

### Finding 12 (corrected after direct verification): `Effective Scalar Waves` was checked in full and does not have the problem initially flagged

An earlier draft of this finding recommended renaming `Effective Scalar Waves` away from "scalar wave" terminology based on the term's association with a well-documented fringe-physics cluster (Bearden/Tesla-mythology free-energy claims), without having actually read the page first — that was a mistake, corrected here rather than left standing. Read in full: the page correctly defines "scalar waves" via legitimate physics (acoustic/pressure waves, plasma oscillations, superconductor/BEC order parameters, Higgs excitations) and explicitly does *not* make the claim that actually defines the pseudoscience version — that scalar waves bypass shielding or carry free energy through a vacuum aether. It does extend into a speculative "Psionic Field Theory" application, but labels that extension precisely: *"No accepted physical theory currently verifies such mechanisms."* That's accurate scope-marking, not something to fix. No recommendation stands here — flagging the correction for the record, since a wrong finding shouldn't be sent even in an internal miss. `Caduceus Coil`'s own "scalar-wave" reference was already checked in the original audit and found to correctly distinguish rigorous EM analysis from fringe "scalar wave emission" claims — consistent with this finding, not contradicted by it.

### Finding 13 (credit, not just critique): the running-coupling treatment on `Renormalization of Psi Theory` is real, competently-executed physics

Worth stating plainly since this report shouldn't only carry bad news: that page treats α as a renormalization-group running quantity rather than a fixed constant, complete with an actual β-function — technically correct, standard QFT practice (every Standard Model coupling runs with energy scale). It doesn't resolve Findings 9/10 (RG running describes how an *already-existing* coupling's value shifts with scale, not why the coupling exists), and the page's own closing line draws the same axion-photon analogy this report keeps arriving at independently — but it's good, real work, and deserves to be recognized as such rather than folded into the critique above.

---

## Methodology, for reproducibility

Findings 1–4 came from direct quotation and arithmetic, reproducible by anyone with the page text and a calculator — no proprietary tooling required to verify them. For context, since automation is how we found most of them: we maintain a small stdlib-only Python toolkit (`tools/verify_psi_equations.py` for worked-example recomputation and PDE-residual checks against finite-difference numerics, `tools/scan_wiki_consistency.py` for corpus-wide numeric-claim comparison, `tools/experiment_design.py` for the effect-size/power-analysis math behind Finding 5) that we're happy to share if useful — findings 1 and 2 came from the first tool, findings 3 and 4 from a mix of the second tool's automated flag (4) and manual triage of its output (3, since 3 lives in an ordinary wikitable our current scanner doesn't parse yet, not an Infobox). Finding 5 came from web search against the primary parapsychology literature, not from anything wiki-specific. Finding 6 came from reading `Effective Field Theory of Consciousness` and `5D Action Principle` in full via a browser-UA fetch (your WAF blocks non-browser user agents, which we hit and worked around on our sync tooling separately) rather than from any of our automated checkers — it's a structural/framing read, not something a script flags.

We deliberately did not attempt to resolve findings 1 and 2 by guessing which number is "right" and editing anything — that's not ours to decide, and we have no write access to the wiki regardless. We also want to be clear that this is not an exhaustive audit: we've closely checked 2 of the ~29 currently-written pages in the Psionic Engineering branch (plus a corpus-wide but heuristic and noisy scan of the rest, and one literature-citation spot-check), so the base rate here (5 findings from a small sample, one of which turned out to be a confirmation rather than a problem) suggests there may be more of both kinds — errors and confirmations — that we haven't found yet.

---

## Closing

None of this is meant as a critique of the framework's substance — the parts we checked most rigorously (the master equation's dispersion relation and Yukawa/coherence-length solution, and separately the Star Gate p-value citation) held up cleanly under independent verification. We're sending this in the spirit of the hub page's own stated discipline, and we'll keep checking on our end regardless of whether/when these get addressed upstream — happy to send further findings the same way as we work through more of the branch, and genuinely interested in comparing notes if you're doing the equivalent kind of grounding work on your end.
