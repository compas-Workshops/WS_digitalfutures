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
from compas_fofin.rhino import ShellHelper

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'FINAL', 'test.json')
FILE_O = os.path.join(DATA, 'FINAL', 'test.json')

shell = Shell.from_json(FILE_I)
artist = ShellArtist(shell, layer="Before")
artist.clear_layer()
artist.draw_vertices()
artist.draw_faces()
artist.redraw()

fkey = ShellHelper.select_face(shell)
key = ShellHelper.select_vertex(shell)
vertices = shell.face_vertices(fkey)
index = vertices.index(key)
before = vertices[index - 1]
nbr = shell.halfedge[key][before]
attr = shell.vertex[key].copy()

inserted = shell.add_vertex(**attr)

vertices.insert(index, inserted)
shell.halfedge[before][inserted] = fkey
shell.halfedge[inserted][key] = fkey
del shell.halfedge[before][key]

vertices = shell.face_vertices(nbr)
ancestor = vertices[vertices.index(key) - 1]
shell.halfedge[ancestor][inserted] = nbr
shell.halfedge[inserted][before] = nbr
vertices.remove(key)
index = vertices.index(before)
vertices.insert(index, inserted)

del shell.halfedge[ancestor][key]
del shell.halfedge[key][before]

shell.to_json(FILE_O)

# artist.layer = "After"
# artist.clear_layer()
# artist.draw_vertices()
# artist.draw_faces()
# artist.redraw()
