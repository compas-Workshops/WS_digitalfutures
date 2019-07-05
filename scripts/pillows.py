from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from random import sample

from compas.datastructures import mesh_subdivide
from compas.rpc import Proxy

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

PROXY = Proxy('compas_fofin.fofin')

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

SHELL = Shell.from_json(FILE_I)

SHELL.update_default_face_attributes({'children': None})

# ==============================================================================
# Subdivide
# ==============================================================================

SUBD1 = mesh_subdivide(SHELL, scheme='quad', k=1)

SUBD1.update_default_face_attributes({'children': None})

for fkey in SHELL.faces():
    children = []
    for u, v in SHELL.face_halfedges(fkey):
        u_nbrs = SUBD1.vertex_neighbors(u)
        v_nbrs = SUBD1.vertex_neighbors(v)
        shared = list(set(u_nbrs) & set(v_nbrs))
        children += shared
    key = list(set.intersection(*[set(SUBD1.vertex_neighbors(key)) for key in children]))[0]
    children.append(key)
    SHELL.set_face_attribute(fkey, 'children', children)

SUBD2 = mesh_subdivide(SUBD1, scheme='quad', k=1)

SUBD2.update_default_face_attributes({'children': None})

for fkey in SUBD1.faces():
    children = []
    for u, v in SUBD1.face_halfedges(fkey):
        u_nbrs = SUBD2.vertex_neighbors(u)
        v_nbrs = SUBD2.vertex_neighbors(v)
        shared = list(set(u_nbrs) & set(v_nbrs))
        children += shared
    key = list(set.intersection(*[set(SUBD2.vertex_neighbors(key)) for key in children]))[0]
    children.append(key)
    SUBD1.set_face_attribute(fkey, 'children', children)


# ==============================================================================
# Visualise
# ==============================================================================

descendants = {}
for root in sample(SHELL.faces(), k=10):
    root = SHELL.get_any_face()
    children = SHELL.get_face_attribute(root, 'children')
    u = children[-1]
    faces = []
    for v in children[:-1]:
        faces.append(SUBD1.halfedge[u][v])
    grandchildren = []
    for fkey in faces:
        grandchildren += SUBD1.get_face_attribute(fkey, 'children')
    descendants[root] = children + grandchildren


ARTIST = ShellArtist(None, layer="Pillows")
ARTIST.clear_layer()

ARTIST.mesh = SHELL
ARTIST.layer = "Pillows::Control"
ARTIST.draw_vertices(
    keys=list(SHELL.face_vertices(root)),
    color={key: (255, 0, 0) for key in SHELL.face_vertices(root)})
ARTIST.draw_edges()

ARTIST.mesh = SUBD2
ARTIST.layer = "Pillows::Subd"
ARTIST.draw_vertices(
    color={key: (0, 255, 0) for key in children + grandchildren})
