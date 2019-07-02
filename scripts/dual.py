from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas.datastructures import mesh_dual
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Compute dual
# ==============================================================================

dual = mesh_dual(shell)
dual.name = "Dual"

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(dual, layer="Geometry::Dual")

artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()
