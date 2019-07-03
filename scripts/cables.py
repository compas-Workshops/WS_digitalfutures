from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.geometry import add_vectors
from compas.datastructures import mesh_subdivide_quad
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist
from compas_fofin.rhino import ShellHelper

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-subd.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(shell, layer="Temp")

artist.clear_layer()
artist.draw_vertices(color={key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})})
artist.draw_edges()
artist.redraw()

# ==============================================================================
# Select
# ==============================================================================

cable = []

edge = ShellHelper.select_edge(shell)

if edge:
    edges = shell.get_continuous_edges(edge)
    for edge in edges:
        if edge not in cable:
            cable.append(edge)
    print(cable)

# ==============================================================================
# Lengths
# ==============================================================================

# ==============================================================================
# Export
# ==============================================================================

wb = Workbook()

ws = wb.active
ws.title = "CABLES"

ws.append(...)
