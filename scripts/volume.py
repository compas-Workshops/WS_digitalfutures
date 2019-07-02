from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import compas
import compas_rhino
import compas_fofin

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

for key in shell.vertices():
    normal = shell.vertex_normal(key)
    xyz = shell.vertex_coordinates(key)

    up = scale_vector(normal, 0.5 * thickness)
    down = scale_vector(normal, -0.5 * thickness)

    edos.set_vertex_attributes(key, 'xyz', add_vectors(xyz, up))
    idos.set_vertex_attributes(key, 'xyz', add_vectors(xyz, down))

# ==============================================================================
# Construct volume
# ==============================================================================

volume = idos.copy()
volume.name = 'Volume'

# flip its cycles to make the bottom normals point downwards

mesh_flip_cycles(volume)

# set the key offset

max_int_key = volume._max_int_key + 1
max_int_fkey = volume._max_int_fkey + 1

# add the vertices of the edos

for key, attr in edos.vertices(True):
    volume.add_vertex(key=key + max_int_key, **attr)

# add the faces of the edos

for fkey in edos.faces():
    vertices = edos.face_vertices(fkey)
    vertices = [key + max_int_key for key in vertices]

    volume.add_face(vertices)

# add the side faces

boundary = edos.vertices_on_boundary(ordered=True)
boundary.append(boundary[0])

for a, b in pairwise(boundary):
    volume.add_face([b, a, a + max_int_key, b + max_int_key])

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(volume, layer="Geometry::Volume")
artist.clear_layer()
artist.draw_mesh(disjoint=True)
artist.redraw()
