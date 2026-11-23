# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "matplotlib"]
# ///
"""Simulate ESD events on the gf180mcu_fd_io bidirectional pad with ngspice.

Writes the figures in docs/esd/figures/ and the result tables in
docs/esd/sim/results/. The work is split across spice.py (paths,
foundry figures, the ngspice runner), calibrate.py (fits to the
foundry's TLP data), testbench.py (the test circuit), report.py
(figures and tables) and cdl2spice.py (the netlist converter). Needs:

* ngspice (44 or later) on PATH, or NGSPICE=/path/to/ngspice
* a checkout of https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_pr
  (the device models), GF180_PR=/path/to/it
* a checkout of https://github.com/google/globalfoundries-pdk-libs-gf180mcu_fd_io
  (the I/O cell netlists), GF180_IO=/path/to/it

Run with, inside a systemd scope that caps its memory and processes:

    GF180_PR=... GF180_IO=... systemd-run --user --scope \
        -p MemoryMax=8G -p MemorySwapMax=0 -p TasksMax=256 \
        uv run docs/esd/sim/esd_sim.py

It runs twelve events at once and takes about twenty minutes. With
--reuse it rebuilds the tables and figures from the waveforms of the last
run, saved in docs/esd/sim/cache/, in about a minute.

SPDX-License-Identifier: Apache-2.0
"""

import concurrent.futures
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from calibrate import (fit_diode, fit_ggnmos, fit_ggpmos,  # noqa: E402
                       load_tlp)
from report import (SHORT_NAMES, event_row, fig_diode_fit,  # noqa: E402
                    fig_sources, fig_sweep, fig_zap, summarise, write_csv)
from spice import FOUNDRY_RS, HERE, TLP_DIODE_AREA  # noqa: E402
from testbench import zap  # noqa: E402
from spice import NgspiceFailed  # noqa: E402

# Waveforms of the last run, for --reuse (not kept in the repository).
CACHE = HERE / "cache" / "waves.pickle"
# Events simulated at once. Each ngspice uses one core and tens of MB.
WORKERS = 12


def _run_job(args):
    kind, volts, tstop, chip, rs_n, rs_p, ggnmos, ggpmos = args
    try:
        return zap(kind, volts, rs_n, rs_p, tstop, ggnmos, ggpmos, **chip)
    except NgspiceFailed as exc:
        print(f"  NO RESULT: {kind} {volts:+.0f} V {chip}: {exc}",
              flush=True)
        return None


def run_parallel(jobs, rs_n, rs_p, ggnmos, ggpmos):
    """Run every zap() in jobs ({key: (kind, volts, tstop, chip)}) in
    parallel; return {key: result}."""
    with concurrent.futures.ProcessPoolExecutor(WORKERS) as pool:
        futures = {key: pool.submit(_run_job, (*job, rs_n, rs_p, ggnmos, ggpmos))
                   for key, job in jobs.items()}
        return {key: f.result() for key, f in futures.items()}


