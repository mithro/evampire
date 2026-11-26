"""Figures of the output transistors of gf180mcu_fd_io__bi_t.

Helper for figures.py: run that script, not this module.

SPDX-License-Identifier: Apache-2.0
"""

from layfig import DVDD, DVSS, HOT, INK, Fig

CELL = "bi_t"


def devices(f, **kw):
    """Silicon, with the gates darker where they cross diffusion."""
    f.silicon(**kw)
    f.layer("contact")
    f.layer("sab", width=1.0)


def nmos_driver():
    """One corner of the NMOS output drivers, with every part named."""
    f = Fig(CELL, (4.6, 66.9, 28.4, 99.6), 22, top=64, right=350, bottom=104)
    devices(f)
    top = f.oy - 34
    f.label("P+ bar along the pad side,\non the core ground VSS", (5.6, 67.75),
            (f.px(0, 67.75)[0] + 72, top - 6))
    f.label("N+ guard ring in an\nN-well, on DVDD", (7.2, 84),
            (f.px(0, 84)[0], top - 6), colour=DVDD, weight="bold")
    # The P+ ring lies under the N+ ring, so its label sits in the gap
    # between it and the fingers, where no leader has to cross a ring.
    x, y = f.px(12.75, 92)
    f.label("P+ guard ring, on DVSS", (11.0, 92), (x, y + 5), colour=DVSS,
            weight="bold")
    # Finger parts, named in the right margin in the order they are drawn.
    x = f.ox + f.dw + 16
    rows = [
        (14.12, "Source, on DVSS", DVSS),
        (15.1, "Gate of the first finger", INK),
        (17.6, "Drain under the silicide block", INK),
        (19.78, "Drain contacts, on the PAD net", HOT),
        (21.9, "Drain, second finger's side", INK),
        (24.47, "Gate of the second finger", INK),
        (25.65, "Source shared by two fingers, on DVSS", DVSS),
        (26.83, "Gate of the third finger", INK),
    ]
    for gx, text, colour in rows:
        y = f.px(gx, 0)[1]
        f.label(text, (gx, 99.2), (x, y + 5), anchor="start", colour=colour,
                lead="left", weight="bold" if colour != INK else "normal")
    f.dim((15.67, 82.5), (19.45, 82.5), "blocked drain: 3.78 µm",
          side="below")
    f.dim((14.52, 78.4), (15.67, 78.4), "gate length: 1.15 µm", side="below")
    bot = f.oy + f.dh + 30
    f.label("Gate contacts, a pair at each end of every gate, to a pre-driver",
            (26.83, 75.05), (f.px(0, 75.05)[0] + 200, bot),
            elbow=(f.px(0, 75.05)[0], f.oy + f.dh + 8))
    f.note(DVSS, "on DVSS")
    f.note(DVDD, "on DVDD")
    f.note(HOT, "on the PAD net")
    return f


def _panel(window, title):
    f = Fig(CELL, window, 30, left=20, top=48, right=20, bottom=112)
    devices(f)
    f.title(title)
    return f


def _inside(f, text, gx, gy, row, dx=44):
    """Text inside a panel, starting at a layout point, tied to a row."""
    x, y = f.px(gx, gy)
    f.label(text, (row, gy + 1.25), (x + dx, y), anchor="start")


def silicide_block():
    """The blocked drains of both drivers beside an ordinary transistor."""
    a = _panel((13.2, 74.6, 26.8, 83.8), "(a) NMOS output driver, blocked")
    a.dim((15.67, 82.9), (19.45, 82.9), "blocked drain: 3.78 µm")
    a.dim((20.11, 82.9), (23.89, 82.9), "blocked drain: 3.78 µm")
    a.dim((14.52, 76.2), (15.67, 76.2), "gate length: 1.15 µm", side="below")
    _inside(a, "Drain contacts", 20.95, 75.0, 19.78)
    _inside(a, "Source contacts, unblocked", 13.62, 75.2, 14.0, dx=8)
    b = _panel((10.2, 144.9, 23.8, 154.1), "(b) PMOS output driver, blocked")
    b.dim((12.295, 153.2), (15.075, 153.2), "blocked drain: 2.78 µm")
    b.dim((15.735, 153.2), (18.515, 153.2), "blocked drain: 2.78 µm")
    b.dim((11.595, 146.5), (12.295, 146.5), "gate length: 0.7 µm", side="below")
    _inside(b, "Drain contacts", 16.58, 145.3, 15.405)
    _inside(b, "Source contacts, unblocked", 10.72, 145.5, 11.1, dx=8)
    c = _panel((20.3, 212.9, 33.9, 222.1), "(c) PMOS pre-driver, not blocked")
    c.dim((27.17, 214.4), (27.87, 214.4), "gate length: 0.7 µm", side="below")
    bot = c.oy + c.dh + 30
    c.label("Contacts beside every gate, on strips\n0.52 µm wide, all silicided", (32.7, 217.5),
            (c.px(0, 217.5)[0], bot))
    a.attach(b)
    a.attach(c)
    return a


FIGURES = {"gds-nmos-driver": nmos_driver, "gds-silicide-block": silicide_block}
