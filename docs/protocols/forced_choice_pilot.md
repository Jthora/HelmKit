# Forced-Choice Pilot Protocol (software-only, Tier 1)

- **Status**: `v0` — protocol and blinding procedure specified; **not yet run**.
- **Gate**: this is a TML-3-adjacent pilot in spirit (first contact with the ψ hypothesis, per the wiki's own TML ladder) but is **not** gated to any HelmKit Mk rung — it needs zero HelmKit hardware. Tier 1 of the "real data acquisition" workstream in `docs/psionic_engineering/computational_toolkit.md`. Tiers 2/3 (real single-subject and dyadic HRV capture) are separate, hardware-gated protocols and are **not** covered here.
- **What this validates**: whether a human subject's forced-choice guesses against a hash-committed random target sequence deviate from chance, using `tools/forced_choice_protocol.py` and the literature-grounded presets in `tools/experiment_design.py` (see `docs/psionic_engineering/literature_grounding.md`).

This is **not** a definitive test of anything. It is a first real empirical data point, run once, small, informally powered relative to what the real literature says is needed (see §6) — the point is to have run something real, honestly reported, rather than to have prepared for something real indefinitely.

---

## 1. Equipment

- **Subject's own machine**: a terminal with Python 3.10+ and this repo checked out, able to run `tools/forced_choice_protocol.py` and `tools/experiment_design.py`. No HelmKit hardware, no sensors.
- **A way to record guesses privately**: a piece of paper, a private note, or a second terminal session the AI assistant does not see — anything that lets the subject log N guesses over the session without those guesses (or the targets) appearing in the conversation with the AI before scoring.
- **Timer** (optional): if trials are meant to be spaced out (e.g. one per minute, or one per "focus" attempt) rather than run back-to-back.

No AI-side equipment is needed for the guessing phase by design — see §3.

---

## 2. Protocol

| Step | Who | Action |
|------|-----|--------|
| 1. Plan | subject or AI, together | Decide k (number of alternatives) and N (trial count) — see §6 for what N a literature-grounded design actually calls for vs. what's realistic for a first pilot. |
| 2. Generate | **subject, alone** | Subject runs `python3 tools/forced_choice_protocol.py generate --n <N> --k <k> --out <path>` **on their own machine**, without pasting the command's output into the AI conversation except the printed `commitment_sha256` line. |
| 3. Publish commitment | subject | The `commitment_sha256` value (and only that value) may be shared with the AI or written down anywhere, before any guessing starts. This is the pre-registration lock — it proves the target sequence existed before guessing began, without revealing it. |
| 4. Guess | **subject, alone** | Subject makes N guesses, by whatever method the pilot is meant to test (calm/meditative attempt, casual guessing, etc.), recording each guess privately (§1). **Do not** open or read the targets file during this step. |
| 5. Score | subject, alone or with AI | Subject runs `python3 tools/forced_choice_protocol.py score --targets <path> --responses <responses.json>` themselves, or shares both files with the AI **only after guessing is complete** for the AI to run scoring. |
| 6. Verify | AI or subject | Run `verify-commitment` against the originally-published hash to confirm the targets file wasn't altered after the fact. |
| 7. Report | AI | Report the full `score` output verbatim — hits, hit rate, z, p-value, Bayes factor — regardless of the result. |

---

## 3. The blinding procedure (read this before step 2)

This is the one part of the protocol that actually matters methodologically, because the "experimenter" here is an AI assistant embedded in the same conversation as the subject, which is a genuinely unusual setup relative to a normal two-person blinded trial.

**Rule**: the AI must not see the contents of the targets file, or the subject's individual guesses, before the subject has finished guessing and requests scoring.

Concretely:
- When the subject runs `generate`, they share **only** the `commitment_sha256` line of the output, not the full terminal output, not the targets file's contents.
- The subject does not narrate individual guesses to the AI during the guessing phase ("I think it's a circle," etc.) — that would let the AI infer information about the target sequence's structure across trials even without seeing the literal file.
- If the AI is asked to help design or troubleshoot the tooling *during* an active guessing session, that's fine (the tooling itself doesn't depend on the target values), but the conversation should not include the targets or the running tally of hits.
- Only at step 5 does the AI see anything result-shaped, and only in aggregate (the `score` command's output), not the raw target-vs-guess pairing beyond what the score report itself includes.

This isn't foolproof (a sufficiently determined subject and AI in the same conversation could subvert it), but it's a real, workable blind for an honest pilot, and it costs nothing to follow.

---

## 4. Data layout

One session = one directory under `captures/` (same top-level convention as [`g2_hrv_validation.md`](g2_hrv_validation.md)):

```
captures/
└── 20260806T090000Z_forcedchoice_op-jt/
    ├── targets.json          # sealed target file (kept private until scoring)
    ├── responses.json        # subject's guesses, JSON list of integers
    ├── commitment.txt        # the published commitment_sha256, saved BEFORE guessing
    ├── score_report.json     # output of `forced_choice_protocol.py score --json`
    └── notes.md              # free-form: method used, conditions, subjective notes
```

`commitment.txt` should be the first file written chronologically (right after `generate`, before any guessing) — its file modification time is informal evidence, alongside the hash itself, that the commitment predates the guesses.

---

## 5. Blinded operator notes

Same spirit as G2 §4 — before looking at the score, the subject writes down (in `notes.md`):

- **Method (free text)**: what they actually did to try to influence guesses (nothing, meditation, a specific technique, pure random guessing as a null-condition run, etc.).
- **Confidence (1–5)**: how confident the subject felt during the session that they were doing better than chance.
- **Conditions**: time of day, any relevant state (tired, rushed, calm).

This exists for the same reason G2's does: to catch "I could tell it wasn't working" or "I felt unusually locked in" before the numbers can bias the write-up.

---

## 6. What N actually needs to be

`tools/experiment_design.py`'s `binom` subcommand, using the literature-grounded presets from `docs/psionic_engineering/literature_grounding.md` (not the wiki's own citation), gives an honest answer:

