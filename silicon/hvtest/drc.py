"""Run the gf180mcuD KLayout DRC deck (as the precheck does) on a GDS, in the precheck image.

    uv run python silicon/hvtest/drc.py IN.gds WORKDIR [TOPCELL]

Writes WORKDIR/drc.lyrdb and WORKDIR/drc.log, then prints the violation count per rule.
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys
from collections import Counter

IMAGE = "ghcr.io/wafer-space/gf180mcu-precheck:latest"


def main(argv):
    src, work = pathlib.Path(argv[0]).resolve(), pathlib.Path(argv[1]).resolve()
    top = argv[2] if len(argv) > 2 else "hvtest"
    work.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, work / "in.gds")
    deck = "$PDK_ROOT/$PDK/libs.tech/klayout/tech/drc/gf180mcu.drc"
    script = (f"klayout -b -zz -r {deck} -rd input=/data/in.gds -rd topcell={top} "
              "-rd report=/data/drc.lyrdb -rd decks=all,-antenna,-density,-cup "
              "-rd variant=gf180mcuD -rd workers=16")  # fmt: skip
    own = f"chown -R {os.getuid()}:{os.getgid()} /data"
    with open(work / "drc.log", "wb") as log:
        rc = subprocess.run(["docker", "run", "--rm", "--network=none", "-v", f"{work}:/data",
                             IMAGE, "sh", "-c", f"({script}); rc=$?; {own}; exit $rc"],
                            stdout=log, stderr=subprocess.STDOUT).returncode  # fmt: skip
    report = work / "drc.lyrdb"
    if not report.is_file():
        print(f"no report (exit {rc}); see {work / 'drc.log'}")
        return 1
    text = report.read_text()
    counts = Counter(re.findall(r"<item>\s*<tags/>\s*<category>'?([^<']+)'?</category>", text))
    if not counts:
        counts = Counter(re.findall(r"<category>'?([^<']+)'?</category>\s*<cell>", text))
    for rule, n in sorted(counts.items()):
        print(f"{rule}: {n}")
    print(f"total {sum(counts.values())} violations in {len(counts)} rules")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
