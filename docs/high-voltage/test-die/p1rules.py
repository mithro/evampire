"""Rules of the breakdown comparison (P1) that act on the measured values.

method.rst, "Comparison with predictions", states each rule; calc.py,
section 5, prints the numbers derived here, and analyse.py applies the
same functions through decide.py.

stand_ins()      the structures that replace a reference lost on every
                 die: only those whose prediction equals the reference's
                 within SAME_PRED under every simulated process.
ratio_verdict()  a measured ratio, or a lower bound on one, against the
                 predicted ratio.
die_factors()    the outlier check by die: the median over structures of
                 the die's value over the median of all dies.

Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import statistics

import pred_data as pd

# Stand-ins, tier by tier: the first tier with a measured member replaces
# the reference. The copies of NT20 differ from it by up to 1.6 % in the
# simulation (NT20c under BD), so 2 % is the simulation's own resolution.
SAME_PRED = 0.02
G1 = ("NT20", "NT20b", "NT20c")
STAND_INS = {
    ("NT20",): (("NT20b", "NT20c"), ("NT20L", "NT20V"), ("NT5",)),
    G1: (("NT20L", "NT20V"), ("NT5",)),
    ("NW0", "NW0b"): (G1, ("NT20L", "NT20V"), ("NT5",)),
    ("NA0p6",): (("NA0p6b",), ("NA0p6T10",)),
    ("NA0p6", "NA0p6b"): (("NA0p6T10",),),
    ("DT20",): (("DT20b",), ("DT2p6",)),
}
# NW0 is the reference only under A, and its stand-ins equal it only there.
ONLY_UNDER = {("NW0", "NW0b"): "A"}

# Outlier check by die: a die whose median factor lies further than this
# from 1 is flagged. It is the tolerance of "the same" and of a ratio.
DIE_BAND = 0.15
DIE_MIN = 3            # dies needed before one can stand out


def same_prediction(ref, cand, pw=None):
    """True when cand's prediction (the lower of edge and corner) is within
    SAME_PRED of ref's under every process, of P-well pw if given, in
    which both are resolved, and both are resolved in at least one."""
    seen = 0
    for p in pd.PRED["processes"]:
        gated, ppw = pd.parse(p)[:2]
        if gated or (pw and ppw != pw):
            continue
        a, b = pd.band_of([p], ref)[0], pd.band_of([p], cand)[0]
        if a and b:
            seen += 1
            if abs(b / a - 1) > SAME_PRED:
                return False
    return seen > 0


def tiers(key, pw=None):
    """The tiers of stand-ins for a reference, each filtered to members
    with the same prediction; () if the key has none or pw excludes it."""
    if key not in STAND_INS or (key in ONLY_UNDER and pw != ONLY_UNDER[key]):
        return ()
    ref = key[0]
    out = []
    for tier in STAND_INS[key]:
        ok = tuple(n for n in tier if same_prediction(ref, n, ONLY_UNDER.get(key)))
        if ok:
            out.append(ok)
    return tuple(out)


def stand_in(key, measured, pw=None):
    """(members to use, note or None). measured(name) is True when the
    structure broke down on at least one die. The key itself is used while
    any member is measured."""
    if any(measured(n) for n in key):
        return key, None
    ts = tiers(key, pw)
    for tier in ts:
        got = tuple(n for n in tier if measured(n))
        if got:
            note = (f"{', '.join(key)}: no breakdown on any die; "
                    f"{', '.join(got)} stand in, with the same prediction "
                    f"within {100 * SAME_PRED:g} % under every simulated "
                    "process")
            if "NT5" in got and "NT5" not in key:
                note += ("; NT5 is itself compared with group 1, so that "
                         "test is then empty")
            return got, note
    if key in STAND_INS and not (key in ONLY_UNDER
                                 and pw != ONLY_UNDER[key]):
        return key, (f"{', '.join(key)}: no breakdown on any die, and no "
                     "stand-in was measured")
    return key, None


def ratio_verdict(m, p, bound):
    """Verdict on a measured ratio m (a lower bound if bound) against the
    predicted ratio p, within pd.RATIO."""
    if not bound:
        return "agrees" if pd.ratio_agrees(m, p) else "disagrees"
    if m > p * (1 + pd.RATIO):
        return "disagrees: the lower bound is above the range"
    if m >= p * (1 - pd.RATIO):
        return "agrees: the lower bound is within the range"
    return "inconclusive: the lower bound is below the range"


def bound_median(vals):
    """(median, bound) of [(value, is a lower bound)]: the median is exact
    when every bound lies above it, since raising those values leaves it
    where it is; otherwise it is a lower bound."""
    m = statistics.median(v for v, _ in vals)
    return m, any(b and v <= m for v, b in vals)


def die_factors(first):
    """{die: (factor, structures)} from {(structure, die): breakdown}: for
    every structure that broke down on DIE_MIN dies or more, the die's
    value over the median of all dies, and the median of those per die."""
    by = {}
    for (st, die), b in first.items():
        if st != "OPEN" and b.kind == "bv":
            by.setdefault(st, {})[die] = b.bv
    per = {}
    for st, vals in by.items():
        if len(vals) >= DIE_MIN:
            m = statistics.median(vals.values())
            for die, v in vals.items():
                per.setdefault(die, []).append(v / m)
    dies = {d for _, d in first}
    if len(dies) < DIE_MIN:
        return {}
    return {d: (statistics.median(fs), len(fs)) for d, fs in per.items()}


def outliers(factors):
    """The dies whose factor lies outside 1 +- DIE_BAND."""
    return sorted(d for d, (f, _) in factors.items()
                  if abs(f - 1) > DIE_BAND)
