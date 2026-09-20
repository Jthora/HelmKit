# Wiki correspondence log

Append-only record of what's been sent to the FusionGirl wiki maintainers and what (if anything) changed upstream afterward. This exists so outreach is an ongoing collaboration record, not a one-off email nobody tracks the outcome of.

**How to check for a response**: run `python3 tools/wiki_sync.py --check` (exit 0 = no tracked page has a new revid since last sync; exit 1 = something changed — run a full `wiki_sync.py` to pull the diff, then check whether the relevant page(s) below were among the changed ones).

---

## Entry 1 — 2026-08-05

- **Report**: [`report_to_wiki_maintainers_2026-08-05.md`](report_to_wiki_maintainers_2026-08-05.md)
- **Sent**: not yet — drafted and reviewed, sending is a manual step for the repo owner (no email capability in this environment).
- **Findings included**: 4 confirmed wiki internal-consistency issues (Bifilar Coil Engineering ×2, Psionic Engineering hub vs. Shepard Tone Synthesis, Smart Composite Fill) + 1 literature-citation cross-check (Star Gate p-value confirmed accurate; Ganzfeld "d≈0.20" citation likely conflates effect-size metrics — see [`literature_grounding.md`](literature_grounding.md)).
- **Pages involved**: `Bifilar Coil Engineering` (revid 12570), `Smart Composite Fill` (revid 12555), `Psionic Engineering` (revid 13195), `Shepard Tone Synthesis` (revid 12571). All confirmed unchanged as of 2026-08-05 via `wiki_sync.py --check`.
- **Response / upstream change observed**: none yet (not sent).

## Entry 3 — 2026-08-06 (Part 2 additions)

- **Report**: "Part 2 additions" appended to [`report_to_wiki_maintainers_2026-08-05.md`](report_to_wiki_maintainers_2026-08-05.md) (still the same still-unsent draft — third round of additions, not a new document).
- **Sent**: not yet.
- **Findings included**: Finding 7 (updated ganzfeld ES=0.088 citation, Tressoldi & Storm 2024 Stage 2 RR), Finding 8 (2020s RNG-PK/precognition null-replication results — Maier & Dechamps 2022, Transparent Psi Project), Finding 9 (the "Effective Physics" taxonomy issue confirmed across 5 pages, `Psi Condensation Threshold` explicitly self-admits its derivation "is not yet done" — recommend recategorization, not disclaimers), Finding 10 (structural argument: non-locality required for ψ's stated cross-brain functions is in direct tension with genuine substrate-derived-field confinement — explains why every derivation attempt stalls), Finding 11 (constructive: setting α=0 collapses the framework cleanly onto real, published CEMI theory, resolving 9/10 without deleting content), Finding 12 (naming flag: "Effective Scalar Waves"/"scalar-wave" language sits adjacent to a real pseudoscience cluster, unrelated to the wiki's actually-legitimate near-field antenna theory), Finding 13 (credit: the running-coupling/β-function treatment on `Renormalization of Psi Theory` is real, correct QFT practice, worth acknowledging even though it doesn't resolve 9/10).
- **Pages involved**: `Psi Field` (revid 13202), `Quantization of the Psi Field`, `Renormalization of Psi Theory` (revid 8455), `Wilson-Cowan Coupled to Psi` (revid 12585), `Psi Condensation Threshold` (revid 13361) — all read via browser-UA fetch, 2026-08-06.
- **Response / upstream change observed**: none yet (not sent). This draft has now accumulated three rounds of findings across two days without being sent — worth deciding whether to send as-is or continue adding.

## Entry 2 — 2026-08-06

- **Report**: Finding 6 appended to [`report_to_wiki_maintainers_2026-08-05.md`](report_to_wiki_maintainers_2026-08-05.md) (same document, not a new one — Entry 1 hasn't been sent yet, so this augments the still-pending draft rather than opening a second thread).
- **Sent**: not yet — same as Entry 1, no email capability, sending is a manual step.
- **Findings included**: a framing/categorization observation, not a numeric bug — `Effective Field Theory of Consciousness` and `5D Action Principle` are read in full and found to postulate ψ's existence rather than derive it from a known substrate, despite being filed under the wiki's "Effective Physics" domain alongside substrate-derived branches (phonons, analogue gravity). Recommended fix: make the epistemic-status framing already present on the `CEMI Field Theory` page (coefficients "empirically open," explicit axion-coupling analogy) equally prominent on the two derivation pages themselves. Full technical backing in [`effective_physics_derivation_audit.md`](effective_physics_derivation_audit.md).
- **Pages involved**: `Effective Field Theory of Consciousness`, `5D Action Principle`, `CEMI Field Theory` (read via browser-UA fetch 2026-08-06; revids not recorded for this entry — informal read, not an API-verified snapshot the way Entry 1's findings were).
- **Response / upstream change observed**: none yet (not sent).

<!--
Template for the next entry:

## Entry N — YYYY-MM-DD

- **Report**: link, or "verbal/informal update to Entry N-1" if not a new document
- **Sent**: date actually sent, or "not yet"
- **Findings included**: one-line summary
- **Pages involved**: title (revid) at time of sending
- **Response / upstream change observed**: what `wiki_sync.py --check` (or a manual page read) showed afterward — did the pages change? did the specific numbers get corrected? silence is also a valid, worth-recording outcome.
-->
