from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.utilities import pairwise
from compas.geometry import add_vectors
from compas.datastructures import mesh_dual
from compas_fofin.datastructures import Shell

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data-extended-strips-split.json')
FILE_O = os.path.join(DATA, 'data-extended-strips-split_test.json')

fabric = Shell.from_json(FILE_I)

# ==============================================================================
# Visualize
# ==============================================================================

# artist = ShellArtist(fabric, layer="Fabric::SplitCorners")
# artist.clear_layer()
# artist.draw_vertices()
# artist.draw_faces()
# artist.draw_edges()
# artist.redraw()

# ==============================================================================
# Assign strips
# ==============================================================================

R0 = list(fabric.faces_where({'panel': 'RING', 'strip': 0}))
R1 = list(fabric.faces_where({'panel': 'RING', 'strip': 1}))
R2 = list(fabric.faces_where({'panel': 'RING', 'strip': 2}))
R3 = list(fabric.faces_where({'panel': 'RING', 'strip': 3}))
R4 = list(fabric.faces_where({'panel': 'RING', 'strip': 4}))
R5 = list(fabric.faces_where({'panel': 'RING', 'strip': 5}))
R6 = list(fabric.faces_where({'panel': 'RING', 'strip': 6}))
R7 = list(fabric.faces_where({'panel': 'RING', 'strip': 7}))
R8 = list(fabric.faces_where({'panel': 'RING', 'strip': 8}))
R9 = list(fabric.faces_where({'panel': 'RING', 'strip': 9}))
R10 = list(fabric.faces_where({'panel': 'RING', 'strip': 10}))

u = 359
v = 411

fkey = fabric.halfedge[u][v]
if fkey not in R0:
    fkey = fabric.halfedge[v][u]
    u, v = v, u

faces = []
faces.append(fkey)

while True:
    vertices = fabric.face_vertices(fkey)
    if len(vertices) != 4:
        break
    i = vertices.index(u)
    v = vertices[i - 1]
    u = vertices[i - 2]
    fkey = fabric.halfedge[v][u]
    if fkey not in R0:
        break
    if fkey == faces[0]:
        break
    faces.append(fkey)
    v, u = u, v

print(R0)
print(faces)

u = 359
v = 360

fkey = fabric.halfedge[u][v]
if fkey not in R1:
    fkey = fabric.halfedge[v][u]
    u, v = v, u

faces = []
faces.append(fkey)

while True:
    vertices = fabric.face_vertices(fkey)
    if len(vertices) != 4:
        break
    i = vertices.index(u)
    v = vertices[i - 1]
    u = vertices[i - 2]
    fkey = fabric.halfedge[v][u]
    if fkey not in R1:
        break
    if fkey == faces[0]:
        break
    faces.append(fkey)
    v, u = u, v

print(R1)
print(faces)

u = 445
v = 446

fkey = fabric.halfedge[u][v]
if fkey not in R2:
    fkey = fabric.halfedge[v][u]
    u, v = v, u

faces = []
faces.append(fkey)

while True:
    vertices = fabric.face_vertices(fkey)
    if len(vertices) != 4:
        break
    i = vertices.index(u)
    v = vertices[i - 1]
    u = vertices[i - 2]
    fkey = fabric.halfedge[v][u]
    if fkey not in R2:
        break
    if fkey == faces[0]:
        break
    faces.append(fkey)
    v, u = u, v

print(R2)
print(faces)


# ==============================================================================
# Export
# ==============================================================================

# fabric.to_json(FILE_O)
