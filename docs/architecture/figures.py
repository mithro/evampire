"""Draw the figures for the architecture page as SVG files.

Usage: python figures.py OUTPUT-DIRECTORY

Writes rate-matching.svg, the rate-matching buffer's fill across one frame
for a receive clock 200 ppm fast and 200 ppm slow, and frame-layout.svg,
the fields of a frame and which block writes each. Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

INK = "#222222"
GREY = "#666666"
FAST = "#c0392b"
SLOW = "#1f4e9c"
GEN = "#fbd9b5"
CPU = "#d4e6d0"


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
            f'height="{h}" viewBox="0 0 {w} {h}" font-family="sans-serif" '
            f'font-size="13">\n<rect width="{w}" height="{h}" fill="white"/>\n'
            + "\n".join(body) + "\n</svg>\n")


def text(x, y, s, anchor="middle", size=13, fill=INK, weight="normal",
         rotate=None):
    r = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
            f'font-size="{size}" fill="{fill}" font-weight="{weight}"{r}>'
            f'{s}</text>')


def line(x1, y1, x2, y2, stroke=INK, width=1.0, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{width}"{d}/>')


def rect(x, y, w, h, fill, stroke=INK, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}"{d}/>')


def rate_matching():
    w, h = 640, 330
    x0, y0, pw, ph = 80, 30, 520, 230
    xmax, ymax = 12000, 3

    def px(b, occ):
        return x0 + pw * b / xmax, y0 + ph * (ymax - occ) / (2 * ymax)

    body = [rect(x0, y0, pw * 10000 / xmax, ph, "#f3f3f3", stroke="none")]
    body.append(text(x0 + pw * 5000 / xmax, y0 + 16, "one frame of "
                     "10 000 bytes", size=12, fill=GREY))
    body.append(text(x0 + pw * 11000 / xmax, y0 + 16, "gap, not", size=12,
                     fill=GREY))
    body.append(text(x0 + pw * 11000 / xmax, y0 + 31, "to scale", size=12,
                     fill=GREY))
    for occ in (-3, -2, -1, 0, 1, 2, 3):
        _, y = px(0, occ)
        body.append(line(x0, y, x0 + pw, y, stroke="#dddddd"))
        s = f"{occ:+d}".replace("-", "−") if occ else "0"
        body.append(text(x0 - 8, y + 4, s, anchor="end", size=12))
    for b in range(0, 12001, 2000):
        x, _ = px(b, 0)
        body.append(text(x, y0 + ph + 18, f"{b:,}".replace(",", " "),
                         size=12))
    for s in (2, -2):
        _, y = px(0, s)
        body.append(line(x0, y, x0 + pw, y, stroke=GREY, width=1.3,
                         dash="6 4"))
    body.append(text(x0 + 6, px(0, 2)[1] - 6, "slack S = 2 bytes",
                     anchor="start", size=12, fill=GREY))
    # The level steps by one byte every 5000 bytes at 200 ppm, then the
    # buffer returns to its centre in the gap.
    for sign, col, name in ((1, FAST, "receive clock 200 ppm fast"),
                            (-1, SLOW, "receive clock 200 ppm slow")):
        pts = []
        for b in range(0, 10001, 50):
            pts.append(px(b, sign * (b // 5000)))
        pts.append(px(10000, sign * 2))
        pts.append(px(10600, 0))
        pts.append(px(12000, 0))
        body.append('<polyline points="' + " ".join(
            f"{x:.1f},{y:.1f}" for x, y in pts) + f'" stroke="{col}" '
            'stroke-width="2.5" fill="none"/>')
        x, y = px(800, sign * 0.6)
        body.append(text(x, y + (0 if sign > 0 else 12), name,
                         anchor="start", size=12, fill=col))
    body.append(rect(x0, y0, pw, ph, "none"))
    body.append(text(x0 + pw / 2, y0 + ph + 40, "time, in byte times",
                     size=13))
    body.append(text(24, y0 + ph / 2, "buffer level from its centre "
                     "(bytes)", size=13, rotate=-90))
    return svg(w, h, body)


ROWS = ((("preamble", "7", GEN, None, 110), ("SFD", "1", GEN, None, 70),
         ("destination", "6", CPU, None, 150),
         ("source", "6", CPU, None, 130)),
        (("VLAN tag", "4", CPU, "4 4", 110), ("type", "2", CPU, None, 70),
         ("payload", "42 or 46 to 1500", CPU, None, 170),
         ("FCS", "4", GEN, None, 110)))


def frame_layout():
    """The fields of a frame in two rows, so the text stays large on a
    narrow screen."""
    w, h = 500, 300
    body = [text(250, 26, "Fields of a frame, in bytes", size=16,
                 weight="bold")]
    for k, row in enumerate(ROWS):
        x, y = 20, 46 + k * 86
        for name, n, fill, dash, wd in row:
            body.append(rect(x, y, wd, 58, fill, dash=dash))
            body.append(text(x + wd / 2, y + 25, name, size=15))
            body.append(text(x + wd / 2, y + 46, n, size=14, fill=GREY))
            x += wd
    body.append(text(20, 226, "the second row follows on from the first",
                     anchor="start", size=13, fill=GREY))
    body.append(rect(20, 240, 20, 16, GEN))
    body.append(text(48, 254, "added by the generator", anchor="start",
                     size=14))
    body.append(rect(20, 266, 20, 16, CPU))
    body.append(text(48, 280, "written by the processor; VLAN tag "
                     "optional", anchor="start", size=14))
    return svg(w, h, body)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    out = pathlib.Path(argv[1])
    (out / "rate-matching.svg").write_text(rate_matching(), encoding="utf-8")
    (out / "frame-layout.svg").write_text(frame_layout(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
