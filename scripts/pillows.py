from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from random import sample

from compas.datastructures import mesh_subdivide
from compas.geometry import scale_vector
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
SHELL.update_default_edge_attributes({'child': None})

# ==============================================================================
# Subdivide
# ==============================================================================

SUBD1 = mesh_subdivide(SHELL, scheme='quad', k=1)

SUBD1.update_default_face_attributes({'children': None})
SUBD1.update_default_edge_attributes({'child': None})

for fkey in SHELL.faces():
    children = []
    for u, v in SHELL.face_halfedges(fkey):
        u_nbrs = SUBD1.vertex_neighbors(u)
        v_nbrs = SUBD1.vertex_neighbors(v)
        shared = list(set(u_nbrs) & set(v_nbrs))
        children += shared
        SHELL.set_edge_attribute((u, v), 'child', shared[0])

    keys = list(set.intersection(*[set(SUBD1.vertex_neighbors(key)) for key in children]))
    SHELL.set_face_attribute(fkey, 'children', children + keys)

# ==============================================================================
# Subdivide
# ==============================================================================

SUBD2 = mesh_subdivide(SUBD1, scheme='quad', k=1)

SUBD2.update_default_face_attributes({'children': None})
SUBD2.update_default_edge_attributes({'child': None})

for fkey in SUBD1.faces():
    children = []
    for u, v in SUBD1.face_halfedges(fkey):
        u_nbrs = SUBD2.vertex_neighbors(u)
        v_nbrs = SUBD2.vertex_neighbors(v)
        shared = list(set(u_nbrs) & set(v_nbrs))
        children += shared
        SUBD1.set_edge_attribute((u, v), 'child', shared[0])

    keys = list(set.intersection(*[set(SUBD2.vertex_neighbors(key)) for key in children]))
    SUBD1.set_face_attribute(fkey, 'child', children + keys)

# ==============================================================================
# Pressure
# ==============================================================================

SUBD2.update_default_edge_attributes({'q': 1.0, 'f': 0.0, 'l': 0.0})
SUBD2.update_default_vertex_attributes({'px': 0.0, 'py': 0.0, 'pz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0, 'is_anchor': False})

SUBD2.set_edges_attributes(['q', 'f', 'l'], [1.0, 0.0, 0.0])
SUBD2.set_vertices_attributes(['px', 'py', 'pz', 'rx', 'ry', 'rz', 'is_anchor'], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False])

for u, v in SHELL.edges():
    child = SHELL.get_edge_attribute((u, v), 'child')
    u_grandchild = SUBD1.get_edge_attribute((u, child), 'child')
    v_grandchild = SUBD1.get_edge_attribute((v, child), 'child')
    SUBD2.set_edge_attribute((u, u_grandchild), 'q', 10.0)
    SUBD2.set_edge_attribute((child, u_grandchild), 'q', 10.0)
    SUBD2.set_edge_attribute((v, v_grandchild), 'q', 10.0)
    SUBD2.set_edge_attribute((child, v_grandchild), 'q', 10.0)

for key in SUBD2.vertices():
    if SHELL.has_vertex(key):
        SUBD2.set_vertex_attribute(key, 'is_anchor', True)
    normal = SUBD2.vertex_normal(key)
    px, py, pz = scale_vector(normal, 0.01)
    SUBD2.set_vertex_attribute(key, 'px', px)
    SUBD2.set_vertex_attribute(key, 'py', py)
    SUBD2.set_vertex_attribute(key, 'pz', pz)

data = PROXY.fofin_numpy_proxy(SUBD2.to_data())    
SUBD2.data = data

# ==============================================================================
# Visualise
# ==============================================================================

anchors = list(SUBD2.vertices_where({'is_anchor': True}))

ARTIST = ShellArtist(SUBD2, layer="Pillows")
ARTIST.clear_layer()
ARTIST.draw_vertices(
    keys=anchors,
    color={key: (255, 0, 0) for key in anchors})
ARTIST.draw_faces()
