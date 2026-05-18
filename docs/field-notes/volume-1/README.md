# HelmKit Field Notes — Volume I

**Status**: scaffolding (no content drafted yet — only this outline)
**Target ship**: late June 2026
**Track plan**: [`../../plan/track-F-field-notes-vol-1.md`](../../plan/track-F-field-notes-vol-1.md)

---

## Outline

| § | File | Title | Source | New writing |
|---|------|-------|--------|-------------|
| 0 | `00_frontmatter.md` | Title, copyright, disclaimer, ToC | `NOTICE.md`, `docs/legal/*` | minimal |
| 1 | `01_manifesto.md` | An open psionic platform | `README.md` AI-stance section | medium |
| 2 | `02_platform.md` | The HelmKit platform | `docs/architecture.md`, `docs/roadmap.md` | low |
| 3 | `03_sister_modules.md` | Psi Defender, Psi Stabilizer | sister-repo READMEs | low |
| 4 | `04_wiki_as_spec.md` | The wiki as design specification | `docs/wiki_anchors.md`, `docs/wiki_synthesis.md` | medium |
| 5 | `05_field_theory.md` | ψ-field, coupling, geometries | `docs/psionics_field_theory.md`, Track C derivations | medium-high |
| 6 | `06_safety_floor.md` | ICNIRP, thermal, SAR, dual-MCU checker | `docs/safety.md` | low |
| 7 | `07_roadmap.md` | Build roadmap Mk0 → Mk3 | `docs/roadmap.md`, `docs/mk_ladder.md` | low |
| 8 | `08_field_notes.md` | Field Notes (short essays) | **new** | high |
| 9 | `09_prior_art.md` | Prior art declaration | `PRIOR_ART.md` | minimal |
| 10 | `10_support.md` | Support, commissions, licensing | `README.md` Support section | minimal |

## Build

```bash
bash build.sh
# → out/HelmKit_FieldNotes_Vol1.pdf
```

Requires `pandoc` and a TeX Live install with `xelatex`. macOS:

```bash
brew install pandoc
brew install --cask mactex-no-gui
```

## Files to be created (in this directory)

```
build.sh
metadata.yml
template.tex
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
figures/          ← populated by Track D notebooks
out/              ← .gitignored
```

## Acceptance for v1.0 ship

See [`../../plan/track-F-field-notes-vol-1.md#acceptance-criteria`](../../plan/track-F-field-notes-vol-1.md).

## Working log

- 2026-05-18: Scaffold directory + plan doc created. No content yet.
