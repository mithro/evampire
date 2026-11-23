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
# capacitance cj (F/m^2), built-in potential pb (V) and grading mj of the
# junctions to the substrate. An abrupt one-sided junction has mj = 0.5; a
# linearly graded one has mj = 1/3. The abrupt formula is a rough estimate.
models = {
    "nwp_6p0, 6 V N-well (line 38193)": (1.4914e-4, 0.43905, 0.30525),
    "nwp_3p3, 3.3 V N-well (line 38162)": (1.4917e-4, 0.5755, 0.33979),
    "dnwps, deep N-well (line 38213)": (2.2998e-4, 0.35175, 0.14716),
}
print("  model                                 mj    N zero bias  "
      "N 1/C^2 slope 2-10 V  flat BV at zero-bias N")
for name, (cjo, pb, mj) in models.items():
    c0 = cjo * 1e-4                                # F/cm^2
    n0 = 2 * pb * c0 ** 2 / (Q * EPS_SI)           # abrupt, zero bias
    # Doping seen by the depletion edge between 2 V and 10 V reverse bias,
    # from the slope of 1/C^2 of the model's C(V) = C0 (1 + V/pb)^-mj.
    c = [c0 * (1 + v / pb) ** -mj for v in (2.0, 10.0)]
    slope = (1 / c[1] ** 2 - 1 / c[0] ** 2) / 8.0
    n_slope = 2 / (Q * EPS_SI * slope)
    print(f"  {name:<36} {mj:5.3f}  {n0:11.2e}  {n_slope:20.2e}  "
          f"{bv_planar(n0):8.0f} V")

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
section("4. Shortest length for a voltage to fall over in a uniform field")
# Effective ionisation coefficient alpha = A_ALPHA * E^7 (Fulop), Park
# Section 3.1.5, Eq. 3.25. Avalanche runs away when the integral of alpha
# across the field reaches 1. For a uniform field E = V/L over a length L
# that is A_ALPHA (V/L)^7 L = 1, so L = (A_ALPHA V^7)^(1/6).
A_ALPHA = 1.8e-35      # cm^6 V^-7
n = 1e15
w, vb = w_planar(n), bv_planar(n)
e_pk = 2 * vb / w                               # triangle: peak = 2 x average
show("check: ionisation integral of Baliga's flat junction at 1e15",
     A_ALPHA * e_pk ** 7 * w / 8)
show("  (its average field, V_B / W_B)", vb / w, "V/cm")
for v in (57.0, 100.0):
    length = (A_ALPHA * v ** 7) ** (1 / 6)
    show(f"uniform field holding {v:g} V: length", length * 1e4, "um")
    show(f"  field", v / length, "V/cm")
    show(f"  length at the flat junction's average field instead",
         v / (vb / w) * 1e4, "um")

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

# ---------------------------------------------------------------------------
section("7. Transistors with a metal layer as the gate")
# Area capacitance of each metal layer to the substrate over the field
# oxide, and over active silicon, in aF/um^2: nominal (min to max corner).
# open_pdks bb8c82e, gf180mcu/magic/gf180mcu-extract.tech, "defaultareacap"
# and "defaultoverlap ... alllvactivenonfet active" lines; the file says the
# values come from GlobalFoundries document PDS_035_03.
STACK = {
    "Metal1": ((29.304, 26.273, 33.126), (39.502, 35.846, 43.987)),
    "Metal2": ((15.016, 13.797, 16.471), (17.305, 16.047, 18.777)),
    "Metal3": ((10.094, 9.354, 10.961), (11.079, 10.337, 11.936)),
    "Metal4": ((7.602, 7.076, 8.213), (8.148, 7.625, 8.749)),
    "Metal5": ((5.798, 5.414, 6.240), (6.110, 5.729, 6.545)),
}
EPS_OX = 3.9 * 8.854e-14   # F/cm, MIT 6.012 slide 7-3
KT = 0.02585               # V at 300 K
NI = 1e10                  # cm^-3, illustration; gives 417 mV at 1e17, close
                           # to the 420 mV of MIT 6.012 slide 7-12
V_FB = -0.9                # V, illustration (an aluminium gate on P-type Si);
                           # anything from -0.3 V to -0.9 V changes little
MU_N = 400.0               # cm^2/(V s), illustration: electrons at the surface
N_LOW = 1.2e15             # lightest substrate estimate (section 2)
# Published threshold of a field transistor gated by Metal1 over field
# oxide, 6 V area, NCH, W/L = 200/0.36: "Vtsat FN-M1", 8.5 V minimum,
# 11 V typical (gf180mcu electrical specification, section 2.0, row 7).
VT_M1 = {"minimum": 8.5, "typical": 11.0}


def mos(n, c_ox):
    """Threshold (V), phi_F (V), Q_dep (C/cm^2), slope (mV/decade)."""
    phi_f = KT * math.log(n / NI)
    q_dep = math.sqrt(2 * Q * EPS_SI * n * 2 * phi_f)
    x_dmax = math.sqrt(2 * EPS_SI * 2 * phi_f / (Q * n))
    vt = V_FB + 2 * phi_f + q_dep / c_ox
    slope = KT * math.log(10) * 1e3 * (1 + (EPS_SI / x_dmax) / c_ox)
    return vt, phi_f, q_dep, slope


def doping_for(vt, c_ox):
    """Doping that gives threshold `vt` under `c_ox` (bisection in log N)."""
    lo, hi = 1e13, 1e19
    for _ in range(200):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if mos(mid, c_ox)[0] < vt else (lo, mid)
    return math.sqrt(lo * hi)


def cap(name, corner=0):
    """Area capacitance over field oxide (F/cm^2); corner 0 nominal."""
    return STACK[name][0][corner] * 1e-10


