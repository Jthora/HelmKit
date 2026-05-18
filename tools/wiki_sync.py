#!/usr/bin/env python3
"""
wiki_sync.py — Pull tracked FusionGirl wiki pages into docs/wiki_cache/.

Design doc: docs/plans/2026-tier1-launch/track-B-wiki-sync-tool.md

Usage:
    python tools/wiki_sync.py                 # full sync
    python tools/wiki_sync.py --dry-run       # report only, no writes
    python tools/wiki_sync.py --page TITLE    # one page (repeatable)
    python tools/wiki_sync.py --check         # exit 1 if any tracked page has new revid
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "tools" / "wiki_pages.yml"
CACHE_DIR = REPO_ROOT / "docs" / "wiki_cache"
CHANGELOG_PATH = CACHE_DIR / "CHANGELOG.md"


def slugify(title: str) -> str:
    """Stable, filesystem-safe slug for a page title."""
    s = title.strip().lower()
    s = re.sub(r"[\s/]+", "_", s)
    s = re.sub(r"[^a-z0-9._-]", "", s)
    return s or "untitled"


@dataclass
class PageResult:
    title: str
    status: str  # "NEW" | "REVISED" | "UNCHANGED" | "MISSING" | "ERROR"
    old_revid: int | None = None
    new_revid: int | None = None
    delta_chars: int | None = None
    detail: str | None = None


def load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_meta(slug: str) -> dict | None:
    meta_path = CACHE_DIR / f"{slug}.meta.json"
    if not meta_path.exists():
        return None
    return json.loads(meta_path.read_text(encoding="utf-8"))


def write_page(slug: str, title: str, wikitext: str, revid: int, lastrev_ts: str, pageid: int, url: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{slug}.wikitext").write_text(wikitext, encoding="utf-8")
    meta = {
        "title": title,
        "pageid": pageid,
        "revid": revid,
        "lastrev_timestamp": lastrev_ts,
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "url": url,
        "sha256": hashlib.sha256(wikitext.encode("utf-8")).hexdigest(),
        "length": len(wikitext),
    }
    (CACHE_DIR / f"{slug}.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch_page(session: requests.Session, api: str, title: str, timeout: int) -> dict | None:
    """Return MediaWiki page dict or None if missing."""
    params = {
        "action": "query",
        "format": "json",
        "prop": "revisions",
        "titles": title,
        "rvprop": "ids|timestamp|content",
        "rvslots": "main",
        "redirects": 1,
        "formatversion": 2,
    }
    r = session.get(api, params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None
    page = pages[0]
    if page.get("missing"):
        return None
    return page


def page_url(api_endpoint: str, title: str) -> str:
    base = api_endpoint.rsplit("/", 1)[0]
    return f"{base}/wiki/{title.replace(' ', '_')}"


def sync_one(session: requests.Session, cfg: dict, title: str, dry_run: bool) -> PageResult:
    api = cfg["api_endpoint"]
    timeout = int(cfg.get("request_timeout_sec", 30))
    try:
        page = fetch_page(session, api, title, timeout)
    except requests.RequestException as e:
        return PageResult(title=title, status="ERROR", detail=str(e))
    if page is None:
        return PageResult(title=title, status="MISSING")

    revs = page.get("revisions", [])
    if not revs:
        return PageResult(title=title, status="ERROR", detail="no revisions returned")
    rev = revs[0]
    new_revid = int(rev["revid"])
    lastrev_ts = rev.get("timestamp", "")
    wikitext = rev.get("slots", {}).get("main", {}).get("content", "")
    pageid = int(page.get("pageid", 0))
    canonical_title = page.get("title", title)
    url = page_url(api, canonical_title)

    slug = slugify(canonical_title)
    old_meta = read_meta(slug)

    if old_meta is None:
        if not dry_run:
            write_page(slug, canonical_title, wikitext, new_revid, lastrev_ts, pageid, url)
        return PageResult(title=canonical_title, status="NEW", new_revid=new_revid, delta_chars=len(wikitext))

    if int(old_meta["revid"]) == new_revid:
        return PageResult(title=canonical_title, status="UNCHANGED", new_revid=new_revid)

    delta = len(wikitext) - int(old_meta.get("length", 0))
    if not dry_run:
        write_page(slug, canonical_title, wikitext, new_revid, lastrev_ts, pageid, url)
    return PageResult(
        title=canonical_title,
        status="REVISED",
        old_revid=int(old_meta["revid"]),
        new_revid=new_revid,
        delta_chars=delta,
    )


def append_changelog(results: list[PageResult], dry_run: bool) -> None:
    if dry_run:
        return
    changed = [r for r in results if r.status in {"NEW", "REVISED", "MISSING", "ERROR"}]
    if not changed:
        # No activity worth logging. Skip entirely so the changelog stays signal-only.
        return
    unchanged_count = sum(1 for r in results if r.status == "UNCHANGED")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    lines: list[str] = [f"\n## {ts}\n"]
    for r in changed:
        if r.status == "NEW":
            lines.append(f"- **NEW**: \"{r.title}\" (revid {r.new_revid}, {r.delta_chars} chars)")
        elif r.status == "REVISED":
            sign = "+" if (r.delta_chars or 0) >= 0 else ""
            lines.append(f"- **REVISED**: \"{r.title}\" (revid {r.old_revid} → {r.new_revid}, {sign}{r.delta_chars} chars)")
        elif r.status == "MISSING":
            lines.append(f"- **MISSING**: \"{r.title}\" (page not present on server)")
        elif r.status == "ERROR":
            lines.append(f"- **ERROR**: \"{r.title}\" ({r.detail})")
    if unchanged_count:
        lines.append(f"- _UNCHANGED_: {unchanged_count} pages")
    lines.append("")
    header = "# Wiki cache changelog\n\nAppend-only log of changes detected by `tools/wiki_sync.py`.\n"
    if not CHANGELOG_PATH.exists():
        CHANGELOG_PATH.write_text(header, encoding="utf-8")
    with CHANGELOG_PATH.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync curated FusionGirl wiki pages.")
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not write cache.")
    parser.add_argument("--page", action="append", default=None, help="Sync a single page (repeatable). Bypasses config list.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if any tracked page has a new revid.")
    parser.add_argument("--config", default=str(CONFIG_PATH), help="Path to wiki_pages.yml.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    cfg = load_config(Path(args.config))
    titles: list[str] = args.page if args.page else list(cfg["pages"])
    delay = float(cfg.get("request_delay_sec", 1.0))

    session = requests.Session()
    session.headers["User-Agent"] = cfg.get("user_agent", "HelmKit-wiki-sync/0.1")

    results: list[PageResult] = []
    for i, title in enumerate(titles):
        if i > 0:
            time.sleep(delay)
        r = sync_one(session, cfg, title, dry_run=args.dry_run or args.check)
        results.append(r)
        marker = {
            "NEW": "+",
            "REVISED": "~",
            "UNCHANGED": ".",
            "MISSING": "?",
            "ERROR": "!",
        }.get(r.status, "?")
        print(f"  {marker} {r.status:<10} {r.title}", file=sys.stderr)

    if not (args.dry_run or args.check):
        append_changelog(results, dry_run=False)

    new_or_revised = [r for r in results if r.status in {"NEW", "REVISED"}]
    print(file=sys.stderr)
    print(f"Summary: {len(results)} tracked, {len(new_or_revised)} new/revised, "
          f"{sum(1 for r in results if r.status == 'UNCHANGED')} unchanged, "
          f"{sum(1 for r in results if r.status == 'MISSING')} missing, "
          f"{sum(1 for r in results if r.status == 'ERROR')} errors.", file=sys.stderr)

    if args.check and new_or_revised:
        return 1
    if any(r.status == "ERROR" for r in results):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
