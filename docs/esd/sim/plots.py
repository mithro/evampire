# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Draw the ESD graphs that need no new simulation.

Writes, into docs/esd/figures/:

* clamp-timing.svg  the rail clamp's timer in a fast event and in a slow
                    power-up, from the hand estimate on io-cells.rst;
* budget.svg        the voltage that series resistance adds at 30 A;
* scaled.svg        the most stressed device against diode width, from
                    results/scaled.csv;
* tvs.svg           a board suppressor's voltage against current, and the
                    current it leaves to the chip.

Run with:  uv run docs/esd/sim/plots.py

SPDX-License-Identifier: Apache-2.0
"""

import csv
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
FIG = HERE.parent / "figures"
plt.rcParams.update({
    "figure.dpi": 100, "font.size": 11, "axes.labelsize": 11,
    "legend.fontsize": 9.5, "svg.fonttype": "none", "axes.grid": True,
    "grid.alpha": 0.3, "savefig.bbox": "tight", "svg.hashsalt": "gf180mcu-esd",
})
COL = {"dvdd": "#c0392b", "node": "#1f4e9c", "gate": "#e08a00",
       "a": "#8e44ad", "b": "#2e8b57"}


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / name, format="svg", metadata={"Date": None})
    plt.close(fig)


def timer(t, dvdd):
    """Timer node of the rail clamp: 360 kOhm charging MOS capacitors that
    hold 0.075 pF while depleted, below about 0.7 V, and 4.5 pF above."""
    v = np.zeros_like(t)
    for k in range(1, len(t)):
        c = 0.075e-12 if v[k - 1] < 0.7 else 4.5e-12
        dt = t[k] - t[k - 1]
        tau = 360e3 * c
        v[k] = dvdd[k] + (v[k - 1] - dvdd[k]) * np.exp(-dt / tau)
    # Three inverters from DVDD: the gate is high while the node is below
    # half of DVDD, once DVDD is high enough to switch them.
    gate = np.where((v < dvdd / 2) & (dvdd > 0.7), dvdd, 0.0)
    return v, gate


def clamp_timing():
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.0, 3.6))
    t = np.linspace(0, 100e-9, 2001)
    dvdd = np.where(t < 5e-9, 4.5 * t / 5e-9,
                    4.5 * np.exp(-(t - 5e-9) / 150e-9))
    v, gate = timer(t, dvdd)
    a.plot(t * 1e9, dvdd, color=COL["dvdd"], lw=2, label="DVDD")
    a.plot(t * 1e9, v, color=COL["node"], lw=2, label="timer node")
    a.plot(t * 1e9, gate, color=COL["gate"], lw=2, ls="--",
           label="clamp gate")
    a.set_title("(a) First 100 ns of an ESD event",
                loc="left", fontsize=11)
    a.set_xlabel("time (ns)")
    a.set_ylabel("voltage (V)")
    a.set_ylim(-0.2, 5.2)
    a.legend(loc="upper right")
    a.annotate("the node lags far below\nDVDD: the gate follows\n"
               "DVDD and the clamp is on", xy=(40, 0.8),
               xytext=(35, 1.6), arrowprops={"arrowstyle": "->"},
               fontsize=9.5)
    t = np.linspace(0, 100e-6, 20001)
    dvdd = 5.0 * t / 100e-6
    v, gate = timer(t, dvdd)
    b.plot(t * 1e6, dvdd, color=COL["dvdd"], lw=2, label="DVDD")
    b.plot(t * 1e6, v, color=COL["node"], lw=2, ls=(0, (4, 3)),
           label="timer node")
    b.plot(t * 1e6, gate, color=COL["gate"], lw=2, ls="--",
           label="clamp gate")
    b.set_title("(b) Power-up over 100 µs, much\nslower than τ = 1.6 µs",
                loc="left", fontsize=11)
    b.set_xlabel("time (µs)")
    b.set_ylim(-0.2, 5.2)
    b.legend(loc="upper left")
    b.annotate("node follows DVDD:\nclamp stays off", xy=(60, 0.05),
               xytext=(45, 1.2), arrowprops={"arrowstyle": "->"},
               fontsize=9.5)
    fig.tight_layout()
    save(fig, "clamp-timing.svg")


def budget():
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    r = np.linspace(0, 0.45, 50)
    ax.plot(r, 30 * r, color=COL["dvdd"], lw=2.2)
    ax.text(0.36, 8.4, "30 A × resistance", fontsize=10, color=COL["dvdd"])
    for v, s in ((10.7, "output NMOS trigger, 10.7 V"),
                 (12.0, "gate oxide breakdown, minimum 12 V")):
        ax.axhline(v, color="#555555", ls=":", lw=1.3)
        ax.text(0.005, v + 0.25, s, fontsize=9.5, color="#555555")
    for rr in (0.1, 0.2, 0.3):
        ax.plot([rr], [30 * rr], "o", color=COL["dvdd"])
        ax.text(rr + 0.008, 30 * rr - 0.9, f"{30 * rr:.0f} V", fontsize=9.5)
    ax.set_xlim(0, 0.45)
    ax.set_ylim(0, 14)
    ax.set_xlabel("resistance between the pad and the grounded supply (Ω)")
    ax.set_ylabel("voltage at 30 A (V)")
    ax.text(0.2, 1.2, "the diode and clamp voltages add to this",
            fontsize=9.5)
    save(fig, "budget.svg")


def scaled():
    rows = list(csv.DictReader((HERE / "results" / "scaled.csv").open()))
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for pads, pol, col, mark in (("1", "+", COL["a"], "o"),
                                 ("4", "+", COL["a"], "s"),
                                 ("1", "−", COL["b"], "o"),
                                 ("4", "−", COL["b"], "s")):
        pts = []
        for r in rows:
            if r["Pads"] != pads or r["Fraction"] == "no result":
                continue
            if (float(r["PAD (V)"]) > 0) != (pol == "+"):
                continue
            pts.append((float(r["Diodes (×)"]), float(r["Fraction"])))
        x, y = zip(*sorted(pts))
        gap = pads == "1" and pol == "−"
        if gap:
            # Same values as four pads at 1x and 4x: shift to stay visible.
            x = tuple(v * 1.07 for v in x)
        ax.plot(x, y, marker=mark, color=col, lw=1.8,
                mfc="white" if gap else col,
                ls="none" if gap else ("-" if pads == "4" else "--"),
                label=f"{'positive' if pol == '+' else 'negative'}, "
                      f"{pads} DVDD and {pads} DVSS "
                      f"pad{'s' if pads == '4' else ''}")
    ax.plot([4], [0.49], marker="*", ms=13, color=COL["a"], ls="none",
            label="positive, 4 pads, 500 ps NMOS trigger")
    ax.axhline(1.0, color="#555555", ls=":", lw=1.3)
    ax.text(1.05, 1.07, "measured failure current", fontsize=9.5,
            color="#555555")
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4], ["1×", "2×", "4×"])
    ax.set_xlabel("diode width, as a multiple of the standard pad's")
    ax.set_ylabel("most stressed device ÷ its failure current")
    ax.set_ylim(0, 5)
    ax.legend(loc="upper right", fontsize=9)
    save(fig, "scaled.svg")


def tvs():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    i = np.linspace(5, 30, 60)
    ax.fill_between(i, 14 + 0.32 * (i - 5), 14 + 0.38 * (i - 5),
                    color=COL["dvdd"], alpha=0.15, lw=0,
                    label="0.32 Ω to 0.38 Ω slope")
    fit = i <= 20
    ax.plot(i[fit], 14 + 0.38 * (i[fit] - 5), color=COL["dvdd"], lw=2.2,
            label="suppressor voltage, 0.38 Ω slope")
    ax.plot(i[~fit], 14 + 0.38 * (i[~fit] - 5), color=COL["dvdd"], lw=2.2,
            ls="--", label="extrapolated beyond the fitted range")
    ax.axvspan(10, 20, color="#2e8b57", alpha=0.08)
    ax.text(15, 10.4, "fitted\n10 A to 20 A", ha="center", fontsize=9.5,
            color="#2e8b57")
    ax.plot([5], [14], "o", color="black")
    ax.annotate("datasheet: 14 V at 5 A", xy=(5, 14), xytext=(4, 11.2),
                arrowprops={"arrowstyle": "->"}, fontsize=9.5)
    ax.plot([30], [23.5], "o", color=COL["dvdd"])
    ax.text(29.3, 24.3, "23.5 V at 30 A", ha="right", fontsize=9.5)
    ax.set_xlim(0, 31)
    ax.set_ylim(10, 26)
    ax.set_xlabel("discharge current through the suppressor (A)")
    ax.set_ylabel("suppressor voltage (V)")
    ax2 = ax.twinx()
    ax2.set_ylim((10 - 4) / 10, (26 - 4) / 10)
    ax2.set_ylabel("chip current through 10 Ω, pad at 4 V (A)")
    ax2.grid(False)
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "tvs.svg")


def main():
    clamp_timing()
    budget()
    scaled()
    tvs()


if __name__ == "__main__":
    main()
