# Ten 5 V transistors in series as diodes, swept to 100 V

A small gf180mcu experiment. Ten `nfet_05v0` (5 V NMOS) transistors are each
wired as a diode (gate tied to drain) and stacked in series. A DC source is
swept from 0 V to 100 V across the whole stack.

```
 V_in ──┬── M1 ── n1 ── M2 ── n2 ── … ── n9 ── M10 ──┬── 0 V
        │  (each Mk: gate = drain, W = 10 µm, L = 0.6 µm)
```

## How to run

```
uv run sim/diode_stack/run.py
```

This needs Docker and the latest `hpretl/iic-osic-tools` image, which holds
ngspice and the open gf180mcuD PDK. Set `IIC_OSIC_IMAGE` to pin another tag
or image ID. `run.py` writes one netlist per variant (`results/*.cir`), runs
ngspice, and writes `results/summary.md` plus three plots. It also runs
`junction_check.cir`. The first line of `results/summary.md` records the
image ID, the ngspice version and the cgroup limits that produced the
results. Every container runs by that image ID, so all runs use the same
image even if the tag moves part-way through.

`run.py` deletes each data file before its run. It stops if ngspice reports
an error, writes the wrong number of rows, or stops short of 100 V.

### Memory limits

Every ngspice run, including `junction_check.cir`, runs in its own container.
The container's cgroup caps memory at 4 GiB with no swap on top, and allows at
most 256 processes. If a simulation runs away, the kernel kills it inside that
cgroup and leaves the rest of the machine alone. Change the caps with
`SIM_MEMORY=16g` or `SIM_PIDS=…`.

The first line of each `results/*.log` is the limit as the container itself
reports it. `run.py` refuses a run whose limits don't match `SIM_MEMORY` and
`SIM_PIDS`, and reports exit code 137 as "killed by the memory limit". The
logs are not committed, so `results/summary.md` repeats the limits.

`uv run sim/diode_stack/test_cgroup.py` checks that the cap really works. It
runs a simulation that needs about 0.6 GB of memory twice. It passes only if
the run finishes under a 2 GiB cap and the cgroup kills it under a 256 MiB
cap.

## The three variants

What happens depends almost entirely on **where each transistor's body
(bulk) is connected**. So the stack is simulated three ways:

| Variant | Body of each NMOS | Buildable in gf180mcu? |
|---|---|---|
| **A** | the shared P-substrate, at 0 V | Yes: this is the default NMOS |
| **B** | its own source, in an isolated P-well inside its own deep N-well; the deep N-well is tied to that transistor's drain | Yes, with the deep N-well layer |
| **C** | its own source, with no junction to the substrate at all | **No.** It is the "textbook" answer, for comparison |

For A and B, the junctions use the PDK's own diode models:

* `diode_nd2ps_06v0`: N+ diffusion to P-substrate. The model sets `bv = 11` V.
  In B it also stands in for each drain's N+ to its own P-well.
* `diode_pw2dw`: P-well to deep N-well. `bv = 14.7` V.
* `diode_dw2ps`: deep N-well to P-substrate. `bv = 30.5` V.

These have to be added by hand. `nfet_05v0` wraps the `nfet_06v0` BSIM4
model, which sets `diomod = 1`. That is BSIM4's junction model without
breakdown, so its `bvs = 11` has no effect: the drain junction passes only
2 nA at 40 V. The PDK diode of the same area passes 0.73 mA at 12 V.
`junction_check.cir` reproduces this.

In A, each transistor's bulk reaches the substrate through its own 0 V
ammeter. That separates the transistor model's own bulk current from the
current in the added diodes.

## Results

![Current drawn vs voltage](results/current_vs_vin.png)

![Voltage across each transistor](results/per_device_voltage.png)

![Where the current goes](results/current_paths.png)

Selected points (full table in `results/summary.md`):

