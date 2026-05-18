# Tools — design docs

This directory holds **design and intent docs** for tooling that lives in `tools/` at the repo root.

The code itself lives in `tools/`. This directory documents *what* each tool is supposed to do, *why* it exists, and *how* to evaluate whether it works.

## Index

| Tool | Design doc | Code path | Status |
|------|-----------|-----------|--------|
| `wiki_sync.py` | [`../plan/track-B-wiki-sync-tool.md`](../plan/track-B-wiki-sync-tool.md) | `tools/wiki_sync.py` | planned |
| `check_links.py` | [`../plan/track-H-repo-hygiene.md`](../plan/track-H-repo-hygiene.md) | `tools/check_links.py` | planned |
| `check_wiki_urls.py` | [`../plan/track-H-repo-hygiene.md`](../plan/track-H-repo-hygiene.md) | `tools/check_wiki_urls.py` | planned |

## Convention

When a new tool is added under `tools/`:

1. Its design doc goes in [`../plan/`](../plan/) if it belongs to a planned track, OR in this directory if it's a one-off utility.
2. The tool itself ships with a top-of-file docstring pointing back to its design doc.
3. A row in the table above is added in the same PR.
