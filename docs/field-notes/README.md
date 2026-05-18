# HelmKit Field Notes

A series of polished, citable PDFs documenting the engineering, theory, and discipline behind the HelmKit open psionic platform.

These are the Tier 1 sellable artifacts of the project. They are also the public record of the work.

**Track plan**: [`../plans/2026-tier1-launch/track-F-field-notes-vol-1.md`](../plans/2026-tier1-launch/track-F-field-notes-vol-1.md)

## Volumes

| # | Title | Status | Target ship |
|---|-------|--------|-------------|
| I | The Platform — manifesto, architecture, safety floor, falsification | scaffolding | late June 2026 |
| II | (TBD — likely Mk1 derivations + measurement results) | not planned | 2027 |

## Build

Each volume builds with `pandoc` + `xelatex` via its own `build.sh`. See [`volume-1/README.md`](volume-1/README.md).

## Distribution

- **Ko-fi Field Notes commission** ($9 + PWYW): paid commissioners receive the PDF within 24 h of release.
- **GitHub Release** tagged `field-notes-vol<N>-v<X.Y.Z>`: PDF attached as release asset.
- **Zenodo DOI**: minted per major version (the project already has DOI `10.5281/zenodo.20183949` for the repo; per-volume DOIs to be minted on first major release).
