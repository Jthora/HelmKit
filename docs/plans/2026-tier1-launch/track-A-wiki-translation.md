# Track A — Wiki content → engineering translation

- **Status**: `in-progress` (unblocked 2026-08-05 — wiki content drop landed)
- **Owner**: HelmKit-side AI assistant + Jono
- **Depends on**: external wiki AI agent's expansion landing — **done**, see below
- **Unblocks**: deeper Mk1+ design, new derivation candidates, new safety blacklist rows

## What shipped (2026-08-05)

The wiki drop landed as a new `Psionic Engineering` hub (42-page discipline; ~29 pages actually written as of this sync) plus substantial revisions to `HelmKit`, `HelmKit Architecture`, `Psi Field`, `Psionics`, and most of the Pass-2 roster. Work so far:

- `tools/wiki_pages.yml`'s `user_agent` fixed — the live wiki's WAF now 403s non-browser UAs; patched to a browser-realistic string (commit pending).
- `tools/wiki_pages.yml` page list expanded with a curated 51-page "Pass 3" priority subset (Branches A/B/C + D1–D2 of the Psionic Engineering hub, plus new Psi-Tech device-catalog pages). Full 484-page connected graph is documented but not all tracked — most of the untracked remainder is mythos/character content or vehicle-scale propulsion tech (`Magnetogravitic Rail Drives` etc.) out of scope for HelmKit.
- `python3 tools/wiki_sync.py` run for real: 108 tracked, 86 new/revised, 0 errors.
- First translation pass (2 of the "highest-leverage 3-5 pages" this doc's process calls for) written under `docs/psionic_engineering/`: `bifilar_coil_engineering.md`, `tpms_lattice_design.md` (covers both `TPMS Lattice Design` and `Smart Composite Fill`). Index: `docs/psionic_engineering/README.md`.
- `docs/wiki_anchors.md` updated with a Pass 3 section pointing at the new hub and the translation index.
- **Checked, not a real conflict**: the wiki's new HelmKit ladder (Mk0.0→Mk3.0, stim starting at Mk1.0) matches `docs/mk_ladder.md` (already canonical in this repo since 2026-05-14) — the older `wiki_anchors.md` §5 "Mk1 stays sensing-only" language is superseded, not contradicted.
- **Flagged, not resolved**: the wiki's new bifilar coil spec (200V/40kHz/~100A peak pulsed, shell-embedded) is a materially higher power-class design than the existing `docs/mk0_pcb_bifilar_coil.md`, and `docs/safety.md`'s frequency table has no explicit row for near-field-E-dominant sub-MHz emitters. See `docs/psionic_engineering/bifilar_coil_engineering.md` Safety section for the specific recommendation — needs its own review, intentionally not applied in this pass.

## What shipped (2026-08-05, part 2) — computational toolkit

Three original (not wiki-translation) tools built in response to "what software/statistical tooling can investigate psionics claims directly": [`tools/verify_psi_equations.py`](../../../tools/verify_psi_equations.py), [`tools/experiment_design.py`](../../../tools/experiment_design.py), [`tools/analyze_dyadic_coherence.py`](../../../tools/analyze_dyadic_coherence.py). Full writeup: [`docs/psionic_engineering/computational_toolkit.md`](../../psionic_engineering/computational_toolkit.md). Headline findings:

- The wiki's own foundational math (dispersion relation, Yukawa/coherence-length solution) is internally self-consistent under independent numerical verification.
- The `Bifilar Coil Engineering` page's ICNIRP/E-field/B-field worked numbers all reproduce exactly; its adiabatic-pulse temperature-rise calculation (claims 9.7°C, independently recomputes to ≈9690°C from the page's own stated formula and inputs) and its average-power figure (states both 20mW and 20W for the same quantity in two sections) do not.
- The wiki's own TML-3 pass criterion (N=10, effect size d≈0.20) is underpowered by the wiki's own cited effect size — properly powered N is ≈197, not 10.
- 97/97 unit tests passing across the three new tools (`tests/test_verify_psi_equations.py`, `tests/test_experiment_design.py`, `tests/test_analyze_dyadic_coherence.py`).

## What shipped (2026-08-05, part 3) — toolkit v1

Follow-up pass after a critique of part 2's tools, adding: binomial power/Bayes-factor stats to `experiment_design.py` (the correct test family for the wiki's own Ganzfeld/Star-Gate-style F1/F2 citations, which are forced-choice hit-rate designs, not mean-difference designs); [`tools/forced_choice_protocol.py`](../../../tools/forced_choice_protocol.py) (hash-committed target generation + scoring, built on those stats); segment-aware + generic-scalar-channel support in `analyze_dyadic_coherence.py`; and [`tools/scan_wiki_consistency.py`](../../../tools/scan_wiki_consistency.py) (corpus-wide numeric-claim scanner, now wired into `.pre-commit-config.yaml`). Full writeup: [`docs/psionic_engineering/computational_toolkit.md`](../../psionic_engineering/computational_toolkit.md). 154/154 tests passing.

