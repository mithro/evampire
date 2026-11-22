Image `hpretl/iic-osic-tools:latest`, ID `sha256:fd31cb46f41bea25c60bcdff1a8106f9e3889b3f05260af80c75a8b625a1c1db`. ngspice: ngspice-47.

## A_shared_substrate
Bulk of every NMOS is the common P-substrate (0 V). This is what you get in gf180mcu without deep N-well.

| V_in (V) | I_in | I via chain bottom | I into substrate | max V across one device (which) | V(top node) |
|---:|---:|---:|---:|---:|---:|
| 2 | 137 fA | 114 fA | 23.2 fA | 0.51 V (M1) | 2.0 V |
| 5 | 1.52 pA | 1.45 pA | 68.8 fA | 0.94 V (M1) | 5.0 V |
| 8 | 111 pA | 111 pA | 125 fA | 1.17 V (M1) | 8.0 V |
| 10 | 6.63 nA | 6.63 nA | 168 fA | 1.29 V (M2) | 10.0 V |
| 12 | 730 µA | 786 nA | 729 µA | 1.45 V (M4) | 12.0 V |
| 15 | 28.5 mA | 12.1 µA | 28.4 mA | 2.99 V (M1) | 15.0 V |
| 20 | 83.5 mA | 23.4 µA | 83.5 mA | 7.55 V (M1) | 20.0 V |
| 30 | 531 mA | 48.1 µA | 531 mA | 16.95 V (M1) | 30.0 V |
| 40 | 1.96 A | 61.6 µA | 1.96 A | 26.62 V (M1) | 40.0 V |
| 50 | 4.26 A | 63.9 µA | 4.26 A | 36.43 V (M1) | 50.0 V |
| 75 | 12.1 A | 67.6 µA | 12.1 A | 60.90 V (M1) | 75.0 V |
| 100 | 12.8 A | 95.3 µA | 12.8 A | 81.14 V (M1) | 100.0 V |

## B_isolated_dnwell
Each NMOS in its own isolated P-well (bulk = source) inside its own deep N-well, deep N-well tied to the drain. Well-to-well and well-to-substrate junctions are modelled.

| V_in (V) | I_in | I via chain bottom | I into substrate | max V across one device (which) | V(top node) |
|---:|---:|---:|---:|---:|---:|
| 2 | 14.3 pA | 14.3 pA | 23.2 fA | 0.20 V (M1) | 2.0 V |
| 5 | 41.3 nA | 41.3 nA | 39.7 fA | 0.50 V (M2) | 5.0 V |
| 8 | 18.1 µA | 18.1 µA | 56.2 fA | 0.80 V (M3) | 8.0 V |
| 10 | 101 µA | 101 µA | 67.2 fA | 1.00 V (M1) | 10.0 V |
| 12 | 231 µA | 231 µA | 78.2 fA | 1.20 V (M2) | 12.0 V |
| 15 | 483 µA | 483 µA | 94.7 fA | 1.50 V (M1) | 15.0 V |
| 20 | 1 mA | 1 mA | 122 fA | 2.00 V (M1) | 20.0 V |
| 30 | 2.25 mA | 2.25 mA | 177 fA | 3.00 V (M1) | 30.0 V |
| 40 | 17 A | 2.88 mA | 17 A | 8.75 V (M1) | 40.0 V |
| 50 | 39.4 A | 3.09 mA | 39.4 A | 17.35 V (M1) | 50.0 V |
| 75 | 109 A | 3.48 mA | 109 A | 32.23 V (M1) | 75.0 V |
| 100 | 181 A | 3.84 mA | 181 A | 48.16 V (M1) | 100.0 V |

## C_ideal_floating
Bulk = source with NO junction to the substrate at all. Not buildable; shows the 'textbook' answer for comparison.

| V_in (V) | I_in | I via chain bottom | I into substrate | max V across one device (which) | V(top node) |
|---:|---:|---:|---:|---:|---:|
| 2 | 14.3 pA | 14.3 pA | 0 A | 0.20 V (M3) | 2.0 V |
| 5 | 41.3 nA | 41.3 nA | 0 A | 0.50 V (M1) | 5.0 V |
| 8 | 18.1 µA | 18.1 µA | 0 A | 0.80 V (M3) | 8.0 V |
| 10 | 101 µA | 101 µA | 0 A | 1.00 V (M1) | 10.0 V |
| 12 | 231 µA | 231 µA | 0 A | 1.20 V (M2) | 12.0 V |
| 15 | 483 µA | 483 µA | 0 A | 1.50 V (M1) | 15.0 V |
| 20 | 1 mA | 1 mA | 0 A | 2.00 V (M1) | 20.0 V |
| 30 | 2.25 mA | 2.25 mA | 0 A | 3.00 V (M1) | 30.0 V |
| 40 | 3.6 mA | 3.6 mA | 0 A | 4.00 V (M1) | 40.0 V |
| 50 | 4.99 mA | 4.99 mA | 0 A | 5.00 V (M1) | 50.0 V |
| 75 | 9.05 mA | 9.05 mA | 0 A | 7.50 V (M1) | 75.0 V |
| 100 | 18.5 mA | 18.5 mA | 0 A | 10.00 V (M1) | 100.0 V |

## Junction breakdown check (junction_check.cir)

| V | nfet_05v0 own drain junction | diode_nd2ps_06v0 |
|---:|---:|---:|
| 12 | 31.6 pA | 729 µA |
| 40 | 2.06 nA | 251 mA |
