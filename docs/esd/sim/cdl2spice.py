"""Convert a gf180mcu_fd_io cell netlist (CDL) into an ngspice subcircuit.

The I/O library ships its cells as CDL netlists that name devices the way
the layout tools do (nfet_06v0, diode_nd2ps_06v0, ...). The ngspice models
in gf180mcu_fd_pr use other names and take some parameters under other
names. This module rewrites each device line for ngspice.

Device mapping (CDL name -> ngspice model):

    nfet_06v0          -> nmos_6p0        (subcircuit, called with X)
    pfet_06v0          -> pmos_6p0
    nfet_06v0_dss      -> nmos_6p0_sab    (silicide-blocked drain)
    pfet_06v0_dss      -> pmos_6p0_sab
    diode_nd2ps_06v0   -> np_6p0          (N+ to P-substrate/P-well diode)
    diode_pd2nw_06v0   -> pn_6p0          (P+ to N-well diode)
    cap_nmos_06v0      -> nmoscap_6p0
    ppolyf_u           -> ppolyf_u        (3-terminal poly resistor)

The silicide-blocked (sab) transistor models of gf180mcu_fd_pr include no
drain junction diode: the CDL gives them no drain area, and the drain
resistor model carries only junction capacitance. The real drain is a
diffusion in a well and forms a diode with it, and in an ESD event that
diode is the main current path. convert() therefore returns the list of
sab transistors, so the test bench can add a drain diode for each one
(see esd_sim.py).

SPDX-License-Identifier: Apache-2.0
"""

import re
from dataclasses import dataclass

MOS_MAP = {
    "nfet_06v0": "nmos_6p0",
    "pfet_06v0": "pmos_6p0",
    "nfet_06v0_dss": "nmos_6p0_sab",
    "pfet_06v0_dss": "pmos_6p0_sab",
}
DIODE_MAP = {
    "diode_nd2ps_06v0": "np_6p0",
    "diode_pd2nw_06v0": "pn_6p0",
}
# Widest transistor the 6 V model bins cover, in metres.
MAX_WIDTH = 100.01e-6
# Instance parameters each ngspice MOSFET subcircuit accepts.
MOS_PARAMS = {"w", "l", "nf", "as", "ad", "ps", "pd", "nrd", "nrs",
              "sa", "sb", "sd", "par", "dtemp", "s_sab", "d_sab"}


@dataclass
class SabDevice:
    """A silicide-blocked output transistor connected to the pad."""
    name: str
    kind: str        # "n" or "p"
    drain: str
    source: str
    width_um: float  # total width, all fingers


def _join_continuations(text):
    lines = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.startswith("*"):
            continue
        if line.startswith("+") and lines:
            lines[-1] += " " + line[1:].strip()
        else:
            lines.append(line)
    return lines


def _params(tokens):
    out = {}
    for tok in tokens:
        if "=" in tok:
            key, val = tok.split("=", 1)
            out[key.lstrip("$").lower()] = val
    return out


def _num(value):
    return float(value)


def convert(cdl_text):
    """Return (ngspice_text, [SabDevice, ...]) for every subcircuit."""
    out = []
    sab = []
    for line in _join_continuations(cdl_text):
        tokens = line.split()
        head = tokens[0].upper()
        if head == ".SUBCKT" or head == ".ENDS":
            out.append(line)
            continue
        kind = tokens[0][0].upper()
        name = tokens[0]
        if kind == "M":
            d, g, s, b, model = tokens[1:6]
            p = _params(tokens[6:])
            if _num(p.pop("m", "1")) != 1:
                raise ValueError(f"{name}: m != 1 is not handled")
            new_model = MOS_MAP[model]
            # The ngspice model bins stop at 100 um total width, so a wider
            # transistor becomes k parallel copies, each with 1/k of the
            # width, fingers and junction areas.
            width = _num(p["w"])
            nf = int(round(_num(p.get("nf", "1"))))
            k = 1
            while width / k > MAX_WIDTH:
                k += 1
                while nf % k and k < nf:
                    k += 1
            if k > 1:
                p["w"] = f"{width / k:.6g}"
                if nf % k == 0:
                    p["nf"] = str(nf // k)
                for key in ("as", "ad", "ps", "pd"):
                    if key in p:
                        p[key] = f"{_num(p[key]) / k:.6g}"
            args = " ".join(f"{k_}={v}" for k_, v in p.items()
                            if k_ in MOS_PARAMS)
            for i in range(k):
                suffix = f"_{i}" if k > 1 else ""
                out.append(
                    f"X{name}{suffix} {d} {g} {s} {b} {new_model} {args}")
            if model.endswith("_dss"):
                width_um = _num(p["w"]) * 1e6
                sab.append(SabDevice(name, model[0], d, s, width_um))
        elif kind == "D":
            anode, cathode, model = tokens[1:4]
            p = _params(tokens[4:])
            out.append(
                f"{name} {anode} {cathode} {DIODE_MAP[model]} "
                f"area={p['area']} pj={p['pj']} m={p.get('m', '1')}")
        elif kind == "C":
            n1, n2 = tokens[1:3]
            model = re.search(r"\$\[(\w+)\]", line).group(1)
            p = _params(tokens[3:])
            if model != "cap_nmos_06v0":
                raise ValueError(f"{name}: unknown capacitor {model}")
            mult = int(round(_num(p.get("m", "1"))))
            # An NMOS capacitor is a 6 V NMOS transistor with its gate as
            # one plate and its source, drain and body as the other. It is
            # simulated as that transistor with the BSIM4 model, which also
            # gives its capacitance against voltage. (The foundry's
            # nmoscap_6p0 expression model fails to start a transient in
            # ngspice.) The multiplier becomes parallel copies.
            for i in range(mult):
                out.append(f"X{name}_{i} {n2} {n1} {n2} {n2} nmos_6p0 "
                           f"w={p['w']} l={p['l']}")
        elif kind == "R":
            n1, n2 = tokens[1:3]
            model = re.search(r"\$\[(\w+)\]", line).group(1)
            p = _params(tokens[3:])
            if model != "ppolyf_u" or _num(p.get("m", "1")) != 1:
                raise ValueError(f"{name}: unsupported resistor")
            # The netlist states each resistor's value (r=), which matches
            # the foundry model's sheet and contact resistance. The
            # foundry's ppolyf_u subcircuit is not used: ngspice 44
            # converts its body resistor, written as a voltage-dependent
            # expression, into a source whose resistance equals the
            # resistor's length in metres. The model's capacitance to the
            # substrate (0.0885 fF/um2) is kept, half at each end.
            area = _num(p["w"]) * _num(p["l"])
            cap = 8.85e-5 * area / 2
            out.append(f"R{name} {n1} {n2} {p['r']}")
            out.append(f"C{name}a {n1} {p['sub']} {cap:.4g}")
            out.append(f"C{name}b {n2} {p['sub']} {cap:.4g}")
        else:
            raise ValueError(f"unhandled line: {line}")
    return "\n".join(out) + "\n", sab
