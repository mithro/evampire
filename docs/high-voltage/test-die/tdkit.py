"""Shared data and drawing helpers for the test-die figures and tables.

Loads the structure list (silicon/hvtest/structures.json, written by the
layout generator's export.py) and the floor plan (manifest.json in this
folder, written by the layout generator's chip.py), and draws one test
structure as a schematic cross-section or as a plan view. The other
modules in this folder import it; figures.py is the script to run.

SPDX-License-Identifier: Apache-2.0
"""

import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # svgdraw.py and fig_graphs.py

from svgdraw import (FOX, GREY, INK, METAL, NPLUS, NWELL, POLY,  # noqa: E402
                     PPLUS, SUB, line, rect, text)

PWELL = "#aac6e6"      # P-well, drawn or generated
NAT = "#2e8b57"        # outline of the NAT layer
STRUCTURES = HERE.parents[2] / "silicon" / "hvtest" / "structures.json"
MANIFEST = HERE / "manifest.json"

# The nine groups of the structures page, in order: key, title, test.
GROUPS = [
    ("surround", "Plain N-well",
     lambda n, p: p["kind"] == "nw" and n[:2] in ("NT", "NC")),
    ("pwell", "Drawn P-well", lambda n, p: n.startswith("NW")),
    ("nat", "NAT layer",
     lambda n, p: p["kind"] == "nw" and p["nat_gap"] is not None
     and not p["gate"] and p["half"] < 50),
    ("dnw", "Deep N-well",
     lambda n, p: p["kind"] == "dnw" and not p["gate"] and p["half"] < 50
     and (not p["plates"] or p["nat_gap"] is not None)),
    ("plates", "Field plates",
     lambda n, p: bool(p["plates"]) and not p["gate"] and p["half"] < 50
     and not p["rings"] and p["nat_gap"] is None),
    ("rings", "Floating rings",
     lambda n, p: bool(p["rings"]) and p["nat_gap"] is None),
    ("gated", "Gated diodes", lambda n, p: p["gate"]),
    ("large", "Large wells", lambda n, p: p["half"] >= 50),
    ("open", "Open reference", lambda n, p: p["kind"] == "open"),
]


def load():
    """(structures, manifest); fails if the two files disagree."""
    structs = json.loads(STRUCTURES.read_text())
    man = json.loads(MANIFEST.read_text())
    sites = {s["name"]: s for s in man["sites"]}
    if sorted(sites) != sorted(structs):
        raise SystemExit("manifest.json and structures.json list different "
                         "structures: regenerate both")
    for name, p in structs.items():
        if sites[name]["params"] != p:
            raise SystemExit(f"{name}: manifest.json and structures.json "
                             "differ: regenerate both")
    return structs, man


def nat_spans(p):
    """The NAT layer as spans [(a, b)] of distance from the well edge: from
    nat_gap to 0.5 um short of the P+ ring, cut 0.6 um clear of each ring
    (junction.py)."""
    if p["nat_gap"] is None:
        return []
    spans, a, d = [], p["nat_gap"], 0.0
    for gap, width in p["rings"]:
        d += gap
        spans.append((a, d - 0.6))
        a = d + width + 0.6
        d += width
    return spans + [(a, p["term"] - 0.5)]


def group_of(name, p):
    hits = [key for key, _, test in GROUPS if test(name, p)]
    if len(hits) != 1:
        raise SystemExit(f"{name}: in groups {hits}, expected exactly one")
    return hits[0]


def members(structs, man, key):
    """Names of one group in the order the die places them."""
    order = [s["name"] for s in man["sites"]]
    return [n for n in order if group_of(n, structs[n]) == key]


def num(v):
    """A dimension as text without a trailing .0."""
    return f"{v:g}"


