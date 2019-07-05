from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

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

artist = ShellArtist(shell, layer="FoFin")
artist.clear_layer()

artist.layer = "FoFin::Data"
artist.draw_vertices(color={key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})})
artist.draw_edges()
artist.draw_faces()

artist.layer= "FoFin::Forces"
artist.draw_forces(scale=0.025)

artist.layer= "FoFin::Reactions"
artist.draw_reactions(scale=0.5)
