"""Write the structure list as JSON, for the TCAD predictions in mithro/gf180-tcad.

    uv run --with klayout python silicon/hvtest/export.py silicon/hvtest/structures.json
"""

import json
import sys

import junction
import structures

if __name__ == "__main__":
    out = {name: {**junction.DEFAULTS, **params} for name, params in structures.SITES + structures.LARGE}
    json.dump(out, open(sys.argv[1], "w"), indent=1, sort_keys=True)
    print(f"{len(out)} structures")
