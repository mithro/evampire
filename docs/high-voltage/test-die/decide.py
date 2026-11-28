"""Turn reduced breakdown sweeps into the process decision and comparison.

The decision follows method.rst, tables tab-hvt-decision and tab-hvt-deep,
with the fixed meanings of "near 14 V", "much higher" and "the same". The
comparison takes the reference structure, the predicted ratio, the band
and the agreement range from pred_data.py, the module that writes the
tables of predictions.rst, so that the two cannot differ.

analyse.py calls this module. Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import statistics

import measure
import pred_data as pd

NEAR = (8.0, 25.0)     # V: "near 14 V"
HIGHER = 40.0          # V: "much higher"
SAME = (0.15, 3.0)     # "the same": less than 15 % of the lower or 3 V
FEW = 5                # fewer dies than this is reported
G1 = ("NT20", "NT20b", "NT20c")          # the group 1 value
G2 = (("NW0", "NW0b"), ("NW1p5",), ("NW3",), ("NW6",))   # by distance
G3 = ("NA0p6", "NA0p6b")                 # NAT beside an N-well
RISE = ("NA0p6T10", "NA0p6")             # P+ ring at 10 um and at 20 um
DEEP = {"B": (("NM1_6", "NM1_6b"), G1), "An": (("NAM1_6",), G3)}


class Summary:
    """One structure over the dies: first sweep at 25 C, 1 uA."""

    def __init__(self, name, per_die):
        self.name, self.per_die = name, per_die
        got = {d: b for d, b in per_die.items() if b.kind != "short"}
        self.shorts = sorted(d for d, b in per_die.items() if b.kind == "short")
        self.open_dies = sorted(d for d, b in got.items() if b.kind == "none")
        self.no_knee = sorted(d for d, b in got.items() if not b.knee)
        vals = [b.bv if b.kind == "bv" else b.limit for b in got.values()]
        self.n = len(vals)
        self.median = statistics.median(vals) if vals else None
        self.lo, self.hi = (min(vals), max(vals)) if vals else (None, None)
        # a lower bound when half the dies or more did not break down
        self.bound = bool(vals) and 2 * len(self.open_dies) >= len(vals)

    def bv(self, die):
        b = self.per_die.get(die)
        return b.bv if b is not None and b.kind == "bv" else None


def near(v):
    return v is not None and NEAR[0] <= v <= NEAR[1]


def higher(v):
    return v is not None and v > HIGHER


def same(a, b):
    if a is None or b is None:
        return False
    return abs(a - b) < max(SAME[0] * min(a, b), SAME[1])


class Data:
    """The summaries of every structure, and helpers over them."""

    def __init__(self, summaries):
        self.s = summaries

    def value(self, names):
        """Mean of the medians of the measured, resolved members."""
        vals = [self.s[n].median for n in names
                if n in self.s and self.s[n].median is not None
                and not self.s[n].bound]
        return sum(vals) / len(vals) if vals else None

    def die_mean(self, names, die):
        vals = [self.s[n].bv(die) for n in names if n in self.s]
        vals = [v for v in vals if v is not None]
        return sum(vals) / len(vals) if vals else None

    def ratio(self, names, refs):
        """Median over the dies of the die's ratio, and the dies used."""
        dies = sorted({d for n in names if n in self.s for d in self.s[n].per_die})
        rs = []
        for d in dies:
            a, b = self.die_mean(names, d), self.die_mean(refs, d)
            if a is not None and b:
                rs.append(a / b)
        return (statistics.median(rs) if rs else None), len(rs)


def fmt(v):
    return "–" if v is None else f"{v:.1f} V"


