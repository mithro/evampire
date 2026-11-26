# /// script
# requires-python = ">=3.11"
# dependencies = ["gdstk", "shapely"]
# ///
"""Compare the protection devices' sizes in the netlists and the layouts.

Reads each device's size from the CDL netlist of gf180mcu_fd_io__bi_t and
gf180mcu_fd_io__dvdd, measures the same device in the cell's GDS, and
writes both to docs/esd/gds/layout-check.csv. Exits with an error if any
pair differs by more than 1 nm (or 0.001 µm²), or if the nets of the
bidirectional pad do not connect as docs/esd/layout.rst says. GF180_IO names a checkout
of the I/O library, as for figures.py:

    GF180_IO=$PWD/globalfoundries-pdk-libs-gf180mcu_fd_io \\
        uv run docs/esd/gds/check.py

SPDX-License-Identifier: Apache-2.0
"""

import csv
import os
import pathlib
import re
import sys

from shapely.geometry import box

import gdskit

HERE = pathlib.Path(__file__).resolve().parent
UM = 1e6


def netlist(cell):
    """The device lines of a cell's CDL netlist, continuations joined."""
    path = (pathlib.Path(os.environ["GF180_IO"]) / "cells" / cell
            / f"gf180mcu_fd_io__{cell}.cdl")
    text = re.sub(r"\n\+", " ", path.read_text())
    return [line for line in text.splitlines() if line[:1] in "MRDC"]


def value(line, key):
    return float(re.search(rf"(?<![a-z_]){re.escape(key)}=(\S+)", line,
                           re.I).group(1))


def spans(geom, window):
    """(x size, y size) of each polygon of geom inside window, sorted."""
    out = []
    for p in gdskit.parts(geom.intersection(box(*window))):
        x0, y0, x1, y1 = p.bounds
        out.append((round(x1 - x0, 4), round(y1 - y0, 4)))
    return sorted(out)


def same(sizes):
    """The one size shared by every polygon, with how many there are."""
    assert len(set(sizes)) == 1, f"sizes differ: {set(sizes)}"
    return len(sizes), sizes[0]


def driver(lay, window, lines, model):
    """Fingers, width, length and silicide block of an output driver."""
    devs = [line for line in lines if model in line]
    net = {"fingers": sum(value(d, "nf") for d in devs),
           "width": sum(value(d, "w") for d in devs) * UM,
           "length": value(devs[0], "l") * UM,
           "drain block": value(devs[0], "d_sab") * UM,
           "source block": value(devs[0], "s_sab") * UM}
    gates = gdskit.parts(lay["poly"].intersection(lay["comp"])
                         .intersection(box(*window)))
    blocks = gdskit.parts(lay["sab"])
    sides = set()
    for g in gates:
        (b,) = [b for b in blocks if b.intersects(g)]
        over = sorted((round(g.bounds[0] - b.bounds[0], 4),
                       round(b.bounds[2] - g.bounds[2], 4)))
        sides.add(tuple(over))
    (side,) = sides
    count, (length, width) = same(spans(lay["poly"].intersection(lay["comp"]),
                                        window))
    gds = {"fingers": count, "width": count * width, "length": length,
           "drain block": side[1], "source block": side[0]}
    return net, gds


def connections(cell, lines):
    """Check the nets docs/esd/layout.rst describes against the netlist."""
    pad, inn = gdskit.net(cell, "PAD"), gdskit.net(cell, "IN")
    on_pad = [line for line in lines if " PAD " in line]
    fets = [d for d in on_pad if d.startswith("M")]
    # Every driver finger has one drain side, and two fingers share a drain.
    fingers = sum(value(d, "nf") for d in fets)
    drains = len(gdskit.parts(pad["comp"]))
    resistors = len(gdskit.parts(pad["poly"]))
    assert drains * 2 == fingers, (drains, fingers)
    assert resistors == len([d for d in on_pad if d.startswith("R")]) == 4
    assert len(on_pad) == len(fets) + resistors, "something else is on PAD"
    assert len(gdskit.parts(inn["comp"])) == 4, "protected net: diode strips"
    lay = gdskit.load(cell)
    window = box(9.8, 71.8, 65.2, 119.1)       # inside the NMOS P+ ring
    sources = lay["comp"].intersection(window).difference(
        pad["comp"].union(lay["poly"]))
    dvss = gdskit.net(cell, "DVSS")["comp"]
    assert sources.difference(dvss.buffer(0.01)).area < 1e-6, "NMOS on DVSS"
    window = box(10.5, 145.9, 64.5, 186.3)     # the PMOS fingers
    sources = lay["comp"].intersection(window).difference(
        pad["comp"].union(lay["poly"]))
    dvdd = gdskit.net(cell, "DVDD")["comp"]
    assert sources.difference(dvdd.buffer(0.01)).area < 1e-6, "PMOS on DVDD"


