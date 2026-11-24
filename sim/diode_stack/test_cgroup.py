# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Check that the cgroup memory cap really stops a runaway simulation.

Runs a trivial netlist whose DC sweep stores about 0.6 GB of vectors through
run.py's ngspice_in_cgroup(), twice:

1. with a 2 GiB cap, where it must finish (the control);
2. with a 256 MiB cap, where it must be killed inside its container.

The control shows that the kill in step 2 comes from the cap, not from
some other fault in the netlist or the container.

Run with:  uv run sim/diode_stack/test_cgroup.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402

cir = run.RESULTS / "cgroup_oom_test.cir"
run.RESULTS.mkdir(exist_ok=True)
(run.RESULTS / ".spiceinit").write_text("set ngbehavior=hsa\nset ng_nomodcheck\n")
cir.write_text("* memory hog: 2e7-point DC sweep, vectors kept in memory\n"
               "V1 a 0 0\nR1 a b 1k\nR2 b 0 1k\n"
               ".dc V1 0 1 5e-8\n.control\nrun\nquit\n.endc\n.end\n")


def attempt(cap: str) -> str | None:
    """Run the hog under `cap`; return None if it finished, else the error."""
    run.SIM_MEMORY = cap
    try:
        run.ngspice_in_cgroup(cir)
    except SystemExit as e:
        return str(e)
    return None


control = attempt("2g")
if control is not None:
    sys.exit(f"FAIL: the control run under 2g did not finish: {control}")
print("control: finished under a 2g limit")
capped = attempt("256m")
if capped is None:
    sys.exit("FAIL: simulation finished; the 256m limit did not stop it")
print(capped)
if "rc=137" not in capped:
    sys.exit("FAIL: run failed, but not by the memory limit")
print("PASS: the same simulation finished under 2g and was killed under 256m")
