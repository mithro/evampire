"""Recompute every number used in the calculations on the USB serial port pages.

Run with:  uv run python docs/usb-serial/calc.py [path/to/gf180mcu_fd_io__bi_t__tt_025C_3v30.lib]

Inputs are USB 2.0 specification values, CDC values, gf180mcu PDK values
(each with its source in a comment), or are marked ESTIMATE or ASSUMPTION.

SPDX-License-Identifier: Apache-2.0
"""
import math
import pathlib
import re
import sys

FS = 12e6            # full-speed bit rate, USB 2.0 section 7.1.11
LS = 1.5e6           # low-speed bit rate
HS = 480e6           # high-speed bit rate
T = 1 / FS

print("== Bit times (USB 2.0 section 7.1.11, table 7-9 TFDRATE) ==")
for name, f in (("low", LS), ("full", FS), ("high", HS)):
    print(f"  {name:5s} {f/1e6:g} Mbit/s: {1/f*1e9:.3f} ns")
for f in (11.97e6, 12.03e6):
    print(f"  {f/1e6:.2f} Mbit/s: {1/f*1e9:.3f} ns")
print(f"  0.25 % of a bit time = {0.0025*T*1e12:.0f} ps")

print("== Inter-packet delay and turnaround (section 7.1.18.1, 7.1.19.1) ==")
for n in (2, 6.5, 7.5, 16, 18):
    print(f"  {n} bit times = {n*T*1e9:.1f} ns")

print("== EOP (section 7.1.13.2.1, table 7-9) ==")
for t in (160e-9, 175e-9, 82e-9):
    print(f"  {t*1e9:.0f} ns = {t/T:.2f} bit times")

print("== Packet lengths in bit times, including EOP (chapter 8) ==")
SYNC, PID, EOP = 8, 8, 3
token = SYNC + PID + 7 + 4 + 5
hand = SYNC + PID
print(f"  token: {token} bits + EOP = {token+EOP}; handshake: {hand} + EOP = {hand+EOP}")
def data_bits(n, stuff=True):
    b = SYNC + PID + 8 * n + 16
    s = (b - SYNC) // 6 if stuff else 0    # ASSUMPTION: worst case, all ones
    return b, s
for n in (0, 8, 64):
    b, s = data_bits(n)
    tot = b + s + EOP
    print(f"  DATA with {n} bytes: {b} bits + up to {s} stuffed + EOP = {tot} "
          f"= {tot*T*1e6:.2f} us")
b64, s64 = data_bits(64)
L64 = b64 + s64 + EOP

print("== Sampling margin (section 7.1.15.1, table 7-9 TJR1) ==")
half = T / 2
tjr1 = 18.5e-9
margin = half - tjr1
print(f"  half bit {half*1e9:.2f} ns - TJR1 {tjr1*1e9} ns = {margin*1e9:.1f} ns")
e_rel = 500e-6 + 2500e-6   # host +-0.05 %, full-speed-only device +-0.25 %
print(f"  drift over 7 bits at {e_rel*1e6:.0f} ppm: {7*T*e_rel*1e9:.2f} ns")
print(f"  drift over {L64} bits at {e_rel*1e6:.0f} ppm: {L64*T*e_rel*1e9:.0f} ns")
print(f"  largest relative error for no re-timing over {L64} bits: "
      f"{margin/(L64*T)*1e6:.0f} ppm")

print("== Software instruction estimates (ESTIMATE, hand-counted RV32I) ==")
RX_BIT = {"read input": 1, "NRZI decode": 2, "bit-stuff count": 3,
          "shift into byte": 1, "end-of-packet check": 1, "loop branch": 1}
RX_BYTE = {"store byte, advance pointer": 2, "CRC16 table update": 7, "byte count": 1}
TX_BIT = {"next bit": 2, "bit-stuff count": 3, "NRZI toggle": 1,
          "write output": 1, "loop branch": 1}
TX_BYTE = {"load byte, advance pointer": 2}
rx = sum(RX_BIT.values()) + sum(RX_BYTE.values()) / 8
tx = sum(TX_BIT.values()) + sum(TX_BYTE.values()) / 8
print(f"  receive: {sum(RX_BIT.values())} per bit + {sum(RX_BYTE.values())} per byte "
      f"= {rx:.2f} per bit")
print(f"  transmit: {sum(TX_BIT.values())} per bit + {sum(TX_BYTE.values())} per byte "
      f"= {tx:.2f} per bit")
for name, n in (("receive", rx), ("transmit", tx)):
    ips = n * FS
    print(f"  {name}: {ips/1e6:.0f} M instructions/s")
# Byte-level software with a hardware deserialiser.
BYTE_SW = {"read byte from FIFO": 1, "store, advance pointer": 2,
           "CRC16 table update": 7, "count, loop": 2}
BYTE_SW_HWCRC = {"read byte from FIFO": 1, "store, advance pointer": 2, "count, loop": 2}
for name, d in (("byte, software CRC", BYTE_SW), ("byte, hardware CRC", BYTE_SW_HWCRC)):
    n = sum(d.values())
    ips = n * FS / 8
    print(f"  {name}: {n} per byte -> {ips/1e6:.1f} M instr/s")
N_TA = 15   # ESTIMATE: check CRC residual, choose handshake, start transmitter
t_ta = 6.5 * T
print(f"  reply: {N_TA} instr in {t_ta*1e9:.1f} ns -> {N_TA/t_ta/1e6:.1f} M instr/s")
print(f"  transmit fill: 2 per byte -> {2*FS/8/1e6:.1f} M instr/s")

