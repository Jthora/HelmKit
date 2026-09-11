# tools/

Repo-root tools for HelmKit. Each tool ships with a top-of-file docstring pointing back to its design doc under [`../docs/tools/`](../docs/tools/README.md) or [`../docs/plans/`](../docs/plans/README.md).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/requirements.txt
```

The analysis tools and their tests need only the standard library. Run the suite with the stdlib runner (pytest is
optional and not required):

```bash
python3 -m unittest discover -s tests -t .
```

CI runs the same command on every push that touches `tools/`, `tests/` or the firmware's host scripts
(`.github/workflows/host-tools.yml`).

## Tools

- `wiki_sync.py` — pull tracked FusionGirl wiki pages into `docs/wiki_cache/`. See [`../docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md`](../docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md).
- `verify_psi_equations.py` — independent numerical check of the wiki's Psionic Engineering master-equation math and worked examples. See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
- `experiment_design.py` — power analysis, approximate Bayes factors, and pre-registration locking for F1–F11/TML falsification work. See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
- `analyze_dyadic_coherence.py` — cross-subject RR-interval (or any scalar channel) synchrony analysis with surrogate significance testing, segment-aware (baseline/paced/anchor) analysis. See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
- `forced_choice_protocol.py` — classic forced-choice/RNG-deviation psi protocol: hash-committed target generation and Bayesian/frequentist scoring. See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
- `scan_wiki_consistency.py` — scans `docs/wiki_cache/*.wikitext` for contradictory numeric claims (cross-page and within-page). See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
- `stabilizer_field_model.py` — Biot–Savart / vector-potential field model of the disk's bifilar pancake coil against the tissue screening factor and the ICNIRP 2010/2020 limits (aiding vs opposing connection, lumped L/C/SRF). See [`../docs/psionic_engineering/stabilizer_derivation.md`](../docs/psionic_engineering/stabilizer_derivation.md).
- `capture_service.py` — the log sink (Track N, N-H1 / N-L3): serial NDJSON to one file per boot with `t_wallclock`, heartbeat acknowledgements (`~`), reconnects, a rejects file and a `sessions.json` index; `--replay-fixture` runs it offline. See [`../docs/plans/2026-tier1-launch/track-N-capability-robustness.md`](../docs/plans/2026-tier1-launch/track-N-capability-robustness.md).
- `replay_equivalence.py` — firmware-vs-host equivalence on one capture (Track N gate N-G6): breathing, SCR and mode transitions from the helm against the host references in `analyze_combat_session.py` on the same raw streams; `rr` when raw PPG is present.
- `analyze_combat_session.py` — Track M host-side reference for the combat trim's adhesive-free sensing: per-round coarse HR with the two-source agreement rule, RMSSD only in still rest windows, thermal breathing rate and nose-tip arousal slope, forehead EDA response rate with the sweat rule, impacts, intrusion tallies, and the `CombatModes` state machine (Sanctuary / Tranquil / Combat-prime / Combat-sustain / Recover) the firmware will mirror. See [`../docs/plans/2026-tier1-launch/track-M-combat-trim.md`](../docs/plans/2026-tier1-launch/track-M-combat-trim.md).
- `analyze_ambient_confounds.py` — checks whether an ambient reference channel (RF survey, magnetometer) correlates with a biometric target channel beyond chance, to rule out mundane confounds behind a dyadic/forced-choice result. Analysis-only — never invokes SDR/radio hardware. See [`../docs/psionic_engineering/computational_toolkit.md`](../docs/psionic_engineering/computational_toolkit.md).
