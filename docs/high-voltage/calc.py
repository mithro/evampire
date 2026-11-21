# /// script
# requires-python = ">=3.10"
# ///
"""Recompute every number on the "High voltage above the substrate" pages.

Run with:  uv run docs/high-voltage/calc.py

Each section prints the inputs and the results that the pages quote, in the
order they appear. Inputs marked "illustration" are example values chosen for
a worked example, not evampire design values.

SPDX-License-Identifier: Apache-2.0
"""

import math

Q = 1.602e-19          # electron charge (C)
EPS_SI = 1.035e-12     # permittivity of silicon, 11.7 x 8.854e-14 (F/cm)


def section(title):
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def show(name, value, unit="", fmt=".3g"):
    print(f"  {name:<56} {value:{fmt}} {unit}")


def bv_planar(n):
    """Baliga: breakdown of an abrupt one-sided planar junction (V)."""
    return 5.34e13 * n ** -0.75


def w_planar(n):
    """Baliga: depletion width at breakdown (cm)."""
    return 2.67e10 * n ** -0.875


def ratio_cyl(r_over_w):
    """Baliga and Ghandhi: cylindrical / planar breakdown."""
    x = r_over_w
    return (0.5 * (x ** 2 + 2 * x ** (6 / 7))
            * math.log(1 + 2 * x ** (-8 / 7)) - x ** (6 / 7))


def ratio_sph(r_over_w):
    """Baliga and Ghandhi: spherical / planar breakdown."""
    x = r_over_w
    return x ** 2 + 2.14 * x ** (6 / 7) - (x ** 3 + 3 * x ** (13 / 7)) ** (2 / 3)


# ---------------------------------------------------------------------------
section("1. Breakdown of a flat junction against doping")
print("  N (cm^-3)    BV (V)  W at breakdown (um)  average field (V/cm)  "
      "peak field (V/cm)")
for n in (1e14, 1e15, 2e15, 1e16, 1e17):
    bv, w = bv_planar(n), w_planar(n)
    print(f"  {n:9.0e}    {bv:6.0f}  {w * 1e4:19.2f}  {bv / w:20.3g}  "
          f"{2 * bv / w:16.3g}")

# ---------------------------------------------------------------------------
section("2. Substrate doping estimated from model junction capacitance")
# gf180mcu_fd_pr 9f992d5 models/ngspice/sm141064.ngspice: zero-bias area
# capacitance cjo (F/m^2), built-in potential pb (V), grading mj.
models = {
    "N-well to substrate, 6 V (diode_nw2ps_06v0)": (1.4914e-4, 0.43905, 0.30525),
    "deep N-well to substrate (diode_dw2ps)": (2.2998e-4, 0.35175, 0.14716),
}
for name, (cjo, pb, mj) in models.items():
    c0 = cjo * 1e-4                                # F/cm^2
    n0 = 2 * pb * c0 ** 2 / (Q * EPS_SI)           # abrupt, zero bias
    # Doping seen by the depletion edge between 2 V and 10 V reverse bias,
    # from the slope of 1/C^2 of the model's C(V) = C0 (1 + V/pb)^-mj.
    c = [c0 * (1 + v / pb) ** -mj for v in (2.0, 10.0)]
    slope = (1 / c[1] ** 2 - 1 / c[0] ** 2) / 8.0
    n_slope = 2 / (Q * EPS_SI * slope)
    show(name + ": N, zero bias", n0, "cm^-3")
    show(name + ": N, 1/C^2 slope 2-10 V", n_slope, "cm^-3")
    show("  flat-junction breakdown at the zero-bias N", bv_planar(n0), "V")

# ---------------------------------------------------------------------------
section("3. Curved junction edges break down early")
for n in (1e15, 2e15):
    bv, w = bv_planar(n), w_planar(n) * 1e4      # V, um
    print(f"  N = {n:.0e} cm^-3: flat {bv:.0f} V, W = {w:.1f} um")
    print("    r_j (um)   cylinder (V)   sphere (V)")
    for rj in (0.5, 1.0, 2.0, 3.0):
        x = rj / w
        print(f"    {rj:7.1f}   {bv * ratio_cyl(x):11.0f}   "
              f"{bv * ratio_sph(x):10.0f}")

# ---------------------------------------------------------------------------
section("4. Shortest grading length for a uniform field (illustration)")
for n in (1e15, 5e15):
    e_avg = bv_planar(n) / w_planar(n)          # average field at breakdown
    for v in (57.0, 100.0):
        show(f"N = {n:.0e}: E_avg {e_avg:.3g} V/cm, length for {v:g} V",
             v / e_avg * 1e4, "um")

# ---------------------------------------------------------------------------
section("5. Oxide thickness needed per volt (illustration)")
for field_mv in (10.0, 6.0, 4.0):               # MV/cm
    show(f"thickness for 57 V at {field_mv:g} MV/cm", 57 / (field_mv * 1e6) * 1e7,
         "nm")
    show(f"thickness for 100 V at {field_mv:g} MV/cm",
         100 / (field_mv * 1e6) * 1e7, "nm")

# ---------------------------------------------------------------------------
section("6. Resistive voltage gradients (illustration)")
# A polysilicon divider that forces a linear gradient: current set by design.
for v, i in ((57.0, 1e-6), (57.0, 10e-6)):
    show(f"divider holding {v:g} V at {i * 1e6:g} uA: resistance", v / i / 1e6,
         "Mohm")
    show(f"divider holding {v:g} V at {i * 1e6:g} uA: power", v * i * 1e6, "uW")
# Driving current through the substrate itself: slab between two contacts.
mu_p = 460.0          # hole mobility, cm^2/(V s), NBS SP 400-64 Table 5
n_sub = 1e15
rho = 1 / (Q * mu_p * n_sub)                    # ohm cm
length, width, thick = 0.1, 0.1, 0.03           # cm: 1 mm x 1 mm x 300 um
r_slab = rho * length / (width * thick)
show("substrate resistivity at 1e15 cm^-3", rho, "ohm cm")
show("slab 1 mm long, 1 mm wide, 300 um thick: resistance", r_slab, "ohm")
show("  current at 57 V", 57 / r_slab * 1e3, "mA")
show("  power at 57 V", 57 ** 2 / r_slab, "W")
