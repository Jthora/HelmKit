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
