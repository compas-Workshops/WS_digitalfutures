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
FILE_O = os.path.join(DATA, 'data-fabrication-test.xlsx')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Select
# ==============================================================================

cables = []

for edge in [(136, 203), (45, 200), (103, 105), (156, 255)]:
    cable = []
    edges = shell.get_continuous_edges(edge)
    for edge in edges:
        if edge not in cable:
            cable.append(edge)
    cables.append(cable)

# ==============================================================================
# Lengths
# ==============================================================================

lengths = []

for cable in cables:
    data = []
    L = 0
    u, v = cable[0]
    l = shell.edge_length(u, v)
    l = 1e3 * l
    L += round(l, 1)

    data.append("{}-{}".format(u, v))
    data.append(50)
    data.append(L - 50)

    for u, v in cable[1:]:
        l = shell.edge_length(u, v)
        l = 1e3 * l
        L += round(l, 1)
        data.append(L)

    L += 50
    data.append(L)
    lengths.append(data)

# ==============================================================================
# Export
# ==============================================================================

wb = Workbook()

ws = wb.active
ws.title = "CABLES"

for data in lengths:
    ws.append(data)

wb.save(FILE_O)
