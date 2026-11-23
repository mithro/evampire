"""The ESD test circuit: the pads, the test generators and one simulated event.

SPDX-License-Identifier: Apache-2.0
"""

from calibrate import diode_model, driver_models
from cdl2spice import convert
from spice import (GGNMOS_VT1, IO, SNAP_FILTER_S, TLP_DIODE_AREA,
                   TLP_DIODE_PJ, TLP_DIODE_WIDTH_UM, NgspiceFailed, header,
                   ngspice)


# The chip under test: one bi_t pad, one DVDD pad and one DVSS pad, sharing
# the DVDD and DVSS rings.

def chip_netlist(rs_n, rs_p, ggnmos, ggpmos, clamps=True, r_ring=0.0,
                 drain_r_scale=1.0, diode_scale=1, supply_pads=1,
                 snap_filter=SNAP_FILTER_S):
    """The test chip. diode_scale widens the pad's diodes, as if dedicated
    diodes (diode_scale - 1) times the drivers' width were added beside
    them. supply_pads is the number of DVDD pads and of DVSS pads, each
    with its rail clamp. snap_filter is the time constant through which
    the snapback reads the pad voltage, in s. ggnmos is the snapback's (holding voltage in V,
    on-resistance in ohm um), from calibrate.fit_ggnmos(); ggpmos the PMOS
    avalanche's (V0 in V, resistance in ohm um), from fit_ggpmos()."""
    ggnmos_vh, ggnmos_ron_ohm_um = ggnmos
    ggpmos_v0, ggpmos_r_ohm_um = ggpmos
    bi_t, sab = convert((IO / "bi_t/gf180mcu_fd_io__bi_t.cdl").read_text())
    dvdd, _ = convert((IO / "dvdd/gf180mcu_fd_io__dvdd.cdl").read_text())
    dvss, _ = convert((IO / "dvss/gf180mcu_fd_io__dvss.cdl").read_text())
    # The drivers' drain diodes have no reverse breakdown: the snapback
    # and avalanche branches below model those junctions in breakdown.
    # Dedicated diodes added beside them keep the foundry's breakdown.
    lines = [diode_model("np_esd", "np_6p0", rs_n * drain_r_scale,
                         breakdown=False),
             diode_model("pn_esd", "pn_6p0", rs_p * drain_r_scale,
                         breakdown=False),
             diode_model("np_ded", "np_6p0", rs_n * drain_r_scale),
             diode_model("pn_ded", "pn_6p0", rs_p * drain_r_scale),
             driver_models(), bi_t, dvdd, dvss]
    w_n = sum(d.width_um for d in sab if d.kind == "n")
    w_p = sum(d.width_um for d in sab if d.kind == "p")
    w_snap = w_n
    w_aval = w_p
    scale_n = w_n / TLP_DIODE_WIDTH_UM
    scale_p = w_p / TLP_DIODE_WIDTH_UM
    ded = diode_scale - 1
    w_n *= diode_scale
    w_p *= diode_scale
    lines.append(f"""
* Drain diodes of the output transistors (absent from the foundry sab
* models), sized by total width from the TLP test structure.
Dndrain DVSSI PAD np_esd area={TLP_DIODE_AREA * scale_n:.4g} pj={TLP_DIODE_PJ * scale_n:.4g}
Dpdrain PAD DVDDI pn_esd area={TLP_DIODE_AREA * scale_p:.4g} pj={TLP_DIODE_PJ * scale_p:.4g}
* Dedicated diodes, {ded} times the drivers' width (none if 0).
Dnded DVSSI PAD np_ded area={TLP_DIODE_AREA * scale_n * max(ded, 1e-9):.4g} pj={TLP_DIODE_PJ * scale_n * max(ded, 1e-9):.4g}
Dpded PAD DVDDI pn_ded area={TLP_DIODE_AREA * scale_p * max(ded, 1e-9):.4g} pj={TLP_DIODE_PJ * scale_p * max(ded, 1e-9):.4g}
* Snapback of the grounded-gate output NMOS ({w_snap:.0f} um), fitted to TLP data.
* Once triggered, the branch conducts (V - Vh) / Ron above the holding
* voltage Vh and nothing below it, with the corner rounded over 50 mV.
* Trigger: the pad voltage, filtered over {snap_filter * 1e12:.0f} ps, charges a latch
* node ggq towards 1 V, at up to 0.02 V/ps, while it is above {GGNMOS_VT1} V (a
* step a few mV wide). Nothing discharges ggq. The branch turns on as ggq
* passes 0.4 V to 0.6 V, over about 10 ps; switching on faster discharges
* the pad's capacitance in a spike of a few picoseconds that no real NMOS
* shows. Every element is continuous
* and nothing feeds back into ggq, so only solved voltages can trigger it.
* (A self-charging latch is bistable: the implicit integrator can jump to
* its latched state in one step.)
Egg ggc 0 PAD DVSSI 1
Rggf ggc ggf 1k
Cggf ggf 0 {snap_filter / 1e3:.4g}
Bggq 0 ggq I = 0.02 * 0.5 * (1 + tanh((V(ggf) - {GGNMOS_VT1}) / 1e-3)) * max(1 - V(ggq), 0)
Cggq ggq 0 1p
Rggq ggq 0 1e15
Bgg PAD ggz I = 0.5 * (1 + tanh((V(ggq) - 0.5) / 0.05)) * {0.05 / (ggnmos_ron_ohm_um / w_snap):.6g} * ln(1 + exp(min((V(PAD,ggz) - {ggnmos_vh:.4f}) / 0.05, 500)))
Rggleak PAD ggz 1e9
Vigg ggz DVSSI 0
* Avalanche of the output PMOS drains ({w_aval:.0f} um) when DVDD is above the
* pad, fitted to TLP data: (V - V0) / R above V0, rounded over 50 mV.
Bgp gpx PAD I = {0.05 / (ggpmos_r_ohm_um / w_aval):.6g} * ln(1 + exp(min((V(gpx,PAD) - {ggpmos_v0:.4f}) / 0.05, 500)))
Vigp DVDDI gpx 0
""")
    lines.append("""
* Pad under test. Core-side inputs are tied low (unpowered core).
Xpad A0 CS0 DVDDI DVSSI IE0 OE0 PAD PD0 PDRV00 PDRV10 PU0 SL0 VDDC VSSC Y
+ gf180mcu_fd_io__bi_t
""")
    for n in ["A0", "CS0", "IE0", "OE0", "PD0", "PDRV00", "PDRV10", "PU0",
              "SL0"]:
        lines.append(f"R{n} {n} VSSC 1")
    # Ring resistance between the pad under test and the supply pads. With
    # none, a 0 V source joins the nodes: a tiny resistor would make the
    # circuit too stiff for the solver at the highest test voltages.
    if r_ring:
        lines.append(f"Rdd DVDDI DVDD {r_ring}")
        lines.append(f"Rss DVSSI DVSS {r_ring}")
    else:
        lines.append("Vdd_ring DVDDI DVDD 0")
        lines.append("Vss_ring DVSSI DVSS 0")
    if clamps:
        lines.append("Xvdd DVDD DVSS VSSC gf180mcu_fd_io__dvdd")
        lines.append("Xvss DVDD DVSS VDDC gf180mcu_fd_io__dvss")
        for i in range(1, supply_pads):
            lines.append(f"Xvdd{i} DVDD DVSS VSSC gf180mcu_fd_io__dvdd")
            lines.append(f"Xvss{i} DVDD DVSS VDDC gf180mcu_fd_io__dvss")
    # The tester grounds DVSS; every other pin floats.
    lines.append("Vdvss DVSS 0 0")
    lines.append("Rvssc VSSC DVSS 1\nRvddc VDDC 0 1e9\nRdvddleak DVDD 0 1e9")
    lines.append("Ry Y 0 1e9")
    return "\n".join(lines), w_n, w_p, w_snap, w_aval


