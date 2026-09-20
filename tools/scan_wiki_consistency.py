#!/usr/bin/env python3
"""
scan_wiki_consistency.py — corpus-wide numeric-claim consistency scanner
for the cached FusionGirl wiki pages under docs/wiki_cache/.

Design doc: docs/psionic_engineering/computational_toolkit.md

Why this exists: `tools/verify_psi_equations.py` hand-checks one page
(Bifilar Coil Engineering) against its own transcribed arithmetic and
found two genuine, confirmed internal errors. A third was found by a
human re-reading a second page (Smart Composite Fill) five minutes
later. Two pages out of the ~108 tracked is not a sample size anyone
should generalize from by hand-checking one page at a time — this tool
generalizes the technique across the whole cached corpus.

Two check families, both HEURISTIC (see "What this does NOT do" below —
this is a triage aid, not a proof of contradiction):

  1. Cross-page label matching (higher confidence). Every wiki Infobox
     is `{{Infobox | label9 = X | data9 = Y ...}}` -- structured
     key/value pairs. This extracts every (label, value) pair across
     every cached page, groups by normalized label text, and flags
     cases where the SAME label appears on different pages (or more
     than once) with numerically different values for the same unit.

  2. Within-page keyword-proximity matching (lower confidence,
     heuristic). For each infobox (label, value) pair with a numeric
     claim, searches the REST of that same page for other numeric
     claims of the same (canonicalized) unit near an occurrence of the
     label's most distinctive keyword. This is what would catch, e.g.,
     an infobox stating one number for "BST tunability" while a
     different section of the same page states a different number for
     the same concept in prose. It is inherently fuzzy — a keyword
     match near a same-unit number is circumstantial, not proof the two
     numbers describe the same claim. Every result is flagged
     `confidence: low` and needs a human read of the actual page to
     confirm.

Known, already-triaged issues (found manually before this tool existed,
or confirmed and reported upstream but not yet fixed) are suppressed via
`tools/wiki_consistency_known_issues.yml`, mirroring the existing
`tools/known_missing.yml` pattern used by `check_wiki_urls.py` — this
turns a permanent CI failure on an issue nobody in this repo can fix
(the wiki content, not this repo, needs to change) into a tracked,
visible, non-blocking entry. New, un-triaged conflicts still fail.

What this does NOT do:

  - Parse LaTeX <math> blocks fully. It extracts a narrow pattern (a
    bare decimal immediately after \\geq/\\leq/\\approx/\\sim/>/</=
    inside a <math> block, treated as a percentage if in [0,1]) because
    that specific pattern is what caught the BST tunability
    discrepancy. General LaTeX semantic parsing is out of scope; a
    quantitative claim embedded in more complex math markup can be
    missed entirely.
  - Understand semantics. Two different numbers near the same keyword
    might correctly describe two different things (e.g. a gap and a
    width both near "0.2mm" and "0.3mm" tokens). Every flagged item
    needs a human to actually read the page.
  - Replace `verify_psi_equations.py`. That tool re-derives arithmetic
    from stated formulas; this tool only compares stated numbers to
    other stated numbers. A page can pass this scanner (no contradictory
    numbers) and still be arithmetically wrong (its numbers agree with
    each other but don't follow from its own formula), or vice versa.

Stdlib only. No numpy, no scipy — see tools/requirements.txt. PyYAML is
an existing project dependency (already used by wiki_sync.py).

Exit codes:
    0 — no new (non-allowlisted) conflicts found
    1 — at least one new conflict found
    2 — file/parse error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WIKI_CACHE_DIR = REPO_ROOT / "docs" / "wiki_cache"
KNOWN_ISSUES_PATH = REPO_ROOT / "tools" / "wiki_consistency_known_issues.yml"

# ---------------------------------------------------------------------------
# Numeric claim extraction
# ---------------------------------------------------------------------------

_UNIT_ALIASES = {
    "uh": "µH", "µh": "µH", "uf": "µF", "µf": "µF", "ut": "µT", "µt": "µT",
    "um": "µm", "µm": "µm", "ohm": "Ω", "ohms": "Ω", "degc": "°C",
}
_UNIT_TOKENS = [
    "GHz", "MHz", "kHz", "Hz", "kV", "mV", "V", "mA", "kA", "A", "kW", "mW", "W",
    "MΩ", "kΩ", "Ω", "ohm", "ohms", "pF", "nF", "uF", "µF", "nH", "uH", "µH", "mH", "H",
    "mm", "cm", "m", "µm", "um", "nm", "°C", "degC", "K", "%", "dB",
    "µT", "uT", "mT", "T", "N", "Pa", "kPa", "MPa", "g", "kg", "S/m", "pC/N",
]
_UNIT_ALT = "|".join(re.escape(u) for u in sorted(_UNIT_TOKENS, key=len, reverse=True))
_NUM = r"[-+]?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?"
# Trailing boundary is `(?![A-Za-z])`, NOT `\b`: several units (%, Ω, °C)
# end in a non-word character, and `\b` only matches at a transition
# between a word and non-word character -- it never matches right after
# "%" followed by a space or end-of-string, since neither side is a
# word character. That silently dropped every "%"/"Ω" claim followed by
# whitespace (i.e. almost all of them) until a failing test caught it.
_UNIT_TOKEN_RE = re.compile(rf"({_NUM})\s*({_UNIT_ALT})(?![A-Za-z])")
_MATH_BLOCK_RE = re.compile(r"<math>(.*?)</math>", re.DOTALL)
_MATH_RATIO_RE = re.compile(r"(?:\\geq|\\leq|\\approx|\\sim|[><=])\s*(\d*\.\d+|\d+\.\d*)")
# LaTeX inside <math> blocks sometimes states a percentage directly with
# an escaped percent sign (e.g. "\geq 35\%") rather than as a bare [0,1]
# ratio (e.g. "\geq 0.70") -- these need separate handling because the
# value is already in percent units, not a fraction to multiply by 100.
_MATH_PERCENT_RE = re.compile(r"(\d*\.?\d+)\s*\\%")


def _canon_unit(u: str) -> str:
    return _UNIT_ALIASES.get(u.lower(), u)


@dataclass(frozen=True)
class NumericClaim:
    raw: str
    value: float
    unit: str
    position: int


def extract_numeric_claims(text: str) -> list[NumericClaim]:
    """Extract (value, unit) claims from free text: explicit number+unit
    tokens, plus a narrow LaTeX-ratio pattern (see module docstring)."""
    claims: list[NumericClaim] = []
    for m in _UNIT_TOKEN_RE.finditer(text):
        try:
            val = float(m.group(1).replace(",", ""))
        except ValueError:
            continue
        claims.append(NumericClaim(raw=m.group(0), value=val, unit=_canon_unit(m.group(2)), position=m.start()))
    for block_match in _MATH_BLOCK_RE.finditer(text):
        block = block_match.group(1)
        base = block_match.start(1)
        for m in _MATH_PERCENT_RE.finditer(block):
            claims.append(NumericClaim(raw=m.group(0), value=float(m.group(1)), unit="%", position=base + m.start()))
        for m in _MATH_RATIO_RE.finditer(block):
            val = float(m.group(1))
            if 0.0 <= val <= 1.0:
                claims.append(NumericClaim(raw=m.group(0), value=val * 100.0, unit="%", position=base + m.start()))
    claims.sort(key=lambda c: c.position)
    return claims


# ---------------------------------------------------------------------------
# Infobox extraction
# ---------------------------------------------------------------------------

_INFOBOX_FIELD_RE = re.compile(r"^\|\s*(label|data)(\d+)\s*=\s*(.*)$", re.MULTILINE)
_INFOBOX_BLOCK_RE = re.compile(r"\{\{Infobox.*?\}\}", re.DOTALL)


@dataclass(frozen=True)
class InfoboxPair:
    label: str
    value: str
    claims: tuple[NumericClaim, ...]


def extract_infobox_pairs(wikitext: str) -> list[InfoboxPair]:
    labels: dict[str, str] = {}
    datas: dict[str, str] = {}
    for m in _INFOBOX_FIELD_RE.finditer(wikitext):
        kind, num, value = m.group(1), m.group(2), m.group(3).strip()
        (labels if kind == "label" else datas)[num] = value
    pairs = []
    for num, label in labels.items():
        if num in datas and label:
            value = datas[num]
            pairs.append(InfoboxPair(label=label, value=value, claims=tuple(extract_numeric_claims(value))))
    return pairs


def _normalize_label(label: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", label.lower()).strip()


_STOPWORDS = {"the", "and", "for", "value", "with", "from", "this", "that",
              "specifications", "overview", "target", "domain", "output"}


def _distinctive_keywords(label: str, *, min_len: int = 5) -> list[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-z]+", label)]
    return [w for w in words if len(w) >= min_len and w not in _STOPWORDS]


# ---------------------------------------------------------------------------
# Check family 1: cross-page label matching
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Conflict:
    kind: str            # "cross_page_label" | "within_page_keyword"
    confidence: str       # "high" | "low"
    page: str
    label: str
    value_a: str
    value_b: str
    context: str
    other_page: str | None = None


def find_cross_page_label_conflicts(pages: dict[str, str], *, rel_tol: float = 0.02) -> list[Conflict]:
    by_label: dict[str, list[tuple[str, InfoboxPair]]] = defaultdict(list)
    for page, text in pages.items():
        for pair in extract_infobox_pairs(text):
            if pair.claims:
                by_label[_normalize_label(pair.label)].append((page, pair))

    conflicts: list[Conflict] = []
    for norm_label, entries in by_label.items():
        if len(entries) < 2:
            continue
        seen: dict[str, tuple[str, InfoboxPair]] = {}
        for page, pair in entries:
            claim = pair.claims[0]
            prior = seen.get(claim.unit)
            if prior is None:
                seen[claim.unit] = (page, pair)
                continue
            prior_page, prior_pair = prior
            prior_claim = prior_pair.claims[0]
            if prior_claim.value == 0:
                continue
            rel_diff = abs(claim.value - prior_claim.value) / abs(prior_claim.value)
            if rel_diff > rel_tol and prior_page != page:
                conflicts.append(Conflict(
                    kind="cross_page_label", confidence="high",
                    page=page, label=pair.label,
                    value_a=f"{prior_pair.label}={prior_claim.raw} ({prior_page})",
                    value_b=f"{pair.label}={claim.raw} ({page})",
                    context=norm_label, other_page=prior_page,
                ))
    return conflicts


# ---------------------------------------------------------------------------
# Check family 2: within-page keyword-proximity matching
# ---------------------------------------------------------------------------


# Splits page body into small, semantically-scoped chunks (blank lines,
# list-item boundaries, table-row boundaries, sentence boundaries) so a
# keyword match only pulls in numbers from the SAME claim, not anything
# within N characters. An earlier fixed-character-window version of this
# function was tried against the real corpus and had a ~100% false-
# positive rate — e.g. flagging a 0.2mm trace GAP against an unrelated
# 100mm distance from a falloff table eleven lines later, just because
# both mentioned "mm" near the word "gap" somewhere in a wide window.
# Chunk-scoping is a blunt fix (it can still mis-scope a claim that
# genuinely spans a sentence boundary) but is far more conservative.
_CHUNK_SPLIT_RE = re.compile(r"\n{2,}|\n(?=[*#|!])|(?<=[.!?])\s+(?=[A-Z])")


def _split_chunks(text: str) -> list[str]:
    return [c for c in _CHUNK_SPLIT_RE.split(text) if c.strip()]


def find_within_page_conflicts(
    page: str, wikitext: str, *, rel_tol: float = 0.20
) -> list[Conflict]:
    pairs = extract_infobox_pairs(wikitext)
    body = _INFOBOX_BLOCK_RE.sub("", wikitext, count=1)
    chunks = _split_chunks(body)
    conflicts: list[Conflict] = []
    seen_keys: set[tuple[str, str]] = set()

    for pair in pairs:
        if not pair.claims:
            continue
        claim0 = pair.claims[0]
        keywords = _distinctive_keywords(pair.label)
        if not keywords:
            continue
        kw_re = re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
        for chunk in chunks:
            if not kw_re.search(chunk):
                continue
            for other in extract_numeric_claims(chunk):
                if other.unit != claim0.unit or claim0.value == 0:
                    continue
                rel_diff = abs(other.value - claim0.value) / abs(claim0.value)
                if rel_diff <= rel_tol:
                    continue
                dedup_key = (pair.label, other.raw)
                if dedup_key in seen_keys:
                    continue
                seen_keys.add(dedup_key)
                conflicts.append(Conflict(
                    kind="within_page_keyword", confidence="low",
                    page=page, label=pair.label,
                    value_a=claim0.raw, value_b=other.raw,
                    context=chunk.strip().replace("\n", " ")[:220],
                ))
    return conflicts


# ---------------------------------------------------------------------------
# Known-issues allowlist
# ---------------------------------------------------------------------------


def load_known_issues(path: Path = KNOWN_ISSUES_PATH) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("issues", [])


def is_known_issue(conflict: Conflict, known_issues: list[dict]) -> dict | None:
    for issue in known_issues:
        if issue.get("page") != conflict.page:
            continue
        match = issue.get("match", "")
        haystack = f"{conflict.label} {conflict.context} {conflict.value_a} {conflict.value_b}"
        if match.lower() in haystack.lower():
            return issue
    return None


# ---------------------------------------------------------------------------
# Corpus loading + report
# ---------------------------------------------------------------------------


def load_corpus(cache_dir: Path = WIKI_CACHE_DIR) -> dict[str, str]:
    pages = {}
    for p in sorted(cache_dir.glob("*.wikitext")):
        pages[p.stem] = p.read_text(encoding="utf-8")
    return pages


def scan(pages: dict[str, str]) -> tuple[list[Conflict], list[Conflict]]:
    """Returns (new_conflicts, known_conflicts)."""
    known_issues = load_known_issues()
    all_conflicts = find_cross_page_label_conflicts(pages)
    for page, text in pages.items():
        all_conflicts.extend(find_within_page_conflicts(page, text))

    new_conflicts, known_conflicts = [], []
    for c in all_conflicts:
        if is_known_issue(c, known_issues):
            known_conflicts.append(c)
        else:
            new_conflicts.append(c)
    return new_conflicts, known_conflicts


def format_report(new_conflicts: list[Conflict], known_conflicts: list[Conflict]) -> str:
    out = ["Wiki Numeric-Claim Consistency Scan", "=" * 60, ""]
    out.append(f"Scanned corpus; {len(new_conflicts)} new conflict(s), "
               f"{len(known_conflicts)} known/allowlisted.")
    out.append("")
    for c in new_conflicts:
        out.append(f"[{c.confidence.upper()}] {c.kind} — page: {c.page}")
        out.append(f"    label: {c.label}")
        out.append(f"    a: {c.value_a}")
        out.append(f"    b: {c.value_b}")
        if c.context:
            out.append(f"    context: {c.context}")
        out.append("")
    if known_conflicts:
        out.append(f"({len(known_conflicts)} known issue(s) suppressed — see "
                    f"tools/wiki_consistency_known_issues.yml)")
    return "\n".join(out)


def conflicts_to_json(conflicts: list[Conflict]) -> list[dict]:
    return [
        {"kind": c.kind, "confidence": c.confidence, "page": c.page, "label": c.label,
         "value_a": c.value_a, "value_b": c.value_b, "context": c.context, "other_page": c.other_page}
        for c in conflicts
    ]


def _cli(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="scan_wiki_consistency.py",
        description="Scan docs/wiki_cache/*.wikitext for contradictory numeric claims.",
    )
    p.add_argument("--cache-dir", default=str(WIKI_CACHE_DIR))
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-low-confidence", action="store_true",
                    help="By default, exit 0 unless a HIGH-confidence new conflict is found "
                         "(low-confidence/heuristic hits are reported but non-blocking). "
                         "Pass this to also fail on low-confidence hits.")
    args = p.parse_args(argv)

    cache_dir = Path(args.cache_dir)
    if not cache_dir.exists():
        print(f"scan_wiki_consistency: cache dir not found: {cache_dir}", file=sys.stderr)
        return 2

    pages = load_corpus(cache_dir)
    new_conflicts, known_conflicts = scan(pages)

    if args.json:
        print(json.dumps({
            "new_conflicts": conflicts_to_json(new_conflicts),
            "known_conflicts": conflicts_to_json(known_conflicts),
        }, indent=2, sort_keys=True))
    else:
        print(format_report(new_conflicts, known_conflicts))

    blocking = [c for c in new_conflicts if c.confidence == "high" or args.fail_on_low_confidence]
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