class Section:
    """A schematic radial cross-section of one structure, to scale along
    the surface and not to scale in depth. x is micrometres from the well
    edge, positive outwards."""

    DEPTH = 96

    def __init__(self, p, x0, y0, wpx, left=-7.0, right=None):
        self.p, self.x0, self.y0, self.wpx = p, x0, y0, wpx
        self.left = left
        self.right = right or p["term"] + p["ncomp_w"] + 3.0
        self.s = wpx / (self.right - left)

    def x(self, um):
        return self.x0 + (um - self.left) * self.s

    def box(self, a, b, top, h, fill, **kw):
        return rect(self.x(a), self.y0 + top, (b - a) * self.s, h, fill, **kw)

    def silicon(self, pwell=(), deep=None):
        """Substrate, P-well spans [(a, b, label)], well, rings, trench
        oxide and the two contact rings. deep draws the deep P layer:
        "well" under the well only, "all" under the whole section."""
        p, y0 = self.p, self.y0
        b = [rect(self.x0, y0, self.wpx, self.DEPTH, SUB)]
        if deep:
            wd = self.wpx if deep == "all" else self.x(0) - self.x0
            b.append(rect(self.x0, y0 + 70, wd, 9, PWELL, stroke="none"))
            b.append(text(self.x0 + 6, y0 + 91, "deep P layer",
                          anchor="start", size=11))
        for a, e, label in pwell:
            b.append(self.box(a, e, 0, 36, PWELL))
            b.append(text(self.x((a + e) / 2), y0 + 30, label, size=11))
        deep = p["kind"] == "dnw"
        h, r, xe = (60 if deep else 42), 9, self.x(0)
        b.append(f'<path d="M{self.x0:.1f},{y0} L{self.x0:.1f},{y0 + h} '
                 f'L{xe - r:.1f},{y0 + h} Q{xe:.1f},{y0 + h} {xe:.1f},'
                 f'{y0 + h - r} L{xe:.1f},{y0} Z" fill="{NWELL}" '
                 f'stroke="{INK}"/>')
        b.append(text(self.x0 + 6, y0 + h - 8,
                      "deep N-well" if deep else "N-well", anchor="start",
                      size=12))
        d = 0.0
        for k, (gap, width) in enumerate(p["rings"]):
            d += gap
            xa = self.x(d)
            b.append(f'<path d="M{xa:.1f},{y0} L{xa:.1f},{y0 + 36} '
                     f'Q{xa:.1f},{y0 + 42} {xa + 5:.1f},{y0 + 42} '
                     f'L{self.x(d + width) - 5:.1f},{y0 + 42} '
                     f'Q{self.x(d + width):.1f},{y0 + 42} '
                     f'{self.x(d + width):.1f},{y0 + 36} '
                     f'L{self.x(d + width):.1f},{y0} Z" fill="{NWELL}" '
                     f'stroke="{INK}"/>')
            b.append(text(self.x(d + width / 2), y0 + 56, str(k + 1),
                          size=11))
            d += width
        ins, w, term = p["inset"], p["ncomp_w"], p["term"]
        if deep:    # the N-well drawn under the contact ring of a deep N-well
            b.append(self.box(-ins - w - 0.3, -ins + 0.3, 0, 30, "#f8c58f"))
        for a, e in ((self.left, -ins - w), (-ins, term),
                     (term + w, self.right)):
            b.append(self.box(a, e, 0, 7, FOX, stroke="none"))
        b.append(self.box(-ins - w, -ins, 0, 10, NPLUS))
        b.append(self.box(term, term + w, 0, 10, PPLUS))
        b.append(text(self.x(-ins - w / 2), y0 + 22, "N+", size=11))
        b.append(text(self.x(term + w / 2), y0 + 22, "P+", size=11))
        b.append(text(self.x0 + self.wpx - 6, y0 + self.DEPTH - 8,
                      "P substrate", anchor="end", size=12))
        return b

    def nat(self):
        spans = nat_spans(self.p)
        b = [rect(self.x(a), self.y0 - 4, (e - a) * self.s, 50, "none",
                  stroke=NAT, dash="5 3") for a, e in spans]
        if spans:
            a, e = max(spans, key=lambda s: s[1] - s[0])
            b.append(text(self.x((a + e) / 2), self.y0 + 64, "NAT layer",
                          size=11, fill=NAT))
        return b

    def metal(self, lead=True):
        """Contacts, plates and (optionally) the Metal5 lead."""
        p, y0 = self.p, self.y0
        ins, w, term = p["inset"], p["ncomp_w"], p["term"]
        plates, gate = p["plates"], p["gate"]
        b = []
        xc = self.x(-ins - w / 2)
        b.append(rect(xc - 2, y0 - 28, 4, 28, METAL, stroke="none"))
        m1_out = -ins
        g0 = -0.5    # a gated plate starts 0.5 um inside the well edge
        if "poly" in plates:
            a = g0 if gate else -ins + 0.4
            b.append(self.box(a, plates["poly"], -7, 7, POLY))
            if not gate:
                b.append(rect(self.x(-ins + 0.85) - 1.5, y0 - 28, 3, 21,
                              METAL, stroke="none"))
                m1_out = -ins + 1.3
        if "m1" in plates and not gate:
            m1_out = plates["m1"]
        b.append(self.box(-ins - w, m1_out, -36, 8, METAL))
        if "m1" in plates and gate:
            b.append(self.box(g0, plates["m1"], -36, 8, METAL))
        if "m2" in plates:
            a = g0 if gate else -ins - w
            b.append(self.box(a, plates["m2"], -60, 8, METAL))
            if not gate:
                b.append(rect(xc - 2, y0 - 52, 4, 16, METAL, stroke="none"))
        xp = self.x(term + w / 2)
        b.append(rect(xp - 2, y0 - 28, 4, 28, METAL, stroke="none"))
        b.append(self.box(term, term + w, -36, 8, METAL))
        b.append(text(xp, y0 - 42, "0 V", size=12, weight="bold"))
        if lead:
            b.append(rect(xc - 2, y0 - 84, 4, 48, METAL, stroke="none"))
            b.append(rect(xc - 8, y0 - 92, self.x0 + self.wpx - xc + 8, 8,
                          METAL))
            b.append(text(self.x0 + self.wpx - 4, y0 - 98,
                          "Metal5 lead to the well pad", anchor="end",
                          size=11))
        return b

    def dim(self, a, e, label, level=0, above=False):
        """A dimension arrow between two positions on the surface."""
        y = (self.y0 - 110 - 18 * level if above
             else self.y0 + self.DEPTH + 16 + 30 * level)
        xa, xe = self.x(a), self.x(e)
        b = [line(xa, self.y0, xa, y, stroke=GREY, dash="2 3", width=1),
             line(xe, self.y0, xe, y, stroke=GREY, dash="2 3", width=1)]
        if xe - xa > 22:
            b.append(line(xa + 1, y, xe - 1, y, marker=True, start=True,
                          width=1.2))
        else:
            b.append(line(xa, y, xe, y, width=1.2))
        b.append(text((xa + xe) / 2, y + 14, label, size=12))
        return b


