import os
from math import pi
from math import sqrt

import compas_fofin
from compas_fofin.datastructures import Shell

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')

FILE_I = os.path.join(DATA, 'box.json')
FILE_O = os.path.join(DATA, 'cablenet.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# cables
# ==============================================================================

# E = 210.0

for u, v, attr in shell.edges_where({'is_edge': True}, True):
    f = attr['f']
    E = attr['E'] or 210

    # f_factored_N = 1.0 * f * 1e3
    # S_factored_N_m2 = pi * 400 * 1e6

    # r = sqrt(f_factored_N / S_factored_N_m2) * 1e3
    r = 2

    A = 3.14159 * r**2

    x = f / (E * A)
    l  = shell.edge_length(u, v)
    l0 = l / (1 + x)

    print(l)
    print(l0)
    print()

# ==============================================================================
# serialisation
# ==============================================================================

shell.to_json(FILE_O)
