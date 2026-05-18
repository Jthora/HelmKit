# Track F — Field Notes Vol. I (Tier 1 PDF artifact)

- **Status**: `ready`
- **Effort**: ~35 hours over 4 weeks (mostly lift-and-edit from existing docs)
- **Depends on**: pandoc + TeX Live installation; minor figure assets from Track D
- **Unblocks**: **Tier 1 product ships**; cash flow; validates the Field Notes commission listing on Ko-fi

---

## Goal

Produce **HelmKit Field Notes Vol. I** — a polished, citable, ~60–80 page PDF that is the first sellable artifact of this project. It is what every Ko-fi Field Notes ($9 + PWYW) commissioner receives.

This is the deliverable that closes the loop on Tier 1 well ahead of the Tier 1 DIY Build Kit (August 2026) and the Tier 2 Hand-Built Unit (Sept–Oct 2026).

## Pitch

> An honest, technical, falsifiable engineering field-book for an open psionic platform. Written for makers, researchers, and the wiki-literate. Includes derivations, BOM logic, mode protocols, safety floors, and the F1–F10 falsification framework. Not a medical device. Not a cosplay prop. The work.

## Outline (11 sections, ~5–8 pp each)

| § | Section | Source | New writing |
|---|---------|--------|-------------|
| 0 | Front matter, copyright, disclaimer | `NOTICE.md`, `docs/legal/*` | minimal |
| 1 | Manifesto: why an open psionic platform | `README.md` § AI assistants stance | medium |
| 2 | The HelmKit platform | `docs/architecture.md`, `docs/roadmap.md` | low |
| 3 | Sister modules: Psi Defender, Psi Stabilizer | sister-repo READMEs | low |
| 4 | The wiki as design specification | `docs/wiki_anchors.md`, `docs/wiki_synthesis.md` | medium |
| 5 | Field theory: ψ-field, coupling, geometries | `docs/psionics_field_theory.md`, Track C derivations | medium-high |
| 6 | Safety floor: ICNIRP, thermal, SAR, dual-MCU checker | `docs/safety.md` | low |
| 7 | Build roadmap Mk0 → Mk3 | `docs/roadmap.md`, `docs/mk_ladder.md` | low |
| 8 | Field Notes (short essays) | **new** | high |
| 9 | Prior art declaration | `PRIOR_ART.md` | minimal |
| 10 | Support, commissions, licensing | `README.md` § Support | minimal |

**Lift ratio**: ~70 % of total length is consolidation/editing of existing repo content. Only § 5 (partial), § 8 (full), and front matter require fresh writing.

## Build pipeline

```
docs/field-notes/volume-1/
  README.md                  ← outline, status, build instructions
  build.sh                   ← pandoc invocation
  metadata.yml               ← title, author, ISBN-free identifier, cover image
  template.tex               ← LaTeX template (pandoc --template=)
  00_frontmatter.md
  01_manifesto.md
  02_platform.md
  03_sister_modules.md
  04_wiki_as_spec.md
  05_field_theory.md
  06_safety_floor.md
  07_roadmap.md
  08_field_notes.md
  09_prior_art.md
  10_support.md
  figures/                   ← png + pdf assets (populated by Track D)
  out/                       ← .gitignored build output
```

`build.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p out
pandoc \
  --metadata-file=metadata.yml \
  --template=template.tex \
  --pdf-engine=xelatex \
  --toc --toc-depth=2 \
  --number-sections \
  --resource-path=.:figures \
  -o out/HelmKit_FieldNotes_Vol1.pdf \
  0[0-9]_*.md 10_*.md
```

## GH Actions PDF build

`.github/workflows/field-notes.yml` runs `build.sh` on every push touching `docs/field-notes/**` and uploads the PDF as an artifact. On tagged release `field-notes-vol1-v1.0.0`, also creates a GitHub Release with the PDF attached.

## Acceptance criteria

1. `bash docs/field-notes/volume-1/build.sh` produces `out/HelmKit_FieldNotes_Vol1.pdf` on a clean clone (with pandoc + TeX Live installed).
2. PDF passes a 3-reader smoke read (one technical, one maker, one wiki-literate). All three can finish without confusion.
3. Every claim in § 5 is either (a) consensus-cited, (b) wiki-cited with pageid+revid, or (c) extrapolated with reasoning shown.
4. Every figure regenerates from a Track D notebook.
5. Output: ≥ 60 pages, ≤ 100 pages.
6. PDF is delivered to all paid Field Notes commissioners within 24 hours of release.

## What ships

- v0 (scaffold): `docs/field-notes/volume-1/` skeleton + `build.sh` + LaTeX template + placeholder PDF. Commit titled `field-notes: scaffold Vol. I pandoc pipeline`.
- v0.5 (content-complete draft): sections 0–10 all drafted, beta-read pending. Commit titled `field-notes: Vol. I content-complete draft`.
- v1.0 (ship): post-beta-read revision. Tag `field-notes-vol1-v1.0.0`. GitHub Release + Ko-fi delivery + announcement post.
