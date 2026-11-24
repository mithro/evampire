# /// script
# requires-python = ">=3.10"
# ///
"""Write startup-timeline.svg: the 1000BASE-T start-up after
autonegotiation has chosen its result. It draws the timers that
autonegotiation.rst and 1000base-t-receiver.rst quote from IEEE
802.3-2022: maxwait_timer (40.4.5.2), link_fail_inhibit_timer and
break_link_timer (Table 28-9). Each bar is solid up to the timer's minimum
and lighter up to its maximum. Run with:

    uv run docs/ethernet/phy-electrical/startup_timeline.py

SPDX-License-Identifier: Apache-2.0
"""

import pathlib

from svgplot import Axes, Fig, BLUE, RED, GREEN, GREY, INK, fmt

HERE = pathlib.Path(__file__).parent

# (label, start ms, minimum end ms, maximum end ms, colour)
ROWS = [
    ("Slave trains: maxwait_timer, 350 ms ± 5 ms", 0, 345, 355, BLUE),
    ("Master trains: maxwait_timer, 750 ms ± 10 ms", 0, 740, 760, BLUE),
    ("link_fail_inhibit_timer, 750 ms to 1000 ms: the link must be up",
     0, 750, 1000, GREEN),
    ("If no link by then: silent for break_link_timer,\n1200 ms to 1500 ms, then negotiation restarts", 1000, 2200,
     2500, RED),
]


def main():
    fig = Fig(480, 350)
    ax = Axes(fig, 20, 70, 466, 300, (-300, 2600), (0, 4))
    ax.band(0, 4, "#f2f2f2", -300, 0)
    ax.frame([0, 500, 1000, 1500, 2000, 2500], [], "Time after the "
             "autonegotiation result (ms)", None, xfmt=fmt, grid=True)
    fig.text(ax.X(-150), 50, "page\nexchange", size=12, fill=GREY)
    fig.text(ax.X(-150), ax.Y(0.5), "bursts\nevery\n8 ms to\n24 ms",
             size=11, fill=GREY)
    fig.text(20, 22, "Each bar is solid to the timer's minimum and pale to "
             "its maximum.", size=12, anchor="start", fill=GREY)
    for i, (label, start, lo, hi, colour) in enumerate(ROWS):
        y = ax.Y(3.5 - i)
        fig.rect(ax.X(start), y - 7, ax.X(lo) - ax.X(start), 14, fill=colour,
                 stroke="none")
        fig.rect(ax.X(lo), y - 7, ax.X(hi) - ax.X(lo), 14, fill=colour,
                 stroke="none")
        fig.add(f'<rect x="{ax.X(lo):.1f}" y="{y - 7:.1f}" '
                f'width="{ax.X(hi) - ax.X(lo):.1f}" height="14" '
                'fill="#ffffff" fill-opacity="0.6"/>')
        fig.text(ax.X(0) + 4, y - 18 - 7 * label.count("\n"), label, size=12,
                 anchor="start")
    fig.save(HERE / "startup-timeline.svg")


if __name__ == "__main__":
    main()
