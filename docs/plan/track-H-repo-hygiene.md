# Track H — Repo hygiene (link-check + wiki-URL probe + pre-commit)

- **Status**: `ready`
- **Effort**: ~3 hours
- **Depends on**: nothing
- **Unblocks**: confidence that the docs we ship don't have broken refs (which is embarrassing for a project whose pitch is "discipline")

---

## Goal

Two tiny tools + a pre-commit hook + a CI gate, so that every commit to `master` has:

1. No broken Markdown links (internal or external).
2. No dead wiki URLs (where "dead" = HTTP 404 or pageid missing on `wiki.fusiongirl.app`).
3. No `TODO(reviewer)` or `XXX` markers left in shippable docs.

This is the project equivalent of `cargo check` — fast, cheap, runs in CI.

## Tool 1: `tools/check_links.py`

- Walks `docs/`, `README.md`, `NOTICE.md`, `PRIOR_ART.md`, `external/*/README.md`.
- Extracts every Markdown link.
- For relative links: assert target exists in working tree.
- For absolute links to known-good domains (github.com, ko-fi.com, fusiongirl.app, zenodo.org, docs.google.com): HEAD request, expect 2xx or 3xx; cache results 24h in `.cache/check_links.json`.
- For arbitrary external links: skip (too noisy in CI).
- Exit non-zero on first failure with line+col.

## Tool 2: `tools/check_wiki_urls.py`

- Extracts every link matching `wiki.fusiongirl.app/wiki/<title>` from the same file set.
- For each: call `api.php?action=query&titles=<title>` and assert `pageid > 0` (no `missing` flag).
- Cache 24h.
- Exit non-zero on first missing page.

## Pre-commit hook

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: check-links
        name: Markdown link integrity
        entry: python tools/check_links.py
        language: system
        pass_filenames: false
        types_or: [markdown]
      - id: check-wiki-urls
        name: Wiki URL probe
        entry: python tools/check_wiki_urls.py
        language: system
        pass_filenames: false
        types_or: [markdown]
        stages: [pre-push]  # network call, not on every commit
```

## CI gate

`.github/workflows/lint-docs.yml`:

```yaml
on: [push, pull_request]
jobs:
  lint-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r tools/requirements.txt
      - run: python tools/check_links.py
      - run: python tools/check_wiki_urls.py
```

## Acceptance criteria

1. Running `python tools/check_links.py` on `master` reports zero failures.
2. Running `python tools/check_wiki_urls.py` on `master` reports zero failures.
3. Introducing a broken relative link in a doc and pushing causes CI to fail.
4. Pre-commit hook installs cleanly with `pre-commit install`.

## File deliverables

- `tools/check_links.py`
- `tools/check_wiki_urls.py`
- `.pre-commit-config.yaml`
- `.github/workflows/lint-docs.yml`
- `.gitignore` row for `.cache/`

## What ships

One commit titled `tools: add doc lint + wiki URL probe + pre-commit + CI`.