def outline(half, corner, cx, cy, s):
    """SVG path of a structure outline: a square of half-side `half` um with
    its corners cut as the layout cuts them (geom.shape)."""
    a = half * s
    c = min(0.586 * corner, half * 0.999) * s
    if c <= 0:
        pts = [(-a, -a), (a, -a), (a, a), (-a, a)]
    else:
        pts = [(-a + c, -a), (a - c, -a), (a, -a + c), (a, a - c),
               (a - c, a), (-a + c, a), (-a, a - c), (-a, -a + c)]
    return "M" + " L".join(f"{cx + px:.1f},{cy + py:.1f}"
                           for px, py in pts) + " Z"


def plan(p, cx, cy, s, well_fill=NWELL):
    """Plan view of a structure centred on (cx, cy) at s pixels per um."""
    half, corner = p["half"], p["corner"]

    def shape(d, fill, stroke=INK, dash=None, width=1):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<path d="{outline(half + d, max(corner + d, 0), cx, cy, s)}'
                f'" fill="{fill}" stroke="{stroke}" stroke-width="{width}"'
                f'{da}/>')

    term, w, ins = p["term"], p["ncomp_w"], p["inset"]
    b = [shape(term + w, PPLUS), shape(term, "white")]
    if p["pwell_gap"] is not None:
        b = [shape(term + w + 1, PWELL)] + b[:1] + [
            shape(term, PWELL), shape(p["pwell_gap"], "white")]
    rings = []
    d = 0.0
    for gap, width in p["rings"]:
        d += gap
        rings.append((d, d + width))
        d += width
    for a, e in reversed(rings):
        b += [shape(e, NWELL), shape(a, "white")]
    b.append(shape(0, well_fill))
    b += [shape(-ins, NPLUS), shape(-ins - w, well_fill)]
    for layer, length in p["plates"].items():
        b.append(shape(length, "none", stroke=POLY if layer == "poly"
                       else GREY, dash="5 3", width=1.6))
    for a, e in nat_spans(p):
        b.append(shape(e, "none", stroke=NAT, dash="5 3"))
        b.append(shape(a, "none", stroke=NAT, dash="5 3"))
    return b
