# Safety floor

<!-- Source: docs/legal/disclaimer.md, IEEE C95.1, ICNIRP 2020
     Status: stub
     TODO: SAR ceilings, peak SAR at 10 g averaged, distance / duty rules,
           thermal floor, acoustic SPL ceilings, dual-MCU checker pattern
           description, hardware kill switches, and the "not a medical
           device" repeat callout.
-->

The HelmKit platform commits to a hard safety floor: every emitter has
both a software ceiling and an independent hardware ceiling. Specific
Absorption Rate (SAR) is gated by [IEEE C95.1](https://standards.ieee.org/ieee/C95.1/7064/)
and [ICNIRP 2020](https://www.icnirp.org/cms/upload/publications/ICNIRPrfgdl2020.pdf)
guidelines for whole-head exposure. A dual-MCU checker pattern monitors
the emitter MCU and trips a hardware kill on any out-of-bounds reading.

(Detailed numbers and circuit diagrams to follow.)
