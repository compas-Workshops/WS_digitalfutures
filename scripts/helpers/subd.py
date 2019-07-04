from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas.datastructures import mesh_subdivide_quad
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-subd.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Subdivide
# ==============================================================================

subd = mesh_subdivide_quad(shell, k=2)
subd.name = 'Subd'

# ==============================================================================
# Update attributes
# ==============================================================================

subd.update_default_vertex_attributes(shell.default_vertex_attributes)
subd.update_default_edge_attributes(shell.default_edge_attributes)

for key, attr in shell.vertices(True):
    if subd.has_vertex(key):
        for name in attr:
            subd.set_vertex_attribute(key, name, attr[name])
        subd.set_vertex_attribute(key, 'is_anchor', True)

# dva = shell.default_vertex_attributes
# gkey_key = shell.gkey_key()
#
# for key, attr in subd.vertices(True):
#     gkey = geometric_key(subd.vertex_coordinates(key))
#     if gkey in gkey_key:
#         key = gkey_key[gkey]
#         for name in dva:
#             subd.set_vertex_attribute(key, name, shell.get_vertex_attribute(key, name))
#         subd.set_vertex_attribute(key, 'is_anchor', True)

# ==============================================================================
# Serialize
# ==============================================================================

subd.to_json(FILE_O)

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(subd, layer="Geometry::Subd")

artist.clear_layer()
# artist.draw_vertices(color={key: (255, 0, 0) for key in subd.vertices_where({'is_anchor': True})})
# artist.draw_edges()
artist.draw_mesh(color=(0, 255, 0))
artist.redraw()
