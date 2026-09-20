# Computational psionics toolkit — math verification, experiment design, dyadic coherence

**Status**: v0 landed 2026-08-05; v1 (binomial designs, forced-choice protocol, segment/multi-channel dyadic, corpus-wide wiki scanner) landed the same day after a critique pass; v2 (real literature grounding, Dicke N² scaling test design, confound rejection, forced-choice pilot protocol) landed the same day again under [Track L](../plans/2026-tier1-launch/track-L-psionics-foundational-research.md), after a second critique concluded prior work mostly checked the wiki against itself rather than reality.
**Tools**: [`tools/verify_psi_equations.py`](../../tools/verify_psi_equations.py), [`tools/experiment_design.py`](../../tools/experiment_design.py), [`tools/analyze_dyadic_coherence.py`](../../tools/analyze_dyadic_coherence.py), [`tools/forced_choice_protocol.py`](../../tools/forced_choice_protocol.py), [`tools/scan_wiki_consistency.py`](../../tools/scan_wiki_consistency.py), [`tools/analyze_ambient_confounds.py`](../../tools/analyze_ambient_confounds.py).
**Tests**: `tests/test_verify_psi_equations.py`, `tests/test_experiment_design.py`, `tests/test_analyze_dyadic_coherence.py`, `tests/test_forced_choice_protocol.py`, `tests/test_scan_wiki_consistency.py`, `tests/test_analyze_ambient_confounds.py`.

## Why these three, and why now

This repo's existing biometrics tooling (`tools/analyze_g2.py`, `tools/analyze_capture.py`) is single-subject HRV analysis — real, tested, and useful, but it doesn't engage anything the wiki's own framework claims is distinctively *psionic*. Single-subject RMSSD-rises-under-paced-breathing is standard biofeedback, not a psi-adjacent measurement.

Three gaps stood out after the [Psionic Engineering wiki translation](README.md) as places where software — no new hardware, no wearer risk — could do real work:

1. **The wiki's own math might not be internally consistent.** A 42-page equation-derived engineering discipline is exactly the kind of thing that accumulates copy/paste and unit errors across pages. Nobody had checked.
2. **The falsification framework's own methodological floor (`docs/falsification.md`: pre-registration, 80% power, standard frequentist/Bayesian stats) has no enforcement mechanism.** Nothing computes the N a study needs, or locks an analysis plan before data collection.
3. **Every biometric tool in this repo is single-subject.** The wiki's `Collective Consciousness` claim (field energy scaling as N⁴ with practitioner coherence) is specifically a claim about CROSS-subject coupling. Nothing tests that class of claim.

## 1. `verify_psi_equations.py` — does the wiki's own math check out?

**What it does NOT do**: adjudicate whether the ψ field is real. That's an empirical question outside a math checker's scope.

