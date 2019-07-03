from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas_rhino

from compas.utilities import pairwise
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import cross_vectors

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-extended.json')

shell = Shell.from_json(FILE_I)

mesh = shell.copy()

# ==============================================================================
# Add vertices
# ==============================================================================

guids = compas_rhino.select_points()
points = compas_rhino.get_point_coordinates(guids)

for x, y, z in points:
    mesh.add_vertex(x=x, y=y, z=z)

# ==============================================================================
# Export
# ==============================================================================

mesh.to_json(FILE_O)

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(mesh, layer="Fabric::Extended")
artist.clear_layer()
artist.draw_vertices()
artist.draw_faces()
artist.redraw()
