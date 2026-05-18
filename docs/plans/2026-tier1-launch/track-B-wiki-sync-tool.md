# Track B — Wiki sync tool (`tools/wiki_sync.py`)

- **Status**: `ready`
- **Effort**: ~4 hours (~150 LOC Python)
- **Depends on**: nothing (uses public MediaWiki API)
- **Unblocks**: Track A (gives us automatic notification when wiki content lands)

---

## Goal

A small, deterministic tool that pulls a curated set of wiki pages from `https://wiki.fusiongirl.app/api.php`, caches their wikitext + metadata under `docs/wiki_cache/`, and writes a human-readable changelog of revisions since the last run.

The repo becomes self-contained: anyone (human or AI assistant) cloning HelmKit gets a snapshot of the wiki pages this project depends on, even if the live wiki goes down.

## Non-goals

- Not a full mirror. Only the curated page list.
- Not a Markdown converter. We store raw wikitext + metadata; conversion to MD is Track A's problem.
- Not a CMS. One-way pull only.

## Design

### Inputs

- `tools/wiki_pages.yml` — list of pages to track, seeded from [`../wiki_anchors.md`](../wiki_anchors.md):
  ```yaml
  api_endpoint: https://wiki.fusiongirl.app/api.php
  pages:
    - title: "HelmKit"
    - title: "Psi Defender"
    - title: "Psi Stabilizer"
    - title: "Caduceus coil"
    - title: "Bifilar coil"
    # ... etc, ~30 pages from wiki_anchors.md
  ```

### Outputs

- `docs/wiki_cache/<page_slug>.wikitext` — raw wikitext.
- `docs/wiki_cache/<page_slug>.meta.json` — `{pageid, revid, title, lastrev_timestamp, fetched_at, url, sha256}`.
- `docs/wiki_cache/CHANGELOG.md` — append-only, one row per (run, page, change):
  ```
  ## 2026-05-18T20:00Z
  - **NEW**: "Caduceus coil enhancement formula" (pageid 412, revid 8821)
  - **REVISED**: "HelmKit" (revid 7700 → 8819, +1240 chars)
  - **UNCHANGED**: 27 pages
  ```

### Algorithm

```
for page in config.pages:
    GET api.php?action=query&prop=revisions&titles=<page>&rvprop=ids|timestamp|content&rvslots=main&format=json
    if pageid missing on the server: log "MISSING", continue
    new_revid = response.revid
    old_meta = read(meta_file) if exists else None
    if old_meta is None:
        write wikitext + meta; CHANGELOG: NEW
    elif old_meta.revid != new_revid:
        write wikitext + meta; CHANGELOG: REVISED (old_revid → new_revid, ±chars)
    else:
        CHANGELOG: UNCHANGED (rolled up at end)
```

Rate-limit: 1 req/sec. User-Agent header: `HelmKit-wiki-sync/0.1 (https://github.com/Jthora/HelmKit)`.

### CLI

```
python tools/wiki_sync.py                 # full sync, write to docs/wiki_cache/
python tools/wiki_sync.py --dry-run       # report only, no writes
python tools/wiki_sync.py --page "Caduceus coil"   # single page
python tools/wiki_sync.py --check         # exit 1 if any page revised, for CI
```

### Dependencies

`requests`, `pyyaml`. Both stdlib-ish. Add to `tools/requirements.txt`.

## Acceptance criteria

1. Running with no `docs/wiki_cache/` produces a populated cache and a CHANGELOG entry listing all pages as `NEW`.
2. Running again immediately produces a CHANGELOG entry showing all pages as `UNCHANGED` and zero file writes.
3. `--check` exits 1 when any tracked page has a new revid since last sync.
4. Hidden `.meta.json` files round-trip: same revid in → "UNCHANGED" out.
5. Works offline if `docs/wiki_cache/` is populated (read-only operations).

## Optional GH Actions cron

`.github/workflows/wiki-sync.yml` runs the script daily at 13:00 UTC. If `--check` reports changes, opens (or updates) an issue titled "Wiki drop detected: N pages revised since last sync" with the CHANGELOG diff in the body.

## File deliverables

- `tools/wiki_sync.py`
- `tools/wiki_pages.yml`
- `tools/requirements.txt`
- `docs/wiki_cache/.gitkeep`
- `docs/wiki_cache/CHANGELOG.md` (created on first run)
- (optional) `.github/workflows/wiki-sync.yml`

## What ships

A single commit titled `tools: add wiki_sync.py + curated page list`. CI workflow lands in a follow-up commit so it can be reviewed separately.
