"""Geometry helpers on klayout.db Regions. Public functions take micrometres; regions are
in database units of 1 nm, and every coordinate is snapped to the 5 nm manufacturing grid."""

from __future__ import annotations

import klayout.db as kdb

DBU = 0.001
GRID = 5  # nm


def nm(um: float) -> int:
    """Micrometres to database units, on the 5 nm grid."""
    return int(round(um / DBU / GRID)) * GRID


def octagon(half: float, chamfer: float = 0.0, cx: float = 0.0, cy: float = 0.0) -> kdb.Region:
    """A square of side 2*half centred on (cx, cy) with 45-degree corners cut by `chamfer`."""
    a, c, x, y = nm(half), nm(chamfer), nm(cx), nm(cy)
    if c <= 0:
        return kdb.Region(kdb.Box(x - a, y - a, x + a, y + a))
    pts = [(-a + c, -a), (a - c, -a), (a, -a + c), (a, a - c),
           (a - c, a), (-a + c, a), (-a, a - c), (-a, -a + c)]  # fmt: skip
    return kdb.Region(kdb.Polygon([kdb.Point(x + px, y + py) for px, py in pts]))


def shape(half: float, corner: float) -> kdb.Region:
    """The outline family of one structure: a square of half-size `half` whose corners are
    cut so that the corner behaves like an arc of radius `corner` (chamfer = 0.2929 * 2 * r
    makes the octagon corner touch the arc's midpoint). corner = 0 gives a sharp square."""
    return octagon(half, min(0.586 * corner, half * 0.999))


def ring(outer: kdb.Region, inner: kdb.Region) -> kdb.Region:
    return outer - inner


def contacts(area: kdb.Region, size: float, pitch: float, enclosure: float) -> kdb.Region:
    """Square cuts of `size` on a `pitch` grid, kept where the cut plus `enclosure` is inside
    `area`."""
    out = kdb.Region()
    s, p = nm(size), nm(pitch)
    keep = area.sized(-nm(enclosure))
    b = keep.bbox()
    if b.empty():
        return out
    x0 = (b.left // p) * p
    y0 = (b.bottom // p) * p
    cells = kdb.Region()
    x = x0
    while x + s <= b.right:
        y = y0
        while y + s <= b.top:
            cells.insert(kdb.Box(x, y, x + s, y + s))
            y += p
        x += p
    return cells.inside(keep)


def box(x0: float, y0: float, x1: float, y1: float) -> kdb.Region:
    return kdb.Region(kdb.Box(nm(x0), nm(y0), nm(x1), nm(y1)))


def text(layout: kdb.Layout, s: str, height: float, x: float, y: float) -> kdb.Region:
    """Polygons of a text label `height` um tall with its lower-left corner at (x, y)."""
    gen = kdb.TextGenerator.default_generator()
    mag = height / (gen.height() * gen.dbu())
    reg = gen.text(s, DBU, mag)
    reg.move(nm(x), nm(y))
    return reg
