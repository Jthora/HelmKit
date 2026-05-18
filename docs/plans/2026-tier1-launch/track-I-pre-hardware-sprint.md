# Track I — Pre-Hardware Sprint (Mk0.5 bench bring-up scaffolding)

- **Status**: `scoped`
- **Effort**: ~6–9 hours across 6 commits
- **Depends on**: Track E Wave J `dsp-landed` (`11f9fb9`). No further code prerequisites.
- **Unblocks**:
  - First on-bench Mk0.5 power-on session (procure → wire → boot → stream).
  - G2 HRV validation gate deferred from Track E.
  - Tier 1 DIY Build Kit content (BOM and wiring doc are reusable as kit collateral).
  - Tier 2 Hand-Built physical prototype work.

---

## Goal

Close the **scaffolding gap** between "firmware functionally complete"
(Wave J) and "operator can sit down at a bench and actually run the
device." Every artifact in this track is a small, cheap-to-write
document or tool that, if missing, turns the first physical session
into improvisation.

Explicit non-goals:

- **No new firmware features.** Wave J is honestly enough for a
  first wrist session.
- **No final enclosure design.** First physical session is breadboard
  + tape + cardboard. Enclosure design follows from what the bench
  teaches us about PPG mechanical coupling — not the other way around.
- **No BLE / wireless uplift.** USB-CDC NDJSON is the bench transport.
- **No SpO2 / multi-channel sensor expansion.** PPG-only retires G2.

---

## Inventory of artifacts (six commits)

Each row is one commit, scoped to a single artifact. Order is
optimised so each commit unblocks the next decision.

| # | Path | Purpose | Notes |
|---|------|---------|-------|
| 1 | `docs/firmware/mk0.5_bom.md` | Exact parts, vendor links, total cost, lead times. | Single source of truth for ordering. Lists Heltec WiFi LoRa 32 V3, MAX30102 breakout (SparkFun or Adafruit, not Aliexpress clone), JST/jumper wires, Li-Po cell, USB-C cable, optional reference device (Polar H10). |
| 2 | `docs/firmware/mk0.5_wiring.md` | Single-page pinout: Heltec V3 GPIO ↔ MAX30102 pad. | ASCII sketch + table. Each row quotes the matching `board.h` constant. Includes power topology (3v3 vs Vbus) and decoupling notes. Resolves the `kExtI2cSda` / `kExtI2cScl` reverse-lookup that today requires `grep`. |
| 3 | `docs/protocols/g2_hrv_validation.md` | Written G2 test procedure. | The 5/5/5 protocol: 5 min seated baseline → 5 min paced 6 br/min → 5 min recovery. Records device-under-test ppg-rr stream + reference oracle stream simultaneously. Pass band: |RMSSD_DUT − RMSSD_ref| / RMSSD_ref ≤ 20 % across the paced-breathing window. Includes data-storage layout and the analysis script entry point. |
| 4 | `tools/capture_ndjson.py` | Serial → file capture. | ~50 lines, pure stdlib + `pyserial`. Opens `/dev/tty.usbserial-*` (or env override), reads line-buffered, writes timestamped `.ndjson` to `captures/<UTC-ISO>_<label>.ndjson`. Honours Ctrl-C cleanly. Has a `--replay-fixture` mode that reads a recorded fixture instead of the serial port, so the capture path itself is testable. |
| 5 | `docs/mechanical/ppg_mounting_notes.md` | Half-page primer on PPG mechanical coupling. | What "good" looks like: skin pressure (firm but not blanching), ambient-light shroud (any opaque tape works on the bench), motion isolation (forearm rest), finger-vs-wrist tradeoff (finger first — known-good for getting bench data; wrist is the eventual product geometry). |
| 6 | `docs/protocols/g2_oracle_device.md` | Identify and document the reference truth source. | Decision doc: which oracle device, why, SDK / capture-tool status, where its RR stream gets written so the G2 analysis can consume both streams uniformly. Default recommendation: Polar H10 chest strap via the Polar Sensor Logger Android app exporting CSV. |

Total: 4 docs + 1 tool + 1 decision doc.

---

## Acceptance criteria

The sprint is `done` when **all** of the following hold:

1. The six files above exist on `master`.
2. `tools/capture_ndjson.py --replay-fixture <fixture.ndjson>` round-trips
   a known fixture to an output file byte-identically (modulo the
   header timestamp).
3. The Track H lint gate still passes (`tools/check_links.py` +
   `tools/check_wiki_urls.py`), i.e. all links in the new docs
   resolve.
4. The Mk0.5 BOM, when summed, produces a total under **$80** for
   the bench-prototype configuration (not including the oracle
   device).
5. The wiring doc's pin table is **mechanically verified** against
   `firmware/mk0.5/src/board/board.h` — there is a comment in each
   row referencing the constant it pairs with, and a `grep` confirms
   no orphaned pin constants.
6. The G2 protocol doc names a concrete pass criterion (the 20 %
   RMSSD band above, or a written justification for changing it).

---

## What this track does **not** decide

- The actual numerical value of `RMSSD_ref` for any given operator —
  that's data, not protocol.
- Whether the wrist or finger geometry wins long-term — bench data
  decides.
- The Mk1 BOM. Mk0.5 only.
- Enclosure CAD. Defers to the post-bench mechanical track.

---

## Sequencing

Slot into the existing plan as the **bridge between Vol. I shipping
and Mk0.5 physical bring-up**. The current sequencing doc already
notes "Begin Mk0.5 physical prototype build" in the post-Vol. I
window; Track I is the structured version of that prep.

Recommended placement: **week of June 22** (the week after Vol. I
ships), three days, six commits. Detailed slot:

| Day | Commits | Hrs |
|-----|---------|-----|
| Mon | 1 (BOM), 2 (wiring) | 3 |
| Tue | 3 (G2 protocol), 6 (oracle device) | 3 |
| Wed | 4 (capture tool), 5 (PPG mounting notes) | 2 |

Parts order goes out at end of day Monday (BOM in hand). With typical
US lead times (3–7 days), parts arrive same week as the sprint
finishes; the **first physical session is then early July**, after
Vol. I has shipped and before the Tier 1 DIY content window opens.

---

## Risks

1. **BOM drift**: a part goes out of stock between scoping and ordering.
   Mitigation: BOM lists primary + one backup vendor per part.
2. **Oracle device delay**: Polar H10 has a long-running app/SDK
   situation. Mitigation: commit 6 evaluates alternatives (Wahoo
   TICKR, Garmin HRM-Dual) and the fallback choice is captured in
   the doc, not in a comment thread.
3. **Wiring doc rots**: `board.h` constants change. Mitigation: the
   acceptance criterion's `grep` requirement is also a CI candidate —
   if this track lands cleanly, a tiny `tools/check_pinout.py` is a
   natural Track H follow-up (out of scope for Track I itself).

---

## What shipped

(Populated as commits land. Empty at scoping time.)
