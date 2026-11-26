"""Read gf180mcu_fd_io cell layouts and pick out their layers and nets.

Helper for figures.py: run that script, not this module. The cells come
from a checkout of the foundry I/O library named by the environment
variable GF180_IO, at the commit docs/esd/simulation.rst pins.

SPDX-License-Identifier: Apache-2.0
"""

import functools
import os
import pathlib

import gdstk
import shapely
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# GDS layer and datatype of each gf180mcu layer the figures draw.
LAYERS = {
    "nwell": (21, 0), "pwell": (204, 0), "comp": (22, 0), "poly": (30, 0),
    "pplus": (31, 0), "nplus": (32, 0), "sab": (49, 0), "contact": (33, 0),
    "metal1": (34, 0), "via1": (35, 0), "metal2": (36, 0), "via2": (38, 0),
    "metal3": (42, 0), "via3": (40, 0), "metal4": (46, 0), "via4": (41, 0),
    "metal5": (81, 0), "pad": (37, 0), "resistor": (110, 5),
    "diode": (115, 5), "moscap": (166, 5), "esd": (24, 5),
}
# The metal stack from the silicon up: each conductor and the cut above it.
STACK = [("comp", "contact"), ("poly", "contact"), ("metal1", "via1"),
         ("metal2", "via2"), ("metal3", "via3"), ("metal4", "via4"),
         ("metal5", None)]


def cell_path(cell):
    root = pathlib.Path(os.environ["GF180_IO"]) / "cells"
    return root / cell / f"gf180mcu_fd_io__{cell}_5lm.gds"


CACHE = pathlib.Path(__file__).resolve().parent / "cache"
CUTS = {"contact", "via1", "via2", "via3", "via4"}


@functools.cache
def _flat(cell):
    lib = gdstk.read_gds(str(cell_path(cell)))
    return lib.top_level()[0].flatten()


class Cell(dict):
    """{layer name: merged shapely geometry}, each merged when first used.

    Merging the hundred thousand cuts of a pad cell takes minutes, so each
    merged layer is kept in the git-ignored cache folder beside this file.
    """

    def __init__(self, cell):
        super().__init__()
        self.cell = cell

    def __missing__(self, name):
        key = LAYERS[name]
        src = cell_path(self.cell)
        file = CACHE / f"{self.cell}-{name}-{int(src.stat().st_mtime)}.wkb"
        if file.exists():
            geom = shapely.from_wkb(file.read_bytes())
        else:
            flat = _flat(self.cell)
            # Wires drawn as paths count too: convert them to polygons.
            shapes = flat.polygons + [q for p in flat.paths
                                      for q in p.to_polygons()]
            polys = [Polygon(p.points) for p in shapes
                     if (p.layer, p.datatype) == key]
            polys = [p if p.is_valid else p.buffer(0) for p in polys]
            if name in CUTS:   # cuts never overlap: no merge needed
                geom = shapely.MultiPolygon(polys)
            else:
                geom = unary_union(polys)
            CACHE.mkdir(exist_ok=True)
            file.write_bytes(shapely.to_wkb(geom))
        self[name] = geom
        return geom


@functools.cache
def load(cell):
    """Return the layers of the flattened cell, by name."""
    return Cell(cell)


@functools.cache
def labels(cell):
    """Return [(text, x, y, gds layer)] of the flattened cell's labels."""
    return [(t.text, t.origin[0], t.origin[1], t.layer)
            for t in _flat(cell).labels]


def parts(geom):
    """The polygons of a geometry, as a list."""
    if geom.is_empty:
        return []
    if geom.geom_type == "Polygon":
        return [geom]
    return [g for g in getattr(geom, "geoms", []) if g.geom_type == "Polygon"]


def clip(geom, window):
    """The part of a geometry inside window (x0, y0, x1, y1)."""
    return geom.intersection(box(*window))


def bounds(cell):
    lay = load(cell)
    return unary_union([lay["metal5"], lay["nwell"], lay["comp"]]).bounds


# Where each net of interest starts: (layer, x, y) of one of its shapes.
# PAD and the supplies start on their metal 5 labels; IN is the unlabelled
# net between the secondary resistors and the input buffer.
STARTS = {
    "bi_t": {"PAD": ("metal5", 37.5, 32.0), "DVDD": ("metal5", 3.925, 189.35),
             "DVSS": ("metal5", 3.58, 94.16), "IN": ("poly", 32.85, 273.9)},
    "dvdd": {"DVDD": ("metal5", 38.9, 34.27), "DVSS": ("metal5", 3.58, 94.16)},
    "dvss": {"DVSS": ("metal5", 37.98, 32.73),
             "DVDD": ("metal5", 3.925, 189.35)},
}


def net(cell, name):
    """The shapes of a named net of a cell, by layer."""
    return trace(cell, *STARTS[cell][name])


@functools.cache
def trace(cell, layer, x, y):
    """Follow a net from the shape of layer at (x, y) through the stack.

    Returns {layer name: geometry on the net}. Comp and poly join the net
    only through contacts, and a transistor channel does not conduct.
    """
    lay = load(cell)
    shapes = {}
    for name in ("metal1", "metal2", "metal3", "metal4", "metal5"):
        shapes[name] = parts(lay[name])
    # A polysilicon resistor's body separates its two ends.
    shapes["poly"] = parts(lay["poly"].difference(lay["resistor"]))
    # Diffusion is cut by the gates that cross it.
    shapes["comp"] = parts(lay["comp"].difference(lay["poly"]))
    trees = {n: shapely.STRtree(s) for n, s in shapes.items()}
    cuts = {}
    for lower, cut in STACK:
        if cut:
            cuts.setdefault(cut, shapely.STRtree(parts(lay[cut])))
    above = {"comp": ["metal1"], "poly": ["metal1"], "metal1": ["metal2"],
             "metal2": ["metal3"], "metal3": ["metal4"], "metal4": ["metal5"]}
    cut_of = dict(STACK)
    below = {"metal1": ["comp", "poly"], "metal2": ["metal1"],
             "metal3": ["metal2"], "metal4": ["metal3"], "metal5": ["metal4"]}
    pt = shapely.Point(x, y)
    start = [i for i in trees[layer].query(pt, "intersects")]
    if not start:
        raise ValueError(f"no {layer} at ({x}, {y}) in {cell}")
    seen = {(layer, int(start[0]))}
    todo = list(seen)
    while todo:
        name, i = todo.pop()
        shape = shapes[name]
        for other in above.get(name, []) + below.get(name, []):
            lower = name if other in above.get(name, []) else other
            tree = cuts[cut_of[lower]]
            cut_shapes = tree.geometries
            for c in tree.query(shape[i], "intersects"):
                for j in trees[other].query(cut_shapes[c], "intersects"):
                    key = (other, int(j))
                    if key not in seen:
                        seen.add(key)
                        todo.append(key)
    net = {}
    for name, i in seen:
        net.setdefault(name, []).append(shapes[name][i])
    return {name: unary_union(g) for name, g in net.items()}
