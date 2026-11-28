"""Self-test of analyse.py on synthetic measurement sets.

    uv run --with pytest pytest docs/high-voltage/test-die/test_analyse.py

Each test writes SYNTHETIC records with synth.py, ideal diode sweeps at
the predicted breakdown voltage of one process times a factor, with a
die-to-die spread from a fixed seed, and checks what analyse.py makes of
them: the decision, the extracted voltages, the verdicts and the edge
cases of method.rst.

SPDX-License-Identifier: Apache-2.0
"""

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analyse  # noqa: E402
import cv  # noqa: E402
import p1rules  # noqa: E402
import rules  # noqa: E402
import synth  # noqa: E402

HYPOTHESES = ["AL", "AnL", "AnD", "BL", "BD"]


def run(tmp_path, hyp, **kw):
    truth = synth.make(tmp_path / "m", hyp, **kw)
    return truth, analyse.Result(tmp_path / "m", kw.pop("family", None))


@pytest.mark.parametrize("hyp", HYPOTHESES)
def test_decision_and_agreement(tmp_path, hyp):
    truth, r = run(tmp_path, hyp)
    assert not r.errors and not r.unusable
    assert r.pwell == hyp[:-1], r.pwell_why
    # under A no breakdown voltage answers the deep-layer question
    assert r.deep == (None if hyp[:-1] == "A" else hyp[-1]), r.deep_why
    for (st, die), bv in truth.items():
        b = r.first[(st, die)]
        if bv is None:
            assert b.kind == "none"
        else:
            assert b.kind == "bv" and abs(b.bv - bv) <= synth.STEP, (st, die)
    rows = [row for row in r.rows if row["range"] and not row["bound"]]
    assert len(rows) > 50
    for row in rows:
        assert row["absolute"] == "in range", row
        assert row["ratio"] != "disagrees", row


@pytest.mark.parametrize("hyp", ["AL", "BL", "BD"])
def test_out_of_range_at_one_and_a_half(tmp_path, hyp):
    _, r = run(tmp_path, hyp, factor=1.5)
    r = analyse.Result(tmp_path / "m", hyp)      # the family named by hand
    rows = [row for row in r.rows if row["range"]]
    above = 0
    for row in rows:
        hi = row["range"][1]
        if row["median"] > hi:
            assert row["absolute"].startswith("above"), row
            above += 1
        elif not row["bound"]:
            assert row["absolute"] == "in range", row
        if row["ratio"] not in ("reference",):
            assert row["ratio"] != "disagrees", row  # ratios cancel a factor
    assert above >= 0.8 * len(rows)
    named = {row["name"]: row for row in r.rows}
    assert named["NT5"]["absolute"].startswith("above")


def test_edge_cases(tmp_path):
    edits = {("NT5", 2): "short", ("NR4S", None): "none",
             ("NT20", None): "drop"}
    _, r = run(tmp_path, "BL", edits=edits)
    assert (r.pwell, r.deep) == ("B", "L")
    nt5 = r.summ["NT5"]
    assert nt5.shorts == ["SYN2"] and nt5.n == 4
    assert any(i.startswith("NT5: short") for i in r.issues)
    nr4s = {row["name"]: row for row in r.rows}["NR4S"]
    assert nr4s["bound"] and nr4s["absolute"].startswith(
        "above (no breakdown below 150.0 V)")
    assert any(i.startswith("NR4S: no breakdown below 150.0 V")
               for i in r.issues)
    assert "NT20" not in r.summ
    nw6 = {row["name"]: row for row in r.rows}["NW6"]
    # the copies of NT20 stand in for it as the reference
    assert nw6["ref"] == "NT20 (NT20b, NT20c stand in)"
    assert nw6["ratio"] == "agrees" and nw6["absolute"] == "in range"
    assert any(i.startswith("NT20: no breakdown on any die; NT20b, NT20c "
                            "stand in") for i in r.issues)


def test_single_die(tmp_path):
    _, r = run(tmp_path, "BD", dies=1)
    assert (r.pwell, r.deep) == ("B", "D")
    assert all(row["n"] == 1 for row in r.rows)
    assert any("at least 5" in i for i in r.issues)


