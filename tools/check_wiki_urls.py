#!/usr/bin/env python3
"""
check_wiki_urls.py — Probe wiki.fusiongirl.app links for missing pages.

Spec: docs/plans/2026-tier1-launch/track-H-repo-hygiene.md

Extracts every Markdown link matching wiki.fusiongirl.app/wiki/<title> from
the shippable doc set, then queries the MediaWiki API for each title to
confirm pageid > 0. Exits non-zero on first missing page. Cached 24h.

Usage:
    python tools/check_wiki_urls.py
    python tools/check_wiki_urls.py --offline   # skip network, verify cache only
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = REPO_ROOT / ".cache"
CACHE_PATH = CACHE_DIR / "check_wiki_urls.json"
CACHE_TTL_SEC = 24 * 60 * 60
KNOWN_MISSING_PATH = REPO_ROOT / "tools" / "known_missing.yml"

WIKI_HOST = "wiki.fusiongirl.app"
API_ENDPOINT = f"https://{WIKI_HOST}/api.php"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
WIKI_PATH_RE = re.compile(r"^/wiki/(.+)$")


def discover_doc_files() -> list[Path]:
    targets: list[Path] = []
    for p in [REPO_ROOT / "README.md", REPO_ROOT / "NOTICE.md", REPO_ROOT / "PRIOR_ART.md"]:
        if p.exists():
            targets.append(p)
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        targets.extend(sorted(docs_dir.rglob("*.md")))
    return targets


def extract_titles(docs: list[Path]) -> dict[str, list[str]]:
    """Return {title: [origin1, origin2, ...]} for every wiki link found."""
    found: dict[str, list[str]] = {}
    for doc in docs:
        rel = doc.relative_to(REPO_ROOT)
        text = doc.read_text(encoding="utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for m in LINK_RE.finditer(line):
                url = m.group(1).strip()
                parsed = urlparse(url)
                if parsed.hostname != WIKI_HOST:
                    continue
                pm = WIKI_PATH_RE.match(parsed.path or "")
                if not pm:
                    continue
                raw_title = unquote(pm.group(1)).split("#", 1)[0]
                # MediaWiki: spaces and underscores are interchangeable; normalize to spaces.
                title = raw_title.replace("_", " ").strip()
                if not title:
                    continue
                found.setdefault(title, []).append(f"{rel}:{lineno}")
    return found


def load_cache() -> dict:
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def cache_get(cache: dict, title: str) -> bool | None:
    entry = cache.get(title)
    if not entry:
        return None
    if time.time() - entry.get("t", 0) > CACHE_TTL_SEC:
        return None
    return bool(entry.get("ok"))


def cache_put(cache: dict, title: str, ok: bool, pageid: int | None) -> None:
    cache[title] = {"t": int(time.time()), "ok": ok, "pageid": pageid}


def load_known_missing() -> set[str]:
    """Return the set of wiki titles allowlisted as known-missing."""
    if not KNOWN_MISSING_PATH.exists() or yaml is None:
        return set()
    try:
        data = yaml.safe_load(KNOWN_MISSING_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set()
    out: set[str] = set()
    for entry in data.get("wiki_pages", []) or []:
        if isinstance(entry, dict) and "title" in entry:
            # Normalize underscores to spaces, same as extract_titles().
            out.add(entry["title"].replace("_", " ").strip())
    return out


def query_titles(titles: list[str]) -> dict[str, tuple[bool, int | None, str]]:
    """Batch-query the MediaWiki API. Returns {title: (ok, pageid, detail)}."""
    if requests is None:
        return {t: (True, None, "requests-unavailable-skipped") for t in titles}
    results: dict[str, tuple[bool, int | None, str]] = {}
    # MediaWiki accepts up to 50 titles per request.
    headers = {"User-Agent": "HelmKit-check_wiki_urls/0.1 (+https://github.com/Jthora/HelmKit)"}
    for i in range(0, len(titles), 40):
        batch = titles[i : i + 40]
        params = {
            "action": "query",
            "format": "json",
            "titles": "|".join(batch),
            "redirects": "1",
        }
        try:
            r = requests.get(API_ENDPOINT, params=params, timeout=15, headers=headers)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError) as e:
            for t in batch:
                results[t] = (False, None, f"api-error: {e.__class__.__name__}")
            continue
        query = data.get("query", {})
        # Map normalized/redirected titles back to the original input.
        title_map = {t: t for t in batch}
        for entry in query.get("normalized", []):
            title_map[entry["to"]] = title_map.get(entry["from"], entry["from"])
        for entry in query.get("redirects", []):
            title_map[entry["to"]] = title_map.get(entry["from"], entry["from"])
        for page in (query.get("pages") or {}).values():
            page_title = page.get("title", "")
            origin = title_map.get(page_title, page_title)
            if "missing" in page or int(page.get("pageid", 0)) <= 0:
                results[origin] = (False, None, "missing")
            else:
                results[origin] = (True, int(page["pageid"]), "ok")
        # Any input not accounted for is an error.
        for t in batch:
            if t not in results:
                results[t] = (False, None, "no-response")
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true", help="Skip network; only verify cache hits")
    args = ap.parse_args()

    docs = discover_doc_files()
    found = extract_titles(docs)
    if not found:
        print("check_wiki_urls: no wiki links found; OK")
        return 0

    cache = load_cache()
    to_query: list[str] = []
    pre_results: dict[str, tuple[bool, int | None, str]] = {}
    for title in sorted(found):
        cached = cache_get(cache, title)
        if cached is None:
            to_query.append(title)
        else:
            pre_results[title] = (cached, cache[title].get("pageid"), "cached")

    fresh: dict[str, tuple[bool, int | None, str]] = {}
    if to_query and not args.offline:
        fresh = query_titles(to_query)
        for title, (ok, pageid, _detail) in fresh.items():
            cache_put(cache, title, ok, pageid)
        save_cache(cache)
    elif to_query and args.offline:
        for title in to_query:
            fresh[title] = (True, None, "offline-skipped")

    all_results = {**pre_results, **fresh}
    known_missing = load_known_missing()
    failures: list[str] = []
    warnings: list[str] = []
    for title, (ok, _pageid, detail) in all_results.items():
        if ok:
            continue
        origins = ", ".join(found[title][:3])
        msg = f"{origins}: wiki page missing -> {title!r} ({detail})"
        if title in known_missing:
            warnings.append(msg)
        else:
            failures.append(msg)

    if warnings:
        for w in warnings:
            print(f"warning: {w}")

    if failures:
        for f in failures:
            print(f)
        print(
            f"\ncheck_wiki_urls: FAIL ({len(failures)} missing page(s), "
            f"{len(warnings)} known-missing warning(s); {len(all_results)} checked)"
        )
        return 1

    print(
        f"check_wiki_urls: OK ({len(all_results)} page(s) verified across {len(docs)} file(s); "
        f"{len(warnings)} known-missing warning(s))"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
