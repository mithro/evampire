"""Draw part of a cell layout as an annotated SVG figure.

Helper for figures.py: run that script, not this module. Every figure
shares one palette, a scale bar and a legend, and is drawn with the bond
pad at the left: GDS y runs left to right and GDS x runs top to bottom,
which turns the foundry's drawing a quarter turn clockwise.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit
from shapely.affinity import translate

# Silicon colours match the cross-sections of docs/esd/sim/sections.py.
SUB = "#dbe8f5"
NWELL = "#fbd9b5"
NPLUS = "#f5b46e"
PPLUS = "#7fa7d6"
POLY = "#c9a0dc"
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
    "poly": (POLY, "#6f3f93", "polysilicon"),
    "sab": ("url(#hatch)", INK, "silicide block"),
    "contact": ("#333333", "none", "contact"),
    "metal": (METAL, "#6b7684", "metal"),
    "pad": ("none", INK, "pad opening"),
    "padnet": (HOT, "#7d1f14", "PAD net, metal 2"),
    "paddrain": ("#7d1f14", "#4a0f08", "drain on the PAD net"),
    "dvdd": (DVDD, "#6a1c53", "diffusion on DVDD"),
    "dvss": (DVSS, "#0d5045", "diffusion on DVSS"),
    "dvddrail": (DVDD, "#6a1c53", "DVDD rail, metal 5"),
    "dvssrail": (DVSS, "#0d5045", "DVSS rail, metal 5"),
    "innet": (SECONDARY, "#12305f", "protected input net"),
    "other": ("#c4c9cf", "#8a9199", "other diffusion"),
    "resistor": ("none", SECONDARY, "resistor body"),
    "gate": ("#8e5bb5", "#4f2a70", "gate over diffusion"),
    "clampfet": (CLAMP, "#8a5500", "clamp transistor"),
}
FONT = 14


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
        self.body.append(
            f'<rect x="{self.ox:.1f}" y="{self.oy:.1f}" width="{self.dw:.1f}" '
            f'height="{self.dh:.1f}" fill="{SUB}"/>')

    # -- coordinates ------------------------------------------------------
    def px(self, gx, gy):
        x0, y0, _, _ = self.win
        return (self.ox + (gy - y0) * self.s, self.oy + (gx - x0) * self.s)

    def _path(self, geom):
        d = []
        for poly in gdskit.parts(geom):
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

    def layer(self, name, cell=None, shift=0.0, **kw):
        """Draw a layer of a cell, moved by `shift` along GDS x."""
        style = kw.pop("style", name)
        geom = derived(cell or self.cell, name)
        if shift:
            geom = translate(geom, xoff=shift)
        self.geom(geom, style, **kw)

    def silicon(self, contacts=False, **kw):
        """The layers that make the devices, from the wells up."""
        for name in ("nwell", "pdiff", "ndiff", "poly"):
            self.layer(name, **kw)
        if contacts:
            self.layer("contact", **kw)

    def outline(self, geom, colour, width=2.0, dash=None):
        d = self._path(gdskit.clip(geom, self.win))
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.over.append(f'<path d="{d}" fill="none" stroke="{colour}" '
                         f'stroke-width="{width}"{extra}/>')

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
              weight="normal", lead="auto"):
        """Text at pixel position `at` with a leader to a layout point.

        The leader leaves the text below or above it (lead="auto", for
        labels in the top and bottom margins) or at its left or right end
        (for labels in the side margins), and ends in a dot on the target.
        """
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
        self.text(ax, ay, s, anchor=anchor, fill=colour, weight=weight)

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

    def flow(self, points, colour=HOT, width=4.0, dash=None, pixels=False):
        """An arrow along layout points: the direction of a current."""
        pts = points if pixels else [self.px(*p) for p in points]
        d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        mid = {HOT: "hot", CLAMP: "clamp", SECONDARY: "second",
               SNAP: "snap"}[colour]
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.over.append(f'<polyline points="{d}" fill="none" stroke="#fff" '
                         f'stroke-width="{width + 3}" opacity="0.9" '
                         'stroke-linejoin="round"/>')
        self.over.append(
            f'<polyline points="{d}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linejoin="round"{extra} '
            f'marker-end="url(#arrow-{mid})"/>')

    def box(self, window, colour=INK, dash="6,4", width=1.6):
        """Outline a region of the layout (x0, y0, x1, y1)."""
        (xa, ya), (xb, yb) = self.px(window[0], window[1]), self.px(
            window[2], window[3])
        self.over.append(
            f'<rect x="{min(xa, xb):.1f}" y="{min(ya, yb):.1f}" '
            f'width="{abs(xb - xa):.1f}" height="{abs(yb - ya):.1f}" '
            f'fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-dasharray="{dash}"/>')

    def attach(self, other, gap=24):
        """Put another figure of the same scale to the right as a panel."""
        assert other.s == self.s, "panels share one scale bar"
        self.panels.append((other, self.w - 20 + gap))
        self.w += gap + other.w - 20
        self.h = max(self.h, other.h)
        self.keys += [k for k in other.keys if k not in self.keys]

    def title(self, s):
        """A panel title above the top-left corner of the layout."""
        self.text(self.ox, self.oy - 10, s, anchor="start", weight="bold",
                  halo=False)

    # -- furniture --------------------------------------------------------
    def _scalebar(self, y):
        target = self.dw / self.s / 5
        length = max(v for v in (0.5, 1, 2, 5, 10, 20, 50, 100)
                     if v <= max(target, 0.5))
        x0, x1 = self.ox, self.ox + length * self.s
        out = [f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="6" '
               f'fill="{INK}"/>']
        label = f"{length:g} µm"
        out.append(f'<text x="{x1 + 8:.1f}" y="{y + 8}" font-size="{FONT}" '
                   f'fill="{INK}">{label}</text>')
        return out, x1 + 8 + len(label) * FONT * 0.6

    def _legend(self, x, y, extra):
        out = []
        items = [(STYLES[k][0], STYLES[k][1], STYLES[k][2],
                  "4,2" if k in ("pad", "sab") else None)
                 for k in STYLES if k in self.keys] + extra
        x_start = x
        for fill, stroke, name, dash in items:
            width = 26 + 6 + len(name) * FONT * 0.56 + 18
            if x + width > self.w - 10:
                x, y = x_start, y + 24
            d = f' stroke-dasharray="{dash}"' if dash else ""
            out.append(f'<rect x="{x:.1f}" y="{y - 12}" width="26" '
                       f'height="14" fill="{fill}" stroke="{stroke}"{d}/>')
            out.append(f'<text x="{x + 32:.1f}" y="{y}" font-size="{FONT}" '
                       f'fill="{INK}">{name}</text>')
            x += width
        return out, y

    def _content(self):
        return [*self.body,
                f'<rect x="{self.ox:.1f}" y="{self.oy:.1f}" '
                f'width="{self.dw:.1f}" height="{self.dh:.1f}" fill="none" '
                f'stroke="{GREY}" stroke-width="1"/>', *self.over]

    def save(self, path, extra_keys=()):
        """Write the SVG, with the scale bar and legend under the layout."""
        base = self.h - 44
        bar, x = self._scalebar(base)
        legend, y_end = self._legend(x + 24, base + 9, list(extra_keys))
        h = max(self.h, y_end + 16)
        defs = [
            '<pattern id="hatch" width="6" height="6" '
            'patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<line x1="0" y1="0" x2="0" y2="6" stroke="{INK}" '
            'stroke-width="1.2"/></pattern>']
        for name, colour in (("hot", HOT), ("clamp", CLAMP),
                             ("second", SECONDARY), ("snap", SNAP)):
            defs.append(
                f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="7" '
                'refY="5" markerWidth="4.5" markerHeight="4.5" '
                'orient="auto"><path d="M0,0 L10,5 L0,10 z" '
                f'fill="{colour}"/></marker>')
        svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w:.0f}" '
               f'height="{h:.0f}" viewBox="0 0 {self.w:.0f} {h:.0f}" '
               'font-family="sans-serif">',
               "<defs>" + "".join(defs) + "</defs>",
               f'<rect width="{self.w:.0f}" height="{h:.0f}" fill="#ffffff"/>',
               *self._content()]
        for other, dx in self.panels:
            svg += [f'<g transform="translate({dx:.1f},0)">',
                    *other._content(), "</g>"]
        svg += [*bar, *legend, "</svg>"]
        path.write_text("\n".join(svg) + "\n")
