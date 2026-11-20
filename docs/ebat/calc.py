"""Recompute every number used in the calculations on the ebat pages.

Run with:  uv run python docs/ebat/calc.py

The class powers come from IEEE 802.3-2022 (Table 145-11, Table 145-27,
Table 145-29). The efficiencies and the board power are the illustrative
values used on the evampire pages that the ebat pages link to, marked
ASSUMPTION below.

SPDX-License-Identifier: Apache-2.0
"""
import math

# Power at the powered device (W). Single-signature class 3: Table 145-29.
# Dual-signature class 3 on one pair set: Table 145-27.
P_CLASS3_PD = 13.0
# Lowest power at the power sourcing equipment (W): Table 145-11.
P_CLASS_PSE = {1: 4.0, 2: 6.7, 3: 14.0, 4: 30.0, 5: 45.0, 6: 60.0,
               7: 75.0, 8: 90.0}

# ASSUMPTION: the illustrative values of the USB Power Delivery translation
# page (docs/power/usb-pd/power-translation.rst).
ETA_USB = 0.900
P_BOARD_USB = 3.10
# ASSUMPTION: the illustrative values of the Power over Ethernet translation
# page (docs/power/poe/translation.rst): input converter 90 %, high-voltage
# converter 94 %.
ETA_POE = 0.90 * 0.94

INPUTS = (
    ("single-signature, class 3", P_CLASS3_PD),
    ("dual-signature, class 3, one pair set powered", P_CLASS3_PD),
    ("dual-signature, class 3, both pair sets powered", 2 * P_CLASS3_PD),
)


def floor2(x):
    """Round a current down to 10 mA (PD Section 3.2.1, item 1)."""
    return math.floor(x * 100 + 1e-9) / 100


def usb_offers(pdp, port_max_pdp):
    """Fixed offers for a Port Present PDP (PD Section 3.2.4, Table 3.2).

    A voltage above 5 V is offered when the Port Maximum PDP allows it:
    9 V above 15 W, 15 V above 27 W, 20 V above 45 W.
    """
    offers = [(5, min(3.0, floor2(pdp / 5)))]
    for volts, threshold in ((9, 15), (15, 27), (20, 45)):
        if port_max_pdp > threshold:
            offers.append((volts, min(3.0, floor2(pdp / volts))))
    return offers


print("== Ethernet in, USB out ==")
print(f"  ASSUMPTION eta = {ETA_USB}, P_board = {P_BOARD_USB} W")
for name, p_in in INPUTS:
    p_out = p_in * ETA_USB - P_BOARD_USB
    pdp = math.floor(p_out)
    # The port's power can never exceed this input, so the Port Maximum PDP
    # equals the Port Present PDP in this mode.
    offers = usb_offers(pdp, pdp)
    text = ", ".join(f"{v} V at {i:.2f} A" for v, i in offers)
    print(f"  {name}: P_in = {p_in:.1f} W, "
          f"P_out = {p_in:.1f} x {ETA_USB} - {P_BOARD_USB} = {p_out:.2f} W, "
          f"PDP = {pdp} W -> {text}")

print("== Ethernet in, Ethernet out ==")
print(f"  ASSUMPTION eta = 0.90 x 0.94 = {ETA_POE:.3f}")
for name, p_in in INPUTS:
    after = p_in * ETA_POE
    fits = [c for c, p in P_CLASS_PSE.items() if p <= after]
    best = max(fits)
    board_max = after - P_CLASS_PSE[best]
    print(f"  {name}: P_in = {p_in:.1f} W, after conversion "
          f"{after:.2f} W -> class {best} ({P_CLASS_PSE[best]} W), "
          f"board power up to {board_max:.2f} W")
