"""Compare measurements of the test die with the simulated predictions.

    uv run python docs/high-voltage/test-die/analyse.py MEASUREMENT_DIR [--out REPORT.md] [--family BL]
    uv run python docs/high-voltage/test-die/analyse.py --example DIR

MEASUREMENT_DIR holds the CSV records of method.rst (one file per sweep,
named DIE.STRUCTURE.PROCEDURE.SWEEP.csv), in any sub-folders. The script
extracts the breakdown voltage of every P1 sweep, takes the median over
the dies of the first sweep at 25 C, applies the process decision of
method.rst, and compares each structure with predictions.json under the
family the decision selects, by ratio and by agreement range. It reduces
P2 to P5 as well (procs.py, cv.py), each against the rules of rules.py,
and lists what makes a result inconclusive. --family compares under a family named by hand
instead of the decided one.

The report is Markdown, on standard output or in REPORT.md. The exit
status is 0 whatever the comparison shows, 2 when a record cannot be read;
each error names the file and the row.

--example DIR writes a SYNTHETIC measurement set under process BL into
DIR (synth.py), so that the script can be tried without silicon.

Standard library only.

SPDX-License-Identifier: Apache-2.0
"""

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import decide  # noqa: E402
import measure  # noqa: E402
import p1rules  # noqa: E402
import pred_data as pd  # noqa: E402
import procs  # noqa: E402


class Result:
    """Everything the report holds, for the report and for the tests."""

    def __init__(self, top, family=None, leave_out=()):
        sweeps, self.errors = measure.read_dir(top)
        self.unusable, self.left_out = [], tuple(leave_out)
        known = []
        for w in sweeps:
            if w.die in self.left_out:
                continue
            if w.structure not in pd.STRUCTS:
                self.unusable.append(f"{w.path}: no structure "
                                     f"{w.structure} on the die")
            else:
                known.append(w)
        self.sweeps = known
        self.summ, self.first, self.third, self.hot = decide.summaries(known)
        self.data = decide.Data(self.summ)
        self.dies = sorted({w.die for w in known})
        self.evidence = []
        self.cap = procs.p2(known)
        self.pwell, self.pwell_why = decide.pwell(self.data, self.evidence)
        self.deep, self.deep_why = decide.deep(
            self.data, self.pwell, self.evidence,
            (self.cap["call"], self.cap["why"]))
        self.forced = family
        self.families = [family] if family else decide.families(self.pwell,
                                                                self.deep)
        order = [s["name"] for s in pd.MAN["sites"]
                 if s["name"] in self.summ and s["name"] != "OPEN"]
        self.rows = [decide.compare(self.data, n, f)
                     for n in order for f in self.families]
        self.other = procs.procedures(
            known, self.first, self.families[0] if self.families else None,
            self.cap)
        self.issues = self.inconclusive() + self.data.notes
        self.factors = p1rules.die_factors(self.first)
        self.outliers = p1rules.outliers(self.factors)
        self.issues += [f"{d}: its structures lie at {self.factors[d][0]:.2f} "
                        "times the median of all dies, outside "
                        f"1 ± {p1rules.DIE_BAND:g}; the medians keep it, and "
                        "the report repeats the decision without it."
                        for d in self.outliers]
        self.without = Result(top, family, self.outliers) \
            if self.outliers and not leave_out else None

    def inconclusive(self):
        out = []
        if len(self.dies) < decide.FEW:
            out.append(f"Only {len(self.dies)} dies measured; method.rst asks "
                       f"for at least {decide.FEW}.")
        for n, s in sorted(self.summ.items()):
            if s.shorts:
                out.append(f"{n}: short or leak, already at 1 µA at the first "
                           f"step, on {', '.join(s.shorts)}; left out.")
            if s.no_knee:
                out.append(f"{n}: no knee (100 nA and 1 µA more than "
                           f"{measure.KNEE:g} V apart) on {', '.join(s.no_knee)}.")
            if s.open_dies and n != "OPEN":
                out.append(f"{n}: no breakdown below " + ", ".join(
                    f"{s.per_die[d].limit:.1f} V on {d}" for d in s.open_dies)
                    + ".")
        for (n, d), b3 in sorted(self.third.items()):
            b1 = self.first[(n, d)]
            if b1.kind == b3.kind == "bv" and abs(b3.bv - b1.bv) > measure.WALKOUT:
                out.append(f"{n} on {d}: walk-out, {b1.bv:.1f} V on the first "
                           f"sweep and {b3.bv:.1f} V on the third.")
        for (n, d), bh in sorted(self.hot.items()):
            b1 = self.first.get((n, d))
            if b1 and b1.kind == bh.kind == "bv" and bh.bv <= b1.bv:
                out.append(f"{n} on {d}: the knee does not move up at 85 °C "
                           f"({b1.bv:.1f} V to {bh.bv:.1f} V): not avalanche.")
        out += self.open_check()
        out += self.balance_check()
        return out

    def balance_check(self):
        """P1 and P5: the substrate (and ring) current returns the well
        current within measure.BALANCE once it is above 100 nA."""
        out, missing = [], set()
        for w in self.sweeps:
            if w.procedure not in ("P1", "P5") or not w.room \
                    or w.direction != "up":
                continue
            d = measure.balance(w)
            if d is None:
                if all(r["i_sub_a"] is None for r in w.rows):
                    missing.add(w.die)
            elif d > measure.BALANCE:
                out.append(f"{w.structure} on {w.die}, {w.procedure} sweep "
                           f"{w.sweep}: the returned current differs from "
                           f"the well current by up to {100 * d:.0f} %: "
                           "current leaves by another path.")
        out += [f"Substrate current not recorded on {d}: balance not "
                "checked there." for d in sorted(missing)]
        return out

    def open_check(self):
        """A reading counts only if ten times the OPEN current there."""
        opens = {w.die: w for w in self.sweeps if w.structure == "OPEN"
                 and w.procedure == "P1" and w.room and w.direction == "up"}
        out = [f"OPEN not measured on {d}: pad leakage not checked there."
               for d in self.dies if d not in opens]
        for (n, d), b in sorted(self.first.items()):
            if n == "OPEN" or b.kind != "bv" or d not in opens:
                continue
            i = measure.current_at(opens[d], b.bv)
            if i is not None and measure.OPEN_FACTOR * i > measure.BV_LEVEL:
                out.append(f"{n} on {d}: OPEN carries {i:.2g} A at "
                           f"{b.bv:.1f} V, more than a tenth of 1 µA.")
        return out


