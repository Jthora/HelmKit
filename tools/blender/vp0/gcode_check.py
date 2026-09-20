#!/usr/bin/env python3
"""
gcode_check.py -- read what the printer is ACTUALLY told to do, layer by layer (Track P).

Every diagnosis in this campaign so far has argued from settings. This reads the g-code itself, which is the
only ground truth between the slicer and the machine. It needs no printer, no filament and no USB stick: slice
in QIDI Studio, Export G-code to a local folder, and point this at the file.

Per layer it reports: height, extruded filament, travel distance, the longest single travel, how many separate
extrusion runs there are (a proxy for islands and for stop/start blobbing), retractions, z-hops, the shortest
extrusion run (sub-millimetre runs are where blobs come from) and which feature types appear.

Two files given, it prints them side by side and flags the layers where they diverge most. That is the useful
mode: compare a part that printed against one that failed, same printer and material, and read the difference.

Run:  python3 tools/blender/vp0/gcode_check.py FAILED.gcode [GOOD.gcode] [--layers 12] [--full]
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

NUM = re.compile(r"([XYZEF])(-?\d*\.?\d+)")


class Layer:
    __slots__ = ("z", "n", "extrude", "travel", "max_travel", "runs", "retracts", "hops", "min_run", "types")

    def __init__(self, z, n):
        self.z, self.n = z, n
        self.extrude = self.travel = self.max_travel = 0.0
        self.runs = self.retracts = self.hops = 0
        self.min_run = float("inf")
        self.types = []


def parse(path: Path) -> list[Layer]:
    layers: list[Layer] = []
    cur = Layer(0.0, 0)
    x = y = z = 0.0
    run_len = 0.0
    in_run = False
    prev_z = 0.0
    for raw in path.read_text(errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith(";"):
            low = line.lower()
            if low.startswith(";layer_change") or low.startswith(";layer:"):
                if in_run and run_len > 0:
                    cur.min_run = min(cur.min_run, run_len)
                    cur.runs += 1
                if cur.extrude > 0 or cur.travel > 0:
                    layers.append(cur)
                cur = Layer(z, 0)
                run_len, in_run = 0.0, False
            elif low.startswith(";z:"):
                try:
                    cur.z = float(line.split(":", 1)[1])
                except ValueError:
                    pass
            elif line.startswith(";TYPE:"):
                t = line[6:].strip()
                if t and t not in cur.types:
                    cur.types.append(t)
            continue
        if not (line.startswith("G1") or line.startswith("G0")):
            continue
        vals = dict(NUM.findall(line.split(";")[0]))
        nx = float(vals.get("X", x)); ny = float(vals.get("Y", y)); nz = float(vals.get("Z", z))
        e = vals.get("E")
        d = math.dist((x, y), (nx, ny))
        if e is not None:
            ev = float(e)
            if d < 1e-9 and ev < 0:
                cur.retracts += 1
            elif ev > 0 and d > 0:
                cur.extrude += ev
                if not in_run:
                    in_run, run_len = True, 0.0
                run_len += d
        else:
            if in_run:
                if run_len > 0:
                    cur.min_run = min(cur.min_run, run_len)
                    cur.runs += 1
                in_run, run_len = False, 0.0
            if d > 0:
                cur.travel += d
                cur.max_travel = max(cur.max_travel, d)
            if nz > z + 1e-9 and abs(nz - prev_z) < 1.0 and vals.get("X") is None and vals.get("Y") is None:
                cur.hops += 1
        if nz != z:
            prev_z = z
        x, y, z = nx, ny, nz
    if in_run and run_len > 0:
        cur.min_run = min(cur.min_run, run_len)
        cur.runs += 1
    if cur.extrude > 0 or cur.travel > 0:
        layers.append(cur)
    for i, l in enumerate(layers):
        l.n = i + 1
        if l.z == 0.0 and i:                 # no ;Z: comment in this flavour: fall back to the move height
            l.z = layers[i - 1].z
    return layers


def show(name: str, ls: list[Layer], limit: int) -> None:
    print(f"\n=== {name}   ({len(ls)} layers)")
    print(f"{'lyr':>4} {'z':>6} {'extr mm':>8} {'travel':>8} {'maxtrv':>7} {'runs':>5} {'retr':>5} {'hops':>5} {'minrun':>7}  features")
    for l in ls[:limit]:
        mr = "-" if l.min_run == float("inf") else f"{l.min_run:.2f}"
        print(f"{l.n:>4} {l.z:>6.2f} {l.extrude:>8.1f} {l.travel:>8.0f} {l.max_travel:>7.0f} {l.runs:>5} "
              f"{l.retracts:>5} {l.hops:>5} {mr:>7}  {','.join(l.types[:4])}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--layers", type=int, default=12, help="how many layers to print (default 12)")
    ap.add_argument("--full", action="store_true", help="every layer")
    args = ap.parse_args(argv)
    sets = []
    for f in args.files:
        if not f.exists():
            print(f"missing: {f}", file=sys.stderr)
            return 2
        ls = parse(f)
        sets.append((f.name, ls))
        show(f.name, ls, len(ls) if args.full else args.layers)

    if len(sets) == 2:
        (na, a), (nb, b) = sets
        print(f"\n=== {na} vs {nb}: the first {min(len(a), len(b), args.layers)} layers")
        print(f"{'lyr':>4} {'runs':>13} {'travel':>15} {'minrun':>15}")
        for i in range(min(len(a), len(b), args.layers)):
            print(f"{i+1:>4} {a[i].runs:>6} /{b[i].runs:>6} {a[i].travel:>7.0f} /{b[i].travel:>7.0f} "
                  f"{(a[i].min_run if a[i].min_run != float('inf') else 0):>7.2f} /"
                  f"{(b[i].min_run if b[i].min_run != float('inf') else 0):>6.2f}")
    print("\nWhat to look for: a layer where `runs` jumps sharply (many separate stop/start extrusions),"
          "\n`minrun` falling below about 1 mm (blob-sized dabs the nozzle can catch), `maxtrv` crossing the"
          "\nwhole plate with `hops` at zero (the nozzle dragging over printed work), or travel far exceeding"
          "\nthe part that printed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
