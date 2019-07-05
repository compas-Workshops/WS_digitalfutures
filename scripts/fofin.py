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

SHELL = Shell.from_json(FILE_I)

# ==============================================================================
# Visualise
# ==============================================================================

ARTIST = ShellArtist(SHELL, layer="FoFin")
ARTIST.clear_layer()

ARTIST.layer = "FoFin::Data"
ARTIST.draw_vertices(color={key: (255, 0, 0) for key in SHELL.vertices_where({'is_anchor': True})})
ARTIST.draw_edges()
ARTIST.draw_faces()

ARTIST.layer= "FoFin::Forces"
ARTIST.draw_forces(scale=0.025)

ARTIST.layer= "FoFin::Reactions"
ARTIST.draw_reactions(scale=0.5)