print("== Transmit edge placement (table 7-9 TDJ1) ==")
tdj1 = 3.5e-9
print(f"  clock period <= {tdj1*1e9} ns -> f >= {1/tdj1/1e6:.0f} MHz when not a multiple of 12 MHz")
for f in (125e6, 250e6):
    k = f / FS
    print(f"  {f/1e6:g} MHz: {k:.4f} cycles per bit; intervals {math.floor(k)} or "
          f"{math.ceil(k)} cycles = {math.floor(k)/f*1e9:.1f} or {math.ceil(k)/f*1e9:.1f} ns; "
          f"errors {(math.floor(k)/f-T)*1e9:+.2f} / {(math.ceil(k)/f-T)*1e9:+.2f} ns")

print("== Bus load of NAKed IN polls (worst case, chapter 8 and section 7.1.18) ==")
poll = (token + EOP) + 2 + (hand + EOP) + 2   # token, min turnaround, NAK, min host gap
print(f"  {poll} bit times = {poll*T*1e6:.2f} us -> at most {1e-3/(poll*T):.0f} per 1 ms frame")
busy = (token + EOP) + 6.5 + (hand + EOP)
print(f"  device busy per poll (token + 6.5 + NAK) = {busy} bits = {busy*T*1e6:.2f} us "
      f"= {busy/poll*100:.0f} % of the bus time")

print("== Low-speed interrupt limit (section 5.7.3, 5.7.4) ==")
print(f"  8 bytes every 10 ms = {8/10e-3:.0f} bytes/s")
print(f"  rx/tx rates at low speed are 1/8 of full speed: {rx*LS/1e6:.1f} / {tx*LS/1e6:.1f} M instr/s")

print("== Frame-interval clock tracking (section 7.1.12, table 7-9 TFRAME) ==")
for f in (12e6, 48e6, 125e6):
    n = f * 1e-3
    print(f"  {f/1e6:g} MHz: {n:.0f} counts per frame, 1 count = {1/n*1e6:.1f} ppm")
print(f"  frame tolerance 500 ns / 1 ms = {500e-9/1e-3*1e6:.0f} ppm")

print("== Pull-up and idle level (section 7.1.5.1, table 7-7) ==")
for vt, rpu, rpd in ((3.3, 1.5e3, 15e3), (3.0, 1.575e3, 14.25e3), (3.6, 1.425e3, 15.75e3)):
    v = vt * rpd / (rpu + rpd)
    print(f"  VTERM {vt} V, RPU {rpu:.0f}, RPD {rpd:.0f}: D+ idle = {v:.3f} V")
print(f"  pull-up current at 3.3 V into 15k: {3.3/(16.5e3)*1e3:.2f} mA; "
      f"pull-up power: {(3.3/16.5e3)**2*1.5e3*1e3:.3f} mW")

print("== Driver edge with resistive output only (section 7.1.1.1, 7.1.2.1) ==")
CL = 50e-12   # figure 7-9 test load
for z in (28, 44):
    tau = z * CL
    print(f"  ZDRV {z} ohm x 50 pF: tau = {tau*1e9:.2f} ns, 10-90 % = {tau*math.log(9)*1e9:.2f} ns")

print("== Short to VBUS (section 7.1.1; ASSUMPTIONS 3.3 V pad supply, 0.6 V diode) ==")
VBUS, VDD, VD = 5.25, 3.3, 0.6
print(f"  driver off, pad diode: VBUS - VDD - VD = {VBUS - VDD - VD:.2f} V across RS")
for r in (28, 44):
    print(f"    RS {r} ohm: I = {(VBUS - VDD - VD) / r * 1e3:.0f} mA")
print(f"  driving high, PMOS on: VBUS - VDD = {VBUS - VDD:.2f} V across ZDRV")
for z in (44, 28):
    print(f"    ZDRV {z} ohm: I_H = {(VBUS - VDD) / z * 1e3:.0f} mA")
print(f"  driving low, NMOS on: VBUS = {VBUS} V across ZDRV")
for z in (44, 28):
    print(f"    ZDRV {z} ohm: I_L = {VBUS / z * 1e3:.0f} mA, "
          f"dissipated in ZDRV {VBUS**2 / z:.2f} W")
k = (VBUS - VDD - VD) / VBUS
print(f"  driving low is the largest case while RS > {VBUS - VDD - VD:.2f} / {VBUS} "
      f"= {k:.2f} x ZDRV:")
for z in (28, 44):
    print(f"    ZDRV {z} ohm: RS > {k * z:.1f} ohm")

print("== gf180mcu_fd_io__bi_t output transitions at the largest tabulated load ==")
# Pass the path of gf180mcu_fd_io__bi_t__tt_025C_3v30.lib (from the
# globalfoundries-pdk-libs-gf180mcu_fd_io repository, cells/bi_t/) as the
# first argument to print this table.
LIB = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if LIB:
    t = LIB.read_text()
    pad = t[t.index('pin ("PAD")'):]
    for m in re.finditer(r'timing \(\) \{(.*?)\n\t\t\t\}', pad, re.S):
        blk = m.group(1)
        if 'related_pin : "A"' not in blk:
            continue
        when = re.search(r'when : "([^"]+)"', blk).group(1)
        res = {}
        for kind in ("rise_transition", "fall_transition"):
            body = re.search(kind + r' \("[^"]*"\) \{(.*?)\}', blk, re.S).group(1)
            load = re.search(r'index_2\("([^"]+)"\)', body).group(1).split(",")[-1]
            row = re.findall(r'"([^"]+)"', re.search(r'values\((.*?)\);', body, re.S).group(1))[0]
            res[kind] = float(row.split(",")[-1])
        print(f"  {when:28s} load {float(load):.1f} pF: rise {res['rise_transition']:.2f} ns, "
              f"fall {res['fall_transition']:.2f} ns, rise/fall {res['rise_transition']/res['fall_transition']*100:.0f} %")
else:
    print("  (pass the liberty file path as the first argument)")
