"""Figures and tables of the ESD simulation results.

SPDX-License-Identifier: Apache-2.0
"""

import csv

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from calibrate import diode_iv, diode_model  # noqa: E402
from spice import (FOUNDRY_RS, GATE_OXIDE_BV_MIN,  # noqa: E402
                   GGNMOS_VT1, HERE, IT2_MA_PER_UM)
from testbench import short_circuit  # noqa: E402

FIG = HERE.parent / "figures"
RES = HERE / "results"
STYLE = {
    "figure.dpi": 100, "font.size": 11, "axes.titlesize": 11,
    "axes.labelsize": 11, "legend.fontsize": 9.5, "svg.fonttype": "none",
    "axes.grid": True, "grid.alpha": 0.3, "savefig.bbox": "tight",
    # Drop points that make no visible difference, to keep the SVGs small.
    "path.simplify": True, "path.simplify_threshold": 1.0,
    # Fixed element ids, so a rerun with the same data gives the same file.
    "svg.hashsalt": "gf180mcu-esd",
}
plt.rcParams.update(STYLE)
COL = {"pad": "#1f4e9c", "dvdd": "#c0392b", "inner": "#2e8b57",
       "src": "#7f7f7f", "pdiode": "#c0392b", "ndiode": "#1f4e9c",
       "clamp": "#e08a00", "snap": "#8e44ad", "aval": "#8c564b"}


def save(fig, name):
    FIG.mkdir(exist_ok=True)
    fig.savefig(FIG / name, format="svg", metadata={"Date": None})
    plt.close(fig)


def fig_diode_fit(tlp, fits):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    currents = np.linspace(0, 3.0, 61)
    for dev, base, colour in [("N+/P-well diode", "np_6p0", COL["ndiode"]),
                              ("P+/N-well diode", "pn_6p0", COL["pdiode"])]:
        pts = tlp[dev]
        ax.plot(pts[:, 0], pts[:, 1], "o", ms=4, color=colour,
                label=f"{dev}, measured (TLP)")
        v0 = diode_iv(diode_model("d0", base, FOUNDRY_RS), "d0", currents)
        ax.plot(v0, currents, "--", color=colour, lw=1.2,
                label=f"{dev}, foundry model")
        v1 = diode_iv(diode_model("d1", base, fits[dev][0]), "d1", currents)
        ax.plot(v1, currents, "-", color=colour, lw=1.8,
                label=f"{dev}, fitted model")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 3.2)
    ax.set_xlabel("Voltage across the diode (V)")
    ax.set_ylabel("Current (A)")
    ax.legend(loc="lower right")
    save(fig, "diode-fit.svg")


def fig_sources():
    t1, i1 = short_circuit("hbm", 2000, 600e-9)
    t2, i2 = short_circuit("iec", 8000, 120e-9)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.4))
    a1.plot(t1 * 1e9, i1, color=COL["pad"])
    a1.set_title("Human body model, 2 kV")
    a1.set_xlabel("Time (ns)")
    a1.set_ylabel("Current into a short (A)")
    a2.plot(t2 * 1e9, i2, color=COL["dvdd"])
    a2.set_title("IEC 61000-4-2 contact, 8 kV")
    a2.set_xlabel("Time (ns)")
    fig.tight_layout()
    save(fig, "sources.svg")

    def metrics(t, i):
        k = np.argmax(i)
        t10 = t[np.argmax(i > 0.1 * i[k])]
        t90 = t[np.argmax(i > 0.9 * i[k])]
        return i[k], (t90 - t10) * 1e9
    return metrics(t1, i1), metrics(t2, i2)


