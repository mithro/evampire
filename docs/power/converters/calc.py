# /// script
# requires-python = ">=3.10"
# ///
"""Recompute every number on the "Voltage converters" page.

Run with:  uv run docs/power/converters/calc.py

Each section prints the inputs and the results that the page quotes, in
the order they appear on the page. Inputs marked "illustration" are example
values chosen for a worked example, not evampire design values.

SPDX-License-Identifier: Apache-2.0
"""

import math


def section(title):
    print()
    print("=" * len(title))
    print(title)
    print("=" * len(title))


def show(name, value, unit="", fmt=".4g"):
    print(f"  {name:<48} {value:{fmt}} {unit}")


# ---------------------------------------------------------------------------
section("1. Linear regulator compared with a switching converter")
# Powered-device input range 37 V to 57 V (see the PoE page); USB outputs
# 5 V and 20 V at 3 A.
for vin in (37.0, 57.0):
    for vout in (5.0, 20.0):
        iout = 3.0
        pout = vout * iout
        pin_lin = vin * iout          # a linear regulator passes the load current
        eta_lin = vout / vin
        loss_lin = (vin - vout) * iout
        print(f"  Vin={vin:4.0f} V Vout={vout:4.0f} V Iout={iout} A: "
              f"Pout={pout:.0f} W, Pin(linear)={pin_lin:.0f} W, "
              f"eta(linear)={eta_lin*100:.1f} %, loss={loss_lin:.0f} W")
# Switching converter loss for the same 60 W output at illustrative efficiencies.
for eta in (0.90, 0.96):
    pout = 60.0
    show(f"switching loss, Pout=60 W, eta={eta}", pout * (1 / eta - 1), "W", ".3g")
    show(f"switching input power, Pout=60 W, eta={eta}", pout / eta, "W", ".3g")

# ---------------------------------------------------------------------------
section("2. Buck converter worked example (illustration)")
vin, vout, fsw, L, pout = 48.0, 12.0, 250e3, 47e-6, 25.5
D = vout / vin
T = 1 / fsw
iout = pout / vout
di = (vin - vout) * D * T / L
show("duty cycle D = Vout/Vin", D)
show("period T", T * 1e6, "us")
show("on time D*T", D * T * 1e6, "us")
show("output current Iout = Pout/Vout", iout, "A")
show("ripple dI = (Vin-Vout) D T / L", di, "A")
show("ripple ratio dI/Iout", di / iout)
show("peak inductor current Iout + dI/2", iout + di / 2, "A")
show("valley inductor current Iout - dI/2", iout - di / 2, "A")
show("DCM boundary current dI/2", di / 2, "A")
for v in (37.0, 57.0):
    show(f"duty cycle at Vin={v:.0f} V", vout / v)
# Volt-second balance check: on-time and off-time volt-seconds equal.
show("on-time volt-seconds (Vin-Vout) D T", (vin - vout) * D * T * 1e6, "V.us")
show("off-time volt-seconds Vout (1-D) T", vout * (1 - D) * T * 1e6, "V.us")
# Output voltage ripple from the inductor ripple into an ideal capacitor.
C = 22e-6
show("output ripple dV = dI / (8 fsw C), C = 22 uF", di / (8 * fsw * C) * 1e3, "mV")
# Loss in the freewheel path: diode compared with a synchronous switch.
vf, r_on = 0.5, 0.020
show("diode loss Vf Iout (1-D), Vf = 0.5 V", vf * iout * (1 - D), "W", ".3g")
show("synchronous switch loss R Iout^2 (1-D), R = 20 mohm",
     r_on * iout**2 * (1 - D), "W", ".3g")
# Switching and gate-drive losses (illustration values).
t_rf = 40e-9         # sum of rise and fall times
show("switching loss 0.5 Vin Iout (tr+tf) fsw, tr+tf = 40 ns",
     0.5 * vin * iout * t_rf * fsw, "W", ".3g")
show("gate drive loss Qg Vg fsw, 10 nC, 5 V", 10e-9 * 5.0 * fsw * 1e3, "mW", ".3g")
# Inductance needed for the same ripple at other switching frequencies.
for f in (100e3, 250e3, 600e3, 2.2e6):
    print(f"    L for dI=0.766 A at {f / 1e3:6.0f} kHz: "
          f"{(48.0 - 12.0) * 0.25 / (0.766 * f) * 1e6:6.1f} uH")

