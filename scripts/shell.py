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

SHELL = Shell.from_json(FILE_I)

THICKNESS = 0.04

# ==============================================================================
# Compute offset surfaces
# ==============================================================================

EDOS = SHELL.copy()
IDOS = SHELL.copy()

EDOS.name = 'Extrados'
IDOS.name = 'Intrados'

for key in SHELL.vertices():
    normal = SHELL.vertex_normal(key)
    xyz = SHELL.vertex_coordinates(key)

    up = scale_vector(normal, 0.5 * THICKNESS)
    down = scale_vector(normal, -0.5 * THICKNESS)

    EDOS.set_vertex_attributes(key, 'xyz', add_vectors(xyz, up))
    IDOS.set_vertex_attributes(key, 'xyz', add_vectors(xyz, down))

mesh_flip_cycles(IDOS)

# ==============================================================================
# Construct VOLUME
# ==============================================================================

VOLUME = IDOS.copy()
VOLUME.name = 'Volume'

max_int_key = VOLUME._max_int_key + 1
max_int_fkey = VOLUME._max_int_fkey + 1

for key, attr in EDOS.vertices(True):
    VOLUME.add_vertex(key=key + max_int_key, **attr)

for fkey in EDOS.faces():
    vertices = EDOS.face_vertices(fkey)
    vertices = [key + max_int_key for key in vertices]
    VOLUME.add_face(vertices)

boundary = EDOS.vertices_on_boundary(ordered=True)
boundary.append(boundary[0])

for a, b in pairwise(boundary):
    VOLUME.add_face([b, a, a + max_int_key, b + max_int_key])

# ==============================================================================
# Visualise
# ==============================================================================

ARTIST = ShellArtist(SHELL, layer="Shell")
ARTIST.clear_layer()

# ARTIST.layer = "Shell::FoFin"
# ARTIST.draw_vertices(color={key: (255, 0, 0) for key in SHELL.vertices_where({'is_anchor': True})})
# ARTIST.draw_edges()
# ARTIST.draw_faces()
# ARTIST.draw_reactions(scale=0.5)
# ARTIST.draw_forces(scale=0.025)

# ARTIST.layer = "Shell::Intrados"
# ARTIST.mesh = IDOS
# ARTIST.draw_mesh(color=(255, 0, 0))
# ARTIST.draw_facenormals(color=(255, 0, 0), scale=0.05)

# ARTIST.layer = "Shell::Extrados"
# ARTIST.mesh = EDOS
# ARTIST.draw_mesh(color=(0, 0, 255))
# ARTIST.draw_facenormals(color=(0, 0, 255), scale=0.05)

ARTIST.layer = "Shell::Volume"
ARTIST.mesh = VOLUME
ARTIST.draw_mesh()

ARTIST.redraw()