def rows():
    out = []

    def add(device, quantity, unit, net, gds):
        out.append((device, quantity, unit, f"{net:g}", f"{gds:g}"))
        if abs(net - gds) > 1e-3:
            raise SystemExit(f"{device}, {quantity}: netlist {net}, "
                             f"layout {gds}")

    lay, lines = gdskit.load("bi_t"), netlist("bi_t")
    for name, window, model in (
            ("NMOS output driver", (13, 74, 62, 115), "nfet_06v0_dss"),
            ("PMOS output driver", (10, 145, 65, 187), "pfet_06v0_dss")):
        net, gds = driver(lay, window, lines, model)
        add(name, "Fingers", "", net["fingers"], gds["fingers"])
        add(name, "Total width", "µm", net["width"], gds["width"])
        add(name, "Gate length", "µm", net["length"], gds["length"])
        add(name, "Silicide block over the drain", "µm", net["drain block"],
            gds["drain block"])
        add(name, "Silicide block over the source", "µm",
            net["source block"], gds["source block"])
    res = [line for line in lines if line.startswith("R")
           and line.split()[1] == "PAD"]
    count, (w, length) = same(spans(lay["resistor"], (30, 268, 45, 276)))
    add("Secondary resistor", "Count", "", len(res), count)
    add("Secondary resistor", "Width", "µm", value(res[0], "$W") * UM, w)
    add("Secondary resistor", "Length", "µm", value(res[0], "$L") * UM,
        length)
    strips = gdskit.net("bi_t", "IN")["comp"]
    for name, model, implant in (
            ("Secondary diode to DVDD", "diode_pd2nw_06v0", "pplus"),
            ("Secondary diode to DVSS", "diode_nd2ps_06v0", "nplus")):
        (dev,) = [line for line in lines if model in line and " n20 " in line]
        parts = gdskit.parts(strips.intersection(lay[implant]))
        (area,) = {round(p.area, 4) for p in parts}
        add(name, "Count", "", value(dev, "m"), len(parts))
        add(name, "Area of each", "µm²", value(dev, "AREA") * UM * UM, area)
    connections("bi_t", lines)

    lay, lines = gdskit.load("dvdd"), netlist("dvdd")
    (fet,) = [line for line in lines if line.startswith("M")
              and value(line, "nf") == 80]
    count, (width, length) = same(spans(
        lay["poly"].intersection(lay["comp"]), (10, 72, 65, 192)))
    add("Clamp transistor", "Fingers", "", value(fet, "nf"), count)
    add("Clamp transistor", "Total width", "µm", value(fet, "w") * UM,
        count * width)
    add("Clamp transistor", "Gate length", "µm", value(fet, "l") * UM, length)
    res = [line for line in lines if line.startswith("R")]
    count, (length, w) = same(spans(lay["resistor"], (0, 270, 75, 300)))
    add("Timer resistor", "Count", "", len(res), count)
    add("Timer resistor", "Width", "µm", value(res[0], "$W") * UM, w)
    add("Timer resistor", "Length", "µm", value(res[0], "$L") * UM, length)
    plates = lay["poly"].intersection(lay["comp"])
    for name, key, window in (("Timer capacitor", "n8", (0, 215, 75, 276)),
                              ("Supply capacitor", "DVDD", (0, 326, 75, 350))):
        (cap,) = [line for line in lines if line.startswith("C")
                  and line.split()[1] == key]
        count, (a, b) = same(spans(plates, window))
        add(name, "Count", "", value(cap, "m"), count)
        add(name, "Plate area of each", "µm²",
            value(cap, "l") * value(cap, "w") * UM * UM, a * b)
    (dio,) = [line for line in lines if line.startswith("D")]
    parts = gdskit.parts(lay["comp"].intersection(lay["diode"]))
    (area,) = {round(p.area, 4) for p in parts}
    add("Supply diode", "Count", "", value(dio, "m"), len(parts))
    add("Supply diode", "Area of each", "µm²", value(dio, "AREA") * UM * UM,
        area)
    return out


def main():
    table = rows()
    with open(HERE / "layout-check.csv", "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["Device", "Quantity", "Unit", "Netlist", "Layout"])
        w.writerows(table)
    print(f"{len(table)} quantities agree; wrote layout-check.csv")


if __name__ == "__main__":
    sys.exit(main())