# ---------------------------------------------------------------------------
section("3. Boost converter worked example (illustration)")
vin, vout, fsw, L, pout = 20.0, 54.0, 250e3, 100e-6, 30.0
D = 1 - vin / vout
iin = pout / vin
di = vin * D / (L * fsw)
show("duty cycle D = 1 - Vin/Vout", D)
show("input (inductor) current Iin = Pout/Vin (lossless)", iin, "A")
show("output current Iout = Pout/Vout", pout / vout, "A")
show("ripple dI = Vin D / (L fsw)", di, "A")
show("ripple ratio dI/Iin", di / iin)
show("peak inductor current", iin + di / 2, "A")
R = vout**2 / pout
f_rhp = (1 - D) ** 2 * R / (2 * math.pi * L)
show("load resistance R = Vout^2/Pout", R, "ohm")
show("right-half-plane zero (1-D)^2 R / (2 pi L)", f_rhp / 1e3, "kHz")
show("one fifth of the RHP zero", f_rhp / 5 / 1e3, "kHz")
print("  duty cycle needed to reach 54 V from each USB fixed voltage:")
for v in (5.0, 9.0, 15.0, 20.0, 28.0, 36.0, 48.0):
    print(f"    Vin={v:4.0f} V: D={1 - v / 54.0:.3f}, gain 1/(1-D)={54.0 / v:.2f}")

# ---------------------------------------------------------------------------
section("4. Buck-boost converters")
# Inverting buck-boost: switch must block Vin + |Vout|.
vin_max, vout_inv = 57.0, 48.0
show("inverting buck-boost switch stress Vin+|Vout|", vin_max + vout_inv, "V")
D_inv = vout_inv / (vin_max + vout_inv)
show("inverting duty for |Vout|=48 V at Vin=57 V", D_inv)
# Four-switch buck-boost: conversion ratio M = Vout/Vin for PoE in to USB out.
for vin in (37.0, 57.0):
    for vout in (5.0, 20.0, 48.0):
        M = vout / vin
        if M <= 1:
            print(f"  Vin={vin:.0f} V -> Vout={vout:.0f} V: M={M:.3f}, buck mode, D_buck={M:.3f}")
        else:
            print(f"  Vin={vin:.0f} V -> Vout={vout:.0f} V: M={M:.3f}, boost mode, D_boost={1 - 1 / M:.3f}")

# ---------------------------------------------------------------------------
section("5. Flyback converter worked example (illustration)")
n = 4.0            # turns ratio Np/Ns, illustration
vout = 12.0
for vin in (37.0, 57.0):
    k = vout * n / vin            # D/(1-D)
    Dfb = k / (1 + k)
    show(f"duty at Vin={vin:.0f} V (Vout=12 V, Np/Ns=4)", Dfb)
show("reflected output voltage n*Vout", n * vout, "V")
show("switch stress Vin_max + n*Vout (no leakage spike)", 57.0 + n * vout, "V")

# ---------------------------------------------------------------------------
section("6. Converter operating ranges")
# Power over Ethernet: power at the powered device, lowest voltage at the
# powered device, PSE output power and lowest PSE voltage per type
# (PoE page and power index page).
poe = {
    1: dict(p_pd=13.0, v_pd=37.0, p_pse=15.4, v_pse=44.0),
    2: dict(p_pd=25.5, v_pd=42.5, p_pse=30.0, v_pse=50.0),
    3: dict(p_pd=51.0, v_pd=42.5, p_pse=60.0, v_pse=50.0),
    4: dict(p_pd=71.3, v_pd=41.2, p_pse=90.0, v_pse=52.0),
}
for t, d in poe.items():
    print(f"  Type {t}: input converter max input current "
          f"{d['p_pd']}/{d['v_pd']} = {d['p_pd'] / d['v_pd']:.3f} A; "
          f"high-voltage converter max output current "
          f"{d['p_pse']}/{d['v_pse']} = {d['p_pse'] / d['v_pse']:.3f} A")
