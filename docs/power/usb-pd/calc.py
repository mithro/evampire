"""Recompute every number used in the calculations on usb-pd.rst.

Run with:  uv run python docs/power/usb-pd/calc.py

All inputs are spec or datasheet values (see the comments) or are marked
as ESTIMATE / ASSUMPTION.

SPDX-License-Identifier: Apache-2.0
"""
import math
import zlib

print("== Rp/Rd divider, nominal values (Type-C Tables 4-27, 4-28) ==")
RD = 5.1e3
for name, vsrc, rp in (("Default", 5.0, 56e3), ("1.5 A", 5.0, 22e3), ("3.0 A", 5.0, 10e3),
                        ("Default", 3.3, 36e3), ("1.5 A", 3.3, 12e3), ("3.0 A", 3.3, 4.7e3)):
    print(f"  {name:8s} {vsrc} V via {rp/1e3:g}k: {vsrc*RD/(rp+RD):.3f} V  (Rp+Rd={(rp+RD)/1e3:.1f}k)")
for name, ip in (("Default", 80e-6), ("1.5 A", 180e-6), ("3.0 A", 330e-6)):
    print(f"  {name:8s} {ip*1e6:g} uA: {ip*RD:.3f} V")

print("== Unit interval (PD Table 5.9) ==")
for f in (270e3, 300e3, 330e3):
    print(f"  {f/1e3:g} kbit/s: UI = {1/f*1e6:.3f} us, half UI = {0.5/f*1e6:.3f} us")
UI_MIN = 1 / 330e3

print("== Transmit edge: RC model (ASSUMPTION: single-pole RC edge) ==")
t1090 = 300e-9  # PD Table 5.10 tRise/tFall minimum
tau = t1090 / math.log(9)
print(f"  ln 9 = {math.log(9):.3f}; tau = {tau*1e9:.1f} ns")
vs, vlim = 1.125, 1.04  # PD Table 5.10 vSwing nom, Table 5.7 Y8Tx
frac = vs / (vs - vlim)
print(f"  1.125/(1.125-1.04) = {frac:.2f}; ln = {math.log(frac):.3f}; t = {math.log(frac)*tau*1e9:.0f} ns")
print(f"  0.25 UI at 330k = {0.25*UI_MIN*1e9:.0f} ns; 0.015 UI at 300k = {0.015/300e3*1e9:.0f} ns")
print(f"  0.07 UI at 330k = {0.07*UI_MIN*1e9:.0f} ns")
# slowest RC edge that still meets the 0.25 UI point
tau_max = 0.25 * UI_MIN / math.log(frac)
print(f"  largest tau meeting 0.25 UI: {tau_max*1e9:.0f} ns -> 10-90 = {tau_max*math.log(9)*1e9:.0f} ns")

print("== Packet lengths (PD Section 5.3.1.1) ==")
def bits(n):
    return 64 + 20 + 20 + 40 * n + 40 + 5
for n in (0, 1, 7):
    b = bits(n)
    print(f"  {n} data objects: {b} bits, {b/300e3*1e6:.0f} us at 300k, {b/270e3*1e6:.0f} us at 270k")

print("== CRC check against PD Figure 5.1 example ==")
print(f"  crc32(41 02) = {zlib.crc32(bytes([0x41, 0x02])):08X} (spec: 46B50D97)")

print("== PDO/RDO examples (PD Tables 6.10, 6.19) ==")
print(f"  9 V 3 A fixed PDO: voltage field {9/0.05:.0f}, current field {3/0.01:.0f}, "
      f"word {(int(9/0.05) << 10) | int(round(3/0.01)):08X}")
print(f"  RDO pos 2, 2 A: {(2 << 28) | (200 << 10) | 200:08X}")

print("== Source power budget example (ASSUMPTION: illustrative numbers) ==")
p_in, p_board, eff = 25.0, 5.0, 0.90
p_out = (p_in - p_board) * eff
print(f"  P_out = ({p_in} - {p_board}) x {eff} = {p_out:.1f} W")
print(f"  5 V max current = {p_out/5:.2f} A -> capped at 3 A; 9 V = {p_out/9:.3f} A -> {math.floor(p_out/9*100)/100:.2f} A")

print("== VCONN inrush (Type-C Tables 4-5, 4-6, 4-32) ==")
c, v, t = 10e-6, 3.0, 2e-3
print(f"  I = C*V/t = {c*1e6:g} uF x {v} V / {t*1e3:g} ms = {c*v/t*1e3:.0f} mA")
print(f"  100 mW at 5 V = {0.1/5*1e3:.0f} mA; 100 mW at 3 V = {0.1/3*1e3:.1f} mA")