| V_in | A: current | A: worst device | B: current | B: worst device | C: current | C: worst device |
|---:|---:|---:|---:|---:|---:|---:|
| 5 V   | 1.5 pA  | 0.9 V  | 41 nA   | 0.5 V  | 41 nA   | 0.5 V |
| 10 V  | 6.6 nA  | 1.3 V  | 101 µA  | 1.0 V  | 101 µA  | 1.0 V |
| 12 V  | 730 µA  | 1.5 V  | 231 µA  | 1.2 V  | 231 µA  | 1.2 V |
| 20 V  | 84 mA   | 7.6 V  | 1.0 mA  | 2.0 V  | 1.0 mA  | 2.0 V |
| 30 V  | 0.53 A\* | 17 V\* | 2.2 mA  | 3.0 V  | 2.2 mA  | 3.0 V |
| 40 V  | 2.0 A\*  | 27 V\* | 17 A    | 8.7 V  | 3.6 mA  | 4.0 V |
| 50 V  | 4.3 A\*  | 36 V\* | 39 A    | 17 V   | 5.0 mA  | 5.0 V |
| 100 V | 12.8 A\* | 81 V\* | 181 A   | 48 V   | 18.5 mA | 10 V  |

"Worst device" is the largest voltage across any one transistor. For a
diode-connected transistor this is both V_GS and V_DS, so it is also the
voltage across its gate oxide.

\* Above about 25 V, most of A's current is the transistor model's
impact-ionisation current, far outside its fitted range (see below). These
rows show what the model does, not what silicon would do.

### What happens

**C, the ideal stack.** The ten transistors share the voltage equally, each
taking V_in / 10. The stack starts to conduct around 7–8 V, which is ten
thresholds of about 0.7–0.8 V each. Above 50 V every transistor is past its
5 V rating, and at 100 V each one has 10 V across it. So **even the ideal
stack cannot stand off 100 V with 5 V transistors.** It would need at least
20 of them.

**A, the default layout.** Every N+ diffusion forms a junction with the one
shared substrate. At about 11.7 V, the top transistor's drain junction to the
substrate breaks down: the substrate current passes 1 nA at 11.6 V, 1 µA at
11.75 V and 1 mA at 12.05 V. From then on, nearly all the current goes
**straight into the substrate** (microamps along the chain, milliamps into
the substrate). The stack stops sharing voltage. Breakdown holds node n1 at
12.0–13.6 V from 15 V to 50 V, and the nine lower transistors share only
that. The top transistor M1 takes the rest.

Above about 20 V, M1 has more than 7 V from drain to source, and the
transistor model's impact-ionisation term starts to dominate. M1's own bulk
current is 4 % of the substrate current at 20 V, 37 % at 25 V, 66 % at 30 V
and 93 % at 100 V. The input current even falls, from 16.4 A at 90 V to
12.8 A at 100 V. That negative resistance is a model artefact. Only the
breakdown onset near 11.7 V is a result to rely on.

**B, isolated wells.** This behaves like C until about 31 V. There, the deep
N-well of the top transistor, which is tied to V_in, breaks down to the
substrate (`bv = 30.5` V): its substrate current passes 1 µA at 31.05 V.
Above that, the source drives amps straight into the substrate. The next
deep N-well down then holds n1 near 31 V at first (31.3 V at 40 V). But n1
then rises, to 42.8 V at 75 V and 51.9 V at 100 V. Each broken-down deep
N-well has only its model's series resistance, about 0.5 Ω for this area,
so its voltage rises with its current. **Isolating each transistor moves the
weak point from about 11.7 V to about 31 V.** That 31 V comes from how this
deep N-well is doped and shaped, not from silicon itself. A junction's breakdown voltage
rises as its lighter-doped side gets more lightly doped, because the
depletion region spreads wider before the field reaches its avalanche value.
That critical field is about 3–4×10⁵ V/cm and rises slowly with doping
(εE²/2qN gives 4.3×10⁵ V/cm at 60 V and 10¹⁶ cm⁻³). Sze's empirical rule for silicon gives about 60 V at
10¹⁶ cm⁻³ and about 340 V at 10¹⁵ cm⁻³. So holding more voltage needs an
isolation junction that is lightly doped, several µm wide, and has gently
curved edges. That would be a new structure to design and model, not one this
process forbids.

