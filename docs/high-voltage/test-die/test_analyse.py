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
    assert {row[0] for row in r.other["P5"]} >= {"NR1S2", "NR1S3"}
    p5 = {row[0]: row for row in r.other["P5"]}["NR1S2"]
    assert abs(p5[2] - p5[6]["punch_through_v"]) <= synth.STEP


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
