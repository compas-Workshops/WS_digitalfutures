import os
import json

import compas
import compas_rhino
import compas_fofin

from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.utilities import pairwise
from compas.datastructures import mesh_flip_cycles
from compas.datastructures import mesh_add_vertex_to_face_edge

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist
from compas_fofin.rhino import ShellHelper

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'FINAL', 'after.json')
FILE_O = os.path.join(DATA, 'FINAL', 'after.json')

shell = Shell.from_json(FILE_I)
# artist = ShellArtist(shell, layer="Before")
# artist.clear_layer()
# artist.draw_vertices()
# artist.draw_faces()
# artist.redraw()

# key = ShellHelper.select_vertex(shell)
# fkey = ShellHelper.select_face(shell)
# v = ShellHelper.select_vertex(shell)

# mesh_add_vertex_to_face_edge(shell, key, fkey, v)

# shell.delete_face(357)

shell.add_face([276, 283, 334, 279])
shell.add_face([283, 229, 125, 148, 334])

# for fkey in [73, 124, 218, 239]:
#     shell.delete_face(fkey)

shell.to_json(FILE_O)
