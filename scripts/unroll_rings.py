from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas

from collections import deque

from functools import partial
from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import cross_vectors
from compas.geometry import normalize_vector
from compas.geometry import Point
from compas.geometry import offset_polygon
from compas.geometry import scale_vector
from compas.geometry import add_vectors
from compas.utilities import flatten
from compas.utilities import pairwise
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles
from compas.datastructures import mesh_flip_cycles
from compas_plotters import MeshPlotter
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellHelper
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Helpers
# ==============================================================================

def split_ring(faces):
    fkey = faces[-1]
    for u, v in FABRIC.face_halfedges(fkey):
        if FABRIC.halfedge[v][u] == faces[0]:
            break
        else:
            u = None
            v = None
    if not u and not v:
        return
    a = FABRIC.vertex_coordinates(u)
    b = FABRIC.vertex_coordinates(v)
    uu = FABRIC.add_vertex(x=a[0], y=a[1], z=a[2])
    vv = FABRIC.add_vertex(x=b[0], y=b[1], z=b[2])
    vertices = FABRIC.face_vertices(fkey)
    i = vertices.index(u)
    j = vertices.index(v)
    vertices[i] = uu
    vertices[j] = vv
    for u, v in pairwise(vertices + vertices[:1]):
        FABRIC.halfedge[u][v] = fkey


def triangulate_strips(zone):
    meshes = []
    for faces in zone:
        mesh = Mesh()
        mesh.update_default_vertex_attributes(FABRIC.default_vertex_attributes)
        mesh.update_default_edge_attributes(FABRIC.default_edge_attributes)
        mesh.update_default_face_attributes(FABRIC.default_face_attributes)

        for fkey in faces:
            keys = FABRIC.face_vertices(fkey)
            for key in keys:
                if key not in mesh.vertex:
                    attr = FABRIC.vertex[key].copy()
                    mesh.add_vertex(key=key, attr_dict=attr)
            attr = FABRIC.facedata[fkey].copy()
            mesh.add_face(keys, fkey=fkey, attr_dict=attr)

        for u, v, attr in mesh.edges(True):
            for name in attr:
                value = FABRIC.get_edge_attribute((u, v), name)
                attr[name] = value

        trimesh = mesh.copy()
        mesh_quads_to_triangles(trimesh, check_angles=True)
        meshes.append([mesh, trimesh])

    return meshes


def unroll(meshes, edge):
    quadmesh, trimesh = meshes
    flatmesh = trimesh.copy()

    u, v = edge
    root = trimesh.halfedge[u][v]
    if root is None:
        root = trimesh.halfedge[v][u]
        u, v = v, u

    origin = trimesh.vertex_coordinates(u)
    zaxis = trimesh.face_normal(root, unitized=True)
    xaxis = normalize_vector(trimesh.edge_direction(u, v))
    yaxis = normalize_vector(cross_vectors(zaxis, xaxis))
    frame = Frame(origin, xaxis, yaxis)

    frame_to = Frame.worldXY()

    T = Transformation.from_frame_to_frame(frame, frame_to)

    for key in trimesh.face_vertices(root):
        x, y, z = trimesh.vertex_coordinates(key)
        point = Point(x, y, z)
        point.transform(T)
        flatmesh.set_vertex_attributes(key, 'xyz', point)

    tovisit = list(trimesh.faces())
    tovisit.remove(root)

    fkey = root

    while tovisit:
        for u, v in trimesh.face_halfedges(fkey):
            nbr = trimesh.halfedge[v][u]
            if nbr is None:
                continue
            if nbr not in tovisit:
                continue
            tovisit.remove(nbr)
            break

        fkey = nbr
        u, v = v, u

        origin = trimesh.vertex_coordinates(u)
        zaxis = trimesh.face_normal(fkey, unitized=True)
        xaxis = normalize_vector(trimesh.edge_direction(u, v))
        yaxis = normalize_vector(cross_vectors(xaxis, zaxis))
        frame = Frame(origin, xaxis, yaxis)

        origin = flatmesh.vertex_coordinates(u)
        zaxis = [0, 0, 1.0]
        xaxis = normalize_vector(flatmesh.edge_direction(u, v))
        yaxis = normalize_vector(cross_vectors(xaxis, zaxis))
        frame_to = Frame(origin, xaxis, yaxis)

        T = Transformation.from_frame_to_frame(frame, frame_to)
        w = trimesh.face_vertex_ancestor(fkey, u)
        x, y, z = trimesh.vertex_coordinates(w)
        point = Point(x, y, z)
        point.transform(T)
        flatmesh.set_vertex_attributes(w, 'xyz', point)

    for key, attr in quadmesh.vertices(True):
        x, y, z = flatmesh.vertex_coordinates(key)
        attr['x'] = x
        attr['y'] = y
        attr['z'] = z

    return quadmesh

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')
FILE_I = os.path.join(DATA, 'fabric.json')