# USB source: output current at each power level.
for v, i in ((5, 3), (9, 3), (15, 3), (20, 3), (20, 5), (28, 5), (36, 5), (48, 5)):
    print(f"  USB {v:2d} V at {i} A: {v * i:5.0f} W")
show("SPR worst-case VBUS 20 V * 1.05 + 0.5 V", 20 * 1.05 + 0.5, "V")
show("EPR worst-case VBUS 48 V * 1.05 + 0.5 V", 48 * 1.05 + 0.5, "V")
show("EPR 48 V fixed supply lower tolerance 48 * 0.95", 48 * 0.95, "V")
show("EPR 48 V fixed supply upper tolerance 48 * 1.05", 48 * 1.05, "V")

# ---------------------------------------------------------------------------
section("7. Arrangement options: efficiency of chained stages (illustration)")
# One stage between eta_lo and eta_hi; values are illustrations taken from
# commercial data sheets, not evampire values.
eta_lo, eta_hi = 0.90, 0.97
for stages in (1, 2):
    show(f"{stages} stage(s): eta range low", eta_lo**stages, "", ".3f")
    show(f"{stages} stage(s): eta range high", eta_hi**stages, "", ".3f")
# Power available to outputs, P_out = P_in * eta - P_board, Type 4 input.
p_in = 71.3
for stages in (1, 2):
    for eta1 in (eta_lo, eta_hi):
        eta = eta1**stages
        print(f"  P_in={p_in} W, {stages} stage(s), eta={eta:.3f}: "
              f"P_out = {p_in * eta:.1f} W - P_board")
# Pass-through switch loss: I^2 R for a Type 4 current through an
# illustrative 0.1 ohm switch.
i4 = 90.0 / 52.0
show("pass-through loss, 1.731 A through 0.1 ohm", i4**2 * 0.1, "W", ".3g")
show("pass-through efficiency at 90 W", 1 - i4**2 * 0.1 / 90.0, "", ".4f")
# Pass-through from a PoE input to a PoE output: lowest input voltage that
# still meets each type's lowest PSE output voltage, for an illustrative
# 0.2 V drop in the switches.
for t, d in poe.items():
    print(f"  Type {t} output by pass-through needs input >= "
          f"{d['v_pse'] + 0.2:.1f} V (lowest PD input of that type {d['v_pd']} V)")
# A linear regulator between an Ethernet input and an Ethernet output.
for vi, vo in ((57.0, 52.0), (54.0, 52.0), (57.0, 44.0)):
    print(f"  linear {vi:.0f} V -> {vo:.0f} V at 1.731 A: eta {vo / vi:.3f}, "
          f"loss {(vi - vo) * i4:.2f} W")
# Switched-capacitor ladder: ideal ratio efficiency when the ratio is not exact.
for vi in (37.0, 48.0, 57.0):
    vo_ideal = vi / 4
    print(f"  4:1 switched capacitor from {vi:.0f} V: unloaded output {vo_ideal:.2f} V; "
          f"linear-like efficiency at 9 V out {9.0 / vo_ideal:.3f}" if vo_ideal >= 9
          else f"  4:1 switched capacitor from {vi:.0f} V: unloaded output {vo_ideal:.2f} V")

# ---------------------------------------------------------------------------
section("8. PWM resolution")
f_clk = 125e6
for fsw in (100e3, 250e3, 600e3, 2.2e6):
    steps = f_clk / fsw
    print(f"  fsw={fsw / 1e3:6.0f} kHz: counter steps {steps:7.1f}, "
          f"bits {math.log2(steps):5.2f}, duty step {1 / steps:.2e}, "
          f"buck output step at 57 V {57.0 / steps * 1e3:6.1f} mV")
# Duty step needed for a 20 mV change at the largest input voltage (buck).
dD = 0.020 / 57.0
show("duty step for 20 mV at Vin = 57 V", dD, "", ".3e")
show("bits for that duty step", math.log2(1 / dD), "bits", ".3g")
show("counter clock for that step at 250 kHz", 250e3 / dD / 1e6, "MHz", ".4g")
show("time step for that duty step at 250 kHz", dD / 250e3 * 1e12, "ps", ".4g")
for taps in (4, 8, 16, 32):
    step = 1 / f_clk / taps
    print(f"  125 MHz counter + {taps:2d}-tap delay line: step {step * 1e12:6.0f} ps, "
          f"steps per 250 kHz period {(1 / 250e3) / step:7.0f}")
