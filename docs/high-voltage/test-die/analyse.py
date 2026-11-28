"""Compare measurements of the test die with the simulated predictions.

    uv run python docs/high-voltage/test-die/analyse.py MEASUREMENT_DIR [--out REPORT.md] [--family BL]
    uv run python docs/high-voltage/test-die/analyse.py --example DIR

MEASUREMENT_DIR holds the CSV records of method.rst (one file per sweep,
named DIE.STRUCTURE.PROCEDURE.SWEEP.csv), in any sub-folders. The script
extracts the breakdown voltage of every P1 sweep, takes the median over
the dies of the first sweep at 25 C, applies the process decision of
method.rst, and compares each structure with predictions.json under the
family the decision selects, by ratio and by agreement range. It reduces
P3 and P5 as well, checks P2 and P4 records, and lists what makes a
result inconclusive. --family compares under a family named by hand
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
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import decide  # noqa: E402
import measure  # noqa: E402
import pred_data as pd  # noqa: E402
import pred_extra  # noqa: E402


class Result:
    """Everything the report holds, for the report and for the tests."""

    def __init__(self, top, family=None):
        sweeps, self.errors = measure.read_dir(top)
        self.unusable = []
        known = []
        for w in sweeps:
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
        self.pwell, self.pwell_why = decide.pwell(self.data, self.evidence)
        self.deep, self.deep_why = decide.deep(self.data, self.pwell,
                                               self.evidence)
        self.forced = family
        self.families = [family] if family else decide.families(self.pwell,
                                                                self.deep)
        order = [s["name"] for s in pd.MAN["sites"]
                 if s["name"] in self.summ and s["name"] != "OPEN"]
        self.rows = [decide.compare(self.data, n, f)
                     for n in order for f in self.families]
        self.other = self.procedures()
        self.issues = self.inconclusive()

    def procedures(self):
        """Rows of P3, P5 and the second part of P4; P2 and the first part
        of P4 are listed as checked but not reduced."""
        p3, p4, p5, checked = {}, {}, {}, {}
        fam = self.families[0] if self.families else None
        for w in sorted(self.sweeps, key=lambda w: w.sweep):
            key = w.structure
            if w.procedure == "P3" and w.direction == "up":
                p3.setdefault(key, {}).setdefault(w.die, measure.ring_onset(w))
            elif w.procedure == "P5" and w.direction == "up":
                p5.setdefault(key, {}).setdefault(w.die, measure.punch(w))
            elif w.procedure == "P4" and measure.gated_part(w) == 2:
                plate = statistics.median(w.col("v_aux_v"))
                b = measure.breakdown(w)
                if b.kind == "bv":
                    p4.setdefault((key, plate), []).append(b.bv)
            elif w.procedure in ("P2", "P4"):
                bad = measure.capacitance_checks(w) if w.procedure == "P2" else 0
                c = checked.setdefault((key, w.procedure), [0, 0])
                c[0] += 1
                c[1] += bad
        out = {"P3": [], "P5": [], "P4": [], "checked": []}
        for st, by in p3.items():
            curve = (pd.entry(st, fam) or {}).get("ring_v") if fam else None
            pred = measure.linear_crossing(
                [c[0] for c in curve], [c[1] for c in curve],
                measure.RING_LEVEL) if curve else None
            ons = [x[0] for x in by.values() if x[0] is not None]
            out["P3"].append((st, len(by), med(ons), len(ons), pred,
                              med([x[1] for x in by.values()])))
        for st, by in p5.items():
            pts = [x[0] for x in by.values() if x[0] is not None]
            tops = [x[1] for x in by.values() if x[0] is None]
            mech = sorted(x[2] for x in by.values())
            e = pred_extra.P5.get(st, {}).get(fam) if fam else None
            out["P5"].append((st, len(by), med(pts), len(pts),
                              max(tops) if tops else None,
                              mech[len(mech) // 2], e))
        for (st, plate), bvs in sorted(p4.items()):
            out["P4"].append((st, plate, med(bvs), len(bvs)))
        for (st, proc), (n, bad) in sorted(checked.items()):
            out["checked"].append(
                f"{st}: {n} {proc} records read and not reduced"
                + (f"; {bad} rows with a dissipation factor above 0.1"
                   if bad else ""))
        return out

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
            "–" if row["m_ratio"] is None else f"{row['m_ratio']:.2f}",
            "–" if row["p_ratio"] is None else f"{row['p_ratio']:.2f}",
            row["ratio"], f"{v(row['band'][0])} to {v(row['band'][1])}",
            "–" if rng is None else f"{v(rng[0])} to {v(rng[1])}",
            row["absolute"]]) + " |")
    if not r.rows:
        out.append("| – | No family selected: nothing compared. |"
                   + " |" * 10)
    out += procedures_md(r)
    out += ["", "## Inconclusive items", ""]
    out += [f"- {i}" for i in r.issues] or ["- None."]
    out += ["", "## Files not used", ""]
    out += [f"- {u}" for u in r.unusable] or ["- None."]
    return "\n".join(out) + "\n"


def procedures_md(r):
    o = r.other
    fam = r.families[0] if r.families else "no family"
    out = ["", "## Other procedures", "",
           "No agreement rule is documented for P3, P4 and P5, so the "
           f"prediction under {fam} stands beside the measured median.", ""]
    if o["P3"]:
        out += ["| Structure | Dies | P3 onset at 1 V (V) | Dies with an onset "
                "| Predicted onset (V) | Step at the top (V) |",
                "|---|---|---|---|---|---|"]
        out += [f"| {st} | {n} | {v(on)} | {k} | {v(pr)} | {v(step)} |"
                for st, n, on, k, pr, step in o["P3"]]
        out.append("")
    if o["P5"]:
        out += ["| Structure | Dies | P5 punch-through at 1 nA (V) "
                "| Dies with one | Predicted (V) | Mechanism at the end |",
                "|---|---|---|---|---|---|"]
        for st, n, pt, k, top, mech, e in o["P5"]:
            pr = "–" if not e else (v(e["punch_through_v"])
                                    if e["punch_through_v"] is not None
                                    else f"> {e['reached_v']:.1f}")
            got = v(pt) if pt is not None else f"> {top:.1f}"
            out.append(f"| {st} | {n} | {got} | {k} | {pr} | {mech} |")
        out.append("")
    if o["P4"]:
        out += ["| Structure | P4 plate (V) | Breakdown at 1 µA, median (V) "
                "| Dies |", "|---|---|---|---|"]
        out += [f"| {st} | {plate:g} | {v(bv)} | {n} |"
                for st, plate, bv, n in o["P4"]]
        out.append("")
    out += [f"- {c}" for c in o["checked"]]
    return out


def med(xs):
    return statistics.median(xs) if xs else None


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
