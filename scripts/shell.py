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
# Compute offset surfaces
# ==============================================================================

thickness = 0.04

edos = shell.copy()
idos = shell.copy()

edos.name = 'Extrados'
idos.name = 'Intrados'

for key in shell.vertices():
    normal = shell.vertex_normal(key)
    xyz = shell.vertex_coordinates(key)

    up = scale_vector(normal, 0.5 * thickness)
    down = scale_vector(normal, -0.5 * thickness)

    edos.set_vertex_attributes(key, 'xyz', add_vectors(xyz, up))
    idos.set_vertex_attributes(key, 'xyz', add_vectors(xyz, down))

mesh_flip_cycles(idos)

# ==============================================================================
# Construct volume
# ==============================================================================

volume = idos.copy()
volume.name = 'Volume'

max_int_key = volume._max_int_key + 1
max_int_fkey = volume._max_int_fkey + 1

for key, attr in edos.vertices(True):
    volume.add_vertex(key=key + max_int_key, **attr)

for fkey in edos.faces():
    vertices = edos.face_vertices(fkey)
    vertices = [key + max_int_key for key in vertices]
    volume.add_face(vertices)

boundary = edos.vertices_on_boundary(ordered=True)
boundary.append(boundary[0])

for a, b in pairwise(boundary):
    volume.add_face([b, a, a + max_int_key, b + max_int_key])

# ==============================================================================
# Visualise
# ==============================================================================

artist = ShellArtist(shell, layer="Shell")
artist.clear_layer()

# artist.layer = "Shell::FoFin"
# artist.draw_vertices(color={key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})})
# artist.draw_edges()
# artist.draw_faces()
# artist.draw_reactions(scale=0.5)
# artist.draw_forces(scale=0.025)

# artist.layer = "Shell::Intrados"
# artist.mesh = idos
# artist.draw_mesh(color=(255, 0, 0))
# artist.draw_facenormals(color=(255, 0, 0), scale=0.05)

# artist.layer = "Shell::Extrados"
# artist.mesh = edos
# artist.draw_mesh(color=(0, 0, 255))
# artist.draw_facenormals(color=(0, 0, 255), scale=0.05)

artist.layer = "Shell::Volume"
artist.mesh = volume
artist.draw_mesh()

artist.redraw()
