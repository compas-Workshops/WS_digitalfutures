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
FILE_I = os.path.join(DATA, 'data-extended.json')
FILE_O = os.path.join(DATA, 'data-extended-dual.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Compute dual
# ==============================================================================

dual = mesh_dual(shell)
dual.name = "Dual"

for key in dual.vertices_on_boundary():
    for u, v in shell.face_halfedges(key):
        if shell.is_edge_on_boundary(u, v):
            midpoint = shell.edge_midpoint(u, v)
            dual.set_vertex_attributes(key, 'xyz', midpoint)
            break

# ==============================================================================
# Export
# ==============================================================================

dual.update_default_face_attributes({'panel' : None, 'strip': None, 'count': None})

dual.to_json(FILE_O)

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(dual, layer="Geometry::Dual")

artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.draw_faces()
artist.redraw()
