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

ARTIST = ShellArtist(SHELL, layer="Cablenet")
ARTIST.clear_layer()

ARTIST.layer = "Cablenet::Nodes"
ARTIST.draw_vertices()

ARTIST.layer = "Cablenet::Edges"
ARTIST.draw_edges()

ARTIST.redraw()
