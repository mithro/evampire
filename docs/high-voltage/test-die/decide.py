"""Turn reduced breakdown sweeps into the process decision and comparison.

The decision follows method.rst, tables tab-hvt-decision and tab-hvt-deep:
by the pattern between structures ("the same", "much higher" as a factor,
the border of pred_data.REGIME), with the absolute windows "near 14 V" and
"above 40 V" reported beside it, and with the capacitance call of cv.py
for the deep layer. The comparison takes the reference structure, the predicted ratio, the band
and the agreement range from pred_data.py, the module that writes the
tables of predictions.rst, so that the two cannot differ.

analyse.py calls this module. Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import statistics

import measure
import p1rules
import pred_data as pd

NEAR = (8.0, 25.0)     # V: "near 14 V", a secondary statement only
HIGHER = 40.0          # V: "above 40 V", a secondary statement only
SAME = (0.15, 3.0)     # "the same": less than 15 % of the lower or 3 V
MUCH = 2.0             # "much higher": a factor of two or more
FEW = 5                # fewer dies than this is reported
G1 = p1rules.G1                          # the group 1 value
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


def much(a, b):
    """a is "much higher" than b: by a factor of MUCH or more."""
    return a is not None and b is not None and a >= MUCH * b


def same(a, b):
    if a is None or b is None:
        return False
    return abs(a - b) < max(SAME[0] * min(a, b), SAME[1])


class Data:
    """The summaries of every structure, and helpers over them. A
    reference lost on every die is replaced by its stand-ins (p1rules),
    and each replacement is noted once in self.notes."""

    def __init__(self, summaries):
        self.s = summaries
        self.notes = []

    def measured(self, name):
        return name in self.s and any(b.kind == "bv"
                                      for b in self.s[name].per_die.values())

    def resolve(self, names, pw=None):
        names, note = p1rules.stand_in(tuple(names), self.measured, pw)
        if note and note not in self.notes:
            self.notes.append(note)
        return names

    def value(self, names, sub=False):
        """Mean of the medians of the measured, resolved members; with sub,
        a lost group is replaced by its stand-ins."""
        if sub:
            names = self.resolve(names)
        vals = [self.s[n].median for n in names
                if n in self.s and self.s[n].median is not None
                and not self.s[n].bound]
        return sum(vals) / len(vals) if vals else None

    def die_mean(self, names, die, bounds=False):
        """(mean on one die, whether it is a lower bound). With bounds, a
        member without breakdown counts at the highest voltage it
        reached, as a lower bound."""
        vals, bound = [], False
        for n in names:
            b = self.s[n].per_die.get(die) if n in self.s else None
            if b is not None and b.kind == "bv":
                vals.append(b.bv)
            elif bounds and b is not None and b.kind == "none":
                vals.append(b.limit)
                bound = True
        return (sum(vals) / len(vals) if vals else None), bound

    def ratio(self, names, refs, pw=None):
        """(median over the dies of the die's ratio, dies used, whether it
        is a lower bound). A die where the structure did not break down
        gives a lower bound; the reference must break down."""
        refs = self.resolve(refs, pw)
        dies = sorted({d for n in names if n in self.s for d in self.s[n].per_die})
        rs = []
        for d in dies:
            (a, bound), b = self.die_mean(names, d, True), \
                self.die_mean(refs, d)[0]
            if a is not None and b:
                rs.append((a / b, bound))
        if not rs:
            return None, 0, False
        m, bound = p1rules.bound_median(rs)
        return m, len(rs), bound


def fmt(v):
    return "–" if v is None else f"{v:.1f} V"


def pwell(data, ev):
    """(A, An, B or None, reason), with the evidence appended to ev."""
    g1, nt1, nt5 = data.value(G1, True), data.value(("NT1",)), \
        data.value(("NT5",))
    g2 = [data.value(m) for m in G2]
    g3 = data.value(G3, True)
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
        why = "no resolved value for " + ", ".join(miss)
        if g2[0] is None:
            why += (" (NW0 and NW0b are the only wells with P-well drawn "
                    "against them, so nothing stands in for them here)")
        return None, why
    flat = same(nt1, g1) and same(nt5, g1) and all(same(v, g1) for v in g2)
    rising = all(b >= a or same(a, b) for a, b in zip(g2, g2[1:]))
    levels(ev, g1, g2[0], g3)
    if flat and g1 < pd.REGIME:
        if much(g3, g1):
            return "An", "pattern of the first row of tab-hvt-decision"
        if same(g3, g1):
            return "A", "pattern of the second row of tab-hvt-decision"
        return None, ("every N-well at one voltage, and group 3 neither the "
                      "same nor much higher")
    if flat:
        return None, (f"every N-well at one voltage, {fmt(g1)}, which is not "
                      f"below {pd.REGIME:g} V: no heavy surface limits it, "
                      "and no row of tab-hvt-decision fits")
    if much(g1, g2[0]) and same(nt5, g1) and same(g2[-1], g1) and rising \
            and same(g3, g1) and g1 >= pd.REGIME:
        if near(nt1):
            ev.append("NT1 is near 14 V while the wells with a distant ring "
                      "are much higher: a P+ region close to the well can "
                      "explain the published value")
        return "B", "pattern of the third row of tab-hvt-decision"
    if same(nt5, g1) and g2[-1] > g2[0] and not same(g2[-1], g2[0]):
        return None, ("group 2 rising with distance without the pattern of "
                      "B: drawing P-well stops the generation (fourth row "
                      "of tab-hvt-decision), which no simulated family holds")
    return None, "the pattern matches no row of tab-hvt-decision"


def levels(ev, g1, nw0, g3):
    """The absolute windows, as a statement beside the pattern."""
    def where(v):
        if v is None:
            return "–"
        return (f"{v:.1f} V, " + ("inside" if near(v) else "outside")
                + f" {NEAR[0]:g} V to {NEAR[1]:g} V"
                + (f", above {HIGHER:g} V" if higher(v) else ""))
    ev.append(f"Absolute levels, beside the pattern: group 1 {where(g1)}; "
              f"NW0 {where(nw0)}; group 3 {where(g3)}")


def deep(data, pw, ev, cap=(None, "no capacitance result")):
    """(L, D or None, reason) from tab-hvt-deep: the breakdown ratios where
    some N-well edge is clear of P-well, and the capacitance call of cv.py
    (cap = (call, reason)) in every case."""
    if pw is None:
        return None, "the P-well question is undecided"
    bd, why = (None, "under A every N-well breaks down at its surface") \
        if pw == "A" else deep_breakdown(data, pw, ev)
    ev.append(f"Deep layer from the capacitance (P2): {cap[0] or 'none'}: "
              f"{cap[1]}")
    if bd and cap[0] and bd != cap[0]:
        return None, (f"breakdown selects {bd} ({why}) and capacitance "
                      f"selects {cap[0]}")
    if bd:
        return bd, why + ("; the capacitance agrees" if cap[0] else "")
    if cap[0]:
        return cap[0], f"{why}; capacitance: {cap[1]}"
    return None, f"{why}; capacitance: {cap[1]}"


def deep_breakdown(data, pw, ev):
    """(L, D or None, reason) from the breakdown rows of tab-hvt-deep."""
    num, den = DEEP[pw]
    m, n, mb = data.ratio(num, den, pw)
    pl = pd.ratio_value(num[0], pw + "L")[1]
    ev.append(f"Deep layer: mean of {', '.join(num)} over the mean of "
              f"{', '.join(den)}: measured "
              + ("–" if m is None else
                 f"{'> ' if mb else ''}{m:.2f} on {n} dies")
              + f"; predicted {pl:.2f} under {pw}L and 1 under {pw}D")
    over, above = [], []
    for name, s in sorted(data.s.items()):
        if name not in pd.STRUCTS or pd.STRUCTS[name]["kind"] != "nw" \
                or s.median is None:
            continue
        ref, pr, test = pd.ratio_value(name, pw + "D")
        refs = pd.REF_MEMBERS.get(ref, (ref,))
        if test and pr and name not in refs:
            r = data.ratio((name,), refs, pw)[0]   # a bound counts too
            if r is not None and r > pr * (1 + pd.RATIO):
                over.append(f"{name} ({r:.2f} against {pr:.2f})")
        lo, hi, _ = pd.band(name, pw + "D")
        if lo is not None and s.median > pd.agreement(lo, hi)[1]:
            above.append(name)
    if above:
        ev.append("Beside the ratios: above the agreement range of their D "
                  "prediction: " + ", ".join(above))
    if over:
        ev.append("Ratio to the reference above the D prediction by more "
                  f"than {100 * pd.RATIO:.0f} %: " + ", ".join(over))
        return "L", ("N-well structures hold more against their reference "
                     "than D allows")
    if m is None:
        return None, f"no die has both {num[0]} and its reference measured"
    if mb:      # a lower bound rules out only what lies wholly below it
        ok_l, ok_d = m <= pl * (1 + pd.RATIO), m <= 1 + pd.RATIO
        if ok_l and ok_d:
            return None, (f"the plate ratio is only a lower bound, > {m:.2f}, "
                          "which leaves both L and D open")
    else:
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
    pw = pd.parse(fam)[1]
    used = data.resolve(refs, pw) if ref else ()
    if ref and used != tuple(refs):
        row["ref"] = f"{ref} ({', '.join(used)} stand in)"
    row["m_ratio"], _, row["m_bound"] = data.ratio((name,), refs, pw) \
        if ref else (None, 0, False)
    if ref is None:
        row["ratio"] = "not simulated"
    elif ref == name or name in refs:
        row["ratio"] = "reference"
    elif pr is None:
        row["ratio"] = "no predicted ratio"
    elif not test:
        row["ratio"] = "across regimes: not a test"
    elif s.median is None:
        row["ratio"] = "no value"
    elif row["m_ratio"] is None:
        row["ratio"] = f"{ref} not measured on the same die"
    else:
        row["ratio"] = p1rules.ratio_verdict(row["m_ratio"], pr,
                                             row["m_bound"])
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
