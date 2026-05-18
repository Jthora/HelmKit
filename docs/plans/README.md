# Plans

Phase-scoped execution plans for HelmKit. Each subdirectory is one **phase** with its own track docs, sequencing, and acceptance criteria.

A phase is a time-bounded, goal-bounded slice of project work. When a phase ships (or is abandoned), its directory remains as the historical record — do not delete.

## Phases

| Phase | Window | Goal | Status |
|-------|--------|------|--------|
| [`2026-tier1-launch/`](2026-tier1-launch/README.md) | May 2026 → August 2026 | Ship Tier 1 Field Notes PDF + open Tier 1 DIY pre-orders | active |

## Naming convention

`<year>-<short-slug>/` — slug describes the *goal*, not the *date*. Examples of future phases:

- `2026-tier1-ship/` — once Field Notes ships, the next phase is shipping the Tier 1 DIY Build Kit.
- `2026-q4-mk1-design/` — Mk1 design and SAR/FDTD work.
- `2027-mk1-build/` — Mk1 physical build.
- `2027-mk2-rf-review/` — Mk2 high-power-RF safety/regulatory review.

## When to start a new phase

Start a new phase directory when:

1. The current phase's goal is met (ship event) or abandoned (with a written `POSTMORTEM.md` in the closed phase dir).
2. The next chunk of work has a different set of acceptance criteria (different "done" definition).
3. The new chunk depends on the current phase's output (i.e. it can't start in parallel).

For parallel-but-independent work, do **not** start a new phase — add a track to the current phase.

## Cross-phase tracking

The top-level [`docs/roadmap.md`](../roadmap.md) is the multi-year strategic view (Mk0 → Mk3). The phase plans here are the **tactical** view inside each strategic window.