print("== Software receive cost (ESTIMATES) ==")
T_POLL = 250e-9  # chosen sampling period
polls_per_bit = UI_MIN / T_POLL
print(f"  polls per bit at 330k = {polls_per_bit:.1f} -> use 12")
I_POLL, I_EDGE, I_BIT, I_SYM = 3, 10, 4, 16  # ESTIMATED instruction counts
per_bit_poll = 12 * I_POLL + 2 * I_EDGE + I_BIT + I_SYM / 5
per_bit_cap = 2 * (I_EDGE + 2) + I_BIT + I_SYM / 5
for name, ipb in (("polling", per_bit_poll), ("capture FIFO", per_bit_cap)):
    mips = ipb * 330e3 / 1e6
    print(f"  {name}: {ipb:.1f} instr/bit -> {mips:.1f} M instr/s; "
          f"CPI 1.3 -> {mips*1.3:.0f} MHz; CPI 4 -> {mips*4:.0f} MHz")
# PicoRV32 cycles per poll iteration: lw 5 + taken branch 5 (README CPI table)
print(f"  multi-cycle poll iteration 10 cycles at 4 MS/s -> {10*4:.0f} MHz for polling alone")
print(f"  pipelined poll iteration 4 cycles at 4 MS/s -> {4*4:.0f} MHz for polling alone")

print("== Interrupt per edge (ESTIMATE) ==")
edges = 2 * 330e3
for cyc in (40, 60):
    print(f"  {cyc} cycles/edge x {edges/1e3:.0f}k edges/s = {cyc*edges/1e6:.1f} M cycles/s")

print("== Transmit edge placement ==")
for f in (31.25e6, 50e6, 62.5e6):
    for cyc, name in ((4, "pipelined wait loop"), (12, "multi-cycle wait loop")):
        print(f"  {f/1e6:g} MHz, {name} {cyc} cycles: jitter {cyc/f*1e9:.0f} ns pk-pk")

print("== Capture FIFO depth vs latency ==")
for n in (8, 16, 32):
    print(f"  {n} entries x {0.5*UI_MIN*1e6:.3f} us = {n*0.5*UI_MIN*1e6:.1f} us")

print("== CPU blocked time per received message (worst case) ==")
t_msg = bits(7) / 270e3
t_gap = 195e-6
t_gc = bits(0) / 270e3
print(f"  {t_msg*1e6:.0f} + {t_gap*1e6:.0f} + {t_gc*1e6:.0f} = {(t_msg+t_gap+t_gc)*1e6:.0f} us")

print("== Ethernet frame arrivals during that time (ASSUMPTION: 1 Mbit/s of frames to the CPU) ==")
frame_bits = 1522 * 8
print(f"  1522-byte frame at 1 Mbit/s every {frame_bits/1e6*1e3:.1f} ms")

print("== ESD events versus a VBUS short ==")
# Renesas TB505: HBM 100 pF / 1.5 kOhm, IEC 61000-4-2 150 pF / 330 Ohm.
for name, c, r, v in (("HBM 2 kV (gf180mcu I/O target)", 100e-12, 1.5e3, 2e3),
                      ("IEC 61000-4-2 8 kV contact", 150e-12, 330.0, 8e3)):
    q = c * v
    e = 0.5 * c * v * v
    print(f"  {name}: Q = {q*1e9:.0f} nC, E = {e*1e3:.2f} mJ, tau = {r*c*1e9:.1f} ns, "
          f"V/R = {v/r:.2f} A")
# ASSUMPTION: short lasts 1 s, source keeps supplying 3 A, clamp holds 6 V.
i_s, t_s, v_cl = 3.0, 1.0, 6.0
print(f"  VBUS short: Q = {i_s*t_s:.0f} C, E in clamp = {v_cl*i_s*t_s:.0f} J, "
      f"P = {v_cl*i_s:.0f} W; charge ratio to HBM = {i_s*t_s/200e-9:.1e}")

print("== High-resistance poly divider (PDK 3 kOhm/sq option) ==")
for r in (1e6, 2e6):
    print(f"  {r/1e6:g} MOhm / 3 kOhm per square = {r/3e3:.0f} squares; "
          f"current at 21 V = {21/r*1e6:.1f} uA, at 50.9 V = {50.9/r*1e6:.1f} uA")

print("== Standard cell register overhead (gf180mcu 7-track, TT 5 V 25 C) ==")
clkq, setup = 0.6763, 0.2290
print(f"  clk-to-Q {clkq} ns + setup {setup} ns = {clkq+setup:.3f} ns")
for f in (31.25e6, 50e6, 62.5e6):
    print(f"  {f/1e6:g} MHz period {1/f*1e9:.1f} ns -> {1/f*1e9-(clkq+setup):.1f} ns left for logic")
