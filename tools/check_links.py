#!/usr/bin/env python3
"""
check_links.py — Markdown link integrity checker.

Spec: docs/plans/2026-tier1-launch/track-H-repo-hygiene.md

Walks a fixed set of docs and:
  - For every relative Markdown link target, asserts the path exists.
  - For absolute links to known-good domains, issues a HEAD (falls back to
    GET) request, expects 2xx/3xx, caches results for 24h.
  - For all other external links, skips (too noisy for CI).
  - Also fails on TODO(reviewer) / XXX markers in shippable docs.

Exit non-zero on first failure. Prints file:line for every problem.

Usage:
    python tools/check_links.py            # full check
    python tools/check_links.py --offline  # skip network checks
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

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
CACHE_PATH = CACHE_DIR / "check_links.json"
CACHE_TTL_SEC = 24 * 60 * 60
KNOWN_MISSING_PATH = REPO_ROOT / "tools" / "known_missing.yml"

# Domains we will actually hit over the network. Anything else is skipped.
# wiki.fusiongirl.app is deliberately NOT in this set — check_wiki_urls.py
# probes it via the MediaWiki API instead, which gives better diagnostics.
KNOWN_DOMAINS = {
    "github.com",
    "raw.githubusercontent.com",
    "ko-fi.com",
    "zenodo.org",
    "docs.google.com",
}

# Hosts we explicitly skip even if they are subdomains of a known domain.
SKIP_HOSTS = {
    "wiki.fusiongirl.app",
}

# Markdown link / image regex. Captures the URL inside the parens.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

# Tokens that should not survive into shippable docs (final output surface
# for the public: README/NOTICE/PRIOR_ART, the field-notes PDF source,
# the legal copy, and outreach posts). Internal sprint specs and plans
# routinely use 'XXX' as a placeholder marker, which is fine.
FORBIDDEN_TOKENS = ("TODO(reviewer)", "XXX")
SHIPPABLE_PREFIXES = (
    "README.md",
    "NOTICE.md",
    "PRIOR_ART.md",
    "docs/field-notes/",
    "docs/legal/",
    "docs/outreach/",
)


def is_shippable(rel_path: str) -> bool:
    rel = rel_path.replace("\\", "/")
    return any(rel == p or rel.startswith(p) for p in SHIPPABLE_PREFIXES)


def discover_doc_files() -> list[Path]:
    """All Markdown files we consider 'shippable' for link integrity."""
    targets: list[Path] = []
    for p in [REPO_ROOT / "README.md", REPO_ROOT / "NOTICE.md", REPO_ROOT / "PRIOR_ART.md"]:
        if p.exists():
            targets.append(p)
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        targets.extend(sorted(docs_dir.rglob("*.md")))
    external_dir = REPO_ROOT / "external"
    if external_dir.exists():
        for sub in external_dir.iterdir():
            readme = sub / "README.md"
            if readme.exists():
                targets.append(readme)
    return targets


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


def cache_get(cache: dict, url: str) -> int | None:
    entry = cache.get(url)
    if not entry:
        return None
    if time.time() - entry.get("t", 0) > CACHE_TTL_SEC:
        return None
    return entry.get("status")


def cache_put(cache: dict, url: str, status: int) -> None:
    cache[url] = {"t": int(time.time()), "status": status}


def http_check(url: str, cache: dict) -> tuple[bool, str]:
    """Return (ok, detail). Uses cache to avoid hammering."""
    if requests is None:
        return True, "requests-unavailable-skipped"
    cached = cache_get(cache, url)
    if cached is not None:
        ok = 200 <= cached < 400
        return ok, f"cached:{cached}"
    headers = {"User-Agent": "HelmKit-check_links/0.1 (+https://github.com/Jthora/HelmKit)"}
    try:
        r = requests.head(url, allow_redirects=True, timeout=10, headers=headers)
        if r.status_code in (403, 405, 501):  # some servers dislike HEAD
            r = requests.get(url, allow_redirects=True, timeout=15, headers=headers, stream=True)
            r.close()
        status = r.status_code
    except requests.RequestException as e:
        return False, f"network-error: {e.__class__.__name__}"
    cache_put(cache, url, status)
    ok = 200 <= status < 400
    return ok, f"http:{status}"


def is_known_external(url: str) -> bool:
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return False
    if host in SKIP_HOSTS:
        return False
    return any(host == d or host.endswith("." + d) for d in KNOWN_DOMAINS)


def load_known_missing_external() -> set[str]:
    if not KNOWN_MISSING_PATH.exists() or yaml is None:
        return set()
    try:
        data = yaml.safe_load(KNOWN_MISSING_PATH.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return set()
    out: set[str] = set()
    for entry in data.get("external_urls", []) or []:
        if isinstance(entry, dict) and "url" in entry:
            out.add(entry["url"].strip())
    return out


def resolve_relative(doc: Path, target: str) -> Path:
    # Strip URL fragment and query.
    cleaned = target.split("#", 1)[0].split("?", 1)[0]
    if not cleaned:
        # Pure fragment like "#section" — internal anchor, accept.
        return doc
    candidate = (doc.parent / cleaned).resolve()
    return candidate


def check_file(doc: Path, cache: dict, offline: bool, known_missing: set[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    text = doc.read_text(encoding="utf-8", errors="replace")
    rel = doc.relative_to(REPO_ROOT)
    rel_str = str(rel)
    in_external = rel_str.replace("\\", "/").startswith("external/")

    # Forbidden tokens — only on the shippable doc surface.
    if is_shippable(rel_str):
        for lineno, line in enumerate(text.splitlines(), start=1):
            for tok in FORBIDDEN_TOKENS:
                if tok in line:
                    errors.append(f"{rel}:{lineno}: forbidden token {tok!r}")

    # Track line numbers for each link by re-scanning per line.
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in LINK_RE.finditer(line):
            url = m.group(1).strip()
            if not url or url.startswith("mailto:") or url.startswith("data:"):
                continue
            if url.startswith("#"):
                continue  # in-page anchor
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https"):
                if offline:
                    continue
                if not is_known_external(url):
                    continue
                ok, detail = http_check(url, cache)
                if not ok:
                    if url in known_missing:
                        warnings.append(f"{rel}:{lineno}: known-missing external link {url} ({detail})")
                    else:
                        errors.append(f"{rel}:{lineno}: external link {url} ({detail})")
            elif parsed.scheme == "":
                if in_external:
                    # Submodule READMEs reference paths inside their own
                    # repo; we don't own those trees from here.
                    continue
                target = resolve_relative(doc, url)
                if not target.exists():
                    errors.append(f"{rel}:{lineno}: missing relative target -> {url}")
            else:
                # Unknown scheme (e.g. ftp:, file:) — flag it.
                errors.append(f"{rel}:{lineno}: unsupported URL scheme {parsed.scheme!r} -> {url}")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true", help="Skip network checks")
    args = ap.parse_args()

    cache = load_cache()
    known_missing = load_known_missing_external()
    docs = discover_doc_files()
    if not docs:
        print("check_links: no docs discovered", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []
    for d in docs:
        errs, warns = check_file(d, cache, args.offline, known_missing)
        all_errors.extend(errs)
        all_warnings.extend(warns)

    save_cache(cache)

    if all_warnings:
        for w in all_warnings:
            print(f"warning: {w}")

    if all_errors:
        for e in all_errors:
            print(e)
        print(f"\ncheck_links: FAIL ({len(all_errors)} issue(s), {len(all_warnings)} warning(s) across {len(docs)} file(s))")
        return 1

    print(f"check_links: OK ({len(docs)} file(s) clean, {len(all_warnings)} known-missing warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
