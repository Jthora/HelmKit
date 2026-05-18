# Sequencing — May 18 2026 → August 2026

Stack-ranked by **expected value × independence-from-blockers**. Updated as tracks land.

---

## Week of May 18 (this week)

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon (today) | **B** | Build `tools/wiki_sync.py`, seed `tools/wiki_pages.yml` from `docs/wiki_anchors.md` | 4 | First sync run produces `docs/wiki_cache/` baseline. |
| Mon (today) | **G** | Cut + post one TikTok pointing at Ko-fi. X + Ko-fi update post. | 0.5 | 3 posts live, 3 inbound channels primed. |
| Tue | **F** | Scaffold `docs/field-notes/volume-1/` skeleton + `build.sh` (pandoc → PDF) + LaTeX template + GH Actions PDF build. | 4 | `make field-notes` produces a placeholder PDF. |
| Tue | **G** | Finish remaining 3 Ko-fi commissions (Tier 1 DIY, Tier 2 Hand-Built, Custom). | 1 | All 4 commission listings live. |
| Wed–Fri | **E** | Wave M1 firmware: MAX30102 driver + Pan-Tompkins R-peak + `ch:"rr-ms"` NDJSON. | 12 | RR intervals streaming over BLE NDJSON. |

---

## Week of May 25

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon–Wed | **F** | Field Notes Vol. I: write sections 1, 2, 3 (manifesto, platform, sister modules) — 70% lift from existing docs. | 9 | Three sections in draft. |
| Thu–Fri | **C** | `docs/derivations/bifilar_near_field_enhancement.md` — analytic E²+B²/μ₀ enhancement factor, 2-loop model. | 8 | Derivation doc + figures. |
| Ongoing | **G** | 5 cold-lead emails/day from `docs/outreach/cold-lead-email.md`. | 0.5/day | Re-engagement funnel active. |

---

## Week of June 1

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon–Wed | **F** | Field Notes Vol. I: write sections 5, 6 (field theory, safety floor). | 9 | Two sections drafted. |
| Thu | **D** | Notebook `notebooks/bifilar_near_field.ipynb` — plots for derivation + Vol. I figure 4. | 4 | One reproducible figure. |
| Fri | **H** | Repo hygiene: `tools/check_links.py` + `tools/check_wiki_urls.py` + pre-commit hook. | 4 | CI gates broken links on PR. |

---

## Week of June 8

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon–Wed | **F** | Sections 4 (wiki-as-spec), 7 (roadmap), 9 (prior-art), 10 (support) — mostly lift. | 8 | Vol. I content-complete. |
| Thu | **F** | Section 8 (Field Notes — short essays) — only fully-new writing. | 6 | Vol. I draft-complete. |
| Fri | **F** | Editing pass + figures + cover. | 4 | PDF ready for review. |

---

## Week of June 15

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon | **F** | Beta-read by 2–3 trusted readers. | — | Feedback. |
| Tue–Wed | **F** | Revise. | 6 | Vol. I final. |
| Thu | **F + G** | Ship Vol. I to Ko-fi Field Notes commissioners. Announce on TikTok / X. | 2 | **Tier 1 product shipped.** |
| Fri | **G** | Open the Tier 1 DIY Build Kit Ko-fi commission for pre-orders. | — | Tier 1 DIY pipeline active. |

---

## Week of June 22 (post-Vol. I bridge)

| Day | Track | Action | Hrs | Output |
|-----|-------|--------|-----|--------|
| Mon | **I** | Mk0.5 BOM + wiring doc; place parts order EOD. | 3 | `docs/firmware/mk0.5_bom.md`, `docs/firmware/mk0.5_wiring.md`. |
| Tue | **I** | G2 validation protocol + oracle-device decision doc. | 3 | `docs/protocols/g2_hrv_validation.md`, `docs/protocols/g2_oracle_device.md`. |
| Wed | **I** | `tools/capture_ndjson.py` + PPG mounting notes. | 2 | Serial capture path tested against fixture; mechanical primer for bench. |

Parts in hand by end of week; first physical Mk0.5 session opens early July.

---

## After Vol. I ships (late June → August)

- Resume **Track A** as soon as wiki drop lands (run Track B sync, triage).
- **Track I** (pre-hardware sprint) lands week of June 22 — see above.
- Begin Mk0.5 physical bench bring-up (early July) — unblocks the deferred G2 HRV validation gate from Track E.
- Tier 1 DIY Build Kit content production: BOM (already done in Track I), schematic export, build guide PDF, 3MF/STL pack, firmware binary release.
- Target: **Tier 1 DIY ships August 2026.**

---

## Gating dependencies

```
B (wiki-sync) ──────────────┐
                            ▼
             [wiki drop] ─► A (engineering translation)

F (field notes PDF) ◄── C (bifilar derivation, optional but boosts Vol. I)
                    ◄── D (notebook figures, optional)

Tier 1 DIY (August) ◄── E (Wave J firmware, for honest demo) — dsp-landed
                    ◄── I (pre-hardware sprint: BOM, wiring, G2, capture)
                    ◄── Mk0.5 physical build (for build-guide photos + G2 data)

Tier 2 Hand-Built (Sept–Oct) ◄── Tier 1 DIY shipped
                              ◄── Illinois LLC formed
                              ◄── Attorney review of terms-of-sale
```

---

## What we are **not** doing this period

- Track A engineering-translation docs (wiki-blocked).
- LLC formation (deferred until first physical Tier 2 shipment imminent).
- Attorney review (deferred, $400–600 budget, before first Tier 2 ship).
- Mk1 SAR/FDTD work (Mk1 is a Q4 2026 / 2027 problem).
- iOS app revival (`iOS_oldBuild/` stays archived).
