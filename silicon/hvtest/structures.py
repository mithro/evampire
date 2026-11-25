"""The list of test structures on the die: (name, junction parameters)."""

SITES = [
    ("NWR4", {"rings": [[2.0, 2.0], [2.5, 2.0], [3.0, 2.0], [3.5, 2.0]], "term": 30.0, "sense": True}),
    ("GP", {"plates": {"poly": 3.0}, "gate": True}),
    ("GM1", {"plates": {"m1": 6.0}, "gate": True}),
    ("GM2", {"plates": {"m2": 6.0}, "gate": True}),
    ("GPM", {"plates": {"poly": 3.0, "m1": 6.0}, "gate": True}),
    ("NW0", {}),
    ("NWS", {"corner": 0.0}),
    ("NWP", {"plates": {"poly": 3.0}}),
    ("NWM1", {"plates": {"m1": 6.0}}),
    ("NWPM", {"plates": {"poly": 2.0, "m1": 5.0, "m2": 9.0}}),
    ("NWPW", {"pwell_gap": 3.0}),
    ("NWNAT", {"nat_gap": 0.5}),
    ("DN0", {"kind": "dnw", "term": 20.0}),
    ("DNM1", {"kind": "dnw", "plates": {"m1": 6.0}}),
]