```
$ python3 tools/experiment_design.py binom --p0 0.25 --preset ganzfeld-storm2010-optimistic
required N = 587 trials   # optimistic, older meta-analytic hit rate (30.1%)

$ python3 tools/experiment_design.py binom --p0 0.25 --preset ganzfeld-storm2010-conservative
required N = 3736 trials  # more conservative subset (27%)
```

Neither of these is a realistic single-sitting pilot trial count. **This protocol does not pretend otherwise.** A first pilot run at, say, N=20–50 trials is not adequately powered to detect an effect of this size — it exists to produce one real, honestly-reported data point and exercise the full pipeline (commitment, blinding, scoring, Bayes factor reporting) end to end, not to draw a confident conclusion. Report the actual Bayes factor from `score` and its Jeffreys-scale interpretation (`tools/experiment_design.py`'s `interpret_bayes_factor`) rather than treating a small-N null or positive result as decisive either way.

---

## 7. Pre-flight checklist

- [ ] N and k decided and written into `notes.md` before `generate` is run.
- [ ] `generate` was run on the subject's own machine, not pasted output-first into the AI conversation.
- [ ] Only `commitment_sha256` was shared/published before guessing began.
- [ ] `commitment.txt` exists and its timestamp predates the guessing session.
- [ ] Subject has a private method for recording guesses that doesn't involve narrating them to the AI mid-session.

---

## 8. Failure modes and remediation

| Failure mode | Symptom | Remediation |
|---|---|---|
| Targets file pasted into conversation before scoring | AI has seen target values ahead of guessing | Session is no longer blinded — discard and re-run with a fresh `generate`. |
| Guesses narrated live | AI can infer structure across trials before scoring | Same as above — discard and re-run. |
| Commitment not published before guessing | No verifiable proof the sequence predates the guesses | Not fatal to running the session, but weakens it — note this explicitly in `notes.md` rather than silently treating it as equivalent to a properly-committed run. |
| `verify-commitment` reports MISMATCH | Targets file was altered after commitment (accidentally or otherwise) | Do not score or report this session's result as valid. Investigate before re-running. |
| Subject stops partway through planned N | Fewer trials than planned | Score exactly what was collected; report the actual N, don't pad or extrapolate. |

---

## 9. Reporting

Every session's `score_report.json` plus `notes.md` gets committed under `docs/field-notes/` (mirroring G2's `docs/field-notes/volume-1/g2_sessions/` convention) so the result — whatever it is — is part of the project record, not lost on a laptop. Report the result **regardless of outcome**: a null result at low N is still useful data (and is, honestly, the likely outcome at this N — see §6).

---

## 10. What this protocol does **not** establish

- That psionics is real or unreal. A single small-N pilot cannot answer that in either direction — see §6's power numbers.
- Sensory shielding or physical isolation of subject from target — this is a pure information-theoretic (no-sensory-channel) forced-choice design; it does not address any claim requiring physical proximity or biological coupling (that's Tiers 2/3, hardware-gated, not this protocol).
- Freedom from experimenter effects beyond the specific blinding procedure in §3 — a more adversarial or higher-stakes test would need independent third-party target generation, which this protocol does not provide.
- A pass/fail gate of any kind. There is no "this device passes" analog here — only a reported effect size, p-value, and Bayes factor, honestly interpreted at whatever N was actually run.
