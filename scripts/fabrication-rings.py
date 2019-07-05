from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from openpyxl import Workbook

from compas.geometry import add_vectors
from compas_fofin.datastructures import Shell

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-fabrication-rings.xlsx')

SHELL = Shell.from_json(FILE_I)

# ==============================================================================
# Select
# ==============================================================================

CABLES = []

for edge in [(136, 203), (45, 200), (103, 105), (156, 255)]:
    cable = []
    edges = SHELL.get_continuous_edges(edge)
    for edge in edges:
        if edge not in cable:
            cable.append(edge)
    CABLES.append(cable)

# ==============================================================================
# Lengths
# ==============================================================================

LENGTHS = []

for cable in CABLES:
    data = []
    L = 0
    u, v = cable[0]
    l = SHELL.edge_length(u, v)
    l = 1e3 * l
    L += round(l, 1)

    data.append("{}-{}".format(u, v))
    data.append(50)
    data.append(L - 50)

    for u, v in cable[1:]:
        l = SHELL.edge_length(u, v)
        l = 1e3 * l
        L += round(l, 1)
        data.append(L)

    L += 50
    data.append(L)
    LENGTHS.append(data)

# ==============================================================================
# Export
# ==============================================================================

WB = Workbook()

WS = WB.active
WS.title = "CABLES"

for data in LENGTHS:
    WS.append(data)

WB.save(FILE_O)