HBM = {"C": 100e-12, "R": 1500.0, "L": 5e-6}
IEC = {"C1": 150e-12, "R1": 330.0, "L1": 2e-6,
       "C2": 6e-12, "R2": 200.0, "L2": 120e-9}


def source(kind, volts):
    """The test generator, discharging into node 'zap'.

    A capacitor charged to V is the same, seen from outside, as an
    uncharged capacitor in series with a source that steps from 0 to V. The
    step form lets the simulation start from an ordinary operating point
    with every node at 0 V.
    """
    step = f"EXP(0 {volts} 0 {STEP_TAU} 1 1)"
    if kind == "hbm":
        return f"""
Vhbm g0 0 {step}
Chbm g0 g1 {HBM['C']}
Rhbm g1 g2 {HBM['R']}
Lhbm g2 zap {HBM['L']}
"""
    return f"""
Viec g0 0 {step}
Ciec1 g0 g1 {IEC['C1']}
Riec1 g1 g2 {IEC['R1']}
Liec1 g2 zap {IEC['L1']}
Ciec2 g0 g3 {IEC['C2']}
Riec2 g3 g4 {IEC['R2']}
Liec2 g4 zap {IEC['L2']}
"""


# Time constant of the exponential step that stands for the charged
# capacitor, much shorter than either generator's own rise time. An
# exponential has no corner after t = 0; a straight ramp's corner stalls
# the solver at high test voltages.
STEP_TAU = 50e-12


# Channel currents of the PMOS and NMOS output drivers (the transistor
# inside each silicide-blocked subcircuit is named m0).
PMOS_DRIVERS = ["M10", "M13", "M14", "M17", "M18", "M21", "M22", "M25"]
NMOS_DRIVERS = ["M11", "M12", "M15", "M16", "M19", "M20", "M23", "M24"]
# Gate of the PMOS driver M10.
PMOS_GATE = "v(Xpad.n43)"
CHANNEL_VECS = ([f"@m.xpad.x{m.lower()}.m0[id]" for m in PMOS_DRIVERS]
                + [f"@m.xpad.x{m.lower()}.m0[id]" for m in NMOS_DRIVERS])
