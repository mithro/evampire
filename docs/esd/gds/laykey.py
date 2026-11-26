"""The scale bar and legend under a layout figure.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from layfig import FONT, GREY, INK, NWELL, STYLES, SUB


def scalebar(fig, y):
    target = fig.dw / fig.s / 5
    length = max(v for v in (0.5, 1, 2, 5, 10, 20, 50, 100)
                 if v <= max(target, 0.5))
    x0, x1 = fig.ox, fig.ox + length * fig.s
    out = [f'<rect x="{x0:.1f}" y="{y}" width="{x1 - x0:.1f}" height="6" '
           f'fill="{INK}"/>']
    label = f"{length:g} µm" + (", all panels" if fig.panels else "")
    out.append(f'<text x="{x1 + 8:.1f}" y="{y + 8}" font-size="{FONT}" '
               f'fill="{INK}">{label}</text>')
    return out, x1 + 8 + len(label) * FONT * 0.6


def legend(fig, x, y):
    """Swatches in columns of one width, drawn as they are in the layout."""
    items = []
    if fig.wells:
        items.append(("swatch", (SUB, GREY, None, 1.0),
                      "P-type silicon, no N-well"))
    for k in STYLES:
        if k in fig.keys:
            fill, stroke, name = STYLES[k]
            dash = "4,2" if k == "pad" else None
            kind = "contact" if k == "contact" else "swatch"
            items.append((kind, (fill, stroke, dash, fig.alpha[k]), name))
    items += [(kind, colour, text) for kind, colour, text in fig.notes]
    widths = [(0 if kind == "plain" else 32) + len(name) * FONT * 0.56 + 22
              for kind, _, name in items]
    # As many columns as fit, each as wide as its widest entry.
    for per_row in range(len(items), 0, -1):
        cols = [max(widths[i::per_row]) for i in range(per_row)]
        if sum(cols) <= fig.w - 10 - x:
            break
    lefts = [x + sum(cols[:i]) for i in range(per_row)]
    out = []
    for i, (kind, style, name) in enumerate(items):
        cx, cy = lefts[i % per_row], y + (i // per_row) * 24
        if kind == "plain":   # a remark, with no swatch
            out.append(f'<text x="{cx:.1f}" y="{cy}" font-size="{FONT}" '
                       f'fill="{INK}">{name}</text>')
            continue
        if kind in ("box", "outline"):
            d = ' stroke-dasharray="5,4"' if kind == "box" else ""
            out.append(f'<rect x="{cx:.1f}" y="{cy - 12}" width="26" '
                       f'height="14" fill="none" stroke="{style}" '
                       f'stroke-width="2"{d}/>')
        elif kind == "tint":   # translucent metal with a firm edge
            fill, stroke, alpha = style
            out.append(f'<rect x="{cx:.1f}" y="{cy - 12}" width="26" '
                       f'height="14" fill="{fill}" fill-opacity="{alpha}" '
                       f'stroke="{stroke}" stroke-width="2"/>')
        elif kind == "cut":
            out.append(f'<line x1="{cx:.1f}" y1="{cy - 5}" x2="{cx + 27:.1f}" '
                       f'y2="{cy - 5}" stroke="{style}" stroke-width="2" '
                       'stroke-dasharray="9,3,2,3"/>')
        elif kind == "crop":
            out.append(f'<line x1="{cx:.1f}" y1="{cy - 5}" x2="{cx + 26:.1f}" '
                       f'y2="{cy - 5}" stroke="{INK}" stroke-width="1.3" '
                       'stroke-dasharray="7,5"/>')
        elif kind == "dashes":
            out.append(f'<line x1="{cx:.1f}" y1="{cy - 5}" x2="{cx + 27:.1f}" '
                       f'y2="{cy - 5}" stroke="{style}" stroke-width="4" '
                       'stroke-dasharray="7,4"/>')
        elif kind == "arrow":
            out.append(f'<line x1="{cx:.1f}" y1="{cy - 5}" x2="{cx + 18:.1f}" '
                       f'y2="{cy - 5}" stroke="{style}" stroke-width="4"/>')
            out.append(f'<path d="M{cx + 16:.1f},{cy - 11} L{cx + 27:.1f},'
                       f'{cy - 5} L{cx + 16:.1f},{cy + 1} z" fill="{style}"/>')
        elif kind == "label":
            out.append(f'<text x="{cx:.1f}" y="{cy}" font-size="{FONT}" '
                       f'font-weight="bold" fill="{style}">Abc</text>')
        else:
            fill, stroke, dash, alpha = style
            d = f' stroke-dasharray="{dash}"' if dash else ""
            w, h, dx = (8, 8, 9) if kind == "contact" else (26, 14, 0)
            if fill != "none":   # show a tint over what lies under it
                under = (NWELL if name == STYLES["dvdd"][2]
                         and "nwell" in fig.keys else SUB)
                out.append(f'<rect x="{cx:.1f}" y="{cy - 12}" width="26" '
                           f'height="14" fill="{under}"/>')
            out.append(
                f'<rect x="{cx + dx:.1f}" y="{cy - 12 + (14 - h) / 2:.1f}" '
                f'width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" '
                f'opacity="{alpha}"{d}/>')
        out.append(f'<text x="{cx + 34:.1f}" y="{cy}" font-size="{FONT}" '
                   f'fill="{INK}">{name}</text>')
    return out, y + ((len(items) - 1) // per_row) * 24
