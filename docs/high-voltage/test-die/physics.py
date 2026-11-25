"""The equations the test-die pages quote, as plain functions.

calc.py prints the worked examples from these, and fig_pred.py and
fig_method.py plot them. Lengths in cm, fields in V/cm, doping in cm^-3
unless a name says otherwise.

SPDX-License-Identifier: Apache-2.0
"""

import math

Q = 1.602e-19          # electron charge, C
EPS = 1.035e-12        # permittivity of silicon, F/cm
KT = 0.02585           # thermal voltage at 300 K, V
NI = 1e10              # intrinsic carrier density at 300 K, cm^-3

# van Overstraeten and de Man (1970), alpha = a exp(-b / E), at 300 K.
AN, BN = 7.03e5, 1.231e6
AP_LO, BP_LO = 1.582e6, 2.036e6     # holes, field up to 4e5 V/cm
AP_HI, BP_HI = 6.71e5, 1.693e6      # holes, field above 4e5 V/cm
E_SWITCH = 4.0e5


def alpha_n(e):
    return AN * math.exp(-BN / e) if e > 1 else 0.0


def alpha_p(e):
    if e <= 1:
        return 0.0
    if e > E_SWITCH:
        return AP_HI * math.exp(-BP_HI / e)
    return AP_LO * math.exp(-BP_LO / e)


def depletion_width(n, v):
    """Width of a one-sided abrupt junction's depletion region at v volts
    (the built-in voltage is neglected)."""
    return math.sqrt(2 * EPS * v / (Q * n))


def integral_abrupt(n, v, steps=4000):
    """Electron ionisation integral of a one-sided abrupt junction of
    doping n at v volts. The field is a triangle: zero at the P-side edge
    of the depletion region (x = 0), largest at the junction (x = W)."""
    w = depletion_width(n, v)
    h = w / steps
    total, inner = 0.0, 0.0     # inner = integral of (alpha_n - alpha_p)
    prev_d, prev_f = 0.0, 0.0
    for k in range(1, steps + 1):
        e = Q * n * (k * h) / EPS
        an, ap = alpha_n(e), alpha_p(e)
        d = an - ap
        inner += 0.5 * (d + prev_d) * h
        f = an * math.exp(-inner)
        total += 0.5 * (f + prev_f) * h
        prev_d, prev_f = d, f
    return total


def breakdown_abrupt(n):
    """Voltage at which integral_abrupt reaches 1, by bisection."""
    lo, hi = 1.0, 5000.0
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if integral_abrupt(n, mid) < 1.0:
            lo = mid
        else:
            hi = mid
    return hi


def c_junction(c0, vbi, m, v):
    """Capacitance of a junction model at reverse voltage v."""
    return c0 / (1 + v / vbi) ** m


def phi_f(n):
    return KT * math.log(n / NI)


def field_threshold(n, cox, vr, vfb):
    """Plate voltage, measured to the substrate, at which the surface under
    the plate inverts while the inversion layer is held at vr by the well."""
    psi = 2 * phi_f(n) + vr
    return vfb + psi + math.sqrt(2 * EPS * Q * n * psi) / cox


def octagon(half, corner):
    """(area um^2, perimeter um) of a well outline as the layout draws it."""
    c = min(0.586 * corner, half * 0.999)
    side = 2 * half
    return side * side - 2 * c * c, 4 * (side - 2 * c) + 4 * c * math.sqrt(2)
