# HelmKit Field Notes — Volume I

**Status**: scaffold complete; section stubs in place; content drafting next
**Target ship**: late June 2026
**Track plan**: [`../../plans/2026-tier1-launch/track-F-field-notes-vol-1.md`](../../plans/2026-tier1-launch/track-F-field-notes-vol-1.md)

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

Requires `pandoc` (>= 3.0) and one of: `tectonic`, `xelatex`, `lualatex`.
Tectonic is preferred (self-contained, reproducible). macOS:

```bash
brew install pandoc tectonic
```

Linux:

```bash
sudo apt-get install pandoc
cargo install tectonic
```

The build script auto-picks the first available engine.

## Files in this directory

```
build.sh                  ← pandoc invocation; chooses tectonic/xelatex/lualatex
metadata.yml              ← title / author / geometry / KOMA scrartcl config
00_frontmatter.md         ← trademark, disclaimer, license summary
01_manifesto.md           ← stub: AI-assistant epistemic stance + discipline
02_platform.md            ← stub: frame + hardpoints + L2 bus
03_sister_modules.md      ← stub: Psi Defender + Psi Stabilizer
04_wiki_as_spec.md        ← stub: wiki-as-design-source + wiki_sync
05_field_theory.md        ← stub: near-field / bifilar / Schumann
06_safety_floor.md        ← stub: ICNIRP / IEEE C95.1 / dual-MCU checker
07_roadmap.md             ← stub: Mk0 → Mk3 + Tier 1–Tier 2 schedule
08_field_notes.md         ← stub: bench session entries (to be populated)
09_prior_art.md           ← stub: annotated bibliography
10_support.md             ← stub: four-doors CTA + acknowledgements
figures/                  ← populated by Track D notebooks (.gitkeep present)
out/                      ← .gitignored
```

Each stub file carries an HTML comment block at the top with its **Source**,
**Status**, and **TODO** so any author (human or AI) can pick it up cold.

## Acceptance for v1.0 ship

See [`../../plans/2026-tier1-launch/track-F-field-notes-vol-1.md#acceptance-criteria`](../../plans/2026-tier1-launch/track-F-field-notes-vol-1.md).

## Working log

- 2026-05-18: Scaffold directory + plan doc created. No content yet.
- 2026-05-18: Track F v0 scaffold landed — `build.sh`, `metadata.yml`, 11 section
  stubs with source / TODO comment blocks, `figures/.gitkeep`, `.gitignore`
  excluding `out/`. Pandoc HTML render smoke-tested OK (271 lines of HTML
  produced from the 11 stubs with full ToC); PDF render path now
  prefers `tectonic` if installed.
