# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Plot the foundry's TLP measurements of the four 6 V ESD devices.

Reads tlp_gf180mcu.csv (points read from the gf180mcu design manual,
sections 14.5.5 to 14.5.8) and writes docs/esd/figures/tlp-limits.svg:
current per micrometre of width against voltage, with each device's
failure point and the breakdown voltages that bound the pad. It needs no
ngspice or PDK, so it runs on its own:

    uv run docs/esd/sim/tlp_plot.py

The widths, failure currents and limits repeat those in spice.py, which
cannot be imported without the PDK checkouts.

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

# Device: (width in um, failure current in mA/um, voltage at failure in V,
# colour), design manual tables 14.5.5 to 14.5.8.
DEVICES = {
    "N+/P-well diode": (100.0, 30.0, 6.7, "#1f4e9c"),
    "P+/N-well diode": (100.0, 31.0, 6.9, "#c0392b"),
    "grounded-gate NMOS": (200.0, 7.0, 8.0, "#8e44ad"),
    "grounded-gate PMOS": (300.0, 5.3, 14.1, "#8c564b"),
}
GGNMOS_VT1, GGNMOS_FAIL_A, GGPMOS_VAV = 10.7, 1.42, 9.7
LIMITS = [(8.5, "6 V junction, min. 8.5 V"),
          (12.0, "6 V gate oxide, min. 12 V")]


def load():
    out = {}
    with (HERE / "tlp_gf180mcu.csv").open() as f:
        for r in csv.DictReader(f):
            out.setdefault(r["device"], []).append(
                (float(r["voltage_V"]), float(r["current_A"])))
    return {k: np.array(v) for k, v in out.items()}


def limits(ax, label):
    for v, text in LIMITS:
        ax.axvline(v, color="#555555", ls=":", lw=1.3)
        if label:
            ax.text(v + 0.12, 0.97, text, transform=ax.get_xaxis_transform(),
                    rotation=90, va="top", ha="left", fontsize=9,
                    color="#555555")


def plot(ax, tlp, dev, label):
    width, it2, vfail, colour = DEVICES[dev]
    pts = tlp[dev]
    ax.plot(pts[:, 0], 1e3 * pts[:, 1] / width, "o", ms=4, color=colour,
            label=label)
    ax.plot([vfail], [it2], "X", ms=10, color=colour, mec="black", mew=0.8)


def main():
    tlp = load()
    fig, (top, bot) = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True)
    plot(top, tlp, "N+/P-well diode", "N+/P-well diode, forward")
    plot(top, tlp, "P+/N-well diode", "P+/N-well diode, forward")
    top.set_ylim(0, 35)
    top.set_ylabel("Current per width (mA/µm)")
    top.set_title("(a) Diodes, forward biased", loc="left", fontsize=11)
    limits(top, True)

    plot(bot, tlp, "grounded-gate NMOS", "grounded-gate NMOS")
    plot(bot, tlp, "grounded-gate PMOS", "grounded-gate PMOS")
    # NMOS: blocks to its 10.7 V trigger, then snaps back to its first
    # measured point. The straight-line fit below 1.42 A meets zero
    # current at the holding voltage.
    _, _, _, cn = DEVICES["grounded-gate NMOS"]
    pn = tlp["grounded-gate NMOS"]
    bot.plot([0, GGNMOS_VT1], [0, 0], color=cn, lw=2)
    bot.plot([GGNMOS_VT1, pn[0, 0]], [0, 1e3 * pn[0, 1] / 200.0], "--",
             color=cn, lw=1.2)
    fit = pn[pn[:, 1] < GGNMOS_FAIL_A]
    slope, v0 = np.polyfit(fit[:, 1], fit[:, 0], 1)
    bot.plot([v0, pn[-1, 0]], [0, 1e3 * (pn[-1, 0] - v0) / slope / 200.0],
             "-", color=cn, lw=1, alpha=0.6)
    bot.text(0.2, 0.3, f"NMOS blocks to {GGNMOS_VT1} V,\nthen snaps back",
             fontsize=9.5, color=cn)
    bot.annotate(f"fit meets zero\ncurrent at {v0:.1f} V", xy=(v0, 0.05),
                 xytext=(3.0, 2.6), fontsize=9.5,
                 arrowprops={"arrowstyle": "->", "color": cn})
    # PMOS: blocks to its 9.7 V avalanche voltage and does not snap back.
    _, _, _, cp = DEVICES["grounded-gate PMOS"]
    pp = tlp["grounded-gate PMOS"]
    bot.plot([GGPMOS_VAV, pp[0, 0]], [0, 1e3 * pp[0, 1] / 300.0], "-",
             color=cp, lw=1.2)
    bot.annotate(f"PMOS avalanches\nat {GGPMOS_VAV} V, no\nsnapback",
                 xy=(GGPMOS_VAV, 0.25), xytext=(12.2, 0.4), fontsize=9.5,
                 arrowprops={"arrowstyle": "->", "color": cp})
    bot.set_ylim(0, 9.5)
    bot.set_ylabel("Current per width (mA/µm)")
    bot.set_title("(b) Grounded-gate transistors", loc="left", fontsize=11)
    bot.set_xlim(0, 15)
    bot.set_xlabel("TLP voltage (V)")
    limits(bot, False)
    bot.plot([], [], "X", ms=9, color="white", mec="black", mew=0.8,
             label="failure (second breakdown)")
    for ax in (top, bot):
        ax.legend(loc="lower right" if ax is top else "upper right")
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / "tlp-limits.svg", format="svg", metadata={"Date": None})
    print(f"grounded-gate NMOS fit: holding {v0:.2f} V")


if __name__ == "__main__":
    main()