**What it DOES do**: two independent check families, both stdlib-only (no sympy — see [Design note: why not SymPy](#design-note-why-not-sympy) below).

- **PDE residual checks** (Branch A foundation math): instantiate a claimed closed-form solution on a numerical grid, apply the claimed differential operator via central finite differences, and confirm the residual vanishes only at the claimed parameter value — not just that it's small for any input (which would make the check vacuous). Covers the dispersion relation (ω²=k²+m_eff²) and the Yukawa static solution / coherence length (ψ(r)=-GM/r·e^(-mr)). Both **pass**: the wiki's own foundational math is self-consistent by this test.
- **Worked-example recomputation** (`Bifilar Coil Engineering`, the most numerically concrete page found): re-derive every concrete number on that page from its own stated inputs. Six of seven pass cleanly (E-field peak, the full far-field falloff table, B-field cancellation and ICNIRP margins all reproduce exactly). **Two genuine discrepancies found, both root-caused, not just detected**:
  - The page's claimed 9.7°C adiabatic pulse temperature rise does not follow from its own stated formula and inputs — literal recomputation gives ≈9690°C, roughly 1000× larger. **Root cause identified**: substituting *average* power (P_peak × the page's own 0.1% duty cycle = 20W) for the formula's labeled `P_peak` reproduces 9.69°C almost exactly — the page appears to have used average power where its own formula calls for peak power. Whether the physically-correct answer is the peak-power or average-power version is a real modeling question, left to the wiki maintainers.
  - The page states two different numbers for the same "average pulsed drive power" quantity in two different sections (20 mW in the body text vs. 20 W in its own later sanity-check table, which matches straightforward P_peak×duty_cycle arithmetic) — an internal contradiction, possibly related to the same peak-vs-average mix-up as the first finding.
- A **cross-page citation check**, found while triaging `scan_wiki_consistency.py`'s output: the `Psionic Engineering` hub's Branch D table states the Shepard-tone drive uses carriers at "10, 20, 40 kHz," while `Shepard Tone Synthesis` — the detailed page this summarizes, with load-bearing derivations (FPGA clock division, PZT harmonic subordination) that only work for this specific triple — consistently states 40, 80, 160 kHz. The hub's mention looks like a stale summary that wasn't updated when the detailed page was written.
- A final category, **citation checks**, covers results that are standard textbook physics (the retarded Green's function) or where an "established analog" is presented more tightly than it actually holds (the ψ-impedance-vs-EM-impedance analogy is structurally a reactance, not a lossless-medium impedance — flagged as an overstated analogy, not an error).

Run it: `python3 tools/verify_psi_equations.py` (or `--json`). Exit code 0 iff every check passes without a flag.

### Design note: why not SymPy?

`tools/` has a deliberate stdlib-only discipline (see `analyze_g2.py`'s docstring; `tools/requirements.txt` only has `requests`/`PyYAML`). True symbolic algebra would be easier with SymPy, but numerical PDE-residual verification via finite differences is arguably a *more* independent check than symbolic re-manipulation would be — it doesn't risk mechanically reproducing the same algebra that produced the claim in the first place. If a future check genuinely needs symbolic manipulation (e.g. verifying a multi-step Lagrangian derivation) rather than "does this closed form solve this PDE," that's the point to introduce a scoped `tools/requirements-symbolic.txt` rather than bloat the default install.

## 2. `experiment_design.py` — enforcing the methodological floor

`docs/falsification.md` states the floor every pre-registration must meet: power ≥80%, pre-registered analysis, standard (not "special psi") statistics. This tool makes that mechanically checkable instead of aspirational.

- **`power`**: required N for a target power (or achieved power at a given N), for paired/one-sample/two-sample designs. Normal approximation to the noncentral-t power function — standard for planning, validated against the classic Cohen d=0.5/two-sample textbook answer (~64/group; the tool gives 63). Applied to the wiki's own TML-3 criterion (d≈0.20, the Star Gate-class effect size the framework cites): **required N ≈ 197**, not the N=10 pilot / N=10 replication the wiki's own TML-3 row names. That's a real, immediately actionable finding — the wiki's own pass criterion is underpowered for the effect size it itself cites as the target.
- **`bayes`**: approximate (BIC-based, Wagenmakers 2007 / Masson 2011) Bayes factor from a t-statistic and N, with Jeffreys (1961) verbal interpretation. Explicitly documented as an approximation to the exact Rouder et al. (2009) JZS Bayes factor, not a replacement for it — cross-check against a real implementation (R's `BayesFactor`, JASP) before quoting a number in anything published.
- **`preregister`**: takes a YAML/JSON spec (hypothesis, primary endpoint, effect size, alpha, power, design), computes the required N, and writes a timestamped, SHA-256-hashed lock file. Refuses to overwrite an existing lock — pre-registrations are append-only; a changed plan is a new dated file, not an edit. **Known limitation**: only hashes the study *parameters*, not the analysis code that will run — a post-hoc change to the analysis script itself isn't caught. Fixing that (hashing a pointer to the actual analysis script alongside the spec) is a natural v2.
- **`binom`** (v1 addition): the mean-difference tools above are the wrong test family for the wiki's own F1/F2 citations (Ganzfeld, Star Gate) — those are **forced-choice hit-rate** designs, a proportion test against chance (1/k), not a t-test. `required_n_binomial`/`achieved_power_binomial` (same normal-approximation family as above) and `binomial_bayes_factor` (an **exact** closed-form Beta-Binomial Bayes factor, not an approximation — computed via `math.lgamma`, unlike the t-test path's BIC approximation) cover this design. See `tools/forced_choice_protocol.py` below for the tool built on top of these.
- **`binom --preset`** (v2 addition): `GANZFELD_HIT_RATE_PRESETS` sources real hit rates from [`literature_grounding.md`](literature_grounding.md) — e.g. `ganzfeld-storm2010-optimistic` (30.1% vs. 25% chance) — instead of a hand-typed number derived from the wiki's own (likely unit-conflated) "d≈0.20" citation. Running the numbers honestly is sobering: even the *optimistic* preset needs **587 trials** for 80% power, and the more conservative one needs **3736** — a real, load-bearing finding about what a properly-powered forced-choice study actually requires, not achievable in a casual pilot (see `docs/protocols/forced_choice_pilot.md`'s §6).
- **`dicke-scaling`** (v2 addition): `docs/mk_ladder.md`'s Mk3.0 gate names a specific test — "F7 + 2-emitter Dicke superradiance N² scaling test" — that nothing in the toolkit addressed until now. `dicke_scaling_effect_size`/`required_replicates_for_dicke_test` translate the physical claim (N coherent emitters give intensity ∝N², vs. ∝N for N independent ones — the textbook Dicke 1954 result) into a standard one-sample power-analysis problem: the two hypotheses' predicted values at N=2 diverge by a fixed amount, and that gap divided by the assumed measurement noise is exactly a Cohen's-d-equivalent effect size, so this reuses `required_n` rather than inventing new statistics. This is test-design math only — running it for real stays gated behind Mk0.5→Mk2.5 per the ladder's own no-skipping rule; nothing in this repo schedules that run.

Run it: `python3 tools/experiment_design.py power --d 0.20 --design paired`, `... bayes --t 2.5 --n 20`, `... binom --p0 0.25 --preset ganzfeld-storm2010-optimistic`, `... dicke-scaling --noise-sd 2.0`, `... preregister --spec spec.yml --out docs/protocols/preregistrations/2026-08-05_mode_geometry_test.json`.

## 3. `analyze_dyadic_coherence.py` — is there synchrony between two wearers beyond chance?

Extends the RR-interval loading in `analyze_g2.py` from single-subject metrics to cross-subject synchrony:

- **Lagged cross-correlation** — Pearson r between two subjects' resampled RR streams at every lag in a window, reporting the peak and its lag.
- **Cross-recurrence quantification (CRQA)** — recurrence rate and determinism from a distance-thresholded cross-recurrence plot (Marwan et al. 2007), a standard method in dyadic physiological-coupling research.
- **Surrogate significance testing** — circular time-shift surrogates (Theiler et al. 1992): shift one subject's series by a random circular offset (preserving that subject's own autocorrelation while destroying true cross-subject alignment), recompute the statistic hundreds of times, and report an empirical p-value against that null distribution.

**The surrogate test is not optional decoration.** Two people breathing in the same room, or both entrained to the same background audio, will show real cross-correlation for entirely mundane reasons. A raw correlation number without a null distribution is not evidence of anything unusual. The tool's own report text says so explicitly and points at `docs/falsification.md`'s sham-control requirements before any psi-adjacent read of a positive result.

One methodological subtlety surfaced while building this and worth keeping in mind for future use: circular-shift surrogates lose power against a *periodic* shared signal (e.g. both subjects entrained to the same fixed-frequency breathing pacer) — shifting a periodic signal by multiples related to its own period leaves it correlated with the original at many shifts, not just zero. The self-test validation deliberately uses an *aperiodic* shared component (a smoothed random walk) for this reason; a real paced-breathing confound would need a different surrogate scheme (e.g. block-shuffling separated by more than one period) to be properly nulled out.

Run it: `python3 tools/analyze_dyadic_coherence.py --a subjectA.ndjson --b subjectB.ndjson`, or `--self-test correlated` / `--self-test independent` to see it on synthetic data.

**v1 additions** (after a critique pass identified these as the two biggest comprehensiveness gaps):

- **Segment-aware analysis** (`analyze_dyadic_by_segment`, `--segmented` CLI flag). Reuses `analyze_g2.py`'s `Segment`/`make_default_segments` so the same baseline/paced/recovery windows used for single-subject G2 analysis apply here too. This is what makes "did synchrony rise specifically during the intervention window" askable, instead of only "was there synchrony somewhere in the whole session" — a materially weaker, more confound-prone claim (a stable trait-level correlation between two calm — or two stressed — people is a far more mundane explanation than a transient, intervention-locked rise). `segment_contrast()` computes the delta between two named segments' metrics, but honestly flags that the delta itself is descriptive only — it has not been surrogate-tested (that needs a block-permutation scheme across the segment boundary, not yet implemented); use each segment's own p-value for a rigorous claim.
- **Generic scalar-channel support** (`ScalarSample`, `load_scalar_channel_from_ndjson`). The v0 version only accepted RR-interval data. GSR and temperature channels already exist in the Mk0.5 sensor roster and may show cross-subject coupling that HRV does not. The new loader is deliberately separate from `load_rr_from_ndjson`, not a parameterization of it — the RR loader's "v≤0 is a first-peak sentinel" convention does not apply to a generic scalar channel (a GSR reading of exactly 0 is a real observation).

## `forced_choice_protocol.py` — classic Ganzfeld/Star-Gate-style hit-rate testing

The wiki's F1/F2 falsifiers cite forced-choice designs specifically — a subject guesses which of *k* alternatives a random-number generator picked, repeated over many trials. This needs **zero HelmKit hardware**: a target sequence, an RNG, a way to record guesses, and correct statistics (the `binom` additions to `experiment_design.py` above).

Three historically-significant failure modes of this exact paradigm, each addressed directly:

1. **Post-hoc target selection / "the experimenter misremembers."** `generate` produces the full target sequence up front via `random.SystemRandom` (the OS CSPRNG, not a seeded PRNG) and computes a SHA-256 **commitment hash** you publish *before* the session. `verify-commitment` lets anyone later confirm the revealed target file matches what was committed.
2. **Wrong statistics for the design.** `score` uses `one_proportion_z_test` (frequentist) and the exact Beta-Binomial `binomial_bayes_factor` — not a t-test.
3. **Silent optional stopping.** `score` reports the result for exactly the N in the targets file. Sequential designs with proper stopping boundaries are explicitly **not implemented** — see below.

What this does NOT do: conduct a live, blinded, in-person session (sensory shielding, experimenter blinding, timing) — that's a physical-protocol question for the wiki's own `Sham Control Design` page and `docs/falsification.md`, not a software one. Only target generation/commitment and post-hoc scoring are covered.

Run it: `python3 tools/forced_choice_protocol.py plan --k 4 --p1 0.35`, `... generate --n 200 --k 4 --out targets.json`, `... score --targets targets.json --responses responses.json`, or `... self-test --mode psi` to see it on synthetic data.

## `scan_wiki_consistency.py` — corpus-wide numeric-claim scanner

`verify_psi_equations.py` hand-checking one page found two confirmed errors; a human re-reading a second page found a third five minutes later. This generalizes the technique across all ~108 cached wiki pages instead of one at a time.

Two check families, both against `docs/wiki_cache/*.wikitext`:

- **Cross-page label matching** (`confidence: high`). Every wiki Infobox is structured `{{Infobox | label9 = X | data9 = Y ...}}` key/value pairs — this extracts every (label, value) across the whole corpus and flags the same label appearing on different pages with numerically different values. **Blocks the pre-commit hook by default** (the only check in this tool that does). Found zero hits on the current corpus — either a genuinely clean result, or (more likely, given how page-specific infobox phrasing tends to be) a check that just hasn't had a chance to fire yet; it should matter more as similar device pages accumulate.
- **Within-page keyword-proximity matching** (`confidence: low`, heuristic, non-blocking by default). For each infobox claim, searches the same page for other same-unit numbers near the label's most distinctive keyword, scoped to the same paragraph/bullet/table-row/sentence chunk (an earlier fixed-character-window version was tried against the real corpus first and had a ~100% false-positive rate — e.g. flagging a 0.2mm trace *gap* against an unrelated 100mm distance from a falloff table eleven lines later, just because both mentioned "mm" somewhere near the word "gap"; chunk-scoping cut that down substantially but did not eliminate it). **This check family found the real BST-tunability discrepancy** (infobox states ≥70%, prose elsewhere states ≥35% — now in `tools/wiki_consistency_known_issues.yml`) but also produces genuine noise (e.g. flagging a page's trace *gap* dimension against its trace *width* dimension, which are legitimately different numbers, not a contradiction). Every result is explicitly labeled low-confidence and the tool's own report says so; **read the actual page before trusting any single-page hit.**