def fig_zap(r, name, title, tmax_ns, show_snap=True):
    t = r["t"] * 1e9
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True)
    a1.plot(t, r["pad"], color=COL["pad"], lw=1.8, label="PAD")
    a1.plot(t, r["dvdd"], color=COL["dvdd"], lw=1.4, label="DVDD ring")
    a1.plot(t, r["inner"], color=COL["inner"], lw=1.4,
            label="input transistor gates")
    if r["clamp_gate"] is not None:
        a1.plot(t, r["clamp_gate"], color=COL["clamp"], lw=1.2, ls="--",
                label="rail clamp gate")
    a1.axhline(GATE_OXIDE_BV_MIN, color="k", ls=":", lw=1)
    a1.text(tmax_ns * 0.98, GATE_OXIDE_BV_MIN - 0.3,
            "gate oxide breakdown, minimum", ha="right", va="top",
            fontsize=9)
    a1.set_ylabel("Voltage (V)")
    a1.set_title(title)
    a1.legend(loc="best")
    a2.plot(t, r["i"], color=COL["src"], lw=2.4, label="total")
    # Every current is drawn positive when it flows out of the pad.
    a2.plot(t, r["pdiode"], color=COL["pdiode"], lw=1.4,
            label="PMOS drain diode")
    a2.plot(t, -r["ndiode"], color=COL["ndiode"], lw=1.4,
            label="NMOS drain diode")
    a2.plot(t, r["pchannel"], color=COL["pdiode"], lw=1.2, ls="--",
            label="PMOS driver channels")
    a2.plot(t, r["nchannel"], color=COL["ndiode"], lw=1.2, ls="--",
            label="NMOS driver channels")
    if show_snap:
        a2.plot(t, r["snap"], color=COL["snap"], lw=1.4,
                label="NMOS snapback")
    if abs(r["aval"]).max() > 0.01:
        a2.plot(t, -r["aval"], color=COL["aval"], lw=1.4,
                label="PMOS avalanche")
    a2.set_xlabel("Time (ns)")
    a2.set_ylabel("Current (A)")
    a2.set_xlim(0, tmax_ns)
    a2.legend(loc="best")
    fig.tight_layout()
    save(fig, name)


def summarise(r):
    """Peak values of one event, and each device's peak current density as
    a fraction of the foundry's measured failure current. None for an
    event that could not be simulated."""
    if r is None:
        return None
    w_n, w_p = r["w_n"], r["w_p"]
    k = int(np.argmax(abs(r["i"])))
    # Forward current only: the diodes' failure currents were measured
    # forward biased, and a reverse spike is charging current.
    jp = max(r["pdiode"].max(), 0) / w_p * 1e3
    jn = max(r["ndiode"].max(), 0) / w_n * 1e3
    js = abs(r["snap"]).max() / r["w_snap"] * 1e3
    ja = abs(r["aval"]).max() / r["w_aval"] * 1e3
    fracs = {"PMOS drain diode": jp / IT2_MA_PER_UM["P+/N-well diode"],
             "NMOS drain diode": jn / IT2_MA_PER_UM["N+/P-well diode"],
             "NMOS snapback": js / IT2_MA_PER_UM["grounded-gate NMOS"],
             "PMOS avalanche": ja / IT2_MA_PER_UM["grounded-gate PMOS"]}
    limit = max(fracs, key=fracs.get)
    frac = fracs[limit]
    above = r["pad"] > GATE_OXIDE_BV_MIN
    dt = np.diff(r["t"], append=r["t"][-1])
    # When the snapback latched (its latch node past half way), and the
    # filtered pad voltage by then. The latch charges only above the
    # trigger voltage, within a few millivolts, so a latch with its
    # control clearly below it means the model is wrong: stop.
    on = np.flatnonzero(r["snap_q"] > 0.5)
    trig = None
    if on.size:
        k_on = on[0]
        ctl = r["snap_ctl"][:k_on + 1].max()
        trig = {"t_ns": r["t"][k_on] * 1e9, "ctl_V": ctl,
                "pad_V": r["pad"][:k_on + 1].max()}
        if ctl < GGNMOS_VT1 - 0.01:
            raise RuntimeError(
                f"snapback latched with its control at {ctl:.3f} V")
    # Share of the rail clamps' drain current that is the transistor
    # model's impact-ionisation current into the substrate, at the clamps'
    # peak current.
    clamp = None
    if r.get("clamp_id") is not None:
        kc = int(np.argmax(abs(r["clamp_id"])))
        clamp = {"id_A": abs(r["clamp_id"][kc]),
                 "isub_A": abs(r["clamp_isub"][kc]),
                 "t_ns": r["t"][kc] * 1e9}
    # Reverse current of any dedicated diodes in breakdown.
    ded_rev = max(-min(r["nded"].min(), 0), -min(r["pded"].min(), 0))
    # Highest level of the latch: 0 never triggered, 1 fully on. Between
    # 0.4 and 0.6 the pad sat at the trigger voltage and the snapback
    # conducted only in part.
    latch = float(r["snap_q"].max())
    return {"trigger": trig, "clamp": clamp, "ded_rev_A": ded_rev,
        "latch": latch,
        "above_ns": float(np.sum(dt[above]) * 1e9),
        "pmos_gate_V": r["pmos_gate"][k] if r["pmos_gate"] is not None else 0,
        "peak_A": abs(r["i"][k]),
        "pad_at_peak_V": r["pad"][k],
        "pad_max_V": r["pad"][np.argmax(abs(r["pad"]))],
        "gate_max_V": r["inner"][np.argmax(abs(r["inner"]))],
        "jp": jp, "jn": jn, "js": js, "ja": ja, "frac": frac,
        "limit": limit,
    }


