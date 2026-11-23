"""Fit the ESD device models to the foundry's TLP measurements.

SPDX-License-Identifier: Apache-2.0
"""

import csv
import re

import numpy as np

from spice import (GGNMOS_WIDTH_UM, GGPMOS_WIDTH_UM, PR, TLP_CSV,
                   TLP_DIODE_AREA, TLP_DIODE_PJ, TLP_FAIL_A, header, ngspice)


def foundry_card(base):
    """The foundry's .model card for a diode, on one line."""
    lines = (PR / "sm141064.ngspice").read_text().splitlines()
    for i, line in enumerate(lines):
        if re.match(rf"\.model\s+{base}\s", line, re.I):
            card = [line]
            for more in lines[i + 1:]:
                if not more.startswith("+"):
                    break
                card.append(more[1:])
            return " ".join(card)
    raise KeyError(base)


def _block(lines, start, is_end):
    """Lines from index start until is_end(line) is true (inclusive)."""
    out = []
    for line in lines[start:]:
        out.append(line)
        if len(out) > 1 and is_end(line):
            break
    return out


def driver_models(suffix="_esd"):
    """Copies of the foundry 6 V transistor models for the output drivers,
    renamed with suffix, with the drain and source junctions' forward
    current limit (ijthsfwd, ijthdfwd) lowered to 1 fA.

    BSIM4 extends each junction's exponential with a straight line above
    that limit; at the foundry's 0.1 A the line carries amperes even for a
    junction of almost no area. The test bench models the drivers' drain
    junctions with diodes fitted to measurement instead, so the
    transistors' own junctions must carry nothing."""
    lines = (PR / "sm141064.ngspice").read_text().splitlines()
    name_re = re.compile(r"\b([np]mos_6p0)(\.\d+)?\b(?!_)", re.I)
    out = []
    seen = set()
    for i, line in enumerate(lines):
        low = line.strip().lower()
        # The typical-corner sections come first in the file; later copies
        # (statistical corners) are skipped.
        key = " ".join(low.split()[:2])
        if key in seen:
            continue
        if re.match(r"\.model\s+[np]mos_6p0\.\d+\s", low):
            seen.add(key)
            card = [line]
            for more in lines[i + 1:]:
                s = more.strip()
                if s.startswith("+") or s.startswith("*") or not s:
                    card.append(more)
                else:
                    break
            out += card
        elif re.match(r"\.subckt\s+[np]mos_6p0\s", low):
            seen.add(key)
            out += _block(lines, i,
                          lambda l: l.strip().lower().startswith(".ends"))
    text = "\n".join(out)
    text = name_re.sub(lambda m: m.group(1) + suffix + (m.group(2) or ""),
                       text)
    text, n = re.subn(r"\b(ijth[sd]fwd)\s*=\s*[\d.eE+-]+", r"\1 = 1e-15",
                      text)
    assert n >= 3, n
    return text


def diode_model(name, base, rs, breakdown=True):
    """The foundry diode model with another series resistance.

    With breakdown=False the reverse breakdown is removed, for a junction
    whose avalanche another branch of the circuit already models.
    """
    card = foundry_card(base)
    card = re.sub(rf"^\.model\s+{base}\s", f".model {name} ", card, flags=re.I)
    card, n = re.subn(r"\brs\s*=\s*'[^']*'", f"rs={rs:.4g}", card)
    assert n == 1, base
    if not breakdown:
        card, n = re.subn(r"\bbv\s*=\s*[\d.eE+-]+", "", card)
        assert n == 1, base
        card = re.sub(r"\bibv\s*=\s*[\d.eE+-]+", "", card)
    return card


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


def fit_line(tlp, device, width_um, i_min=0.0):
    """Straight-line fit V = V0 + I * R to a device's conducting branch,
    from i_min up to the pulse after which its leakage jumps (the device
    has failed). Returns V0 in V and R times width in ohm um."""
    pts = tlp[device]
    pts = pts[(pts[:, 1] >= i_min) & (pts[:, 1] < TLP_FAIL_A[device])]
    slope, v0 = np.polyfit(pts[:, 1], pts[:, 0], 1)
    return v0, slope * width_um


def fit_ggnmos(tlp):
    """The grounded-gate NMOS after snapback: holding voltage and
    on-resistance."""
    return fit_line(tlp, "grounded-gate NMOS", GGNMOS_WIDTH_UM)


def fit_ggpmos(tlp):
    """The grounded-gate PMOS, which does not snap back: the voltage its
    avalanche current extrapolates to at zero, and its resistance. Points
    below 0.2 A, at the knee of the avalanche, are left out."""
    return fit_line(tlp, "grounded-gate PMOS", GGPMOS_WIDTH_UM, i_min=0.2)


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
