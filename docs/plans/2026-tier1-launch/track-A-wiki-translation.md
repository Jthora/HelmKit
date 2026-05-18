# Track A — Wiki content → engineering translation

- **Status**: `blocked-pending` (waiting on FusionGirl wiki content drop)
- **Owner**: HelmKit-side AI assistant + Jono
- **Depends on**: external wiki AI agent's expansion landing
- **Unblocks**: deeper Mk1+ design, new derivation candidates, new safety blacklist rows

---

## What this track is

The FusionGirl wiki is the **design specification** for HelmKit. This track is the work of translating wiki content (intents, geometries, frequencies, coupling claims, BOMs) into engineering documents in this repo:

- BOM rows in `docs/inventory.md` and `docs/inventory_capability_map.md`
- Geometry rows in `docs/sprint_0.2_circuit_spec.md` and `docs/mk0_pcb_bifilar_coil.md`
- Mode rows in `docs/modes.md`
- Pre-registered F1–F10 falsification entries in `docs/falsification.md`
- Safety-blacklist rows in `docs/safety.md`
- Index entries in `docs/wiki_anchors.md`

## Why it's blocked

The wiki AI agent received the engineering critiques produced earlier in this project (sparse math, missing parameter ranges, no closed-form for caduceus enhancement, etc.) and is doing a major content expansion in response. Translating partial content now would be wasted work.

## Unblock signal

Track B (`tools/wiki_sync.py`) will detect the drop automatically and produce a diff under `docs/wiki_cache/CHANGELOG.md`. When new pages or substantial revisions appear:

1. Triage diff by pageid. Group by topic (coils, modes, safety, theory).
2. Pick highest-leverage 3–5 pages for first translation pass.
3. Each translation produces or updates a doc under `docs/`.
4. Each new claim that touches the body gets a row added to F1–F10 or a new F-row if needed.
5. Each new emitter geometry gets a row in the safety blacklist + a calculated SAR ceiling.

## Output template per wiki page

```
docs/<topic>/<page_slug>.md
  - Source: wiki pageid + revid + URL + fetched-at
  - Wiki claim (verbatim or close paraphrase)
  - Engineering interpretation
  - BOM implication (if any)
  - Geometry / parameter implication
  - Safety implication
  - Falsification hook (which F-row tests this)
  - Open questions / extrapolations (flagged as (c) per AI rules of engagement)
```

## What ships when this track runs

A wave of new docs under `docs/` (mostly flat, mirroring existing pattern). Pull request grouped by wiki topic. Each PR is small and self-contained so it can be reviewed and rolled back independently.