A real regex bug was caught by the test suite while building this: the unit-token regex required a trailing `\b` word boundary, which never matches after non-word-character units like `%` and `Ω` followed by whitespace — silently dropping almost every percentage claim in the corpus (including the exact BST-tunability example this tool was built to catch) until a test with a `%`-based fixture failed and exposed it.

Known, already-triaged findings are suppressed via `tools/wiki_consistency_known_issues.yml` (mirrors the existing `tools/known_missing.yml` pattern from `check_wiki_urls.py`) — this is for CONFIRMED issues a human has read and understood, not a way to bulk-silence low-confidence noise.

Run it: `python3 tools/scan_wiki_consistency.py` (or `--json`). Wired into `.pre-commit-config.yaml`, triggered when `docs/wiki_cache/*.wikitext` changes.

## `analyze_ambient_confounds.py` — is a "significant" result actually just a shared external stimulus? (v2)

`analyze_dyadic_coherence.py`'s surrogate test rules out *chance*; it says nothing about whether two subjects' correlated biosignals were driven by a shared ambient cause (an RF transient, an HVAC cycle, a shared audible click) rather than anything dyadic or psi-adjacent. This tool checks that directly: it correlates an ambient reference channel (RF spectrum survey, magnetometer/gradiometer reading — real hardware for this already exists per `docs/inventory.md`) against a biometric target channel, using the exact same surrogate-tested cross-correlation/CRQA machinery as `analyze_dyadic_coherence.py`'s `analyze_dyadic` — imported and reused directly, not reimplemented (per this session's own retrospective on premature infrastructure: no new shared module was extracted, since a second real caller for `analyze_dyadic` already existed).

