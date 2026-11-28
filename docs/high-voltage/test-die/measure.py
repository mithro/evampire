"""Read the measurement records of the test die and reduce each sweep.

The records are the CSV files of method.rst, section "Sample size and
records" (table tab-hvt-record): one file per sweep, one row per bias
point, named DIE.STRUCTURE.PROCEDURE.SWEEP.csv. The columns of a file must
agree with its name. Currents are taken as magnitudes, so the sign
convention of the instrument does not matter.

Reductions, each as method.rst states it:

breakdown()   P1, and the second part of P4: the well voltage at which the
              well current first reaches 1 uA, and the one at 100 nA,
              interpolated between steps on the logarithm of the current.
ring_onset()  P3: the well voltage at which the ring reaches 1 V, and the
              step held by the gap at the highest well voltage.
punch()       P5: the well voltage at which the ring current reaches 1 nA.
balance()     P1 and P5: how far the current returned by the substrate (and
              the ring) differs from the well current, above 100 nA.
gated_levels() P4, first part: the flat-band voltage and field threshold.

analyse.py calls this module. Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import csv
import math
import pathlib
import re

from import_predictions import crossing   # the interpolation of p5.json

COLUMNS = ("die", "structure", "procedure", "sweep", "direction",
           "temperature_c", "v_well_v", "i_well_a", "i_sub_a", "v_aux_v",
           "i_aux_a", "c_f", "d", "freq_hz", "time_s")
NUMERIC = COLUMNS[5:]
NEEDS = {"P1": ("v_well_v", "i_well_a"),
         "P2": ("v_well_v", "c_f", "d", "freq_hz"),
         "P3": ("v_well_v", "i_well_a", "v_aux_v"),
         "P4": ("v_well_v", "i_well_a", "v_aux_v", "i_aux_a"),
         "P5": ("v_well_v", "i_well_a", "i_sub_a", "i_aux_a")}
NAME = re.compile(r"^([A-Za-z0-9-]+)\.([A-Za-z0-9_]+)\.(P[1-5])\.([0-9]+)"
                  r"\.csv$")

BV_LEVEL = 1e-6        # A: the breakdown voltage
LOW_LEVEL = 1e-7       # A: recorded as well
KNEE = 2.0             # V: 100 nA and 1 uA further apart than this: no knee
WALKOUT = 0.5          # V: one step; a larger move from sweep 1 to 3
OPEN_FACTOR = 10       # a reading counts if ten times the OPEN current
RING_LEVEL = 1.0       # V: P3, the ring has started to follow
P5_LEVEL = 1e-9        # A: P5, punch-through
BALANCE = 0.10         # well and returned currents differ by more: flagged
BALANCE_FROM = 1e-7    # A: the balance is checked from this well current
STEP_MIN = 2.0         # P4: a current step smaller than this is not seen
ROOM = (20.0, 30.0)    # degrees C counted as 25 C
HOT = (80.0, 90.0)     # degrees C counted as 85 C


class RecordError(Exception):
    """A file that cannot be read as a record; the message names it."""


class Sweep:
    """One file: its identity and its rows, in the order measured."""

    def __init__(self, path, die, structure, procedure, sweep, direction,
                 temperature, rows):
        self.path, self.die, self.structure = path, die, structure
        self.procedure, self.sweep, self.direction = procedure, sweep, direction
        self.temperature, self.rows = temperature, rows

    def col(self, key):
        return [r[key] for r in self.rows]

    def amps(self, key):
        return [abs(r[key]) for r in self.rows]

    @property
    def room(self):
        return ROOM[0] <= self.temperature <= ROOM[1]

    @property
    def hot(self):
        return HOT[0] <= self.temperature <= HOT[1]


def _number(path, line, key, text):
    try:
        x = float(text)
    except ValueError:
        raise RecordError(f"{path}: row {line}: column {key} is not a "
                          f"number: {text!r}") from None
    if not math.isfinite(x):
        raise RecordError(f"{path}: row {line}: column {key} is {text!r}")
    return x


def read(path):
    """A Sweep from one file; raises RecordError on any fault."""
    path = pathlib.Path(path)
    m = NAME.match(path.name)
    if not m:
        raise RecordError(f"{path}: the name is not "
                          "DIE.STRUCTURE.PROCEDURE.SWEEP.csv")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise RecordError(f"{path}: cannot be read: {e}") from None
    reader = csv.DictReader(text.splitlines())
    head = reader.fieldnames or []
    missing = [c for c in COLUMNS if c not in head]
    if missing:
        raise RecordError(f"{path}: row 1: missing columns "
                          + ", ".join(missing))
    want = dict(zip(("die", "structure", "procedure", "sweep"), m.groups()))
    rows, ident = [], None
    for line, raw in enumerate(reader, start=2):
        if None in raw or any(v is None for v in raw.values()):
            raise RecordError(f"{path}: row {line}: wrong number of cells")
        here = (raw["die"], raw["structure"], raw["procedure"], raw["sweep"],
                raw["direction"], raw["temperature_c"])
        for key in ("die", "structure", "procedure", "sweep"):
            if raw[key] != want[key]:
                raise RecordError(f"{path}: row {line}: {key} is "
                                  f"{raw[key]!r}, the file name says "
                                  f"{want[key]!r}")
        if raw["direction"] not in ("up", "down"):
            raise RecordError(f"{path}: row {line}: direction must be up or "
                              f"down, not {raw['direction']!r}")
        if ident is not None and here != ident:
            raise RecordError(f"{path}: row {line}: direction or temperature "
                              "differs from row 2; one file holds one sweep")
        ident = here
        row = {}
        for key in NUMERIC:
            cell = raw[key].strip()
            row[key] = None if cell == "" else _number(path, line, key, cell)
        for key in NEEDS[want["procedure"]] + ("temperature_c",):
            if row[key] is None:
                raise RecordError(f"{path}: row {line}: column {key} is "
                                  f"empty, and {want['procedure']} needs it")
        rows.append(row)
    if not rows:
        raise RecordError(f"{path}: no rows")
    return Sweep(path, want["die"], want["structure"], want["procedure"],
                 int(want["sweep"]), ident[4], rows[0]["temperature_c"], rows)


def read_dir(top):
    """(sweeps, errors): every *.csv under top, recursively, in name order."""
    sweeps, errors = [], []
    for path in sorted(pathlib.Path(top).rglob("*.csv")):
        try:
            sweeps.append(read(path))
        except RecordError as e:
            errors.append(str(e))
    return sweeps, errors


class Breakdown:
    """The reduction of one breakdown sweep. kind is "bv", "none" (no
    breakdown below `limit` volts) or "short" (already at 1 uA at the first
    step above 0 V)."""

    def __init__(self, kind, bv=None, low=None, limit=None):
        self.kind, self.bv, self.low, self.limit = kind, bv, low, limit

    @property
    def knee(self):
        """False when 100 nA and 1 uA lie more than KNEE apart: leakage."""
        return self.kind != "bv" or self.low is None \
            or self.bv - self.low <= KNEE


def breakdown(sw):
    v, a = sw.col("v_well_v"), sw.amps("i_well_a")
    first = next((k for k, x in enumerate(v) if x > 0), len(v) - 1)
    if any(x >= BV_LEVEL for x in a[:first + 1]):
        return Breakdown("short", limit=max(v))
    bv = crossing(v, a, BV_LEVEL)
    if bv is None:
        return Breakdown("none", limit=max(v))
    return Breakdown("bv", bv, crossing(v, a, LOW_LEVEL), max(v))


def current_at(sw, volts):
    """The well current of a sweep at a well voltage, interpolated on its
    logarithm; None outside the sweep."""
    v, a = sw.col("v_well_v"), sw.amps("i_well_a")
    for k in range(1, len(v)):
        if v[k - 1] <= volts <= v[k] and v[k] > v[k - 1]:
            f = (volts - v[k - 1]) / (v[k] - v[k - 1])
            if a[k - 1] > 0 and a[k] > 0:
                return math.exp(math.log(a[k - 1]) + f * math.log(a[k] / a[k - 1]))
            return a[k - 1] + f * (a[k] - a[k - 1])
    return None


def linear_crossing(xs, ys, level):
    """The x at which ys first reaches level, linearly interpolated."""
    for k, y in enumerate(ys):
        if y >= level:
            if k == 0:
                return xs[0]
            f = (level - ys[k - 1]) / (y - ys[k - 1])
            return xs[k - 1] + f * (xs[k] - xs[k - 1])
    return None


def ring_onset(sw):
    """(onset volts or None, step volts, highest well volts) of a P3 sweep."""
    v, ring = sw.col("v_well_v"), sw.col("v_aux_v")
    top = max(range(len(v)), key=lambda k: v[k])
    return linear_crossing(v, ring, RING_LEVEL), v[top] - ring[top], v[top]


def punch(sw):
    """(punch-through volts or None, highest well volts, mechanism) of a P5
    sweep. The mechanism compares ring and substrate current at the last
    point: current into the ring is punch-through, into the substrate
    avalanche."""
    v = sw.col("v_well_v")
    pt = crossing(v, sw.amps("i_aux_a"), P5_LEVEL)
    ring, sub = sw.amps("i_aux_a")[-1], sw.amps("i_sub_a")[-1]
    return pt, max(v), "punch-through" if ring >= sub else "avalanche"


def balance(sw):
    """Largest |1 - returned / well| over the rows whose well current is
    at least BALANCE_FROM, where `returned` is the substrate current (and,
    in P5, the ring current too); None if not recorded or never reached."""
    worst = None
    for r in sw.rows:
        well = abs(r["i_well_a"] or 0)
        if well < BALANCE_FROM or r["i_sub_a"] is None:
            continue
        back = abs(r["i_sub_a"])
        if sw.procedure == "P5":
            back += abs(r["i_aux_a"] or 0)
        d = abs(1 - back / well)
        worst = d if worst is None else max(worst, d)
    return worst


def gated_levels(sw):
    """(flat-band volts or None, threshold volts or None) of a P4 plate
    sweep: where the well current first rises above the geometric mean of
    its accumulation level and its peak, and where it then falls below the
    geometric mean of the peak and its inversion level. Each level is the
    median of a tenth of the points, at the start and at the end; a step
    smaller than STEP_MIN times is not resolved."""
    pts = sorted(zip(sw.col("v_aux_v"), sw.amps("i_well_a")))
    vs, a = [p[0] for p in pts], [p[1] for p in pts]
    n = max(3, len(a) // 10)
    run = [sorted(a[max(0, k - 2):k + 3])[len(a[max(0, k - 2):k + 3]) // 2]
           for k in range(len(a))]
    acc, inv = sorted(a[:n])[n // 2], sorted(a[-n:])[n // 2]
    peak = max(run)
    if acc <= 0 or peak < STEP_MIN * acc:
        return None, None
    k_pk = run.index(peak)
    up = math.sqrt(acc * peak)
    vfb = next(vs[k] for k in range(len(a)) if run[k] >= up)
    if inv <= 0 or peak < STEP_MIN * inv:
        return vfb, None
    down = math.sqrt(peak * inv)
    vt = next((vs[k] for k in range(k_pk, len(a)) if run[k] <= down), None)
    return vfb, vt


def gated_part(sw):
    """1 when the plate is swept (first part of P4), 2 when the well is."""
    span = lambda xs: max(xs) - min(xs)  # noqa: E731
    return 1 if span(sw.col("v_aux_v")) > span(sw.col("v_well_v")) else 2


def capacitance_checks(sw):
    """Rows of a P2 sweep whose dissipation factor exceeds 0.1."""
    return sum(1 for r in sw.rows if r["d"] > 0.1)
