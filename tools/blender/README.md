# `tools/blender/` — parametric mesh generators

Scripts here generate HelmKit's printable parts deterministically
from canon parameters in `docs/mechanical/`. Treat the scripts as
the **authoritative shape definition**; the generated STLs in
`3D-Models/HelmKit/_generated/` are derivative artifacts that
should be regenerable on demand.

## Run

All scripts run headless inside Blender:

```sh
blender --background --python tools/blender/<script>.py -- --out <path>
```

On macOS with Blender installed at the default location:

```sh
/Applications/Blender.app/Contents/MacOS/Blender \
    --background --python tools/blender/build_crown_shell_r1.py -- \
    --out 3D-Models/HelmKit/_generated/crown_shell_R1.stl
```

## Scripts

| Script | Output | Status |
|---|---|---|
| [`build_crown_shell_r1.py`](build_crown_shell_r1.py) | `crown_shell_R1.stl` (220° forward band + integral curved Picatinny rail body) | SCAFFOLD — rail body sweeps correctly; **tooth slots not yet subtracted** (see G-Print gate). |

## Canon source

All parameters trace back to
[`docs/mechanical/mk0.5_base_crown_architecture.md`](../../docs/mechanical/mk0.5_base_crown_architecture.md).
If a script's hard-coded constant disagrees with that doc, the
doc wins and the script is wrong.

## License hygiene

Scripts here may *reference* (read, measure) third-party STLs
under `3D-Models/HelmKit/_derived/` but must produce **original
HelmKit geometry**. The Picatinny tooth dimensions used in
`build_crown_shell_r1.py` come from MIL-STD-1913 (US-government
public spec), not from any third-party CC-licensed STL.