def main():
    tlp = load_tlp()
    GGNMOS_VH, GGNMOS_RON_OHM_UM = ggnmos = fit_ggnmos(tlp)
    write_csv("ggnmos-fit.csv", [{
        "Holding voltage (V)": f"{GGNMOS_VH:.2f}",
        "On-resistance (Ω·µm)": f"{GGNMOS_RON_OHM_UM:.0f}",
        "On-resistance of 200 µm (Ω)": f"{GGNMOS_RON_OHM_UM / 200:.2f}"}])
    GGPMOS_V0, GGPMOS_R_OHM_UM = ggpmos = fit_ggpmos(tlp)
    write_csv("ggpmos-fit.csv", [{
        "Avalanche onset, fitted (V)": f"{GGPMOS_V0:.2f}",
        "Resistance (Ω·µm)": f"{GGPMOS_R_OHM_UM:.0f}",
        "Resistance of 300 µm (Ω)": f"{GGPMOS_R_OHM_UM / 300:.2f}"}])
    fits = {
        "N+/P-well diode": fit_diode(tlp, "np_6p0", "N+/P-well diode"),
        "P+/N-well diode": fit_diode(tlp, "pn_6p0", "P+/N-well diode"),
    }
    rs_n = fits["N+/P-well diode"][0]
    rs_p = fits["P+/N-well diode"][0]
    fig_diode_fit(tlp, fits)
    write_csv("diode-fit.csv", [
        {"Diode": k,
         "Foundry model (Ω)": f"{FOUNDRY_RS / TLP_DIODE_AREA:.2f}",
         "Fitted (Ω)": f"{v[0] / TLP_DIODE_AREA:.2f}",
         "RMS error of fit (V)": f"{v[1]:.2f}"} for k, v in fits.items()])

    (hbm_pk, hbm_tr), (iec_pk, iec_tr) = fig_sources()
    write_csv("sources.csv", [
        {"Generator": "Human body model", "Voltage (kV)": "2",
         "Peak (A)": f"{hbm_pk:.2f}", "Peak (A/kV)": f"{hbm_pk / 2:.2f}",
         "Rise, 10 % to 90 % (ns)": f"{hbm_tr:.1f}"},
        {"Generator": "IEC 61000-4-2 contact", "Voltage (kV)": "8",
         "Peak (A)": f"{iec_pk:.1f}", "Peak (A/kV)": f"{iec_pk / 8:.2f}",
         "Rise, 10 % to 90 % (ns)": f"{iec_tr:.2f}"},
    ])

    # Every level of both tests, both polarities. The IEC levels are the
    # contact levels, plus 15 kV, the air-discharge level 4, simulated with
    # the contact waveform.
    levels = {"hbm": (0.5, 1, 2, 4, 8), "iec": (2, 4, 6, 8, 15)}
    tstop = {"hbm": 600e-9, "iec": 150e-9}
    jobs = {(kind, sign, kv): (kind, sign * kv * 1000, tstop[kind], {})
            for kind, kvs in levels.items() for kv in kvs for sign in (1, -1)}
    jobs["noclamp"] = ("hbm", 2000, 600e-9, {"clamps": False})
    jobs["drain_r"] = ("hbm", 2000, 600e-9, {"drain_r_scale": 2.0})
    jobs["ring_r"] = ("hbm", 2000, 600e-9, {"r_ring": 1.0})
    # The same pad with wider diodes and more supply pads, at level 4.
    scaled = [(k, m) for k in (1, 2, 4) for m in (1, 4)]
    for k, m in scaled:
        for sign in (1, -1):
            jobs[("scaled", k, m, sign)] = (
                "iec", sign * 8000, 150e-9,
                {"diode_scale": k, "supply_pads": m})
    # --reuse reads the waveforms of the last run instead of simulating,
    # for changes to the tables and figures only.
    if "--reuse" in sys.argv and CACHE.exists():
        with CACHE.open("rb") as f:
            waves = pickle.load(f)
    else:
        waves = run_parallel(jobs, rs_n, rs_p, ggnmos, ggpmos)
        CACHE.parent.mkdir(exist_ok=True)
        with CACHE.open("wb") as f:
            pickle.dump(waves, f)
    sweep = {k: summarise(waves[k]) for k in jobs
             if isinstance(k, tuple) and k[0] != "scaled"}
    def scaled_row(k, m, sign):
        s_ = summarise(waves[("scaled", k, m, sign)])
        row = {"Diodes (×)": k,
               "Pads": m}
        if s_ is None:
            return {**row, "PAD (V)": "no result",
                    "Fraction": "no result",
                    "Most stressed": "no result"}
        return {**row, "PAD (V)": f"{s_['pad_max_V']:.1f}",
                "Fraction": f"{s_['frac']:.2f}",
                "Most stressed": SHORT_NAMES[s_["limit"]]}
    write_csv("scaled.csv", [scaled_row(k, m, sign)
                             for k, m in scaled for sign in (1, -1)])
    fig_sweep(sweep)
    def sweep_row(key, s_):
        kind, sign, kv = key
        row = {"Test": ("HBM" if kind == "hbm" else "IEC")
                       + f" {sign * kv:+g} kV"}
        if s_ is None:
            return {**row, "Peak (A)": "no result",
                    "Highest PAD (V)": "no result",
                    "Fraction of limit": "no result",
                    "Most stressed": "no result"}
        return {**row,
                "Peak (A)": f"{s_['peak_A']:.1f}",
                "Highest PAD (V)": f"{s_['pad_max_V']:.1f}",
                "Fraction of limit": f"{s_['frac']:.2f}",
                "Most stressed": SHORT_NAMES[s_["limit"]]}
    # Every event that needed another solver setting or a shorter run,
    # with the time it was solved to.
    def event_name(key):
        if key[0] == "scaled":
            _, k, m, sign = key
            return (f"IEC {sign * 8:+d} kV, {k}× diodes, {m} pad"
                    + ("s" if m > 1 else ""))
        if not isinstance(key, tuple):
            return {"noclamp": "HBM +2 kV, no clamp",
                    "drain_r": "HBM +2 kV, diode R × 2",
                    "ring_r": "HBM +2 kV, ring 1 Ω"}[key]
        return ("HBM" if key[0] == "hbm" else "IEC") + f" {key[1] * key[2]:+g} kV"
    write_csv("solver.csv", [
        {"Event": event_name(key),
         "Solver": waves[key]["method"],
         "Simulated to (ns)": f"{waves[key]['t'][-1] * 1e9:.0f}"}
        for key, job in jobs.items()
        if waves[key] is not None and (waves[key]["method"] != "gear"
                                       or waves[key]["stop"] < job[2])],
        fieldnames=["Event", "Solver", "Simulated to (ns)"])
    # When each snapback closed, and the filtered pad voltage by then.
    write_csv("trigger.csv", [
        {"Event": event_name(key),
         "Highest PAD before (V)": f"{s_['trigger']['pad_V']:.1f}",
         "Filtered PAD (V)": f"{s_['trigger']['ctl_V']:.1f}",
         "Closed at (ns)": f"{s_['trigger']['t_ns']:.2f}"}
        for key in jobs
        for s_ in [summarise(waves[key])]
        if s_ is not None and s_["trigger"] is not None],
        fieldnames=["Event", "Highest PAD before (V)", "Filtered PAD (V)",
                    "Closed at (ns)"])
    write_csv("sweep.csv", [sweep_row(k, v) for k, v in sweep.items()])

    fig_zap(waves[("hbm", 1, 2)], "hbm-pos.svg",
            "+2 kV human body model, PAD to DVSS", 600)
    fig_zap(waves[("hbm", -1, 2)], "hbm-neg.svg",
            "−2 kV human body model, PAD to DVSS", 600)
    fig_zap(waves[("iec", 1, 8)], "iec-8kv.svg",
            "+8 kV IEC 61000-4-2 contact, PAD to DVSS", 150)
    r = waves["noclamp"]
    fig_zap(r, "hbm-noclamp.svg",
            "+2 kV human body model, no rail clamp", 600)
    rows = [event_row("HBM +2 kV", sweep[("hbm", 1, 2)]),
            event_row("HBM −2 kV", sweep[("hbm", -1, 2)]),
            event_row("HBM +2 kV, no clamp", summarise(r)),
            event_row("IEC +8 kV", sweep[("iec", 1, 8)]),
            event_row("IEC −8 kV", sweep[("iec", -1, 8)]),
            event_row("IEC +15 kV", sweep[("iec", 1, 15)]),
            event_row("IEC −15 kV", sweep[("iec", -1, 15)])]
    volt_cols = ["Event", "PAD at peak (V)",
                 "Highest PAD (V)", "Highest gate (V)",
                 "PAD above 12 V (ns)"]
    cur_cols = ["Event", "PMOS diode (mA/µm)",
                "NMOS diode (mA/µm)", "NMOS snapback (mA/µm)",
                # PMOS avalanche is left out to fit 400 px; only -15 kV has any.
                "Fraction of limit"]
    write_csv("events-voltage.csv",
              [{c: row[c] for c in volt_cols} for row in rows])
    # The caption gives the unit, mA/um, so the headings stay short.
    write_csv("events-current.csv",
              [{c.replace(" (mA/µm)", "").replace("Fraction of limit",
                                                   "Fraction"): row[c]
                for c in cur_cols} for row in rows])

    # Sensitivity of the +2 kV HBM result to the two least-known inputs.
    sens = [event_row("as simulated", sweep[("hbm", 1, 2)])]
    for label, key in [("drain diode resistance × 2", "drain_r"),
                       ("ring resistance 1 Ω each way", "ring_r")]:
        sens.append(event_row(label, summarise(waves[key])))
    write_csv("sensitivity.csv", [
        {"Change": row["Event"],
         "PAD at peak (V)": row["PAD at peak (V)"],
         "Highest PAD (V)": row["Highest PAD (V)"],
         "Highest gate (V)": row["Highest gate (V)"],
         "PMOS diode (mA/µm)": row["PMOS diode (mA/µm)"]} for row in sens])
    print("PMOS driver gate at peak current, +2 kV HBM:",
          f"{sweep[('hbm', 1, 2)]['pmos_gate_V']:.2f} V")
    print("done")


if __name__ == "__main__":
    main()