BASE = Shell.from_json(FILE_I)
mesh_flip_cycles(BASE)

SIDE = 'edos'
SEEM = -0.020

COLOR = (255, 0, 0) if SIDE == 'idos' else (0, 0, 255)
THICKNESS = -0.020 if SIDE == 'idos' else +0.020

# ==============================================================================
# Fabric layer from extended base
# ==============================================================================

FABRIC = BASE.copy()
mesh_flip_cycles(FABRIC)

for key in BASE.vertices():
    normal = BASE.vertex_normal(key)
    xyz = BASE.vertex_coordinates(key)
    offset = scale_vector(normal, THICKNESS)
    point = add_vectors(xyz, offset)
    FABRIC.set_vertex_attributes(key, 'xyz', point)

# ==============================================================================
# Triangulate
# ==============================================================================

RING = [
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '01'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '02'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '03'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '04'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '05'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '06'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '07'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '08'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '09'})),
    list(FABRIC.faces_where({'panel': 'RING', 'strip': '10'})),
]

RING_sorted = []

for faces in RING:
    strip = sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count'))
    RING_sorted.append(strip)

split_ring(RING_sorted[2])
split_ring(RING_sorted[3])
split_ring(RING_sorted[4])
split_ring(RING_sorted[5])
split_ring(RING_sorted[6])
split_ring(RING_sorted[7])
split_ring(RING_sorted[8])

RING_triangulated = triangulate_strips(RING_sorted)

# ==============================================================================
# Unroll
# ==============================================================================

RING_unrolled = [
    unroll(RING_triangulated[0], (359, 411)),
    unroll(RING_triangulated[1], (359, 360)),
    unroll(RING_triangulated[2], (445, 446)),
    unroll(RING_triangulated[3], (444, 445)),
    unroll(RING_triangulated[4], (443, 444)),
    unroll(RING_triangulated[5], (442, 443)),
    unroll(RING_triangulated[6], (441, 442)),
    unroll(RING_triangulated[7], (440, 441)),
    unroll(RING_triangulated[8], (439, 440)),
    unroll(RING_triangulated[9], (356, 358)),
    unroll(RING_triangulated[10], (356, 394)),
]

for mesh in RING_unrolled:
    fkey = mesh.get_any_face()
    panel = mesh.get_face_attribute(fkey, 'panel')
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = '{}-{}'.format(panel, strip.zfill(2))

# ==============================================================================
# Visualize
# ==============================================================================

mesh = RING_unrolled[3]

points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
polygons = [{'points': offset_polygon(points, SEEM)}]

fkey = list(mesh.faces_where({'count': 0}))[0]
facecolor = {fkey: COLOR}

PLOTTER = MeshPlotter(mesh, figsize=(10, 7))
PLOTTER.draw_polygons(polygons)
PLOTTER.draw_faces(
    text={fkey: "{}".format(str(attr['count']).zfill(2)) for fkey, attr in mesh.faces(True)},
    facecolor=facecolor)
PLOTTER.draw_edges()
PLOTTER.show()

# ==============================================================================
# Export
# ==============================================================================

# for mesh in RING_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# ==============================================================================
# Visualize 
# ==============================================================================

# ARTIST = ShellArtist(None)

# for mesh in RING_unrolled:
#     points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
#     polygon = offset_polygon(points, SEEM)
#     polygons = [{'points': polygon + polygon[:1]}]

#     ARTIST.mesh = mesh
#     ARTIST.layer = "Unrolled::{}::{}".format(SIDE, mesh.attributes['name'])
#     ARTIST.clear_layer()
#     ARTIST.draw_faces()
#     ARTIST.draw_facelabels(text={key: "{}".format(attr['count']) for key, attr in mesh.faces(True)})
#     ARTIST.draw_polygons(polygons)