def test_walk_out_and_temperature(tmp_path):
    _, r = run(tmp_path, "BL", dies=2, sweeps=3, extra=True)
    assert not any("walk-out" in i for i in r.issues)    # 0.2 V: one step
    assert not any("85 °C" in i for i in r.issues)       # the knee moved up
    assert {row["name"] for row in r.other["P5"]} >= {"NR1S2", "NR1S3"}


def test_cli_report_and_errors(tmp_path, capsys):
    synth.make(tmp_path / "m", "BL", dies=2)
    out = tmp_path / "report.md"
    assert analyse.main([str(tmp_path / "m"), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "Surface P-well: **B**" in text and "| NW6 | BL |" in text
    bad = tmp_path / "m" / "SYN1.NT1.P1.1.csv"
    lines = bad.read_text(encoding="utf-8").splitlines()
    lines[3] = lines[3].replace("SYN1,NT1,P1,1,up,25,1", "SYN1,NT1,P1,1,up,25,x")
    bad.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert analyse.main([str(tmp_path / "m")]) == 2
    err = capsys.readouterr().err
    assert "SYN1.NT1.P1.1.csv: row 4: column v_well_v is not a number" in err


def test_example(tmp_path):
    assert analyse.main(["--example", str(tmp_path / "ex")]) == 0
    assert "SYNTHETIC" in (tmp_path / "ex" / "README.txt").read_text()
    r = analyse.Result(tmp_path / "ex")
    assert (r.pwell, r.deep, r.families) == ("B", "L", ["BL"])


@pytest.mark.parametrize("factor", [0.7, 1.5])
@pytest.mark.parametrize("hyp", HYPOTHESES)
def test_scaled_decision(tmp_path, hyp, factor):
    """Every prediction scaled by one factor: the pattern still decides,
    and under A the capacitance answers the deep-layer question."""
    _, r = run(tmp_path, hyp, factor=factor, dies=3, extra=True)
    assert r.pwell == hyp[:-1], r.pwell_why
    assert r.deep == hyp[-1], r.deep_why
    assert r.families == [hyp]


@pytest.mark.parametrize("hyp,call,s", [("BL", "L", 0.827), ("BD", "D", 1.023)])
def test_capacitance(tmp_path, hyp, call, s):
    """P2 on the simulated curves: s at 10 V as simulated, the right call
    from both pairs, and the doping that the same reduction finds on the
    simulated curve."""
    _, r = run(tmp_path, hyp, dies=2, extra=True)
    assert r.cap["call"] == call, r.cap["why"]
    assert len(r.cap["pairs"]) == 2 and not r.cap["issues"]
    for row in r.cap["pairs"]:
        assert row["call"] == call and row["v"] == 10
        assert abs(row["s"] - s) < 0.005, row
        assert abs(row["n_sub"] / cv.reference_doping(call) - 1) < 0.01, row
        assert abs(row["cp0"] * 1e6 / synth.ph.NW_CP - 1) < 0.01
    assert abs(r.cap["dope"] - 1) < 0.01


def test_capacitance_profile():
    """cv.profile on one-sided junctions in closed form: the doping of a
    uniform substrate, and a rise at a step to three times it 1.5 um
    down."""
    n, d, q, eps = rules.SUB_NOMINAL, 1.5e-4, synth.ph.Q, synth.ph.EPS
    vs = [0.25 * k for k in range(41)]
    for step in (False, True):
        def width(v):
            w = (2 * eps * (v + 0.7) / (q * n)) ** 0.5
            if step and w > d:      # V + Vbi = q/(2 eps) (N d^2 + 3N (W^2 - d^2))
                w = ((2 * eps * (v + 0.7) / q - n * d * d) / (3 * n)
                     + d * d) ** 0.5
            return w
        prof = cv.profile(vs, [eps / width(v) for v in vs])
        shallow = [x for v, _, x in prof if v <= 1.5]
        assert all(abs(x / n - 1) < 0.05 for x in shallow)
        assert (max(x for *_, x in prof) > 2 * n) == step


def test_capacitance_neither(tmp_path):
    """A ratio that fits neither simulated curve is called neither, and
    the deep layer then rests on the breakdown ratios alone."""
    lo, thr, hi = rules.layer_window(10)
    assert (round(lo, 3), round(thr, 3), round(hi, 3)) == (0.777, 0.925, 1.073)
    assert [rules.layer_call(x, 10) for x in (0.70, 0.83, 0.95, 1.2)] == [
        "neither", "L", "D", "neither"]
    synth.make(tmp_path / "m", "BL", dies=2, extra=True)
    for f in (tmp_path / "m").glob("*.P2.1.csv"):
        st = f.name.split(".")[1]
        rows = synth.cv_rows(st, "L")
        for row in rows:     # an abrupt junction: s = 0.67 at 10 V
            v = row["v_well_v"]
            area = 0 if st == "OPEN" else synth.ph.octagon(
                synth.pd.STRUCTS[st]["half"], synth.pd.STRUCTS[st]["corner"])[0]
            row["c_f"] += area * 1e-8 * cv.model(0) * (
                (1 + v / 0.7) ** -0.5 - cv.model(v) / cv.model(0)
                * cv.sim_ratio("L", v))
        synth.write(tmp_path / "m", f.name.split(".")[0], st, "P2", 1, rows)
    r = analyse.Result(tmp_path / "m")
    assert r.cap["call"] is None and "neither" in r.cap["why"], r.cap["why"]
    assert all(row["call"] == "neither" for row in r.cap["pairs"])
    assert (r.pwell, r.deep) == ("B", "L"), r.deep_why


def test_layer_rule():
    """Thresholds half-way between the recorded curves, normalised to 0 V;
    5 V is the lowest bias whose two values lie 0.05 apart."""
    assert rules.layer_rule(3) is None          # L and D too close
    lo, d, thr = rules.layer_rule(10)
    assert lo < thr < d and rules.layer_bias(12) == 10
    assert [round(rules.layer_rule(v)[2], 3) for v in (5, 7, 10)] == [
        0.93, 0.925, 0.925]
    assert rules.layer_bias(8) == 7 and rules.layer_bias(6) == 5
    assert rules.layer_bias(4) is None


def test_ring_and_punch_through(tmp_path):
    """P3 and P5 recovered from synthetic sweeps, and the verdicts."""
    _, r = run(tmp_path, "BL", dies=2, extra=True)
    p3 = {row["name"]: row for row in r.other["P3"]}
    p5 = {row["name"]: row for row in r.other["P5"]}
    for name in ("NR4S", "NR1S2", "NR1S3", "NR1S5"):
        on = rules.ring_prediction(name, "BL")[0]
        assert abs(p3[name]["onset"] - on) <= synth.STEP, name
        assert p3[name]["verdict"] == "agrees"
        pt = rules.p5_entry(name, "BL")["punch_through_v"]
        assert abs(p5[name]["pt"] - pt) <= synth.STEP, name
        assert p5[name]["verdict"] == "agrees"
    assert p5["NR1S8"]["pt"] is None
    assert p5["NR1S8"]["verdict"].startswith("agrees")
    assert all(row["step_verdict"] == "agrees" for row in r.other["P3"])
    # twice the predicted voltage at 3 um: about 0.8 um of gap too wide
    v = rules.pt_verdict("NR1S3", "BL", "P5", 26.4, 70)
    assert v.startswith("disagrees: equivalent gap +")
    assert rules.pt_verdict("NR1S3", "BL", "P5", None, 40).startswith(
        "disagrees: none by 40.0 V")
    assert rules.pt_verdict("NR1S3", "BL", "P5", None, 12).startswith(
        "inconclusive")
    assert rules.pt_range("NR1S2", "AnL", "P5") == rules.pt_range(
        "NR1S2", "AL", "P5")


def test_current_balance(tmp_path):
    _, r = run(tmp_path, "BL", dies=2, edits={("NT5", 1): "leak"})
    bad = [i for i in r.issues if "returned current" in i]
    assert len(bad) == 1 and bad[0].startswith("NT5 on SYN1, P1 sweep 1")
    assert "30 %" in bad[0]


def test_gated_diode(tmp_path):
    _, r = run(tmp_path, "BL", dies=2, extra=True)
    rows = {(row["name"], row["plate"]): row for row in r.other["P4"]}
    assert rows[("NGM1", 0.0)]["verdict"] == "in range"
    assert rows[("NGM1", 0.0)]["ratio"] == "agrees"
    assert rows[("NGM1", 10.0)]["verdict"] == "no prediction"
    dop = {st: n for st, n, _ in r.other["P4doping"]}
    for st in ("NGM1", "NGP4", "NAGM1"):
        assert abs(dop[st] / rules.SUB_NOMINAL - 1) < 0.05, st
    _, r = run(tmp_path / "a", "AL", dies=1, extra=True)
    p4a = [row for row in r.other["P4a"] if row["name"] == "NGM1"]
    assert p4a and all(row["vt"] is None and row["estimate"] is None
                       for row in p4a)


def test_ratio_lower_bound(tmp_path):
    """A structure without breakdown by 150 V gives a lower bound on its
    ratio, with a verdict that a lower bound allows."""
    _, r = run(tmp_path, "BL", factor=1.6)
    rows = {row["name"]: row for row in r.rows}
    nr4s = rows["NR4S"]
    assert nr4s["bound"] and nr4s["m_bound"] and nr4s["ref"] == "NT20"
    assert abs(nr4s["m_ratio"] - 150 / r.summ["NT20"].median) < 0.03
    assert nr4s["ratio"] == "agrees: the lower bound is within the range"
    assert "| NT20 | > 1.38 | 1.59 |" in analyse.report(r)
    v = p1rules.ratio_verdict
    assert v(2.0, 1.5, True).startswith("disagrees")
    assert v(1.0, 1.5, True).startswith("inconclusive")
    assert v(1.4, 1.5, False) == "agrees"
    assert p1rules.bound_median([(1.0, False), (1.2, False), (3.0, True)]) \
        == (1.2, False)
    assert p1rules.bound_median([(1.0, False), (1.1, True), (3.0, True)]) \
        == (1.1, True)


def add_die(src, die, dst):
    """Copy the records of SYN1 in src into dst as die `die`."""
    for f in pathlib.Path(src).glob("SYN1.*.csv"):
        lines = f.read_text(encoding="utf-8").splitlines()
        body = [die + line[len("SYN1"):] for line in lines[1:]]
        (pathlib.Path(dst) / f.name.replace("SYN1", die, 1)).write_text(
            "\n".join([lines[0]] + body) + "\n", encoding="utf-8")


def test_outlier_die(tmp_path):
    """One die at half the value of five others is flagged, the medians
    keep it, and the report repeats the decision without it."""
    _, r = run(tmp_path, "BL")
    assert not r.outliers and all(abs(f - 1) < 0.05
                                  for f, _ in r.factors.values())
    synth.make(tmp_path / "o", "BL", factor=0.5, dies=1, seed=7)
    add_die(tmp_path / "o", "SYN6", tmp_path / "m")
    r = analyse.Result(tmp_path / "m")
    assert r.outliers == ["SYN6"] and abs(r.factors["SYN6"][0] - 0.5) < 0.03
    assert any(i.startswith("SYN6: its structures lie at 0.5") for i in r.issues)
    assert (r.pwell, r.deep) == ("B", "L")
    assert r.without.dies == ["SYN1", "SYN2", "SYN3", "SYN4", "SYN5"]
    assert (r.without.pwell, r.without.deep) == ("B", "L")
    text = analyse.report(r)
    assert "| SYN6 | 0.50 |" in text and "Without SYN6: surface P-well **B**" in text
    _, r2 = run(tmp_path / "two", "BL", dies=2)
    assert r2.factors == {} and not r2.outliers


def test_reference_stand_ins(tmp_path):
    """References lost on every die are replaced by structures with the
    same prediction, and the replacement is named."""
    assert p1rules.tiers(("NT20", "NT20b", "NT20c")) == (("NT20L", "NT20V"),
                                                          ("NT5",))
    assert p1rules.tiers(("NA0p6", "NA0p6b")) == (("NA0p6T10",),)
    assert p1rules.tiers(("DT20",)) == (("DT20b",), ("DT2p6",))
    assert p1rules.tiers(("NW0", "NW0b")) == ()          # only under A
    assert p1rules.tiers(("NW0", "NW0b"), "A")[0] == ("NT20", "NT20b", "NT20c")
    assert not p1rules.same_prediction("NT20", "NT1")
    lost = {(n, None): "short" for n in ("NT20", "NT20b", "NT20c")}
    _, r = run(tmp_path / "b", "BL", edits=lost)
    assert (r.pwell, r.deep) == ("B", "L"), (r.pwell_why, r.deep_why)
    assert any("NT20L, NT20V stand in" in i for i in r.issues)
    rows = [x for x in r.rows if x["ratio"] not in ("reference", "not simulated",
                                                   "no predicted ratio")
            and not x["ratio"].startswith("across")]
    assert len(rows) > 40 and all("disagrees" not in x["ratio"] for x in rows)
    assert all(x["ref"].endswith("stand in)") for x in rows if
               x["ref"].startswith("NT20"))
    more = {**lost, **{(n, None): "short" for n in ("NT20L", "NT20V", "NT5")}}
    _, r = run(tmp_path / "c", "BL", edits=more)
    assert r.pwell is None and any("no stand-in was measured" in i
                                   for i in r.issues)
    g3 = {(n, None): "short" for n in ("NA0p6", "NA0p6b")}
    _, r = run(tmp_path / "an", "AnL", edits=g3)
    assert r.pwell == "An" and any("NA0p6T10 stand in" in i for i in r.issues)
    dt = {(n, None): "short" for n in ("DT20", "DT20b")}
    _, r = run(tmp_path / "d", "BL", edits=dt)
    dc0 = {x["name"]: x for x in r.rows}["DC0"]
    assert dc0["ref"] == "DT20 (DT2p6 stand in)" and dc0["m_ratio"]


def test_punch_through_doping(tmp_path):
    """P5 read at the doping P2 gives; over the simulated range without P2;
    the scaling reproduces NR3_2 at the three simulated dopings."""
    k = rules.gap_fit("BL", "P3")[0]
    v0 = dict(rules.doping_points())[1.0]
    for f, v in rules.doping_points():
        assert abs(rules.pt_scaled(v0, f, k) / v - 1) < 0.02, (f, v)
    assert rules.GAP_TOL == 0.6
    _, lo, hi = rules.pt_range("NR1S2", "BL", "P5")
    assert (round(lo, 1), round(hi, 1)) == (0.7, 9.3)
    _, r = run(tmp_path / "lo", "BL", dies=2, extra=True, dope=0.6)
    assert abs(r.cap["dope"] - 0.6) < 0.02
    p5 = {row["name"]: row for row in r.other["P5"]}
    for name in ("NR1S2", "NR1S3", "NR1S5"):
        assert p5[name]["verdict"] == "agrees", (name, p5[name])
    # the nominal range alone would reject the wide gap
    assert rules.pt_verdict("NR1S5", "BL", "P5", p5["NR1S5"]["pt"], 150
                            ).startswith("disagrees")
    for f in (tmp_path / "lo" / "m").glob("*.P2.1.csv"):
        f.unlink()
    r = analyse.Result(tmp_path / "lo" / "m")
    assert r.cap["dope"] is None
    assert all(row["verdict"].startswith("agrees") for row in r.other["P5"])


def test_model_check_records():
    """Each value of model_checks.json that names a record equals it; set
    GF180_TCAD to a gf180-tcad checkout to check against the records."""
    import json
    import os
    import pred_extra as px
    rows = px.CHECKS["one_sided"]["rows"]
    assert [r["record"] is None for r in rows] == [False, False, True, False]
    root = pathlib.Path(os.environ.get("GF180_TCAD", "/nonexistent"))
    rec = root / "results" / "hv-junction"
    if not rec.is_dir():
        pytest.skip("GF180_TCAD names no gf180-tcad checkout")
    diodes = json.loads((rec / "diodes.json").read_text())["diodes"]
    for r in rows:
        if r["record"]:
            key = r["record"].split("key ")[1]
            assert round(diodes[key]["bv_v"], 2) == r["integral_v"]
    radius = json.loads((rec / "radius.json").read_text())["cases"]
    for c in px.CHECKS["corner_radius"]["cases"]:
        if c["radius_um"] < 8:
            case = f"NC0r{c['radius_um']:.1f}|{c['process']}|corner"
            assert round(radius[case]["bv_v"], 1) == c["volts"], case
    cap = json.loads((rec / "capacitance.json").read_text())
    mc = px.CHECKS["capacitance"]
    assert mc["volts"] == cap["bias_v"]
    assert mc["without_layer"] == cap["L"]["over_model"]
    assert mc["with_layer"] == cap["D"]["over_model"]
    main = json.loads((rec / "main.json").read_text())["cases"]
    assert round(main["NC0|BL|corner"]["reached_v"], 1) == \
        px.CHECKS["corner"]["last_volts"]