# 100 mV steps (AVS) at 48 V output, through a feedback divider: DAC bits.
show("DAC bits for 20 mV in 21 V", math.log2(21.0 / 0.020), "bits", ".3g")
show("DAC bits for 100 mV in 48 V", math.log2(48.0 / 0.100), "bits", ".3g")

# ---------------------------------------------------------------------------
section("9. Software control: instruction budget per update")
for f_cpu in (25e6, 62.5e6, 125e6):
    for cpi in (1.0, 4.0):
        for f_upd in (250e3, 40e3, 4e3):
            n_instr = f_cpu / (cpi * f_upd)
            print(f"  f_cpu={f_cpu / 1e6:5.1f} MHz CPI={cpi:.0f} "
                  f"f_update={f_upd / 1e3:5.0f} kHz: {n_instr:7.1f} instructions")
show("crossover 1/10 of 250 kHz", 250e3 / 10 / 1e3, "kHz")
show("update rate 10x a 4 kHz crossover", 40.0, "kHz")

# ---------------------------------------------------------------------------
section("10. Fault response: current rise during the response time")
for vin, L, name in ((57.0, 47e-6, "buck, 57 V across 47 uH"),
                     (20.0, 100e-6, "boost switch on, 20 V across 100 uH")):
    slope = vin / L
    show(f"{name}: dI/dt", slope / 1e6, "A/us")
    for t in (100e-9, 1e-6, 4e-6, 10e-6, 100e-6):
        print(f"    rise in {t * 1e6:7.1f} us: {slope * t:8.3f} A")

# ---------------------------------------------------------------------------
section("11. Monitoring resolution")
for i_fs, i_lsb in ((90.0 / 52.0, 1e-3), (90.0 / 52.0, 5e-3), (5.0, 10e-3)):
    print(f"  full scale {i_fs:.3f} A, step {i_lsb * 1e3:.0f} mA: "
          f"{math.log2(i_fs / i_lsb):.2f} bits")

# ---------------------------------------------------------------------------
section("12. Start-up supply")
# Hold-up capacitor: C >= I * t / dV. Illustration with TPS23753A values.
i_ctrl = 0.58e-3       # TPS23753A VC operating current, typical
qg = 10e-9             # illustrative gate charge
fsw = 248e3            # TPS23753A typical with RFRS = 60.4 kohm
i_gate = qg * fsw
i_tot = i_ctrl + i_gate
t_ss = 0.8e-3          # TPS23753A soft-start period, upper typical
dv = 3.5               # TPS23753A VC UVLO hysteresis, typical
show("gate drive current Qg fsw", i_gate * 1e3, "mA")
show("total start-up load current", i_tot * 1e3, "mA")
show("hold-up capacitor C >= I t / dV", i_tot * t_ss / dv * 1e6, "uF", ".3g")
show("start-up current source power at 57 V, 4.3 mA", 57.0 * 4.3e-3 * 1e3, "mW", ".3g")
# Start-up resistor sized for 1 mA at 37 V into a 9 V capacitor.
r_st = (37.0 - 9.0) / 1e-3
show("start-up resistor for 1 mA at 37 V", r_st / 1e3, "kohm", ".3g")
show("its continuous loss at 57 V", (57.0 - 9.0) ** 2 / r_st * 1e3, "mW", ".3g")
show("charging time of 22 uF to 9 V at 4.3 mA", 22e-6 * 9.0 / 4.3e-3 * 1e3, "ms", ".3g")
# USB start: power at the lowest vSafe5V voltage for each advertised current.
for name, i in (("default, USB 2.0", 0.5), ("default, USB 3.2", 0.9),
                ("1.5 A", 1.5), ("3.0 A", 3.0)):
    print(f"  USB {name}: 4.75 V x {i} A = {4.75 * i:.3f} W")
# Power at the powered device per class before any LLDP change (classes 1-8).
for c, p in ((1, 3.84), (2, 6.49), (3, 13.0), (4, 25.5), (5, 40.0), (6, 51.0),
             (7, 62.0), (8, 71.3)):
    print(f"  class {c}: {p} W at the powered device")