def v(x, bound=False):
    return "–" if x is None else ("> " if bound else "") + f"{x:.1f}"


def dies_md(r):
    """The outlier check by die, and the result without the outliers."""
    out = ["", "## Dies", "",
           "Median over the structures of the die's breakdown voltage over "
           "the median of all dies, flagged outside "
           f"1 ± {p1rules.DIE_BAND:g}.", "",
           "| Die | Factor | Structures | Flag |", "|---|---|---|---|"]
    out += [f"| {d} | {f:.2f} | {n} | "
            + ("outlier" if d in r.outliers else "–") + " |"
            for d, (f, n) in sorted(r.factors.items())] or \
        [f"| – | fewer than {p1rules.DIE_MIN} dies: not checked | | |"]
    w = r.without
    if w is None:
        return out
    out += ["", f"Without {', '.join(r.outliers)}: surface P-well "
            f"**{w.pwell or 'undecided'}**, deep P layer "
            f"**{w.deep or 'undecided'}**."]
    old = {(x["name"], x["family"]): x for x in r.rows}
    changed = [f"{x['name']} ({x['family']}): ratio {old[k]['ratio']} to "
               f"{x['ratio']}; absolute {old[k]['absolute']} to "
               f"{x['absolute']}"
               for x in w.rows for k in [(x["name"], x["family"])]
               if k in old and (old[k]["ratio"], old[k]["absolute"])
               != (x["ratio"], x["absolute"])]
    out.append(f"{len(changed)} rows change verdict without "
               f"{', '.join(r.outliers)}" + (":" if changed else "."))
    out += [f"- {c}" for c in changed]
    return out


def report(r):
    out = ["# Test die: measurements against predictions", "",
           f"{len(r.dies)} dies, {len(r.sweeps)} records read.", "",
           "## Decision", "",
           f"- Surface P-well: **{r.pwell or 'undecided'}**: {r.pwell_why}.",
           f"- Deep P layer: **{r.deep or 'undecided'}**: {r.deep_why}."]
    if r.forced:
        out.append(f"- Compared under **{r.forced}**, named by hand.")
    elif r.families:
        out.append(f"- Compared under: {', '.join(r.families)}.")
    out += ["", "Evidence:", ""] + [f"- {e}" for e in r.evidence]
    out += [f"- Stand-in: {n}" for n in r.data.notes]
    out += ["", "## Structures", "",
            "Breakdown voltage at 1 µA, first sweep at 25 °C, median over "
            "the dies. Ratio: to the reference on the same die, median over "
            "the dies.", "",
            "| Structure | Family | Median (V) | Dies | Spread (V) | Reference "
            "| Measured ratio | Predicted ratio | Ratio | Band (V) "
            "| Agreement range (V) | Absolute |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in r.rows:
        lo, hi = row["spread"]
        rng = row["range"]
        out.append("| " + " | ".join([
            row["name"], row["family"], v(row["median"], row["bound"]),
            str(row["n"]), f"{v(lo)} to {v(hi)}", row["ref"] or "–",
            "–" if row["m_ratio"] is None else
            ("> " if row["m_bound"] else "") + f"{row['m_ratio']:.2f}",
            "–" if row["p_ratio"] is None else f"{row['p_ratio']:.2f}",
            row["ratio"], f"{v(row['band'][0])} to {v(row['band'][1])}",
            "–" if rng is None else f"{v(rng[0])} to {v(rng[1])}",
            row["absolute"]]) + " |")
    if not r.rows:
        out.append("| – | No family selected: nothing compared. |"
                   + " |" * 10)
    out += dies_md(r)
    out += procs.markdown(r.other, r.families[0] if r.families else None)
    out += ["", "## Inconclusive items", ""]
    out += [f"- {i}" for i in r.issues] or ["- None."]
    out += ["", "## Files not used", ""]
    out += [f"- {u}" for u in r.unusable] or ["- None."]
    return "\n".join(out) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("measurements", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--family", choices=pd.families())
    ap.add_argument("--example", metavar="DIR")
    a = ap.parse_args(argv)
    if a.example:
        import synth
        synth.make(a.example, "BL", sweeps=3, extra=True)
        print(f"SYNTHETIC measurement set under BL written to {a.example}")
        return 0
    if not a.measurements:
        ap.error("MEASUREMENT_DIR is needed")
    if not pathlib.Path(a.measurements).is_dir():
        print(f"{a.measurements}: not a directory", file=sys.stderr)
        return 2
    r = Result(a.measurements, a.family)
    if r.errors:
        print("\n".join(r.errors), file=sys.stderr)
        return 2
    if not r.sweeps:
        print(f"{a.measurements}: no usable records", file=sys.stderr)
        return 2
    text = report(r)
    if a.out:
        pathlib.Path(a.out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
