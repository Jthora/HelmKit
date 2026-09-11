# tools/

Repo-root tools for HelmKit. Each tool ships with a top-of-file docstring pointing back to its design doc under [`../docs/tools/`](../docs/tools/README.md) or [`../docs/plans/`](../docs/plans/README.md).

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/requirements.txt
```

## Tools

- `wiki_sync.py` — pull tracked FusionGirl wiki pages into `docs/wiki_cache/`. See [`../docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md`](../docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md).
- `stabilizer_field_model.py` — Biot–Savart / vector-potential field model of the disk's bifilar pancake coil against the tissue screening factor and the ICNIRP 2010/2020 limits (aiding vs opposing connection, lumped L/C/SRF). See [`../docs/psionic_engineering/stabilizer_derivation.md`](../docs/psionic_engineering/stabilizer_derivation.md).
- `analyze_combat_session.py` — Track M host-side reference for the combat trim's adhesive-free sensing: per-round coarse HR with the two-source agreement rule, RMSSD only in still rest windows, thermal breathing rate and nose-tip arousal slope, forehead EDA response rate with the sweat rule, impacts, intrusion tallies, and the `CombatModes` state machine (Sanctuary / Tranquil / Combat-prime / Combat-sustain / Recover) the firmware will mirror. See [`../docs/plans/2026-tier1-launch/track-M-combat-trim.md`](../docs/plans/2026-tier1-launch/track-M-combat-trim.md).
