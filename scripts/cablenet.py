from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.utilities import pairwise
from compas.datastructures import mesh_flip_cycles

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
# Visualise
# ==============================================================================

artist = ShellArtist(shell, layer="Cablenet")
artist.clear_layer()

artist.layer = "Cablenet::Nodes"
artist.draw_vertices()

artist.layer = "Cablenet::Edges"
artist.draw_edges()

artist.redraw()
