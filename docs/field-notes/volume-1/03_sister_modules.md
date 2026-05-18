# Sister modules

<!-- Source: external/psiStabilizer/README.md, external/psionicDefender/README.md
     Status: stub
     TODO: brief functional spec for each sister module:
             - Psi Defender (outward / environment / RF + acoustic + EM)
             - Psi Stabilizer (inward / self / EEG + HRV + GSR)
           Explain how each mounts to a HelmKit hardpoint and which bus
           channels it consumes.
-->

The HelmKit is the integration point for two sister-module families:

- **Psi Defender** — outward-facing modules that sense and respond to the
  ambient environment (RF, acoustic, EM).
- **Psi Stabilizer** — inward-facing modules that sense the wearer's
  physiological state (EEG, HRV, GSR) and provide gentle entrainment
  feedback.

Each family is its own repository and its own engineering arc. The HelmKit
hosts them: frame, hardpoints, power, data bus.
