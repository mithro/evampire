"""Shared SVG helpers and colours for the RGMII figure scripts.

SPDX-License-Identifier: Apache-2.0
"""

INK = "#222222"
GREY = "#7f7f7f"
CLOCK = "#1f4e79"
DATA_FILL = "#dbe8f5"
ZONE = "#d9d9d9"        # where an edge may fall
STABLE = "#a9d18e"      # where the data must not change
ACCENT = "#c00000"


def svg(w, h, body):
    defs = ('<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" '
            'font-family="Helvetica, Arial, sans-serif" font-size="13">\n'
            f'<rect width="{w}" height="{h}" fill="white"/>\n{defs}\n'
            + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="start", size=13, weight="normal", fill=INK):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.2, dash=None, arrows=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = (' marker-start="url(#a)" marker-end="url(#a)"' if arrows else "")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}{m}/>')


def rect(x, y, w, h, fill, stroke="none", opacity=1.0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" fill-opacity="{opacity}"/>')