**Safety-relevant design decision**: this tool contains **no SDR/radio invocation code whatsoever** — not "always receive-only," literally no mechanism to run a subprocess at all (verified by a dedicated test that inspects the source file itself, not just its runtime behavior). `docs/inventory.md`'s HackRF One is transmit-capable; rather than adding hardware-driving code here and then trying to constrain it to RX-only calls, capture is treated as a separate, human-operated step entirely outside this tool's scope — it only ever analyzes an already-captured NDJSON log.

No microphone/audio confound channel exists in current inventory — documented as a real, named gap rather than silently unsupported; any scalar NDJSON channel works once one exists.

Run it: `python3 tools/analyze_ambient_confounds.py --ambient rf_survey.ndjson --ambient-channel rf-power-dbm --target session.ndjson --target-channel ppg-rr`, or `--self-test confounded` / `--self-test clean`.

## What this does not do (yet)

- Transfer entropy / directional coupling between dyadic subjects — noted as a natural extension, not implemented.
- ~~Meta-analysis re-computation of the wiki's cited effect sizes~~ — **done**, see [`literature_grounding.md`](literature_grounding.md).
- Geomagnetic/environmental correlation pulls (Persinger-style: does ambient Kp-index correlate with session-level outcomes across many sessions) — still a standalone, unbuilt idea, distinct from `analyze_ambient_confounds.py`'s narrower within-session confound check.
- Sequential/optional-stopping-corrected designs for the forced-choice protocol.
- ~~Confound instrumentation for `analyze_dyadic_coherence.py`~~ — **done**, see `analyze_ambient_confounds.py` above.
- N-way (not just pairwise) group-coherence analysis — the wiki's N⁴ scaling claim is fundamentally about groups of 3+, which pairwise correlation cannot test. The new Dicke-scaling test design (above) covers the *specific* 2-emitter N² case the Mk3.0 gate names, but not a general N-way extension.
- ~~Dicke N² scaling test design~~ — **done**, see `dicke-scaling` above.
- `scan_wiki_consistency.py`'s Infobox-only extraction — ordinary wikitables (not `{{Infobox}}` templates) carry a great deal of the corpus's numeric content and are not yet mined at all; the two discrepancies `verify_psi_equations.py` found by formula recomputation (adiabatic pulse, average power) live in a wikitable, not an infobox, and this scanner does not independently catch either of them.

