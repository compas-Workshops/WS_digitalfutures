from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from math import pi
from math import sqrt

import compas_fofin
from compas_fofin.datastructures import Shell

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')

FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-materialised.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Compute unstressed length
# ==============================================================================

for u, v, attr in shell.edges_where({'is_edge': True}, True):
    f = attr['f']
    E = 210
    r = 2
    A = 3.14159 * r**2

    x = f / (E * A)
    l  = shell.edge_length(u, v)
    l0 = l / (1 + x)

    print(l)
    print(l0)
    print()

    attr['E'] = E
    attr['r'] = r
    attr['l0'] = l0

# ==============================================================================
# Serialize
# ==============================================================================

shell.to_json(FILE_O)
