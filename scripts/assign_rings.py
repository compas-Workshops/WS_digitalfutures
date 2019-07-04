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


def order_faces(ring, edge):
    faces = []

    u, v = edge

    fkey = fabric.halfedge[u][v]
    if fkey not in ring:
        fkey = fabric.halfedge[v][u]
        u, v = v, u

    faces.append(fkey)

    while True:
        vertices = fabric.face_vertices(fkey)
        if len(vertices) != 4:
            break
        i = vertices.index(u)
        v = vertices[i - 1]
        u = vertices[i - 2]
        fkey = fabric.halfedge[v][u]
        if fkey not in ring:
            break
        if fkey == faces[0]:
            break
        faces.append(fkey)
        v, u = u, v

    return faces


# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data-extended-strips-split.json')
FILE_O = os.path.join(DATA, 'data-extended-strips-split.json')

fabric = Shell.from_json(FILE_I)

# ==============================================================================
# Assign strips
# ==============================================================================

R0 = list(fabric.faces_where({'panel': 'RING', 'strip': '00'}))
R1 = list(fabric.faces_where({'panel': 'RING', 'strip': '01'}))
R2 = list(fabric.faces_where({'panel': 'RING', 'strip': '02'}))
R3 = list(fabric.faces_where({'panel': 'RING', 'strip': '03'}))
R4 = list(fabric.faces_where({'panel': 'RING', 'strip': '04'}))
R5 = list(fabric.faces_where({'panel': 'RING', 'strip': '05'}))
R6 = list(fabric.faces_where({'panel': 'RING', 'strip': '06'}))
R7 = list(fabric.faces_where({'panel': 'RING', 'strip': '07'}))
R8 = list(fabric.faces_where({'panel': 'RING', 'strip': '08'}))
R9 = list(fabric.faces_where({'panel': 'RING', 'strip': '09'}))
R10 = list(fabric.faces_where({'panel': 'RING', 'strip': '10'}))

print(R0)
print(R1)
print(R2)
print(R3)
print(R4)
print(R5)
print(R6)
print(R7)
print(R8)
print(R9)
print(R10)

R0_ordered = order_faces(R0, (359, 411))
R1_ordered = order_faces(R1, (359, 360))
R2_ordered = order_faces(R2, (445, 446))
R3_ordered = order_faces(R3, (444, 445))
R4_ordered = order_faces(R4, (443, 444))
R5_ordered = order_faces(R5, (442, 443))
R6_ordered = order_faces(R6, (441, 442))
R7_ordered = order_faces(R7, (440, 441))
R8_ordered = order_faces(R8, (439, 440))
R9_ordered = order_faces(R9, (356, 358))
R10_ordered = order_faces(R10, (356, 394))

for i, fkey in enumerate(R0_ordered):
    fabric.set_face_attribute(fkey, 'strip', '00')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R1_ordered):
    fabric.set_face_attribute(fkey, 'strip', '01')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R2_ordered):
    fabric.set_face_attribute(fkey, 'strip', '02')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R3_ordered):
    fabric.set_face_attribute(fkey, 'strip', '03')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R4_ordered):
    fabric.set_face_attribute(fkey, 'strip', '04')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R5_ordered):
    fabric.set_face_attribute(fkey, 'strip', '05')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R6_ordered):
    fabric.set_face_attribute(fkey, 'strip', '06')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R7_ordered):
    fabric.set_face_attribute(fkey, 'strip', '07')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R8_ordered):
    fabric.set_face_attribute(fkey, 'strip', '08')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R9_ordered):
    fabric.set_face_attribute(fkey, 'strip', '09')
    fabric.set_face_attribute(fkey, 'count', i)

for i, fkey in enumerate(R10_ordered):
    fabric.set_face_attribute(fkey, 'strip', '10')
    fabric.set_face_attribute(fkey, 'count', i)

# ==============================================================================
# Export
# ==============================================================================

fabric.to_json(FILE_O, pretty=True)