## Reporting findings upstream

[`report_to_wiki_maintainers_2026-08-05.md`](report_to_wiki_maintainers_2026-08-05.md) consolidates five findings (four wiki internal-consistency issues plus one literature-citation cross-check — one part of which confirmed a wiki citation as accurate, not just found problems) into a single document intended for the AI maintaining the wiki. It's drafted and ready for review — this repo has no email-sending capability, so actually sending it is a manual step. Before the v2 update, it was re-verified against the live wiki once more (`tools/wiki_sync.py --check` — 0 new/revised) to confirm none of the pages involved had already changed. [`wiki_correspondence_log.md`](wiki_correspondence_log.md) tracks what's been sent and what (if anything) changes upstream afterward, as an ongoing record rather than a one-off.

## Cross-references

- [`README.md`](README.md) — the wiki translation index this toolkit responds to.
- [`bifilar_coil_engineering.md`](bifilar_coil_engineering.md) — the translation doc whose worked-example arithmetic `verify_psi_equations.py` checks.
- [`literature_grounding.md`](literature_grounding.md) — real primary-source effect sizes behind the `binom --preset` values.
- [`../falsification.md`](../falsification.md) — the F1–F11 framework `experiment_design.py` mechanically enforces the methodological floor of.
- [`../mk_ladder.md`](../mk_ladder.md) — the Mk3.0 gate `dicke-scaling` targets.
- [`../protocols/forced_choice_pilot.md`](../protocols/forced_choice_pilot.md) — the prepared-not-run pilot protocol built on `forced_choice_protocol.py` + the literature-grounded presets.
- [`../plans/2026-tier1-launch/track-A-wiki-translation.md`](../plans/2026-tier1-launch/track-A-wiki-translation.md) — Track A status.
- [`../plans/2026-tier1-launch/track-L-psionics-foundational-research.md`](../plans/2026-tier1-launch/track-L-psionics-foundational-research.md) — Track L status (this doc's v2 work).
- [`../../tools/wiki_consistency_known_issues.yml`](../../tools/wiki_consistency_known_issues.yml) — triaged findings from `scan_wiki_consistency.py`.
