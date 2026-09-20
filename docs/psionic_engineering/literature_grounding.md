# Literature grounding — real primary-source effect sizes vs. wiki citations

**Status**: v0, 2026-08-05.
**Closes**: the "independently recompute the wiki's cited Star Gate/Ganzfeld meta-analytic effect size" backlog item in [`../plans/2026-tier1-launch/track-A-wiki-translation.md`](../plans/2026-tier1-launch/track-A-wiki-translation.md).

## Why this doc exists

`docs/falsification.md`'s F1/F2 rows and the wiki's `Psionic Engineering` hub's Falsifiability Framework section both cite specific numbers from real parapsychology literature (Storm et al. 2010, Cardeña 2018, Utts 1996 / the Star Gate program). Prior work this session checked the wiki *against itself* — self-consistency, not truth. This doc checks the wiki's citations *against the actual primary/secondary sources*, via web search, and records what holds up, what doesn't, and what's genuinely unresolved. This is real-world grounding, not wiki QA — the distinction matters (see the project's own self-critique on this point, recorded in memory as `project_psi_computational_toolkit`).

Everything below was found via web search on 2026-08-05, not by fetching and reading the full primary PDFs cover-to-cover. Treat this as a strong first pass, not a systematic review — flagged explicitly wherever confidence is lower.

## Finding 1 (correction owed to our own doc): F1's "d≈0.14–0.20" likely applies the wrong effect-size metric

`docs/falsification.md`'s F1 row states: *"Storm et al. 2010 / Cardeña 2018 aggregate d ≈ 0.14–0.20."*

What the primary literature actually reports:

- **Storm, Tressoldi & Di Risio (2010)**, "Meta-analysis of free-response studies, 1992–2008," *Psychological Bulletin* (or similar venue) — a homogeneous set of 29 ganzfeld studies (1997–2008) yielded a mean **effect size r = 0.142** (Stouffer Z=5.48, p=2.13×10⁻⁸), corresponding to hit rates of 27–30.1% against a 25% chance baseline (4-alternative forced choice). ([source PDF](https://www.aiprinc.org/documents/para-ac02_Storm_et_al_2010a_Meta_Analysis.pdf), [PubMed](https://pubmed.ncbi.nlm.nih.gov/20565164/))
- A more recent **preregistered replication/meta-analysis (~2020–2021, "Stage 2 Registered Report: Anomalous perception in a Ganzfeld condition — a meta-analysis of more than 40 years")** reports a notably *smaller* effect, **r ≈ 0.08 (95% CI 0.04–0.12)**, across studies from 1974–2020. ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11134153/))

Two separate issues with F1's "d≈0.14–0.20":

1. **Unit mismatch.** These meta-analyses report an *r*-type effect size, not Cohen's *d*. r and d are not numerically interchangeable: converting properly (d = 2r/√(1−r²)), Storm 2010's r=0.142 → **d≈0.287**, not 0.14. The wiki's/our own doc's "0.14" appears to be Storm's r value relabeled as d without conversion.
2. **Stale estimate.** Even setting the unit issue aside, the more recent preregistered meta-analysis (r≈0.08, d≈0.16) is meaningfully smaller than the 2010 figure — a common and expected pattern when a field moves from exploratory studies toward preregistration (reduces the degrees of freedom available for inflating effect sizes). Using the older, larger number as a design target risks planning a study that's underpowered for the effect size actually likely to replicate.
3. **Wrong test family, independent of the above.** Ganzfeld studies are fundamentally 4-alternative forced-choice hit-rate designs — a **proportion/binomial** effect (hit rate vs. 25% chance), not a mean-difference effect. Framing this as "Cohen's d" at all reaches for the wrong statistical family. This directly matches why `tools/experiment_design.py` needed binomial power/Bayes-factor functions (added earlier this session) rather than only mean-difference ones — and why the preset added below is a **hit-rate preset for the `binom` subcommand**, not a `d` preset for `power`.

**Recommendation for `docs/falsification.md`**: F1's status column should read something closer to *"Storm et al. 2010: r≈0.142 (29 studies, 1997–2008); more recent preregistered work (2020–2021) finds a smaller r≈0.08. Hit-rate design, not a d-based one — see `literature_grounding.md`."* Not applied to that file in this pass; flagged here for a deliberate, separate doc-fix commit.

I have **not** independently traced exactly which specific Cardeña (2018) figure the falsification.md row's "0.14–0.20" range was meant to include — Cardeña's 2018 *American Psychologist* review is a survey of several meta-analyses rather than a single new effect-size computation, and I did not find a distinct "Cardeña reports d=X" figure separate from the ganzfeld meta-analyses above. Flagged as lower-confidence; a closer read of the actual Cardeña paper would resolve this.

## Finding 2 (citation confirmed accurate): F2 / the wiki's "Star Gate ... p<10⁻²⁰" checks out

The `Psionic Engineering` hub's Falsifiability Framework section cites *"prior from existing anomalous cognition literature (Star Gate review: combined d ≈ 0.20, p < 10⁻²⁰)."* Unlike Finding 1, the aggregate p-value part of this citation is **independently confirmed**: Jessica Utts' 1996 assessment of the U.S. government Star Gate program reported *"the overall probability of observing the results if chance alone was operating to be astronomically small (p = 10×10⁻²⁰)"* across approximately 27,000 trials conducted at SRI and SAIC between 1973 and 1993. ([Psi Encyclopedia summary](https://psi-encyclopedia.spr.ac.uk/articles/jessica-utts))

Component breakdowns from the same assessment (SAIC-specific, a subset of the full aggregate) show much more modest, individually-unremarkable figures — combined effect size 0.124 (p=.04) across all SAIC conditions/viewers, 0.248 (p=.0073) for static targets alone, 0.00 (p=.50) for dynamic targets ([ResearchGate summary](https://www.researchgate.net/publication/250509613_An_Assessment_of_the_Evidence_for_Psychic_Functioning), [primary PDF](https://ics.uci.edu/~jutts/air.pdf)) — these are NOT in tension with the aggregate p<10⁻²⁰ figure; they are individual sub-experiment results feeding into a much larger combined analysis across the program's full ~20-year trial history, not a contradiction of it.

**No correction needed here** — this is a case where checking against reality confirmed the wiki's citation rather than finding an error. Worth recording precisely for that reason: not every citation-check should be expected to turn up a problem, and this doc would be dishonest if it only ever reported bad news.

## What this changes in the toolkit

`tools/experiment_design.py` gains a `GANZFELD_HIT_RATE_PRESETS` dict (see its module docstring for the exact values and sourcing) usable via `--preset` on the `binom` subcommand — e.g. `experiment_design.py binom --preset ganzfeld-storm2010-optimistic --p0 0.25 --power 0.80` for required-N planning. No preset was added for the `power`/`bayes` (mean-difference d) subcommands: the real literature grounding this doc found is a hit-rate literature, and fabricating a d-equivalent preset for it would repeat the exact unit-conflation error this doc exists to fix. A future HRV/RMSSD-specific d preset would need its own literature grounding (a genuine paired-difference biofeedback effect size), not a repurposed ganzfeld number.

## Open items (not resolved here)

- The exact hit-rate (not just r) implied by the newer ~2020–2021 preregistered ganzfeld meta-analysis wasn't found via search — needed before it can become a preset. Recommend fetching the full paper directly if this matters for a near-term study design decision.
- Which specific number(s) from Cardeña (2018) the wiki's/our F1 row intended to cite.
- This is two citations checked, not a systematic literature review. Treat the toolkit's presets as a first, defensible pass — not a finished bibliography.

## Finding 3 (2026-08-06 addendum) — the 2020s preregistered-replication track record, across paradigms this doc hadn't checked yet

A broader literature pass (background research agent, web-search-based — same confidence caveat as everything above: not full primary-source reads) went past ganzfeld into RNG-PK and precognition specifically, since those are the other two paradigms `docs/falsification.md`'s wiki-canonical criteria touch on indirectly. The picture is materially more sobering than the ganzfeld-only checks above, and it would be dishonest to leave this project's grounding docs without it.

**Ganzfeld — resolves an open item above.** The exact figure the first open item asked for: **Tressoldi & Storm's Stage 2 Registered Report** (*F1000Research*, 2024) — the actual preregistered gold-standard format, not just a newer meta-analysis — covers the 1974–2020 literature and reports **ES = 0.088 (95% CI 0.04–0.13)**, passing four separate publication-bias tests with no decline over time. This is now the best available number, and it's what `docs/falsification.md`'s F1 row has been updated to cite (see the "Corrected 2026-08-06" note there) in place of the unit-conflated "d≈0.14–0.20."

**RNG-PK — the field's own most rigorous recent tests find *against* the effect.** The 1988 US National Research Council review already concluded no convincing evidence, a verdict never overturned. Bösch, Steinkamp & Boller's 2006 meta-analysis (*Psychological Bulletin*, 380 studies) found a significant-but-tiny effect that tracked with funnel-plot asymmetry — the statistical signature of publication bias, not a real effect. The tri-lab PEAR/Giessen/Freiburg replication (Jahn et al. 2000, *JSE*), using PEAR's own protocols, **failed on its primary measure**. Most tellingly: **Maier & Dechamps (2022)**, a preregistered exact replication using a quantum-RNG dataset (n=12,254), found, after error-correction, **strong evidence against** the original correlational micro-PK effect. A related preregistered study claiming Bayesian evidence for micro-PK failed to reproduce under stricter reanalysis. The Global Consciousness Project's own lead researcher (Bancel, *Explore*, 2017) has separately suggested its ~7σ cumulative result may trace to the pool of people directly engaged with the experiment rather than a genuine global effect — an internal critique from within the GCP program, not an external skeptic's.

**Precognition — a large, well-designed, multi-lab replication program, consistently null.** Multiple preregistered attempts to replicate Bem's (2011) precognition paradigm have failed (Maier et al. 2020, Schlitz et al. 2021). The **Transparent Psi Project** — a large, ~30-co-author, preregistered confirmatory replication (*Royal Society Open Science*) of Bem's erotic-stimuli-detection paradigm specifically — found no evidence for psi. A 2024/2025 follow-up under the same project's methodology ran three further replication studies totaling **26,483 participants and 420,472 trials**. Also null.

**What this means for this project's grounding, stated plainly**: the pattern across all three paradigms checked so far is the same shape — real, published, nominally-positive meta-analytic effects that shrink or disappear under the field's own most rigorous, best-powered, preregistered recent tests. Ganzfeld is the least-bad case (a small but real, bias-test-passing effect survives at ES=0.088); RNG-PK and precognition specifically do not survive the best available 2020s tests. This project's stated discipline has always been to report null and positive findings with equal rigor — this is exactly that kind of finding, and it belongs in the grounding record even though it's not the news anyone building this project would prefer to find.

**Not yet done**: cross-paradigm umbrella reviews more recent than Tressoldi & Storm's 2021 "Anomalous Cognition" umbrella review weren't found — no 2023–2026 comprehensive meta-meta-analysis spanning all paradigms currently exists in the literature searched. This finding is a synthesis of the best single-paradigm evidence found, not a formal meta-meta-analysis of its own.
