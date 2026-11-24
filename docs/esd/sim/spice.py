"""Paths, foundry figures and the ngspice runner shared by the ESD simulation.

SPDX-License-Identifier: Apache-2.0
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
NGSPICE = os.environ.get("NGSPICE") or shutil.which("ngspice")
PR = pathlib.Path(os.environ["GF180_PR"]) / "models" / "ngspice"
IO = pathlib.Path(os.environ["GF180_IO"]) / "cells"

# ---------------------------------------------------------------------------
# Measured TLP data from the gf180mcu design manual, section 14.5. Points read
# from the figures of sections 14.5.5 (6 V grounded-gate NMOS, 200 um wide),
# 14.5.6 (6 V grounded-gate PMOS, 300 um wide), 14.5.7 (6 V N+/P-well
# diode) and 14.5.8 (6 V P+/N-well diode, both 100 um wide). See
# tlp_gf180mcu.csv.
TLP_CSV = HERE / "tlp_gf180mcu.csv"
TLP_DIODE_WIDTH_UM = 100.0   # 4 fingers of 25 um
TLP_DIODE_AREA = 90e-12      # 4 x 25 um x 0.9 um, m^2
TLP_DIODE_PJ = 207.2e-6      # 4 x 2 x (25 + 0.9) um, m
# Series resistance parameter of the foundry's np_6p0 and pn_6p0 diode
# models (rs = 2e-10 * rsa, rsa = 1 in diode_typical; sm141064.ngspice
# lines 38145 and 38155), in ohm m^2: divided by the area in m^2.
FOUNDRY_RS = 2e-10

# Second-breakdown (failure) currents per micrometre of width, design manual
# tables 14.5.5 to 14.5.8.
IT2_MA_PER_UM = {
    "N+/P-well diode": 30.0,
    "P+/N-well diode": 31.0,
    "grounded-gate NMOS": 7.0,
    "grounded-gate PMOS": 5.3,
}
# TLP current of the pulse after which each transistor's leakage jumps, read
# from the figures: the device has failed, so the fits stop below it.
TLP_FAIL_A = {"grounded-gate NMOS": 1.42, "grounded-gate PMOS": 1.61}
# Grounded-gate NMOS snapback, design manual section 14.5.5: it triggers at
# 10.7 V (table). The holding voltage and on-resistance are fitted to the
# measured points by fit_ggnmos().
GGNMOS_VT1 = 10.7
GGNMOS_WIDTH_UM = 200.0      # 8 fingers of 25 um
# Time constant through which the snapback switch reads its voltage. The
# pad must stay above the trigger voltage for about this long before the
# switch closes, so a trial step of the solver that overshoots cannot
# close it.
SNAP_FILTER_S = 100e-12
# Grounded-gate PMOS, design manual section 14.5.6: it avalanches at 9.7 V
# (table) and does not snap back. fit_ggpmos() fits its avalanche branch.
GGPMOS_WIDTH_UM = 300.0      # 12 fingers of 25 um
# Breakdown limits, gf180mcu electrical parameters sections 5.4 and 5.5.
GATE_OXIDE_BV_MIN = 12.0     # 6 V gate oxide, minimum
JUNCTION_BV_MIN = 8.5        # N+ to P-well of a 6 V NMOS, minimum


def header():
    # The first line of a SPICE netlist is its title.
    return f"""\
* gf180mcu ESD simulation
.param sw_stat_global=0 sw_stat_mismatch=0 mc_skew=3 res_mc_skew=3
+ cap_mc_skew=3 fnoicor=0
.lib {PR}/sm141064.ngspice typical
.lib {PR}/sm141064.ngspice diode_typical
.lib {PR}/sm141064.ngspice res_typical
.lib {PR}/sm141064.ngspice moscap_typical
"""


class NgspiceFailed(RuntimeError):
    pass


def ngspice(netlist, vectors, timeout=180):
    """Run a netlist in batch mode; return {name: array} incl. 'time'."""
    (HERE / "cache").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=HERE / "cache") as tmp:
        tmp = pathlib.Path(tmp)
        out = tmp / "out.txt"
        cir = tmp / "tb.cir"
        cir.write_text(netlist.replace("@OUT@", str(out))
                       .replace("@VECS@", " ".join(vectors)))
        try:
            r = subprocess.run([NGSPICE, "-b", str(cir)],
                               capture_output=True, text=True,
                               timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise NgspiceFailed(f"timed out after {timeout} s") from exc
        if (r.returncode != 0 or not out.exists()
                or "aborted" in r.stdout + r.stderr):
            sys.stderr.write(r.stdout[-2000:] + r.stderr[-2000:])
            raise NgspiceFailed(f"ngspice stopped (exit {r.returncode})")
        data = np.loadtxt(out, skiprows=1, ndmin=2)
    names = ["time"] + list(vectors)
    return {n: data[:, i] for i, n in enumerate(names)}
