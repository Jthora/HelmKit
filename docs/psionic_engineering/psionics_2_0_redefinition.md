# Psionics 2.0 — the discipline with α removed

**Status**: v0, 2026-08-06. A deliberate rebuild, not a retreat: sets the ψ-EM coupling constant α = 0 permanently as the operating definition of this discipline going forward, works out what that does to the rest of the framework (answer: almost nothing breaks), and proposes what "Psionics" means once it's no longer betting on the one unconfirmed, unfalsifiable term. Everything below is a redefinition proposal, not yet adopted anywhere else in this repo.

## The move, precisely

Set α = 0 in the ψ field's own Lagrangian (L_ψ). With no EM coupling, ψ has no way to affect anything observable — a field with zero coupling to everything else is physically equivalent to no field at all. That makes every C-ψ coupling term in the EFT Lagrangian (g₁, g₂, g₃, g₄ — the terms that made ψ matter to consciousness) inert by the same logic: they're couplings to a field with no observable consequences. Delete ψ from the theory entirely. What survives:

```
L = ½∂ᵘC∂ᵤC − V(C) − g_F·C·F_μν F^μν + L_EM
```

with V(C) = ½m_C²C² + (λ_C/4)C⁴ unchanged, and C still defined the same way — a coarse-grained order parameter over the underlying Wilson-Cowan neural-field dynamics.

**This is exactly Johnjoe McFadden's CEMI theory**, formalized with the same rigorous EFT discipline (Landau-Ginzburg potential, phase structure, symmetry-constrained term list) the wiki already built for the larger framework. It isn't a smaller, sadder version of Psionics. It's the part of the original framework that was never resting on the unconfirmed piece — same math, same phase diagram (baseline/focused/critical/runaway), same predictions about attention and integration, minus the one term nothing has ever measured.

## What survives untouched

Everything in this project that was never actually about α:

- **The C order-parameter model of consciousness** — phase transitions, the critical-regime prediction, the runaway/pathological-state warning — all of it derives from V(C) and g_F, not from the deleted terms. Fully intact.
- **HRV biofeedback, tVNS, light-pulse, 40 Hz entrainment** — these were always about modulating C via ordinary neural/autonomic pathways (the Wilson-Cowan substrate underneath C), never via ψ. Zero dependency on the deleted terms.
- **The Mk-ladder, Track A/Track B discipline, falsification framework** — this was a *methodology* for developing hardware under scientific uncertainty. It doesn't care what the uncertain hypothesis was.
- **Devaney-Wolf near-field engineering, the coil's core design rationale** — non-radiating source theory doesn't reference ψ at all; it's real antenna physics regardless of what's driving the coil or why.

## What changes, honestly

**The coil stops being a "ψ transducer" and becomes a CEMI-channel probe.** The g_F C F² term is McFadden's real claim: the brain's own endogenous EM field is (or is tightly coupled to) conscious experience, and — per the actual empirical literature already found this session — external EM perturbation demonstrably affects neural firing and conscious state (that's not exotic; it's the same evidenced ground TMS and tDCS stand on, and it's why this project already excluded tACS/tDCS from Mk1 on safety-conservatism grounds, not evidentiary grounds). A near-field coil, reframed honestly, is now a device testing whether *externally applied, non-thermal, near-field EM coupling specifically* — as opposed to the conventional far-field/contact stimulation methods already studied — has a measurable g_F-channel effect. That's a real, falsifiable, non-exotic research question. It just isn't the same question the coil was originally built to ask.

**The "engineering discipline" has exactly two legitimate channels now, both real:**
1. **Direct/neural** — tVNS, HRV, GVS, photic/audio entrainment. Acts on the Wilson-Cowan substrate underneath C directly. No coupling constant needed at all; this was never theoretical, it's just applied psychophysiology.
2. **CEMI/g_F** — external EM field perturbation of the brain's own endogenous field. Real, evidenced (ephaptic coupling, TMS/tDCS literature), currently excluded from Mk1 hardware for safety reasons already documented in `docs/safety.md`, not because the channel itself is unconfirmed.

**The α-channel doesn't get deleted from institutional memory — it gets retired to an appendix.** Kept explicitly labeled as "if independently confirmed real by someone else's dedicated research (the MEG reanalysis design in `effective_physics_derivation_audit.md` is what that would take), this is where it plugs back into the Lagrangian above." Not pretending it was never considered. Just refusing to let the engineering roadmap owe it anything.

## What to call this

"Psionics" doesn't etymologically require the pop-culture telekinesis reading — ψ/"psi" is the ordinary Greek root for "of the mind," used constantly in mainstream psychology and statistics without any paranormal connotation at all. Two honest options, not mutually exclusive:

- **Keep "Psionics," redefine it explicitly**: *"the engineering discipline of modulating the integrated conscious/attentional order parameter C through its two established physical channels — neural/autonomic and CEMI/electromagnetic — deliberately scoped to exclude unconfirmed coupling terms."* One footnote, no rebrand, and the name still carries whatever narrative value it's had for this project.
- **A more literal name for the same content**: something like "Cortical Field Engineering" or "Consciousness-State Engineering" — less evocative, more immediately legible to someone with no context.

Not resolving which here — that's a naming preference, not a technical question, and it's yours to make.

## Net effect on the actual roadmap

Smaller than it might feel: almost the entire physical build (topology B, the biofeedback floor, the indefatigability stack, the falsification discipline) was already Track A and doesn't move at all. What changes is entirely in how the coil and the theoretical framing get *described* — honestly narrower, resting on a real published theory instead of an invented one, and for the first time, resting on nothing this project can't point to independent, external, peer-reviewed support for. That's not a smaller thing to have built. It's the same thing, with the one part that couldn't hold weight taken off before it had to be found out the hard way.
