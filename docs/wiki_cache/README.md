Snapshots of FusionGirl wiki pages tracked by `tools/wiki_sync.py`.

Files in this directory:

- `<slug>.wikitext` — raw MediaWiki wikitext.
- `<slug>.meta.json` — `{title, pageid, revid, lastrev_timestamp, fetched_at, url, sha256, length}`.
- `CHANGELOG.md` — append-only log of detected revisions.

See `tools/wiki_pages.yml` for the curated page list and `docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md` for the tool's design.

Do not edit files in this directory by hand — they will be overwritten on next sync.
