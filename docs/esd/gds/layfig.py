"""Draw part of a cell layout as an annotated SVG figure.

Helper for figures.py: run that script, not this module. Every figure
shares one palette, a scale bar and a legend, and is drawn with the bond
pad at the left: GDS y runs left to right and GDS x runs top to bottom,
which turns the foundry's drawing a quarter turn clockwise.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit

# Silicon colours match the cross-sections of docs/esd/sim/sections.py.
SUB = "#dbe8f5"        # P-type silicon: every area with no N-well drawn
NWELL = "#fbd9b5"
NPLUS = "#f5b46e"
PPLUS = "#7fa7d6"
POLY = "#c9cf96"         # olive, so that purple is snapback only
METAL = "#9aa5b1"
INK = "#222222"
GREY = "#666666"
# Accent colours match the schematics of docs/esd/sim/schematic.py.
HOT = "#c0392b"        # the pad net and the discharge current
SECONDARY = "#1f4e9c"  # secondary protection
CLAMP = "#e08a00"      # rail clamp
DVDD = "#a02c7d"
DVSS = "#16806f"
SNAP = "#8e44ad"       # snapback, as in the cross-section

# name: (fill, stroke, legend text)
STYLES = {
    "nwell": (NWELL, "#c98f4f", "N-well"),
    "ndiff": (NPLUS, "#a8651c", "N+ diffusion"),
    "pdiff": (PPLUS, "#3d6294", "P+ diffusion"),
    "poly": (POLY, "#5c6620", "polysilicon"),
    "sab": ("url(#hatch)", INK, "silicide block, over any layer"),
    "contact": ("#333333", "none", "contact"),
    "metal": (METAL, "#6b7684", "bond pad metal"),
    "pad": ("none", INK, "pad opening"),
    "padtop": (HOT, "#7d1f14", "PAD net, bond pad"),
    "paddrain": ("#7d1f14", "#4a0f08", "drain on the PAD net"),
    "dvdd": (DVDD, "#6a1c53", "diffusion on DVDD"),
    "dvss": (DVSS, "#0d5045", "diffusion on DVSS"),
    # Stripes are ruled in their net's colour, over the metal 2 they cover.
    "dvddrail": ("url(#rule-dvdd)", "#6a1c53", "DVDD stripes, metal 3 to 5"),
    "dvssrail": ("url(#rule-dvss)", "#0d5045", "DVSS stripes, metal 3 to 5"),
    "dvddm2": ("#eebbdd", "#a02c7d",
               "DVDD metal 2: 5 strips, under the stripes"),
    "dvssm2": ("#cfe8e3", "#0d5045", "DVSS pad's metal 2, under the stripes"),
    "padm2": ("#e2e2e2", "#7d1f14", "PAD net's metal 2, under the stripes"),
    "dvsspad": ("#a3d2ca", "#0d5045", "DVSS bond pad"),
    "other": ("#b3b9c0", "#8a9199", "other diffusion"),
    "gate": ("#7d8a2e", "#444d14", "gate"),
    # Figures that pair with the schematic: its wires are black, so metal
    # is ruled in black, which shows which side of an edge is metal.
    "padwire": ("url(#wire)", INK, "PAD net, metal 2"),
    "nextwire": ("url(#wire2)", INK, "protected net"),
    "primdrain": (HOT, "#7d1f14", "primary: drain on the PAD net"),
}
FONT = 14
# Layers of a figure drawn without colour, from the wells up.
GREYS = (("nwell", "#e6e6e6"), ("pdiff", "#c4c4c4"), ("ndiff", "#8e8e8e"),
         ("poly", "#666666"), ("gate", "#444444"))
PAPER = "#fafafa"      # behind the layers of a grey figure


def derived(cell, name):
    """A drawn layer, including the two this module derives from implants."""
    lay = gdskit.load(cell)
    if name == "ndiff":
        return lay["comp"].intersection(lay["nplus"])
    if name == "pdiff":
        return lay["comp"].intersection(lay["pplus"])
    return lay[name]


class Fig:
    """One figure: a window of a cell with room around it for labels."""

    def __init__(self, cell, window, scale, left=20, top=60, right=20,
                 bottom=95):
        self.cell, self.win, self.s = cell, window, scale
        self.ox, self.oy = left, top
        x0, y0, x1, y1 = window
        self.dw, self.dh = (y1 - y0) * scale, (x1 - x0) * scale
        self.w = left + self.dw + right
        self.h = top + self.dh + bottom
        self.body, self.over, self.keys, self.panels = [], [], [], []
        self.alpha, self.notes = {}, []
        self.wells = True   # False for a figure that draws no silicon
        self.body.append(
            f'<rect x="{self.ox:.1f}" y="{self.oy:.1f}" width="{self.dw:.1f}" '
            f'height="{self.dh:.1f}" fill="{SUB}"/>')

    # -- coordinates ------------------------------------------------------
    def px(self, gx, gy):
        x0, y0, _, _ = self.win
        return (self.ox + (gy - y0) * self.s, self.oy + (gx - x0) * self.s)

    def _path(self, geom):
        d = []
        for poly in gdskit.parts(geom.normalize()):
            for ring in [poly.exterior, *poly.interiors]:
                pts = [self.px(x, y) for x, y in ring.coords[:-1]]
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
                         + "Z")
        return "".join(d)

    # -- layout -----------------------------------------------------------
    def geom(self, geom, style, opacity=1.0, width=0.8, dash=None, key=True):
        """Draw a geometry, clipped to the window, in a named style."""
        fill, stroke, _ = STYLES[style]
        d = self._path(gdskit.clip(geom, self.win))
        if not d:
            return
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.body.append(
            f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}" fill-rule="evenodd" '
            f'opacity="{opacity}"{extra}/>')
        if key and style not in self.keys:
            self.keys.append(style)
            self.alpha[style] = opacity

    def layer(self, name, **kw):
        """Draw a layer of the figure's cell in the style of its name."""
        self.geom(derived(self.cell, name), name, **kw)

    def silicon(self):
        """The layers that make the devices, from the wells up."""
        for name in ("nwell", "pdiff", "ndiff", "poly"):
            self.layer(name)
        lay = gdskit.load(self.cell)
        self.geom(lay["poly"].intersection(lay["comp"]), "gate")

    def grey_silicon(self):
        """The device layers in greys.

        For a figure that pairs with the schematic: colour is then free to
        mark the schematic's parts, and no layer shares a part's colour.
        """
        self.wells = False
        self.body[0] = self.body[0].replace(SUB, PAPER)
        lay = gdskit.load(self.cell)
        for name, fill in GREYS:
            geom = (lay["poly"].intersection(lay["comp"]) if name == "gate"
                    else derived(self.cell, name))
            d = self._path(gdskit.clip(geom, self.win))
            if not d:
                continue
            self.body.append(f'<path d="{d}" fill="{fill}" stroke="#808080" '
                             'stroke-width="0.5" fill-rule="evenodd"/>')
        self.note(("#b9b9b9", "#808080", 1.0), "layout layers, in grey",
                  kind="tint")

    def region(self, window, colour, opacity=0.3, width=3.0):
        """Fill and outline a block of the layout in a schematic colour."""
        (xa, ya), (xb, yb) = self.px(window[0], window[1]), self.px(
            window[2], window[3])
        at = (f'x="{min(xa, xb):.1f}" y="{min(ya, yb):.1f}" '
              f'width="{abs(xb - xa):.1f}" height="{abs(yb - ya):.1f}"')
        self.over.append(f'<rect {at} fill="{colour}" '
                         f'fill-opacity="{opacity}" stroke="#ffffff" '
                         f'stroke-width="{width + 2.5}"/>')
        self.over.append(f'<rect {at} fill="none" stroke="{colour}" '
                         f'stroke-width="{width}"/>')

    def outline(self, geom, colour, width=2.0):
        """Every edge of a geometry, over the layout."""
        d = self._path(gdskit.clip(geom, self.win))
        if d:
            self.over.append(f'<path d="{d}" fill="none" stroke="{colour}" '
                             f'stroke-width="{width}"/>')

    # -- annotation -------------------------------------------------------
    def text(self, x, y, s, anchor="middle", size=FONT, fill=INK,
             weight="normal", halo=True):
        h = (' stroke="#ffffff" stroke-width="3.5" paint-order="stroke" '
             'stroke-linejoin="round"') if halo else ""
        lines = s.split("\n")
        out = []
        for i, line in enumerate(lines):
            out.append(
                f'<text x="{x:.1f}" y="{y + i * size * 1.2:.1f}" '
                f'text-anchor="{anchor}" font-size="{size}" fill="{fill}" '
                f'font-weight="{weight}"{h}>{line}</text>')
        self.over.extend(out)

    def label(self, s, target, at, anchor="middle", colour=INK, elbow=None,
              weight="normal", lead="auto", also=(), leader=None):
        """Text at pixel position `at` with a leader to a layout point.

        The leader leaves the text below or above it (lead="auto", for
        labels in the top and bottom margins) or at its left or right end
        (for labels in the side margins), and ends in a dot on the target.
        `leader` gives the leader a colour other than the text's.
        """
        text_colour, colour = colour, leader or colour
        tx, ty = self.px(*target)
        ax, ay = at
        lines = s.split("\n")
        n = len(lines)
        mid = ay - FONT * 0.35 + (n - 1) * FONT * 0.6
        if lead == "left":
            start = (ax - 6, mid)
        elif lead == "right":
            start = (ax + 6, mid)
        elif ty > ay:
            start = (ax, ay + (n - 1) * FONT * 1.2 + 5)
        else:
            start = (ax, ay - FONT - 1)
        pts = [start] + ([elbow] if elbow is not None else []) + [(tx, ty)]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.over.append(f'<polyline points="{d}" fill="none" stroke="#fff" '
                         'stroke-width="3.2" opacity="0.85"/>')
        self.over.append(f'<polyline points="{d}" fill="none" '
                         f'stroke="{colour}" stroke-width="1.3"/>')
        self.over.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="3.2" '
                         f'fill="{colour}" stroke="#fff" stroke-width="1"/>')
        for extra in also:   # further leaders from the same text
            ex, ey = self.px(*extra)
            self.over.append(
                f'<line x1="{start[0]:.1f}" y1="{start[1]:.1f}" x2="{ex:.1f}" '
                f'y2="{ey:.1f}" stroke="{colour}" stroke-width="1.3"/>')
            self.over.append(
                f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="3.2" fill="{colour}" '
                'stroke="#fff" stroke-width="1"/>')
        self.text(ax, ay, s, anchor=anchor, fill=text_colour, weight=weight)

    def line(self, a, b, colour=INK, width=1.0, dash=None):
        """A thin line between two layout points, such as an extension line."""
        (x1, y1), (x2, y2) = self.px(*a), self.px(*b)
        seg = f'x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"'
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.over.append(f'<line {seg} stroke="#fff" '
                         f'stroke-width="{width + 2.4}" opacity="0.85"/>')
        self.over.append(f'<line {seg} stroke="{colour}" '
                         f'stroke-width="{width}"{extra}/>')

    def dim(self, a, b, s, offset=0.0, colour=INK, side="above"):
        """A dimension line between two layout points, with its text."""
        (x1, y1), (x2, y2) = self.px(*a), self.px(*b)
        horizontal = abs(x2 - x1) >= abs(y2 - y1)
        if horizontal:
            y1 = y2 = y1 + offset
            ticks = [(x1, y1 - 5, x1, y1 + 5), (x2, y2 - 5, x2, y2 + 5)]
            tpos = ((x1 + x2) / 2, y1 - 7 if side == "above" else y1 + FONT + 4)
            anchor = "middle"
        else:
            x1 = x2 = x1 + offset
            ticks = [(x1 - 5, y1, x1 + 5, y1), (x2 - 5, y2, x2 + 5, y2)]
            tpos = ((x1 - 8, (y1 + y2) / 2 + 5) if side == "above"
                    else (x1 + 8, (y1 + y2) / 2 + 5))
            anchor = "end" if side == "above" else "start"
        for seg in [(x1, y1, x2, y2), *ticks]:
            self.over.append(
                '<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                'stroke="#fff" stroke-width="4" opacity="0.85"/>'.format(*seg))
            self.over.append(
                '<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}" '
                'stroke="{}" stroke-width="1.5"/>'.format(*seg, colour))
        self.text(*tpos, s, anchor=anchor, fill=colour, weight="bold")

    def flow(self, points, colour=HOT, width=4.0, key="discharge current",
             head=True):
        """An arrow along layout points: the direction of a current."""
        pts = [self.px(*p) for p in points]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        mid = {HOT: "hot", SNAP: "snap"}[colour]
        if key and ("arrow", colour, key) not in self.notes:
            self.notes.append(("arrow", colour, key))
        self.over.append(f'<polyline points="{d}" fill="none" stroke="#fff" '
                         f'stroke-width="{width + 3}" opacity="0.9" '
                         'stroke-linejoin="round"/>')
        self.over.append(
            f'<polyline points="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linejoin="round"'
            + (f' marker-end="url(#arrow-{mid})"/>' if head else "/>"))

    def box(self, window, colour=INK, dash="6,4", width=1.6):
        """Outline a region of the layout (x0, y0, x1, y1)."""
        (xa, ya), (xb, yb) = self.px(window[0], window[1]), self.px(
            window[2], window[3])
        at = (f'x="{min(xa, xb):.1f}" y="{min(ya, yb):.1f}" '
              f'width="{abs(xb - xa):.1f}" height="{abs(yb - ya):.1f}"')
        # A white line under the dashes, so they show over any layer.
        self.over.append(f'<rect {at} fill="none" stroke="#ffffff" '
                         f'stroke-width="{width + 2.6}" opacity="0.9"/>')
        self.over.append(
            f'<rect {at} fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-dasharray="{dash}"/>')

    def attach(self, other, gap=24):
        """Put another figure of the same scale to the right as a panel."""
        assert other.s == self.s, "panels share one scale bar"
        self.panels.append((other, self.w - 20 + gap, 0))
        self.w += gap + other.w - 20
        self.h = max(self.h, other.h)
        self.keys += [k for k in other.keys if k not in self.keys]
        self.alpha = {**other.alpha, **self.alpha}

    def stack(self, other, overlap=80):
        """Put another figure of the same scale under this one.

        `overlap` is the room this figure kept for its own legend, which
        the pair now shares below both.
        """
        assert other.s == self.s, "panels share one scale bar"
        dy = self.h - overlap
        self.panels.append((other, 0, dy))
        self.w, self.h = max(self.w, other.w), dy + other.h
        self.keys += [k for k in other.keys if k not in self.keys]
        self.alpha = {**other.alpha, **self.alpha}

    def title(self, s, up=10, fill=INK):
        """A panel title above the top-left corner of the layout."""
        self.text(self.ox, self.oy - up, s, anchor="start", weight="bold",
                  halo=False, fill=fill)

    # -- furniture --------------------------------------------------------
    def note(self, colour, text, kind="label"):
        """Explain a label colour or an outline in the legend."""
        self.notes.append((kind, colour, text))

    def _content(self):
        """The layout and its labels, in a frame dashed where it is cropped."""
        x0, y0, x1, y1 = self.win
        l, t, r, b = self.ox, self.oy, self.ox + self.dw, self.oy + self.dh
        edges = [((l, t, l, b), y0 > 0.5), ((r, t, r, b), y1 < 349),
                 ((l, t, r, t), x0 > 0.5),
                 ((l, b, r, b), 0.5 < x1 % 75 < 74.5)]
        frame = []
        for (xa, ya, xb, yb), cropped in edges:
            dash = ' stroke-dasharray="7,5"' if cropped else ""
            if cropped:   # a white edge, so the dashes show over any fill
                frame.append(
                    f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" '
                    f'y2="{yb:.1f}" stroke="#ffffff" stroke-width="3.5"/>')
            frame.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" '
                         f'y2="{yb:.1f}" stroke="{INK}" stroke-width="1.3"'
                         f'{dash}/>')
        return [*self.body, *frame, *self.over]

    def save(self, path):
        """Write the SVG, with the scale bar and legend under the layout."""
        import laykey   # here, because laykey imports this module's palette
        base = self.h - 44
        bar, x = laykey.scalebar(self, base)
        for other, _, _ in self.panels:
            self.notes += [n for n in other.notes if n not in self.notes]
        drawn = self._content() + [line for other, _, _ in self.panels
                                   for line in other._content()]
        crop = ("crop", GREY, "layout continues")
        if (crop not in self.notes
                and any('stroke-dasharray="7,5"' in line for line in drawn)):
            self.notes.append(crop)
        legend, y_end = laykey.legend(self, x + 24, base + 9)
        h = max(self.h, y_end + 16)
        defs = [
            '<pattern id="hatch" width="6" height="6" '
            'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" '
            'stroke-width="1.2"/></pattern>'
            ]
        rules = (("wire", "M0,1.7 H3.4", INK, 0.9, 3.4),
                 ("wire2", "M1.7,0 V3.4", INK, 0.9, 3.4),
                 ("rule-dvdd", "M2.5,0 V5", DVDD, 1.3, 5),
                 ("rule-dvss", "M2.5,0 V5", DVSS, 1.3, 5))
        for name, line, ink, w, p in rules:
            defs.append(
                f'<pattern id="{name}" width="{p}" height="{p}" '
                f'patternUnits="userSpaceOnUse"><path d="{line}" '
                f'stroke="{ink}" stroke-width="{w}"/></pattern>')
        for name, colour in (("hot", HOT), ("snap", SNAP)):
            defs.append(
                f'<marker id="arrow-{name}" viewBox="-1 -1 12 12" refX="7" '
                'refY="5" markerWidth="5.4" markerHeight="5.4" '
                'orient="auto"><path d="M0,0 L10,5 L0,10 z" '
                f'fill="{colour}" stroke="#ffffff" stroke-width="0.7" '
                'stroke-linejoin="round"/></marker>')
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" '
               f'height="{h:.0f}" viewBox="0 0 {self.w:.0f} {h:.0f}" '
               'font-family="sans-serif">',
               "<defs>" + "".join(defs) + "</defs>",
               f'<rect width="{self.w:.0f}" height="{h:.0f}" fill="#ffffff"/>',
               *self._content()]
        for other, dx, dy in self.panels:
            svg += [f'<g transform="translate({dx:.1f},{dy:.1f})">',
                    *other._content(), "</g>"]
        svg += [*bar, *legend, "</svg>"]
        path.write_text("\n".join(svg) + "\n")