# ---------------------------------------------------------------------------
section("13. Gate drivers")
# Drive current needed to move a gate charge in a given time.
for qg, t in ((10e-9, 20e-9), (20e-9, 20e-9), (40e-9, 20e-9)):
    print(f"  Qg={qg * 1e9:.0f} nC in {t * 1e9:.0f} ns: {qg / t:.2f} A")
# Width of 6 V NMOS needed for 1 A, from the documented saturation current.
idsat_6v = 570e-6      # A/um, typical, Vgs = Vds = 6 V
show("6 V NMOS width for 1 A at Idsat 570 uA/um", 1.0 / idsat_6v, "um", ".4g")
show("6 V NMOS width for 1 A at Idsat 480 uA/um (min)", 1.0 / 480e-6, "um", ".4g")
cox_6v = 2.3e-15       # F/um^2, typical
show("gate capacitance of that width at L=0.7 um", 1.0 / idsat_6v * 0.7 * cox_6v * 1e12, "pF", ".3g")
# Bootstrap capacitor: C >= Qtotal / dV.
for qg in (10e-9, 40e-9):
    q = qg + 1e-9      # plus an illustrative 1 nC of driver and leakage charge
    print(f"  bootstrap C for Qg={qg * 1e9:.0f} nC (+1 nC), 0.5 V droop: "
          f"{q / 0.5 * 1e9:.0f} nF; ten times Qg rule: {10 * qg / 5.0 * 1e9:.0f} nF at 5 V")
# Level shifter stress: switch node up to 57 V plus gate drive of 5 V.
show("high-side supply top, 57 V + 5 V", 62.0, "V")
show("n-well to substrate breakdown minimum", 10.0, "V")
show("documented junction margin factor 62 / 10", 62.0 / 10.0, "", ".3g")

# ---------------------------------------------------------------------------
section("14. Power transistors")
idlin = 26.8e-6        # A/um, LDNMOS Idlin typ at Vgs=6 V, Vds=0.1 V
r_w = 0.1 / idlin      # ohm.um
show("LDNMOS on-resistance x width 0.1 V / Idlin", r_w, "ohm.um", ".4g")
show("LDNMOS on-resistance x width, in ohm.mm", r_w / 1e3, "ohm.mm", ".4g")
for R in (0.5, 0.1, 0.05):
    print(f"  single LDNMOS for {R * 1e3:.0f} mohm: W = {r_w / R / 1e3:.1f} mm")
# Stack of n devices: each must be n times wider, total width n^2.
for n_stack in (1, 6, 8):
    R = 0.1
    w_each = n_stack * r_w / R
    print(f"  {n_stack} in series for 100 mohm: each {w_each / 1e3:.0f} mm, "
          f"total {n_stack * w_each / 1e3:.0f} mm of gate width")
show("devices in series for 57 V at 10 V each", math.ceil(57.0 / 10.0), "", ".0f")
# Area with an assumed layout pitch p (um of layout per um of width).
for p in (2.0, 5.0):
    w = 3.73e3 / 0.1   # um, single 100 mohm device
    print(f"  single 100 mohm LDNMOS, assumed pitch {p} um: area "
          f"{w * p / 1e6:.2f} mm^2")
# Metal width for the largest PoE current at the EM limits (85 C).
i_max = 90.0 / 52.0
show("Type 4 PSE current", i_max, "A")
show("Metal 1..top-1 width at 2.09 mA/um", i_max / 2.09e-3, "um", ".4g")
show("30 kA top metal width at 16.52 mA/um", i_max / 16.52e-3, "um", ".4g")
show("contacts or vias at 0.58 mA each", math.ceil(i_max / 0.58e-3), "", ".0f")
# USB 5 A at the EM limit.
show("30 kA top metal width for 5 A", 5.0 / 16.52e-3, "um", ".4g")
show("contacts for 5 A", math.ceil(5.0 / 0.58e-3), "", ".0f")
# Conduction loss and power density.
show("conduction loss 1.731 A in 100 mohm", i_max**2 * 0.1, "W", ".3g")
show("conduction loss 5 A in 20 mohm", 25 * 0.02, "W", ".3g")
