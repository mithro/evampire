# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy>=1.26"]
# ///
"""Check that the cgroup memory cap really stops a runaway simulation.

Runs a trivial netlist whose DC sweep stores ~0.5 GB of vectors through
run.py's ngspice_in_cgroup() with a 256 MiB cap, and expects the run to be
OOM-killed inside its container (not on the host).

Run with:  uv run sim/diode_stack/test_cgroup.py
"""

import os
import sys
from pathlib import Path

os.environ["SIM_MEMORY"] = "256m"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run  # noqa: E402

cir = run.RESULTS / "cgroup_oom_test.cir"
run.RESULTS.mkdir(exist_ok=True)
(run.RESULTS / ".spiceinit").write_text("set ngbehavior=hsa\n")
cir.write_text("* memory hog: 2e7-point DC sweep, vectors kept in memory\n"
               "V1 a 0 0\nR1 a b 1k\nR2 b 0 1k\n"
               ".dc V1 0 1 5e-8\n.control\nrun\nquit\n.endc\n.end\n")
try:
    run.ngspice_in_cgroup(cir)
except SystemExit as e:
    msg = str(e)
    print(msg)
    if "rc=137" in msg:
        print("PASS: simulation was killed by its 256m cgroup limit")
        sys.exit(0)
    sys.exit("FAIL: run failed, but not by the memory limit")
sys.exit("FAIL: simulation finished; the memory limit did not stop it")