print("  Worked example, lightest substrate estimate, Metal1 and Metal5:")
for name in ("Metal1", "Metal5"):
    c = cap(name)
    vt, phi_f, q_dep, slope = mos(N_LOW, c)
    show(f"{name}: C_ox", c, "F/cm^2")
    show(f"{name}: phi_F", phi_f, "V")
    show(f"{name}: Q_dep", q_dep, "C/cm^2")
    show(f"{name}: Q_dep / C_ox", q_dep / c, "V")
    show(f"{name}: V_T", vt, "V")
print()
print("  layer   C field  t_eq field  t_eq active  C spread  "
      "E_ox at 57 V (MV/cm)")
for name, (field, active) in STACK.items():
    c, cmin, cmax = field
    t_f = EPS_OX / (c * 1e-10) * 1e4         # um
    t_a = EPS_OX / (active[0] * 1e-10) * 1e4
    print(f"  {name}  {c:7.2f}  {t_f:10.2f}  {t_a:11.2f}  "
          f"{(cmin / c - 1) * 100:+.0f}/{(cmax / c - 1) * 100:+.0f} %  "
          f"{57 / (t_f * 1e-4) / 1e6:8.2f}")
print()
# Calibration: find the doping that reproduces the published Metal1
# threshold, then apply it under every layer. This lumps doping and any
# charge at the silicon surface together; both scale as 1/C_ox.
N_CAL = {k: doping_for(v, cap("Metal1")) for k, v in VT_M1.items()}
for k, n in N_CAL.items():
    show(f"doping that gives the {k} Metal1 threshold {VT_M1[k]:g} V", n,
         "cm^-3")
print()
print("  layer   V_T: lightest estimate, calibrated minimum, calibrated "
      "typical (V)   slope at the same three (mV/dec)   dV_T per 1e11 cm^-2 (V)")
for name in STACK:
    c = cap(name)
    ns = (N_LOW, N_CAL["minimum"], N_CAL["typical"])
    vts = [mos(n, c)[0] for n in ns]
    slopes = [mos(n, c)[3] for n in ns]
    print(f"  {name}  " + "  ".join(f"{v:6.1f}" for v in vts) + "     "
          + "  ".join(f"{s:6.0f}" for s in slopes)
          + f"     {Q * 1e11 / c:6.2f}")
print()
V_DS = 1.0     # V, illustration: a low-voltage drain


def i_lin(w_over_l, c, v_g, vt):
    """Linear-region drain current (A), MIT 6.012 slide 10-3; 0 if off."""
    return max(0.0, w_over_l * MU_N * c * (v_g - V_DS / 2 - vt) * V_DS)


print("  layer   mu*C_ox (uA/V^2)   I_D at V_G = 57 V, V_DS = 1 V, W/L = 10 "
      "(uA): calibrated minimum, typical   gate C of 100 um x 100 um (fF)")
for name, (field, _) in STACK.items():
    c = cap(name)
    i_min = i_lin(10, c, 57, mos(N_CAL["minimum"], c)[0])
    i_typ = i_lin(10, c, 57, mos(N_CAL["typical"], c)[0])
    print(f"  {name}  {MU_N * c * 1e6:8.2f}   {i_min * 1e6:8.0f}  "
          f"{i_typ * 1e6:8.0f}   {field[0] * 10:8.1f}")
print()
c3 = cap("Metal3")
vt3 = mos(N_CAL["typical"], c3)[0]
print("  Worked example, Metal3, typical calibration, V_G = 57 V, W/L = 10:")
show("V_T", vt3, "V")
show("I_D", i_lin(10, c3, 57, vt3) * 1e6, "uA")
print()
print("  Level shift: two Metal1 gates at V_f and V_f + 5 V, typical "
      "calibration, V_DS = 1 V, W/L = 10")
c1 = cap("Metal1")
vt1 = mos(N_CAL["typical"], c1)[0]
show("Metal1 V_T, typical calibration", vt1, "V")
for vf in (15.0, 20.0, 40.0):
    lo, hi = i_lin(10, c1, vf, vt1), i_lin(10, c1, vf + 5, vt1)
    print(f"  V_f = {vf:4.0f} V: {lo * 1e6:6.1f} uA and {hi * 1e6:6.1f} uA, "
          f"difference {(hi - lo) * 1e6:5.1f} uA")
print()
# A plate also faces low-voltage metal under it. Metal2 over Metal1:
# open_pdks bb8c82e gf180mcu-extract.tech line 529, 59.027 aF/um^2.
t21 = EPS_OX / 59.027e-10
show("Metal2 over Metal1: equivalent thickness", t21 * 1e4, "um")
show("  field at 57 V between them", 57 / t21 / 1e6, "MV/cm")

# ---------------------------------------------------------------------------
section("8. Polysilicon over field oxide as a gate")
# open_pdks bb8c82e gf180mcu-extract.tech line 489: poly to substrate,
# 110.670 aF/um^2. Published field threshold with a polysilicon gate in
# the 3.3 V area: "Vtsat FN-Poly", 6.5 V minimum, 8.5 V typical
# (gf180mcu electrical specification, section 1.0, row 7).
c_poly = 110.670e-10
t_poly = EPS_OX / c_poly
show("equivalent thickness of the field oxide under polysilicon",
     t_poly * 1e4, "um")
for v in (57.0, 100.0):
    show(f"field in that oxide at {v:g} V", v / t_poly / 1e6, "MV/cm")
for n in (N_LOW, N_CAL["minimum"], N_CAL["typical"]):
    show(f"threshold under polysilicon at N = {n:.2g}", mos(n, c_poly)[0], "V")
