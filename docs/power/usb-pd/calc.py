"""Recompute every number used in the calculations on the USB PD pages.

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

# ---------------------------------------------------------------------------
# software.rst: what USB PD needs from the processor.
# No processor clock or CPI is assumed. Needs are instruction rates
# (instructions per second), instructions per bit, times in ns or us.
# Instruction counts are ESTIMATES for hand-written RV32I assembly.
# Numbers labelled REFERENCE are for reference examples only.
# ---------------------------------------------------------------------------
F_BIT_RX = 330e3            # fastest bit rate a receiver must accept (PD Table 5.9)
F_BIT_TX = 300e3            # transmit at the nominal rate (PD Table 5.9)
T_UI_RX = 1 / F_BIT_RX
T_UI_TX = 1 / F_BIT_TX
F_EDGE_RX = 2 * F_BIT_RX    # worst case: every bit a 1, two edges per bit
F_EDGE_TX = 2 * F_BIT_TX
X_RX = 0.07                 # X1Rx, receive edge displacement (PD Table 5.8)
X_TX = 0.015                # X1Tx, left edge of transmit mask (PD Table 5.6)

# ESTIMATED instruction counts
K_POLL = 2      # poll loop: load input word, compare-and-branch
N_EDGE = 10     # per edge: read counter, subtract, compare with 0.75 UI, update
N_BIT = 4 + 16 / 5   # per bit: shift and count (4) + 4b5b and CRC per symbol (16/5)
N_IRQ = 30      # interrupt entry and exit, save and restore registers
N_TS = 12       # per edge from input capture: read FIFO entry and classify
N_OUT = 4       # per transmitted edge: next time, write output (bit-banged)
N_OC = 6        # per transmitted edge with output compare
K_WAIT = 3      # wait loop on the counter: read counter, compare, branch
K_MERGED = 4    # merged loop: load input, branch, read counter, branch
N_REPLY = 30    # end of message to start of GoodCRC, prepared packets

print("== Software: receive sampling period ==")
ts_max = (0.25 - 2 * X_RX) * T_UI_RX
print(f"  T_UI,min = {T_UI_RX*1e6:.3f} us; margin {0.25-2*X_RX:.2f} UI; "
      f"T_s,max = {ts_max*1e9:.0f} ns; f_s,min = {1/ts_max/1e6:.1f} MS/s")
print(f"  bit work per bit N_bit = {N_BIT:.1f}")

print("== Software: polled receive ==")
poll = K_POLL / ts_max
edge = F_EDGE_RX * N_EDGE
bitw = F_BIT_RX * N_BIT
r_poll = poll + edge + bitw
print(f"  k/T_s = {poll/1e6:.2f}; f_edge*N_edge = {edge/1e6:.2f}; "
      f"f_bit*N_bit = {bitw/1e6:.2f}; R_poll = {r_poll/1e6:.1f} M instr/s; "
      f"{r_poll/F_BIT_RX:.1f} instr/bit")
print(f"  REFERENCE PicoRV32 poll iteration lw 5 + taken branch 5 = 10 cycles in "
      f"{ts_max*1e9:.0f} ns -> clock >= {10/ts_max/1e6:.0f} MHz")

print("== Software: interrupt per edge ==")
r_irq = F_EDGE_RX * (N_IRQ + N_EDGE) + bitw
print(f"  N_irq {N_IRQ}: R_irq = {r_irq/1e6:.1f} M instr/s; {r_irq/F_BIT_RX:.1f} instr/bit")
be = K_POLL / (ts_max * F_EDGE_RX)
print(f"  break-even N_irq = k/(T_s f_edge) = {be:.1f} instructions")
print(f"  REFERENCE in cycles, 10-cycle poll iteration: {10/(ts_max*F_EDGE_RX):.0f} cycles")

print("== Software: input capture ==")
r_cap = F_EDGE_RX * N_TS + bitw
print(f"  R_cap = {r_cap/1e6:.1f} M instr/s; {r_cap/F_BIT_RX:.1f} instr/bit")
for d in (8, 16, 32):
    print(f"  FIFO {d} entries x {0.5*T_UI_RX*1e6:.3f} us = {d*0.5*T_UI_RX*1e6:.1f} us")
print(f"  REFERENCE Chromium EC 2.4 MHz capture timer: {1/2.4e6*1e9:.0f} ns per count")

print("== Software: transmit ==")
tgt = X_TX * T_UI_TX
print(f"  edge target {X_TX} UI at 300k = {tgt*1e9:.0f} ns (at 330k {X_TX*T_UI_RX*1e9:.0f} ns); "
      f"window {2*tgt*1e9:.0f} ns")
r_wait = K_WAIT / (2 * tgt)
print(f"  wait loop {K_WAIT} instr in {2*tgt*1e9:.0f} ns -> {r_wait/1e6:.0f} M instr/s; "
      f"{r_wait/F_BIT_TX:.0f} instr/bit")
bb = 2 * N_OUT + N_BIT
print(f"  cycle-exact: {bb:.1f} instr/bit -> {bb*F_BIT_TX/1e6:.2f} M instr/s")
oc = 2 * N_OC + N_BIT
print(f"  output compare: {oc:.1f} instr/bit -> {oc*F_BIT_TX/1e6:.2f} M instr/s; "
      f"reload within {0.5*T_UI_TX*1e6:.3f} us")
print(f"  shift register: {N_BIT:.1f} instr/bit -> {N_BIT*F_BIT_TX/1e6:.2f} M instr/s; "
      f"{bits(7)*N_BIT:.0f} instr per 7-object message")
print(f"  message of 7 objects at 300k: {bits(7)/F_BIT_TX*1e6:.0f} us")

print("== Software: GoodCRC deadline ==")
print(f"  N_reply {N_REPLY} in 195 us -> {N_REPLY/195e-6/1e6:.2f} M instr/s")
n_msg = 2 * bits(7) * N_TS + bits(7) * N_BIT
print(f"  decode after EOP: {n_msg:.0f} instr in 195 us -> {n_msg/195e-6/1e6:.0f} M instr/s")

print("== Software: busy time per received message (worst case, 270 kbit/s) ==")
t_msg = bits(7) / 270e3
t_tr = 195e-6               # tTransmit (PD Table 7.10)
t_gc = bits(0) / 270e3
t_busy = t_msg + t_tr + t_gc
print(f"  {t_msg*1e6:.0f} + {t_tr*1e6:.0f} + {t_gc*1e6:.0f} = {t_busy*1e6:.0f} us")

print("== Software: two ports ==")
r_two = poll + 2 * (edge + bitw)
print(f"  polled, two ports: {r_two/1e6:.1f} M instr/s; {r_two/F_BIT_RX:.1f} instr/bit")
r_m = (K_MERGED + N_EDGE) / (2 * tgt)
print(f"  merged loop ({K_MERGED}+{N_EDGE}) in {2*tgt*1e9:.0f} ns -> {r_m/1e6:.0f} M instr/s; "
      f"{r_m/F_BIT_RX:.0f} instr/bit")
print(f"  merged loop, edge work spread out: {K_MERGED} in {2*tgt*1e9:.0f} ns -> "
      f"{K_MERGED/(2*tgt)/1e6:.0f} M instr/s")

print("== Software: Ethernet frames during the busy time (requirement: below 1 Mbit/s) ==")
frame_bits = 1522 * 8
print(f"  1522-byte frame at 1 Mbit/s every {frame_bits/1e6*1e3:.1f} ms")
print(f"  1 Mbit/s x {t_busy*1e3:.3f} ms = {1e6*t_busy:.0f} bit = {1e6*t_busy/8:.0f} bytes")

print("== Software: CRC-32 table and reference examples ==")
print(f"  16-entry table of 32-bit words = {16*4} bytes")
print(f"  REFERENCE V-USB low speed 1.5 Mbit/s: {12/1.5:.0f} to {20/1.5:.1f} clock cycles per bit")

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
          f"current at 21.5 V = {21.5/r*1e6:.1f} uA, at 50.9 V = {50.9/r*1e6:.1f} uA")

print("== SPR and EPR worst-case VBUS (PD Table 4.7: vSrcNew max, vSrcValid max) ==")
for v in (20.0, 48.0):
    print(f"  {v:g} V x 1.05 + 0.5 V = {v*1.05+0.5:.2f} V")

print("== Dead-battery Rd path (analogue.rst; Type-C Tables 4-27, 4-37) ==")
# Range a source with a current-source Rp reads as Rd (Type-C Table 4-37,
# vCCCur-Rd connect thresholds), with the Rp current range of each level
# (Type-C Table 4-27: 80 uA +-20 %, 180 and 330 uA +-8 %).
LEVELS = (("default", 64e-6, 96e-6, 0.261, 1.32),
          ("1.5 A", 165.6e-6, 194.4e-6, 0.676, 1.32),
          ("3.0 A", 303.6e-6, 356.4e-6, 0.88, 2.181))
for name, ilo, ihi, vlo, vhi in LEVELS:
    print(f"  {name:8s} I_Rp {ilo*1e6:.1f} to {ihi*1e6:.1f} uA, "
          f"V_CC range {vlo} to {vhi} V")
R_STD = 2.0e3
for name, ilo, ihi, vlo, vhi in LEVELS:
    print(f"  standard, 2.0 kOhm, {name}: Vt 0.61 V at {ilo*1e6:.1f} uA -> "
          f"{ilo*R_STD+0.61:.3f} V; Vt 0.85 V at {ihi*1e6:.1f} uA -> "
          f"{ihi*R_STD+0.85:.3f} V")
r_lo = max(vlo / ilo for _, ilo, ihi, vlo, vhi in LEVELS)
r_hi = min((vhi - 0.08) / ihi for _, ilo, ihi, vlo, vhi in LEVELS)
print(f"  native, V_GS 0 to 0.08 V: R_s from {r_lo/1e3:.2f} to "
      f"{r_hi/1e3:.2f} kOhm")
margin = 1.32 - (194.4e-6 * R_STD + 0.85)
print(f"  margin at 1.5 A, standard example: {margin*1e3:.0f} mV; beta for "
      f"that overdrive = {2*194.4e-6/margin**2*1e3:.0f} mA/V^2 "
      f"(at 80 mV: {2*194.4e-6/0.08**2*1e3:.0f} mA/V^2)")
print(f"  source above the P-well at 356.4 uA: standard 2.0 kOhm "
      f"{356.4e-6*R_STD:.2f} V, native 5.9 kOhm {356.4e-6*5.9e3:.2f} V")

print("== Crowbar energy (cc-protection.rst; PD Table 4.7 cSrcBulk) ==")
for v, label in ((21.5, "at 21.5 V, first firing"),
                 (6.0, "at a 6 V trigger, retry by a source that restores "
                       "its old voltage")):
    print(f"  {label}: {0.5*10e-6*v*v*1e3:.2f} to {0.5*120e-6*v*v*1e3:.1f} mJ")

print("== VCONN ramp and load (Type-C Tables 4-5, 4-6) ==")
print(f"  ramp: 15 mA charging + iRaDetect 10 mA = {15+10} mA")
print(f"  75 mW at 3.0 V = {75/3:.0f} mA; 20 mW at 3.0 V = {20/3:.1f} mA")
