# /// script
# requires-python = ">=3.11"
# dependencies = ["matplotlib>=3.8", "numpy>=1.26"]
# ///
"""Ten diode-connected gf180mcu 5 V NMOS transistors in series, swept 0-100 V.

Generates one ngspice netlist per bulk-connection variant, runs each in the
IIC-OSIC-TOOLS container (ngspice + open gf180mcuD PDK), then writes a
summary table and plots into ./results/.

Run with:  uv run sim/diode_stack/run.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
# Local image ID of hpretl/iic-osic-tools (ngspice-47, gf180mcuD); override
# with IIC_OSIC_IMAGE=hpretl/iic-osic-tools:<tag> on another machine.
IMAGE = os.environ.get("IIC_OSIC_IMAGE", "fd31cb46f41b")
NGSPICE = "/foss/tools/ngspice/bin/ngspice"
PDK = "/foss/pdks/gf180mcuD/libs.tech/ngspice"

N = 10                 # transistors in the stack
W = 10e-6              # channel width (m)
L = 0.6e-6             # channel length (m), nfet_05v0 minimum / default
SD_LEN = 0.18e-6       # source/drain diffusion length, xschem symbol default
V_MAX = 100.0
V_STEP = 0.05

# Variant B well geometry (assumed, per transistor): a 20 x 20 um deep
# N-well holding a 16 x 16 um isolated P-well.
DNW_SIDE = 20e-6
PW_SIDE = 16e-6

VARIANTS = {
    "A_shared_substrate": "Bulk of every NMOS is the common P-substrate (0 V). "
                          "This is what you get in gf180mcu without deep N-well.",
    "B_isolated_dnwell": "Each NMOS in its own isolated P-well (bulk = source) "
                         "inside its own deep N-well, deep N-well tied to the drain. "
                         "Well-to-well and well-to-substrate junctions are modelled.",
    "C_ideal_floating": "Bulk = source with NO junction to the substrate at all. "
                        "Not buildable; shows the 'textbook' answer for comparison.",
}


def netlist(variant: str) -> str:
    ad = W * SD_LEN
    pd = 2 * (W + SD_LEN)
    lines = [
        f"* {N} diode-connected nfet_05v0 in series, variant {variant}",
        f".include {PDK}/design.ngspice",
        f".lib {PDK}/sm141064.ngspice typical",
        f".lib {PDK}/sm141064.ngspice diode_typical",
        "",
        "VIN n0 0 0",
        "VBOT n%d 0 0" % N,      # ammeter: current leaving the bottom of the chain
        "VSUB sub 0 0",          # ammeter: current flowing into the P-substrate
        "",
    ]
    for k in range(1, N + 1):
        d, s = f"n{k-1}", f"n{k}"
        bulk = "sub" if variant.startswith("A") else s
        lines.append(f"XM{k} {d} {d} {s} {bulk} nfet_05v0 w={W:g} l={L:g} "
                     f"ad={ad:g} as={ad:g} pd={pd:g} ps={pd:g}")
        if variant.startswith("A"):
            # The BSIM4 nfet model in this PDK does NOT break down its own
            # drain/source-to-body junctions (checked: 2 nA at 40 V), so add
            # the PDK's N+ to P-substrate junction diode (bv = 11 V) for each
            # transistor's drain and source diffusion explicitly.
            lines.append(f"DJD{k} sub {d} diode_nd2ps_06v0 area={ad:g} pj={pd:g}")
            lines.append(f"DJS{k} sub {s} diode_nd2ps_06v0 area={ad:g} pj={pd:g}")
        if variant.startswith("B"):
            # P-well (anode = source node) to deep N-well (cathode = drain node)
            lines.append(f"DPW{k} {s} {d} diode_pw2dw area={PW_SIDE**2:g} pj={4*PW_SIDE:g}")
            # P-substrate (anode) to deep N-well (cathode = drain node)
            lines.append(f"DDW{k} sub {d} diode_dw2ps area={DNW_SIDE**2:g} pj={4*DNW_SIDE:g}")
    # n0 is the sweep itself and n10 is held at 0 V by VBOT, so only the
    # internal nodes are written (the loader rebuilds n0 and n10).
    vecs = " ".join(f"v(n{k})" for k in range(1, N))
    lines += [
        "",
        ".option gmin=1e-15 reltol=1e-4",
        f".dc VIN 0 {V_MAX} {V_STEP}",
        ".control",
        "set wr_singlescale",
        "set wr_vecnames",
        "run",
        f"wrdata {variant}.dat {vecs} i(VIN) i(VBOT) i(VSUB)",
        "quit",
        ".endc",
        ".end",
    ]
    return "\n".join(lines) + "\n"


def run_ngspice(variant: str) -> Path:
    cir = RESULTS / f"{variant}.cir"
    cir.write_text(netlist(variant))
    log = RESULTS / f"{variant}.log"
    cmd = [
        "docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}",
        "-e", f"HOME={RESULTS}", "-v", f"{HERE}:{HERE}", "-w", str(RESULTS),
        "--entrypoint", NGSPICE, IMAGE, "-b", cir.name,
    ]
    with log.open("w") as fh:
        rc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT).returncode
    if rc != 0:
        sys.exit(f"ngspice failed for {variant} (rc={rc}); see {log}")
    return RESULTS / f"{variant}.dat"


def load(dat: Path) -> dict[str, np.ndarray]:
    with dat.open() as fh:
        names = [n.lower() for n in fh.readline().split()]
    data = np.loadtxt(dat, skiprows=1)
    if data.shape[1] != len(names):
        sys.exit(f"{dat}: {len(names)} header names but {data.shape[1]} columns")
    cols = dict(zip(names, data.T))
    vin = data[:, 0]
    out = {"vin": vin}
    out["v"] = np.stack([vin] + [cols[f"v(n{k})"] for k in range(1, N)]
                        + [np.zeros_like(vin)])
    out["i_in"] = -cols["i(vin)"]      # current delivered by the source
    out["i_bot"] = cols["i(vbot)"]
    out["i_sub"] = cols["i(vsub)"]
    return out


def summarise(results: dict[str, dict]) -> str:
    probe = [2, 5, 8, 10, 12, 15, 20, 30, 40, 50, 75, 100]
    rows = []
    for name, r in results.items():
        rows.append(f"\n## {name}\n{VARIANTS[name]}\n")
        rows.append("| V_in (V) | I_in | I via chain bottom | I into substrate "
                    "| max V across one device (which) | V(top node) |")
        rows.append("|---:|---:|---:|---:|---:|---:|")
        for vp in probe:
            i = int(np.argmin(np.abs(r["vin"] - vp)))
            vdev = r["v"][:-1, i] - r["v"][1:, i]
            k = int(np.argmax(vdev))
            rows.append(f"| {r['vin'][i]:.0f} | {eng(r['i_in'][i])}A | "
                        f"{eng(r['i_bot'][i])}A | {eng(r['i_sub'][i])}A | "
                        f"{vdev[k]:.2f} V (M{k+1}) | {r['v'][0, i]:.1f} V |")
    return "\n".join(rows) + "\n"


def eng(x: float) -> str:
    if x == 0 or not np.isfinite(x):
        return f"{x:g} "
    for exp, p in ((9, "G"), (6, "M"), (3, "k"), (0, ""), (-3, "m"), (-6, "µ"),
                   (-9, "n"), (-12, "p"), (-15, "f"), (-18, "a")):
        if abs(x) >= 10 ** exp:
            return f"{x / 10**exp:.3g} {p}"
    return f"{x:.2e} "


# Reference palette (dataviz skill, light mode).
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {"A_shared_substrate": "#2a78d6", "B_isolated_dnwell": "#eb6834",
          "C_ideal_floating": "#1baf7a"}
LABEL = {"A_shared_substrate": "A: bulk = shared substrate",
         "B_isolated_dnwell": "B: isolated wells (deep N-well)",
         "C_ideal_floating": "C: ideal, no substrate junctions"}


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK2)
    ax.tick_params(colors=INK2)
    ax.xaxis.label.set_color(INK2)
    ax.yaxis.label.set_color(INK2)
    ax.title.set_color(INK)


def plot(results: dict[str, dict]) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    # 1. Input current, log scale.
    fig, ax = plt.subplots(figsize=(8, 5), facecolor=SURFACE)
    for name, r in results.items():
        ax.semilogy(r["vin"], np.abs(r["i_in"]) + 1e-18, color=SERIES[name],
                    linewidth=2, label=LABEL[name])
    ax.set_xlabel("Voltage across the stack, V_in (V)")
    ax.set_ylabel("Current drawn from the source (A, log scale)")
    ax.set_title("Ten diode-connected nfet_05v0 in series: current vs voltage",
                 loc="left")
    ax.set_xlim(0, V_MAX)
    ax.set_ylim(1e-15, None)
    style(ax)
    leg = ax.legend(frameon=False, loc="lower right")
    for t in leg.get_texts():
        t.set_color(INK)
    fig.tight_layout()
    fig.savefig(RESULTS / "current_vs_vin.png", dpi=150)
    plt.close(fig)

    # 2. Voltage across each device, one panel per variant (shared y axis).
    ramp = LinearSegmentedColormap.from_list("blue", ["#a9c9f0", "#0d3a73"])
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True,
                             facecolor=SURFACE)
    for ax, (name, r) in zip(axes, results.items()):
        vdev = r["v"][:-1] - r["v"][1:]
        for k in range(N):
            ax.plot(r["vin"], vdev[k], color=ramp(k / (N - 1)), linewidth=1.5)
        ax.axhline(5.0, color=INK2, linewidth=1, linestyle="--")
        ax.text(1, 5.3, "5 V device rating", color=INK2, fontsize=9)
        ax.set_title(LABEL[name], loc="left", fontsize=11)
        ax.set_xlabel("V_in (V)")
        ax.set_xlim(0, V_MAX)
        style(ax)
        # Direct-label top and bottom device only.
        ax.annotate("M1 (top)", (V_MAX, vdev[0, -1]), xytext=(-4, 4),
                    textcoords="offset points", ha="right", color=INK, fontsize=9)
        ax.annotate("M10 (bottom)", (V_MAX, vdev[-1, -1]), xytext=(-4, -12),
                    textcoords="offset points", ha="right", color=INK, fontsize=9)
    axes[0].set_ylabel("Voltage across one transistor, V_GS = V_DS (V)")
    fig.suptitle("Voltage across each transistor (light = top M1 … dark = bottom M10)",
                 x=0.01, ha="left", color=INK)
    fig.tight_layout()
    fig.savefig(RESULTS / "per_device_voltage.png", dpi=150)
    plt.close(fig)

    # 3. Where the current goes (variant A and B): chain bottom vs substrate.
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True,
                             facecolor=SURFACE)
    for ax, name in zip(axes, ["A_shared_substrate", "B_isolated_dnwell"]):
        r = results[name]
        ax.semilogy(r["vin"], np.abs(r["i_bot"]) + 1e-18, color="#2a78d6",
                    linewidth=2, label="out of the bottom of the chain")
        ax.semilogy(r["vin"], np.abs(r["i_sub"]) + 1e-18, color="#eb6834",
                    linewidth=2, label="into the substrate")
        ax.set_title(LABEL[name], loc="left", fontsize=11)
        ax.set_xlabel("V_in (V)")
        ax.set_xlim(0, V_MAX)
        ax.set_ylim(1e-15, None)
        style(ax)
        leg = ax.legend(frameon=False, loc="lower right")
        for t in leg.get_texts():
            t.set_color(INK)
    axes[0].set_ylabel("Current (A, log scale)")
    fig.tight_layout()
    fig.savefig(RESULTS / "current_paths.png", dpi=150)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / ".spiceinit").write_text("set ngbehavior=hsa\nset ng_nomodcheck\n")
    results = {}
    for v in VARIANTS:
        print(f"running {v} ...", flush=True)
        results[v] = load(run_ngspice(v))
    table = summarise(results)
    (RESULTS / "summary.md").write_text(table)
    print(table)
    plot(results)
    print(f"plots written to {RESULTS}")


if __name__ == "__main__":
    main()
