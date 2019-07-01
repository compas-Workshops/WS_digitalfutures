from __future__ import print_function

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas.datastructures import mesh_dual
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'FINAL', 'final1_data.json')

shell = Shell.from_json(FILE_I)

dual = mesh_dual(shell)
dual.name = "Dual"

artist = ShellArtist(dual, layer="Dual")

artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()