EVENT_COLUMNS = [
    ("Event", None),
    ("Peak (A)", lambda s: f"{s['peak_A']:.2f}"),
    ("PAD at peak (V)", lambda s: f"{s['pad_at_peak_V']:.1f}"),
    ("Highest PAD (V)", lambda s: f"{s['pad_max_V']:.1f}"),
    ("Highest gate (V)", lambda s: f"{s['gate_max_V']:.1f}"),
    ("PAD above 12 V (ns)", lambda s: f"{s['above_ns']:.0f}"),
    ("PMOS diode (mA/µm)", lambda s: f"{s['jp']:.1f}"),
    ("NMOS diode (mA/µm)", lambda s: f"{s['jn']:.1f}"),
    ("NMOS snapback (mA/µm)", lambda s: f"{s['js']:.1f}"),
    ("PMOS avalanche (mA/µm)", lambda s: f"{s['ja']:.1f}"),
    ("Fraction of limit", lambda s: f"{s['frac']:.2f}"),
]


def event_row(label, s):
    return {name: (label if f is None else
                   ("no result" if s is None else f(s)))
            for name, f in EVENT_COLUMNS}


def fig_sweep(sweep):
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    styles = {("hbm", 1): ("Human body model, positive", COL["pad"], "-"),
              ("hbm", -1): ("Human body model, negative", COL["pad"], "--"),
              ("iec", 1): ("IEC contact, positive", COL["dvdd"], "-"),
              ("iec", -1): ("IEC contact, negative", COL["dvdd"], "--")}
    for key, (label, colour, ls) in styles.items():
        pts = sorted((kv, s["frac"]) for (kind, sign, kv), s in sweep.items()
                     if (kind, sign) == key and s is not None)
        ax.plot([p[0] for p in pts], [p[1] for p in pts], ls, marker="o",
                ms=4, color=colour, label=label)
    ax.axhline(1.0, color="k", ls=":", lw=1)
    ax.text(0.3, 1.05, "measured failure current (TLP)", fontsize=9,
            va="bottom")
    ax.set_xlabel("Test voltage (kV)")
    ax.set_ylabel("Peak current density / failure current")
    ax.set_xlim(0, 15.5)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.93))
    save(fig, "sweep.svg")


def write_csv(name, rows, fieldnames=None):
    RES.mkdir(exist_ok=True)
    with (RES / name).open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


# Short device names for narrow tables.
SHORT_NAMES = {"PMOS drain diode": "PMOS diode",
               "NMOS drain diode": "NMOS diode",
               "NMOS snapback": "NMOS snapback",
               "PMOS avalanche": "PMOS avalanche"}
