"""Seal ring, fill and wafer.space precheck for the high-voltage test die.

    uv run python silicon/hvtest/flow.py RAW.gds WORKDIR [--skip-precheck]

RAW.gds is the layout build.py writes. All three steps run inside the wafer.space precheck
container, which holds KLayout and the gf180mcuD PDK: the PDK's seal-ring script, its fill
script, then precheck.py for slot 0p5x0p5. WORKDIR receives ring.gds, filled.gds, the
final hvtest.oas and the precheck run directory; every step logs to WORKDIR/<step>.log.
"""

import os
import pathlib
import shutil
import subprocess
import sys

IMAGE = "ghcr.io/wafer-space/gf180mcu-precheck:latest"
TOP = "hvtest"
SLOT, DIE_W, DIE_H = "0p5x0p5", 1936, 2531
TECH = "$PDK_ROOT/$PDK/libs.tech/klayout/tech"


def container(work, name, script):
    """Run a shell script in the precheck image with WORKDIR at /data; log to <name>.log."""
    own = f"chown -R {os.getuid()}:{os.getgid()} /data"
    cmd = ["docker", "run", "--rm", "--network=none", "-v", f"{work}:/data", IMAGE,
           "sh", "-c", f"({script}); rc=$?; {own}; exit $rc"]  # fmt: skip
    with open(work / f"{name}.log", "wb") as log:
        rc = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
    print(f"{name}: exit {rc} ({work / (name + '.log')})", flush=True)
    return rc


def main(argv):
    raw, work = pathlib.Path(argv[0]).resolve(), pathlib.Path(argv[1]).resolve()
    work.mkdir(parents=True, exist_ok=True)
    shutil.copy(raw, work / "raw.gds")
    steps = [
        ("sealring", f"python3 {TECH}/scripts/sealring.py --input /data/raw.gds "
                     f"--output /data/ring.gds --die-width {DIE_W} --die-height {DIE_H}"),
        # Metal4 fill is allowed under Metal5: the pads cover 15 % of the die, and without
        # dummy Metal4 beneath them the Metal4 density is 28 % against the 30 % minimum
        ("fill", f"klayout -b -zz -r {TECH}/scripts/fill_all.rb -rd input=/data/ring.gds "
                 "-rd output=/data/filled.gds -rd Metal4_ignore_active=true"),
    ]  # fmt: skip
    if "--skip-precheck" not in argv:
        steps.append(("precheck",
                      f"rm -rf /data/runs/pc && python precheck.py --input /data/filled.gds --top {TOP} "
                      f"--slot {SLOT} --id G803HVT1 --dir /data --run-tag pc --threads 1 "
                      "--workers 16 --output /data/hvtest.oas"))  # fmt: skip
    for name, script in steps:
        rc = container(work, name, script)
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