VECS = ["v(PAD)", "v(DVDD)", "v(Xpad.n20)", "i(Vzap)", "@Dndrain[id]",
        "@Dpdrain[id]", "@Dnded[id]", "@Dpded[id]", "i(Vigg)", "i(Vigp)",
        "v(ggf)", "v(ggq)", PMOS_GATE] + CHANNEL_VECS + ["v(Xvdd.n4)"]
# Drain and impact-ionisation substrate current of the 40 copies of the
# clamp transistor M17 in the DVDD and the DVSS pad.
CLAMP_VECS = [f"@m.{pad}.xm17_{i}.m0[{q}]" for pad in ("xvdd", "xvss")
              for i in range(40) for q in ("id", "isub")]


# Solver settings to try in turn: (label, integration method and extra
# options, maximum time step or None for the event's default, time limit in
# s). The later settings change only how the solver controls its step.
SOLVERS = (
    ("gear", "gear", None, 120),
    ("trap", "trap", None, 300),
    ("trap, trtol=1", "trap trtol=1", None, 300),
    ("gear, 0.1 ns step", "gear", "0.1n", 300),
)
# Shorter stop time for an event that no setting can finish (s).
SHORT_STOP = 4e-9


def zap(kind, volts, rs_n, rs_p, tstop, ggnmos, ggpmos, **chip):
    """Simulate one event; return its waveforms."""
    print(f"  {kind} {volts:+.0f} V {chip}", flush=True)
    tstep = "0.1n" if kind == "hbm" else "0.02n"
    body, w_n, w_p, w_snap, w_aval = chip_netlist(rs_n, rs_p, ggnmos,
                                                  ggpmos, **chip)
    net = header() + body + source(kind, volts) + f"""
Vzap zap PAD 0
.options method=@METHOD@ reltol=1e-3 itl4=200 gmin=1e-10 abstol=1e-9
+ chgtol=1e-14 rshunt=1e9
.tran {tstep} {tstop}
.control
set wr_vecnames
set wr_singlescale
save @VECS@
run
wrdata @OUT@ @VECS@
.endc
.end
"""
    clamps = chip.get("clamps", True)
    vecs = VECS + CLAMP_VECS if clamps else VECS[:-1]
    # Each solver setting in turn. If none finishes, the event is simulated
    # only to SHORT_STOP: every peak of an IEC pulse falls within its first
    # few nanoseconds.
    attempts = [(*sv, tstop) for sv in SOLVERS]
    attempts += [(*sv, SHORT_STOP) for sv in SOLVERS[:2]]
    for label, method, step, timeout, stop in attempts:
        try:
            d = ngspice(net.replace("@METHOD@", method)
                        .replace(f".tran {tstep} {tstop}",
                                 f".tran {step or tstep} {stop}"),
                        vecs, timeout)
            # A run that ends early without saying so is a failure too.
            if d["time"][-1] < stop * (1 - 1e-6):
                raise NgspiceFailed(
                    f"stopped at {d['time'][-1] * 1e9:.3g} ns")
            break
        except NgspiceFailed as exc:
            print(f"    {label} to {stop * 1e9:g} ns failed ({exc})",
                  flush=True)
    else:
        raise NgspiceFailed(f"{kind} {volts:+.0f} V failed with every method")
    method = label
    print(f"    solved with {method} to {stop * 1e9:g} ns", flush=True)
    return {
        "method": method, "stop": stop,
        "t": d["time"], "pad": d["v(PAD)"], "dvdd": d["v(DVDD)"],
        "inner": d["v(Xpad.n20)"], "i": d["i(Vzap)"],
        # Driver and dedicated diodes together.
        "ndiode": d["@Dndrain[id]"] + d["@Dnded[id]"],
        "pdiode": d["@Dpdrain[id]"] + d["@Dpded[id]"],
        "nded": d["@Dnded[id]"], "pded": d["@Dpded[id]"],
        "snap_q": d["v(ggq)"],
        "clamp_id": (sum(d[v] for v in CLAMP_VECS if v.endswith("[id]"))
                     if clamps else None),
        "clamp_isub": (sum(d[v] for v in CLAMP_VECS
                           if v.endswith("[isub]")) if clamps else None),
        "snap": d["i(Vigg)"], "aval": d["i(Vigp)"], "snap_ctl": d["v(ggf)"],
        "clamp_gate": d["v(Xvdd.n4)"] if clamps else None,
        "pmos_gate": d[PMOS_GATE],
        # Drain current of each driver, positive into the drain (the pad).
        "pchannel": sum(d[v] for v in CHANNEL_VECS[:len(PMOS_DRIVERS)]),
        "nchannel": sum(d[v] for v in CHANNEL_VECS[len(PMOS_DRIVERS):]),
        "w_n": w_n, "w_p": w_p, "w_snap": w_snap, "w_aval": w_aval,
    }


def short_circuit(kind, volts, tstop):
    net = header() + source(kind, volts) + f"""
Vzap zap 0 0
.tran 0.02n {tstop}
.control
set wr_vecnames
set wr_singlescale
run
wrdata @OUT@ @VECS@
.endc
.end
"""
    d = ngspice(net, ["i(Vzap)"])
    return d["time"], d["i(Vzap)"]
