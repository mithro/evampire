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
    assert nw6["ratio"] == "NT20 not measured on the same die"
    assert nw6["absolute"] == "in range"


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


@pytest.mark.parametrize("hyp,call", [("BL", "L"), ("BD", "D")])
def test_capacitance(tmp_path, hyp, call):
    """P2 on a uniform substrate (L) and with a buried heavy layer (D):
    the substrate doping within 5 % and the right call from both pairs."""
    _, r = run(tmp_path, hyp, dies=2, extra=True)
    assert r.cap["call"] == call, r.cap["why"]
    assert len(r.cap["pairs"]) == 2 and not r.cap["issues"]
    for row in r.cap["pairs"]:
        assert row["call"] == call and row["v"] == 10
        assert abs(row["n_sub"] / rules.SUB_NOMINAL - 1) < 0.05, row
        assert abs(row["cp0"] * 1e6 / synth.ph.NW_CP - 1) < 0.01


def test_capacitance_profile():
    """The doping profile of the synthetic junction itself: flat on the
    uniform substrate, and rising at the buried layer."""
    vs = [0.25 * k for k in range(41)]
    for layer in (False, True):
        w = synth.depletion(layer, tuple(vs))
        prof = cv.profile(vs, [synth.ph.EPS / w[v] for v in vs])
        shallow = [n for v, _, n in prof if v <= 1.5]
        assert all(abs(n / rules.SUB_NOMINAL - 1) < 0.05 for n in shallow)
        assert (max(n for *_, n in prof) > 3 * rules.SUB_NOMINAL) == layer


def test_layer_rule():
    assert rules.layer_rule(5) is None          # L and D too close
    lo, d, thr = rules.layer_rule(10)
    assert lo < thr < d and rules.layer_bias(12) == 10
    assert rules.layer_bias(8) == 7 and rules.layer_bias(6) is None


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
