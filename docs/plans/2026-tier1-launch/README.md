# HelmKit — Active Plan (May 2026)

This folder is the **operational plan** for HelmKit work between now (May 18 2026) and the Tier 1 Field Notes ship date (target: late June / early July 2026).

It is updated as tracks land. When a track completes, its design doc gets a `status: done` line at top and the master sequencing table below gets ticked.

---

## Context snapshot

- **Tier 1 sellable artifact**: Field Notes Vol. I (digital PDF), $9 + PWYW, target ship **late June 2026**.
- **Tier 1 DIY Build Kit** (digital, $35) target **August 2026** — needs working L1 firmware demo to be honest.
- **Tier 2 Hand-Built Unit** ($500 deposit) target **Sept–Oct 2026** — needs physical Mk0.5 build complete.
- **Custom Commission** ($5k+) — open immediately; 8–12 week lead.
- **Ko-fi page** live at `ko-fi.com/helmkit`. Funding URLs aligned across all 3 repos (commits `7f0fc91`, `c3c4600`, `800fa84`).
- **Wiki-side**: the FusionGirl wiki AI agent is doing a major content expansion in response to engineering critiques. Any work that depends on new wiki content is `blocked-pending` until that drop lands.

---

## Tracks

| ID | Track | Status | Wiki-blocked? | Design doc |
|----|-------|--------|---------------|------------|
| **A** | Wiki content → engineering translation | `blocked-pending` | yes | [track-A-wiki-translation.md](track-A-wiki-translation.md) |
| **B** | `tools/wiki_sync.py` — auto-ingestion tool | `done` (commit `31ea41a`) | no | [track-B-wiki-sync-tool.md](track-B-wiki-sync-tool.md) |
| **C** | Original math derivations (`docs/derivations/`) | `v0` (bifilar landed) | no | [track-C-derivations.md](track-C-derivations.md) |
| **D** | Executable notebooks (figures for Field Notes) | `v0` (script-only; `.ipynb` deferred) | no | [track-D-notebooks.md](track-D-notebooks.md) |
| **E** | Firmware Wave M1 (MAX30102 + R-peak + RR NDJSON) | `dsp-landed; pending on-target validation` | no | [track-E-firmware-wave-m1.md](track-E-firmware-wave-m1.md) |
| **F** | Field Notes Vol. I (Tier 1 PDF artifact) | `v0-complete` (§§0-10 all drafted) | no | [track-F-field-notes-vol-1.md](track-F-field-notes-vol-1.md) |
| **G** | Social launch + cold-lead outreach | `posts-drafted` | no | [track-G-social-launch.md](track-G-social-launch.md) |
| **H** | Repo hygiene (link-check, wiki-URL probe, pre-commit) | `landed` (tools + CI gate + allowlist) | no | [track-H-repo-hygiene.md](track-H-repo-hygiene.md) |
| **I** | Pre-Hardware Sprint (Mk0.5 BOM + wiring + G2 protocol + capture tool) | `landed` | no | [track-I-pre-hardware-sprint.md](track-I-pre-hardware-sprint.md) |

---

## Sequencing

See [sequencing.md](sequencing.md) for the week-by-week stack-rank and the gating dependencies between tracks.

Short version:

1. **Today**: Track B (wiki-sync tool) + Track G (social announcement).
2. **Tomorrow**: Track F scaffolding (pandoc pipeline + outline).
3. **This week**: Track E (Wave M1 firmware).
4. **Next week**: Track F (Field Notes content), Track C (bifilar derivation), Track D (notebooks for Vol. I figures).
5. **Ongoing**: Track G (cold leads, ~5/day), Track H (one-off when convenient).
6. **When wiki drop lands**: unblock Track A, run Track B against new content, triage into new engineering-translation docs.

---

## Artifact directories

The tracks produce content under these new subdirectories:

- [`docs/derivations/`](../../derivations/) — original math, Track C
- [`docs/field-notes/`](../../field-notes/) — Field Notes Vol. I et seq., Track F
- [`docs/tools/`](../../tools/) — design docs for tooling (Track B, Track H). Actual tool code lives at repo root under `tools/`.
- [`docs/firmware/`](../../firmware/) — firmware feature plans (Track E and beyond). Actual firmware code lives at `firmware/`.

---

## Update protocol

When a track ships:

1. Edit its design doc: set `status:` to `done`, add a "What shipped" section with commit SHAs.
2. Tick the row in the table above.
3. Update [sequencing.md](sequencing.md) if downstream tracks unblock.
4. Do **not** delete completed track docs — they are the project record.

When the wiki drop lands:

1. Run `tools/wiki_sync.py` (once Track B is built).
2. Triage diff into Track A engineering-translation docs.
3. Move Track A from `blocked-pending` to `in-progress`.
