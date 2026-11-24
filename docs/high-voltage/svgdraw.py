"""Shared colours and SVG drawing helpers for the high-voltage figures.

The figure modules in this folder import these, so every cross-section and
graph uses the same colours and lettering.

SPDX-License-Identifier: Apache-2.0
"""

SUB = "#dbe8f5"        # P-type substrate
NWELL = "#fbd9b5"      # N-type regions
NPLUS = "#f5b46e"      # heavily doped N+
PPLUS = "#7fa7d6"      # heavily doped P+
OXIDE = "#e8e8e8"      # insulator
FOX = "#cfcfcf"        # field oxide
POLY = "#c9a0dc"       # polysilicon
METAL = "#9aa5b1"      # metal
INK = "#222222"
GREY = "#666666"
DEPL = "#c0392b"       # depletion edge, and the field
FIELD_FILL = "#f6d5d1"
BLUE = "#2e86de"       # potential, and inversion layers


def n(v):
    """A coordinate as text: integers as they are, floats to 0.1."""
    return str(v) if isinstance(v, int) else str(round(v, 1))


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif" '
            f'font-size="13">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def rect(x, y, w, h, fill, rx=0, stroke=INK, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" '
            f'rx="{rx}" fill="{fill}" stroke="{stroke}"{d}{o}/>')


def text(x, y, s, anchor="middle", size=13, weight="normal", fill=INK,
         rotate=None, style=None):
    r = f' transform="rotate({rotate} {n(x)} {n(y)})"' if rotate else ""
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{n(x)}" y="{n(y)}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"{st}{r}>'
            f'{s}</text>')


def sub(base, low):
    """A symbol with a subscript, for use inside text()."""
    return (f'{base}<tspan dy="4" font-size="0.75em">{low}</tspan>'
            f'<tspan dy="-4"> </tspan>')


def line(x1, y1, x2, y2, stroke=INK, dash=None, width=1.5, marker=False,
         start=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = ' marker-end="url(#arrow)"' if marker else ""
    s = ' marker-start="url(#arrow)"' if start else ""
    return (f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}{m}{s}/>')


def path(d, stroke=DEPL, dash="6 4", fill="none", width=1.8, opacity=None):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<path d="{d}" stroke="{stroke}" stroke-width="{width}"'
            f'{da} fill="{fill}"{o}/>')


def polyline(points, stroke=INK, width=1.8, fill="none", dash=None):
    pts = " ".join(f"{n(x)},{n(y)}" for x, y in points)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{pts}" stroke="{stroke}" '
            f'stroke-width="{width}" fill="{fill}"{da}/>')


ARROW = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
         'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