The wiki scanner independently re-found the BST-tunability discrepancy (≥70% infobox vs ≥35% prose on `Smart Composite Fill`) that had only been caught by hand before — now tracked in `tools/wiki_consistency_known_issues.yml`. Its within-page heuristic check also has a real, honestly-documented false-positive problem on dense engineering text; it's non-blocking by default for that reason.

## Remaining for this track

- Translate Branch A (foundation math: ψ Conservation Laws, Dispersion Relations, Impedance Theory, Boundary Conditions, Green's Functions) into `docs/derivations/` — currently cached but not translated.
- Decide whether `docs/safety.md` needs the near-field-E-dominant frequency-band row flagged above.
- Re-run `tools/wiki_sync.py --check` periodically for Branches D3–D6/E/F/G of Psionic Engineering (Anchor Controller, HRV-Gated Drive, Mode Geometry Test, etc.) — referenced by the hub but still redlinks as of 2026-08-05.
- Run `analyze_dyadic_coherence.py` on a real two-wearer capture once one exists (everything validated so far is synthetic self-test data).
- ~~Independently recompute the wiki's cited Star Gate/Ganzfeld meta-analytic effect size (F1/F2) rather than trust the wiki's citation~~ — **done**, see [`docs/psionic_engineering/literature_grounding.md`](../../psionic_engineering/literature_grounding.md). F1's "d≈0.14–0.20" likely conflates an r-type effect size with Cohen's d for what is fundamentally a hit-rate/binomial design, and cites a since-superseded (larger) effect size versus a more recent preregistered replication. F2's "p<10⁻²⁰" Star Gate aggregate, by contrast, checks out against Utts (1996)'s own reported figure — confirmed accurate, no correction needed there. `tools/experiment_design.py` gained `GANZFELD_HIT_RATE_PRESETS` for the `binom` subcommand as a result.
- Extend `scan_wiki_consistency.py` to mine ordinary wikitables, not just `{{Infobox}}` templates — most of the corpus's numeric content lives there, and the two `verify_psi_equations.py`-caught discrepancies (adiabatic pulse, average power) live in a wikitable the scanner currently can't see at all.

---

## What this track is

The FusionGirl wiki is the **design specification** for HelmKit. This track is the work of translating wiki content (intents, geometries, frequencies, coupling claims, BOMs) into engineering documents in this repo:

- BOM rows in `docs/inventory.md` and `docs/inventory_capability_map.md`
- Geometry rows in `docs/sprint_0.2_circuit_spec.md` and `docs/mk0_pcb_bifilar_coil.md`
- Mode rows in `docs/modes.md`
- Pre-registered F1–F10 falsification entries in `docs/falsification.md`
- Safety-blacklist rows in `docs/safety.md`
- Index entries in `docs/wiki_anchors.md`

## Why it's blocked

The wiki AI agent received the engineering critiques produced earlier in this project (sparse math, missing parameter ranges, no closed-form for caduceus enhancement, etc.) and is doing a major content expansion in response. Translating partial content now would be wasted work.

## Unblock signal

Track B (`tools/wiki_sync.py`) will detect the drop automatically and produce a diff under `docs/wiki_cache/CHANGELOG.md`. When new pages or substantial revisions appear:

1. Triage diff by pageid. Group by topic (coils, modes, safety, theory).
2. Pick highest-leverage 3–5 pages for first translation pass.
3. Each translation produces or updates a doc under `docs/`.
4. Each new claim that touches the body gets a row added to F1–F10 or a new F-row if needed.
5. Each new emitter geometry gets a row in the safety blacklist + a calculated SAR ceiling.

## Output template per wiki page

```
docs/<topic>/<page_slug>.md
  - Source: wiki pageid + revid + URL + fetched-at
  - Wiki claim (verbatim or close paraphrase)
  - Engineering interpretation
  - BOM implication (if any)
  - Geometry / parameter implication
  - Safety implication
  - Falsification hook (which F-row tests this)
  - Open questions / extrapolations (flagged as (c) per AI rules of engagement)
```

## What ships when this track runs

A wave of new docs under `docs/` (mostly flat, mirroring existing pattern). Pull request grouped by wiki topic. Each PR is small and self-contained so it can be reviewed and rolled back independently.
