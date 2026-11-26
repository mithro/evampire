"""GDS layers of gf180mcuD used by the test die (layer, datatype), from the PDK's gf180mcu.lyp."""

COMP = (22, 0)
DNWELL = (12, 0)
NWELL = (21, 0)
LVPWELL = (204, 0)
DUALGATE = (55, 0)  # the 5 V / 6 V thick gate oxide area
POLY2 = (30, 0)
NPLUS = (32, 0)
PPLUS = (31, 0)
CONTACT = (33, 0)
METAL1 = (34, 0)
VIA1 = (35, 0)
METAL2 = (36, 0)
VIA2 = (38, 0)
METAL3 = (42, 0)
VIA3 = (40, 0)
METAL4 = (46, 0)
VIA4 = (41, 0)
METAL5 = (81, 0)  # the top metal of the 5-metal stack; follows the MetalTop rules
PAD = (37, 0)
NAT = (5, 0)
NDMY = (111, 5)  # blocks dummy COMP (and Poly2) fill
PMNDMY = (152, 5)  # blocks dummy Poly2 and metal fill
METAL5_LABEL = (81, 10)

METALS = [METAL1, METAL2, METAL3, METAL4, METAL5]
VIAS = [VIA1, VIA2, VIA3, VIA4]