### Foundry figures

The models are fitted to typical silicon. The guaranteed minimums from the
public gf180mcu electrical specifications are lower:

| Breakdown | Minimum | Typical | Source |
|---|---:|---:|---|
| N+ to P- junction (6 V NMOS) | 8.5 V | 11 V | [5.5 Junction Breakdown Voltage](https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_5.html) |
| N-well to P-substrate junction | 10 V | 14 V | same page |
| 6 V gate oxide | 12 V | 16 V | [5.4 Oxide Breakdown Voltage](https://gf180mcu-pdk.readthedocs.io/en/latest/analog/spice/elec_specs/elec_specs_5_4.html) |
| Deep N-well to P-substrate | not published | not published | the model alone uses 30.5 V |

The 31 V limit in variant B therefore rests only on a fitted model value.
No measured minimum backs it.

The simulated onset in variant A, about 11.7 V, sits near the 11 V typical
figure because the diode model's own `bv = 11` V is that figure. The
agreement is by construction, not a check. A design has to work at 8.5 V. Neither page says how breakdown is defined
(for example, at what leakage current).

### On a pin with ESD protection

The ESD simulations (`docs/esd/`, on the `docs/esd` branch, PR 15, not yet
merged) show the standard gf180mcu I/O cell holding its pad below about
5.6 V for a +2 kV HBM discharge. A +8 kV IEC contact discharge takes the
pad to a 15.3 V peak, and +15 kV to 21.0 V. If this stack sat on such a pin:

* **Isolated stack (B):** 15.3 V puts 1.5 V on each transistor and 15.3 V
  on the top deep N-well, below its 31 V. The stack draws 0.5 mA, while the
  protection carries amps, so the stack is not the weak point. At 21.0 V
  each transistor has 2.1 V, still below the deep N-well's breakdown.
* **Shared-substrate stack (A):** its top junction to the substrate avalanches
  at about 11.7 V (8.5 V minimum), so it becomes an extra ESD path into the
  substrate: 32 mA in the model at 15.3 V. It was never designed to carry
  ESD current.

A pin that is *meant* to carry high voltage can't use the standard cell
at all. Its positive path is a diode from the pad to the I/O supply, which
conducts as soon as the pad rises about 0.7 V above that supply. Its output
NMOS also snaps back at 10.7 V. A high-voltage pin needs a clamp that stays
off up to the pin's working voltage, but turns on before the weakest
junction or oxide attached to the pin breaks down. For a stack, that weakest
point is the isolation junction to the substrate.

### What the simulation cannot tell you

* **Gate-oxide breakdown is not modelled.** The PDK models have no oxide
  failure, so the simulation happily reports 81 V across a gate oxide rated
  for 5 V operation. A real device would be destroyed long before that.
* **The source has no current limit.** The amps shown above 31 V in B come
  from junctions in breakdown driven by an ideal voltage source.
  A real chip would melt its metal or junctions. The point that matters is
  *where* the current starts, not how big it gets.
* **Impact ionisation.** Above about 25 V, most of variant A's substrate
  current flows out of M1's own bulk. It comes from the model's
  impact-ionisation term (`alpha1 = 19`, `beta0 = 36.6`; `agidl = 0`, so not
  GIDL) at V_DS of 7–81 V. That is far outside the range the model was
  fitted for, so A's currents above about 20 V mean nothing.
* **Assumed geometry.** Diffusion length is 0.18 µm (the xschem symbol
  default). In B, each transistor has a 20 × 20 µm deep N-well holding a
  16 × 16 µm P-well. These sizes change leakage and the current after
  breakdown, but not the breakdown voltages.
* Typical corner, 27 °C, DC sweep in 0.05 V steps.
