"""Fit the ESD device models to the foundry's TLP measurements.

SPDX-License-Identifier: Apache-2.0
"""

import csv

import numpy as np

from spice import (GGNMOS_WIDTH_UM, TLP_CSV, TLP_DIODE_AREA,
                   TLP_DIODE_PJ, header, ngspice)


def diode_model(name, base, rs):
    """A copy of the foundry diode model with another series resistance."""
    if base == "np_6p0":
        return (f".model {name} d level=3 is=6.88e-7 jsw=4.88e-13 ik=229000 "
                f"n=1.0541 rs={rs:.4g} cj=0.00095 cjp=1.33e-10 pb=0.606 "
                f"php=0.48 mj=0.296 mjsw=0.01 bv=11 ibv=0.001")
    return (f".model {name} d level=3 is=2.0867e-7 jsw=1.6088e-13 ik=253800 "
            f"n=1.0058 rs={rs:.4g} cj=0.000912 cjsw=1.4649e-10 pb=0.76836 "
            f"php=0.5 mj=0.32713 mjsw=0.056777 bv=10.5 ibv=0.001")


def diode_iv(model_text, model_name, currents):
    net = header() + model_text + f"""
I1 0 a 0
D1 a 0 {model_name} area={TLP_DIODE_AREA} pj={TLP_DIODE_PJ}
.control
dc I1 0 {currents[-1]} {currents[1] - currents[0]}
wrdata @OUT@ @VECS@
.endc
.end
"""
    net = net.replace(".control", ".control\nset wr_vecnames\nset wr_singlescale")
    d = ngspice(net, ["v(a)"])
    return d["v(a)"]


def load_tlp():
    rows = list(csv.DictReader(TLP_CSV.open()))
    out = {}
    for r in rows:
        out.setdefault(r["device"], []).append(
            (float(r["voltage_V"]), float(r["current_A"])))
    return {k: np.array(v) for k, v in out.items()}


def fit_ggnmos(tlp):
    """Straight-line fit V = Vh + I * R to the snapped-back branch."""
    pts = tlp["grounded-gate NMOS"]
    slope, vh = np.polyfit(pts[:, 1], pts[:, 0], 1)
    return vh, slope * GGNMOS_WIDTH_UM


def fit_diode(tlp, base, device):
    """Find the series resistance that fits the TLP points up to 2 A."""
    pts = tlp[device]
    pts = pts[(pts[:, 1] >= 0.2) & (pts[:, 1] <= 2.0)]
    currents = np.linspace(0, 2.0, 41)
    best = None
    for rs in np.linspace(1e-11, 2e-10, 191):
        v = diode_iv(diode_model("dfit", base, rs), "dfit", currents)
        v_at = np.interp(pts[:, 1], currents, v)
        err = np.sqrt(np.mean((v_at - pts[:, 0]) ** 2))
        if best is None or err < best[0]:
            best = (err, rs)
    return best[1], best[0]
