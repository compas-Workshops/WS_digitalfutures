from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from random import sample

from compas.datastructures import mesh_subdivide
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas.rpc import Proxy

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

NUMERICAL = Proxy('compas.numerical')

# ==============================================================================
# Helpers
# ==============================================================================

def subd_tracked(mesh, k):
    levels = []
    for _ in range(k):
        mesh.update_default_face_attributes({'children': None})
        mesh.update_default_edge_attributes({'child': None})
        subd = mesh_subdivide(mesh, scheme='quad', k=1)
        subd.update_default_face_attributes({'children': None})
        subd.update_default_edge_attributes({'child': None})
        for fkey in mesh.faces():
            children = []
            for u, v in mesh.face_halfedges(fkey):
                u_nbrs = subd.vertex_neighbors(u)
                v_nbrs = subd.vertex_neighbors(v)
                shared = list(set(u_nbrs) & set(v_nbrs))
                children += shared
                mesh.set_edge_attribute((u, v), 'child', shared[0])
            keys = list(set.intersection(*[set(subd.vertex_neighbors(key)) for key in children]))
            mesh.set_face_attribute(fkey, 'children', children + keys)
        levels.append(subd)
        mesh = subd
    return levels

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

SHELL = Shell.from_json(FILE_I)

# ==============================================================================
# Subdivide
# ==============================================================================

S1, S2 = subd_tracked(SHELL, k=2)

S2.update_default_edge_attributes({'q': 1.0, 'f': 0.0, 'l': 0.0})
S2.update_default_vertex_attributes({'px': 0.0, 'py': 0.0, 'pz': 0.0, 'rx': 0.0, 'ry': 0.0, 'rz': 0.0, 'is_anchor': False})

S2.set_edges_attributes(['q', 'f', 'l'], [1.0, 0.0, 0.0])
S2.set_vertices_attributes(['px', 'py', 'pz', 'rx', 'ry', 'rz', 'is_anchor'], [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False])

for u, v in SHELL.edges():
    child = SHELL.get_edge_attribute((u, v), 'child')
    u_grandchild = S1.get_edge_attribute((u, child), 'child')
    v_grandchild = S1.get_edge_attribute((v, child), 'child')
    S2.set_edge_attribute((u, u_grandchild), 'q', 10.0)
    S2.set_edge_attribute((child, u_grandchild), 'q', 10.0)
    S2.set_edge_attribute((v, v_grandchild), 'q', 10.0)
    S2.set_edge_attribute((child, v_grandchild), 'q', 10.0)

for key in S2.vertices():
    S2.set_vertex_attribute(key, 'is_anchor', SHELL.has_vertex(key))

# ==============================================================================
# EDOS/IDOS
# ==============================================================================

IDOS = S2.copy()
EDOS = S2.copy()

for key in S2.vertices():
    normal = S2.vertex_normal(key)
    xyz = S2.vertex_coordinates(key)

    IDOS.set_vertex_attributes(key, 'xyz', add_vectors(xyz, scale_vector(normal, -0.02)))
    EDOS.set_vertex_attributes(key, 'xyz', add_vectors(xyz, scale_vector(normal, +0.02)))

    IDOS.set_vertex_attributes(key, ['px', 'py', 'pz'], scale_vector(normal, -0.01))
    EDOS.set_vertex_attributes(key, ['px', 'py', 'pz'], scale_vector(normal, +0.01))

# ==============================================================================
# Pillowing IDOS
# ==============================================================================

key_index = IDOS.key_index()
vertices  = IDOS.get_vertices_attributes('xyz')
edges     = [[key_index[u], key_index[v]] for u, v in IDOS.edges()]
fixed     = [key_index[key] for key in IDOS.vertices_where({'is_anchor': True})]
q         = IDOS.get_edges_attribute('q')
loads     = IDOS.get_vertices_attributes(['px', 'py', 'pz'])

xyz, q, f, l, r = NUMERICAL.fd_numpy(vertices, edges, fixed, q, loads)

for key, attr in IDOS.vertices(True):
    index = key_index[key]
    attr['x'] = xyz[index][0]
    attr['y'] = xyz[index][1]
    attr['z'] = xyz[index][2]

# ==============================================================================
# Pillowing EDOS
# ==============================================================================

key_index = EDOS.key_index()
vertices  = EDOS.get_vertices_attributes('xyz')
edges     = [[key_index[u], key_index[v]] for u, v in EDOS.edges()]
fixed     = [key_index[key] for key in EDOS.vertices_where({'is_anchor': True})]
q         = EDOS.get_edges_attribute('q')
loads     = EDOS.get_vertices_attributes(['px', 'py', 'pz'])

xyz, q, f, l, r = NUMERICAL.fd_numpy(vertices, edges, fixed, q, loads)

for key, attr in EDOS.vertices(True):
    index = key_index[key]
    attr['x'] = xyz[index][0]
    attr['y'] = xyz[index][1]
    attr['z'] = xyz[index][2]

# ==============================================================================
# Volume
# ==============================================================================

# ==============================================================================
# Visualise
# ==============================================================================

ARTIST = ShellArtist(None, layer='Pillows')
ARTIST.clear_layer()

anchors = list(EDOS.vertices_where({'is_anchor': True}))

ARTIST.mesh = EDOS
ARTIST.layer = "Pillows::EDOS"
ARTIST.clear_layer()
ARTIST.draw_vertices(
    keys=anchors,
    color={key: (255, 0, 0) for key in anchors})
ARTIST.draw_mesh()

anchors = list(IDOS.vertices_where({'is_anchor': True}))

ARTIST.mesh = IDOS
ARTIST.layer = "Pillows::IDOS"
ARTIST.clear_layer()
ARTIST.draw_vertices(
    keys=anchors,
    color={key: (255, 0, 0) for key in anchors})
ARTIST.draw_mesh()
