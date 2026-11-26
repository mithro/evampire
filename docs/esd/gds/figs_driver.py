"""Figures of the output transistors of gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

import gdskit
from layfig import DVDD, DVSS, HOT, INK, Fig

CELL = "bi_t"


def devices(f, **kw):
    """Silicon, with the gates darker where they cross diffusion."""
    lay = gdskit.load(CELL)
    f.silicon(**kw)
    f.geom(lay["poly"].intersection(lay["comp"]), "gate")
    f.layer("contact")
    f.layer("sab", width=1.0, dash="4,2")


def nmos_driver():
    """One corner of the NMOS output drivers, with every part named."""
    f = Fig(CELL, (4.6, 65.6, 28.4, 99.6), 22, top=64, right=262, bottom=70)
    devices(f)
    top = f.oy - 34
    f.label("Outer P+ ring,\nto VSS", (16.5, 67.75),
            (f.px(0, 67.75)[0] + 28, top - 6))
    f.label("N+ guard ring in an\nN-well, to DVDD", (7.2, 84),
            (f.px(0, 84)[0], top - 6), colour=DVDD, weight="bold")
    f.label("P+ guard ring, to DVSS", (11.0, 94),
            (f.px(0, 94)[0] + 40, top + 11), colour=DVSS, weight="bold")
    # Finger parts, named in the right margin in the order they are drawn.
    x = f.ox + f.dw + 16
    rows = [
        (14.12, "Source, to DVSS", DVSS),
        (15.1, "Gate, 1.15 µm long", INK),
        (17.6, "Drain under the silicide block", INK),
        (19.78, "Drain contacts, to PAD", HOT),
        (21.9, "Drain under the silicide block", INK),
        (24.47, "Gate of the second finger", INK),
        (25.65, "Source shared by two fingers", DVSS),
        (26.83, "Gate of the third finger", INK),
    ]
    for gx, text, colour in rows:
        y = f.px(gx, 0)[1]
        f.label(text, (gx, 97.6), (x, y + 5), anchor="start", colour=colour,
                lead="left", weight="bold" if colour != INK else "normal")
    f.dim((15.67, 80.5), (19.45, 80.5), "3.78 µm", side="above")
    f.dim((14.52, 84.5), (15.67, 84.5), "1.15 µm", side="above")
    return f


def _panel(window, title):
    f = Fig(CELL, window, 30, left=20, top=48, right=20, bottom=78)
    devices(f)
    f.title(title)
    return f


def silicide_block():
    """The blocked drains of both drivers beside an ordinary transistor."""
    a = _panel((13.2, 74.6, 26.8, 83.8), "(a) NMOS output driver")
    a.dim((15.67, 80.2), (19.45, 80.2), "3.78 µm")
    a.dim((20.11, 80.2), (23.89, 80.2), "3.78 µm", side="below")
    a.dim((14.52, 82.4), (15.67, 82.4), "1.15 µm", side="above")
    a.label("drain contacts", (19.78, 76.4), a.px(17.9, 77.3))
    b = _panel((10.2, 144.9, 23.8, 154.1), "(b) PMOS output driver")
    b.dim((12.295, 150.5), (15.075, 150.5), "2.78 µm")
    b.dim((15.735, 150.5), (18.515, 150.5), "2.78 µm", side="below")
    b.dim((11.595, 152.7), (12.295, 152.7), "0.7 µm", side="above")
    b.label("drain contacts", (15.405, 146.7), b.px(14.0, 147.6))
    c = _panel((20.3, 212.9, 33.9, 222.1), "(c) Pre-driver, not blocked")
    c.label("contacts beside\nevery gate", (25.0, 216.6),
            (c.px(0, 217.8)[0], c.oy + c.dh + 28))
    a.attach(b)
    a.attach(c)
    return a


FIGURES = {"gds-nmos-driver": nmos_driver, "gds-silicide-block": silicide_block}