def pwell(data, ev):
    """(A, An, B or None, reason), with the evidence appended to ev."""
    g1, nt1, nt5 = data.value(G1), data.value(("NT1",)), data.value(("NT5",))
    g2 = [data.value(m) for m in G2]
    g3 = data.value(G3)
    ev.append(f"Group 1: NT1 {fmt(nt1)}, NT5 {fmt(nt5)}, mean of NT20, "
              f"NT20b and NT20c {fmt(g1)}")
    ev.append("Group 2 by P-well distance: " + ", ".join(
        f"{m[0]} {fmt(v)}" for m, v in zip(G2, g2))
        + " (NW0 as the mean of NW0 and NW0b)")
    ev.append(f"Group 3: mean of NA0p6 and NA0p6b {fmt(g3)}")
    knee = [n for n in ("NT1", "NT5") + G1 + sum(G2, ()) + G3
            if n in data.s and 2 * len(data.s[n].no_knee) > data.s[n].n]
    if knee:
        return None, ("no knee on most dies of " + ", ".join(knee)
                      + ": not avalanche (last row of tab-hvt-decision)")
    t10, t20 = data.value(RISE[:1]), data.value(RISE[1:])
    if t10 and t20 and t20 > t10 and not same(t10, t20):
        return None, (f"NA0p6 ({fmt(t20)}) holds more than NA0p6T10 "
                      f"({fmt(t10)}): the breakdown still rises between "
                      "P+ ring distances of 10 µm and 20 µm, so the P+ ring "
                      "is reached first (last row of tab-hvt-decision)")
    if None in (g1, nt1, nt5, g3) or None in g2:
        miss = [n for n, v in (("group 1", g1), ("NT1", nt1), ("NT5", nt5),
                               ("group 3", g3)) if v is None]
        miss += [m[0] for m, v in zip(G2, g2) if v is None]
        return None, "no resolved value for " + ", ".join(miss)
    g1near = near(nt1) and near(nt5) and near(g1)
    g2same = all(same(v, g1) for v in g2)
    if g1near and g2same and higher(g3):
        return "An", "pattern of the first row of tab-hvt-decision"
    if g1near and g2same and same(g3, g1):
        return "A", "pattern of the second row of tab-hvt-decision"
    rising = all(b >= a or same(a, b) for a, b in zip(g2, g2[1:]))
    if higher(nt5) and higher(g1) and near(g2[0]) and same(g2[-1], g1) \
            and rising and same(g3, g1):
        if near(nt1):
            ev.append("NT1 is near 14 V while the wells with a distant ring "
                      "are much higher: a P+ region close to the well can "
                      "explain the published value")
        return "B", "pattern of the third row of tab-hvt-decision"
    if g1near and g2[-1] > g2[0] and not same(g2[-1], g2[0]):
        return None, ("group 1 near 14 V and group 2 rising with distance: "
                      "drawing P-well stops the generation (fourth row of "
                      "tab-hvt-decision), which no simulated family holds")
    return None, "the pattern matches no row of tab-hvt-decision"


def deep(data, pw, ev):
    """(L, D or None, reason) from tab-hvt-deep, by breakdown voltage."""
    if pw is None:
        return None, "the P-well question is undecided"
    if pw == "A":
        return None, ("under A every N-well breaks down at its surface; "
                      "only the capacitance of CVN and CVN2 (P2) answers it")
    num, den = DEEP[pw]
    m, n = data.ratio(num, den)
    pl = pd.ratio_value(num[0], pw + "L")[1]
    ev.append(f"Deep layer: mean of {', '.join(num)} over the mean of "
              f"{', '.join(den)}: measured "
              + ("–" if m is None else f"{m:.2f} on {n} dies")
              + f"; predicted {pl:.2f} under {pw}L and 1 under {pw}D")
    over = []
    for name, s in sorted(data.s.items()):
        if name not in pd.STRUCTS or pd.STRUCTS[name]["kind"] != "nw" \
                or s.median is None:
            continue
        lo, hi, _ = pd.band(name, pw + "D")
        if lo is not None and s.median > pd.agreement(lo, hi)[1]:
            over.append(name)
    if over:
        ev.append("Above the agreement range of their D prediction: "
                  + ", ".join(over))
        return "L", ("N-well structures above the agreement range of their "
                     "D prediction, which D does not allow")
    if m is None:
        return None, f"no die has both {num[0]} and its reference measured"
    ok_l, ok_d = pd.ratio_agrees(m, pl), pd.ratio_agrees(m, 1.0)
    if ok_l and not ok_d:
        return "L", "the plate ratio agrees with the L prediction"
    if ok_d and not ok_l:
        return "D", "the plate ratio is 1: the plate adds nothing"
    return None, ("the plate ratio agrees with both" if ok_l else
                  "the plate ratio agrees with neither L nor D")


