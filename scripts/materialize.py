import os
from math import pi
from math import sqrt

import compas_fofin
from compas_fofin.datastructures import Shell

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')

FILE_I = os.path.join(DATA, 'geometry.json')
FILE_O = os.path.join(DATA, 'cablenet.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# cables
# ==============================================================================

# E = 210.0

for u, v, attr in shell.edges_where({'is_edge': True}, True):
    f = attr['f']
    E = attr['E']

    f_factored_N = 1.0 * f * 1e3
    S_factored_N_m2 = pi * 400 * 1e6

    r = sqrt(f_factored_N / S_factored_N_m2) * 1e3

    x = f / (E * A)
    l  = shell.edge_length(u, v)
    l0 = l / (1 + x)

    print(r)
    print(l0)

# ==============================================================================
# serialisation
# ==============================================================================

shell.to_json(FILE_O)