def families(pw, dp):
    if pw is None:
        return []
    cands = [pw + dp] if dp else [pw + "L", pw + "D"]
    return [f for f in cands if f in pd.families()]


def compare(data, name, fam):
    """One row of the comparison of a structure under a family."""
    s = data.s[name]
    row = {"name": name, "family": fam, "n": s.n, "median": s.median,
           "bound": s.bound, "spread": (s.lo, s.hi)}
    ref, pr, test = pd.ratio_value(name, fam) if name in pd.STRUCTS \
        else (None, None, False)
    row["ref"], row["p_ratio"] = ref, pr
    refs = pd.REF_MEMBERS.get(ref, (ref,))
    row["m_ratio"] = data.ratio((name,), refs)[0] if ref else None
    if ref is None:
        row["ratio"] = "not simulated"
    elif ref == name or name in refs:
        row["ratio"] = "reference"
    elif pr is None:
        row["ratio"] = "no predicted ratio"
    elif not test:
        row["ratio"] = "across regimes: not a test"
    elif row["m_ratio"] is None:
        row["ratio"] = f"{ref} not measured on the same die"
    else:
        row["ratio"] = ("agrees" if pd.ratio_agrees(row["m_ratio"], pr)
                        else "disagrees")
    lo, hi, _ = pd.band(name, fam) if name in pd.STRUCTS else (None, None, 0)
    row["band"] = (lo, hi)
    row["range"] = pd.agreement(lo, hi) if lo is not None else None
    row["absolute"] = absolute(s, name, fam, row["range"])
    return row


def absolute(s, name, fam, rng):
    if s.median is None:
        return "short on every die" if s.shorts else "no value"
    if rng is None:
        return "no range: the simulation gave no band"
    a, b = rng
    if s.bound:
        return (f"above (no breakdown below {s.median:.1f} V)" if s.median > b
                else f"inconclusive: no breakdown below {s.median:.1f} V")
    if a <= s.median <= b:
        return "in range"
    d = s.median - (b if s.median > b else a)
    word = "above" if d > 0 else "below"
    out = f"{word} by {abs(d):.1f} V ({100 * d / (b if d > 0 else a):+.0f} %)"
    square = pd.STRUCTS[name]["corner"] == 0
    cv, ck = pd.value(name, fam, "corner")
    ev, ek = pd.value(name, fam, "edge")
    if square and d > 0:
        out += "; a square corner is expected above its prediction"
    elif not square and d < 0 and ck == "bv" and ek == "bv" and cv < ev:
        out += "; a cut corner is expected below its prediction"
    return out


def summaries(sweeps):
    """{structure: Summary} from the first P1 sweep at 25 C of each die,
    and the per-die results of the third and the hot sweeps."""
    room, hot = {}, {}
    for w in sorted(sweeps, key=lambda w: w.sweep):
        if w.procedure == "P1" and w.direction == "up":
            if w.room:
                room.setdefault((w.structure, w.die), []).append(w)
            elif w.hot:
                hot.setdefault((w.structure, w.die), w)
    first = {k: measure.breakdown(ws[0]) for k, ws in room.items()}
    third = {k: measure.breakdown(ws[2]) for k, ws in room.items()
             if len(ws) >= 3}
    per = {}
    for (st, die), b in first.items():
        per.setdefault(st, {})[die] = b
    return ({n: Summary(n, d) for n, d in per.items()}, first, third,
            {k: measure.breakdown(w) for k, w in hot.items()})
