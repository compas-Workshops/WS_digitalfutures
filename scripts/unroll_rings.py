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


def split_ring(faces):
    fkey = faces[-1]
    for u, v in fabric.face_halfedges(fkey):
        if fabric.halfedge[v][u] == faces[0]:
            break
        else:
            u = None
            v = None
    if not u and not v:
        return
    a = fabric.vertex_coordinates(u)
    b = fabric.vertex_coordinates(v)
    uu = fabric.add_vertex(x=a[0], y=a[1], z=a[2])
    vv = fabric.add_vertex(x=b[0], y=b[1], z=b[2])
    vertices = fabric.face_vertices(fkey)
    i = vertices.index(u)
    j = vertices.index(v)
    vertices[i] = uu
    vertices[j] = vv
    for u, v in pairwise(vertices + vertices[:1]):
        fabric.halfedge[u][v] = fkey


def triangulate_strips(zone):
    meshes = []
    for faces in zone:
        mesh = Mesh()
        mesh.update_default_vertex_attributes(fabric.default_vertex_attributes)
        mesh.update_default_edge_attributes(fabric.default_edge_attributes)
        mesh.update_default_face_attributes(fabric.default_face_attributes)

        for fkey in faces:
            keys = fabric.face_vertices(fkey)
            for key in keys:
                if key not in mesh.vertex:
                    attr = fabric.vertex[key].copy()
                    mesh.add_vertex(key=key, attr_dict=attr)
            attr = fabric.facedata[fkey].copy()
            mesh.add_face(keys, fkey=fkey, attr_dict=attr)

        for u, v, attr in mesh.edges(True):
            for name in attr:
                value = fabric.get_edge_attribute((u, v), name)
                attr[name] = value

        trimesh = mesh.copy()
        mesh_quads_to_triangles(trimesh, check_angles=True)
        meshes.append([mesh, trimesh])

    return meshes


def unroll(quadmesh, trimesh, edge):
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
FILE_I = os.path.join(DATA, 'data-extended-strips-split.json')
FILE_O = os.path.join(DATA, 'data-extended-strips-split.json')

thickness = -0.02

dual = Shell.from_json(FILE_I)
fabric = dual.copy()
mesh_flip_cycles(fabric)

for key in dual.vertices():
    normal = dual.vertex_normal(key)
    xyz = dual.vertex_coordinates(key)
    offset = scale_vector(normal, thickness)
    point = add_vectors(xyz, offset)
    fabric.set_vertex_attributes(key, 'xyz', point)

# ==============================================================================
# Triangulate
# ==============================================================================

RING = [
    list(fabric.faces_where({'panel': 'RING', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '04'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '05'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '06'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '07'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '08'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '09'})),
    list(fabric.faces_where({'panel': 'RING', 'strip': '10'})),
]

RING_sorted = []

for faces in RING:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
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
    unroll(RING_triangulated[0][0], RING_triangulated[0][1], (359, 411)),
    unroll(RING_triangulated[1][0], RING_triangulated[1][1], (359, 360)),
    unroll(RING_triangulated[2][0], RING_triangulated[2][1], (445, 446)),
    unroll(RING_triangulated[3][0], RING_triangulated[3][1], (444, 445)),
    unroll(RING_triangulated[4][0], RING_triangulated[4][1], (443, 444)),
    unroll(RING_triangulated[5][0], RING_triangulated[5][1], (442, 443)),
    unroll(RING_triangulated[6][0], RING_triangulated[6][1], (441, 442)),
    unroll(RING_triangulated[7][0], RING_triangulated[7][1], (440, 441)),
    unroll(RING_triangulated[8][0], RING_triangulated[8][1], (439, 440)),
    unroll(RING_triangulated[9][0], RING_triangulated[9][1], (356, 358)),
    unroll(RING_triangulated[10][0], RING_triangulated[10][1], (356, 394)),
]

for mesh in RING_unrolled:
    fkey = mesh.get_any_face()
    panel = mesh.get_face_attribute(fkey, 'panel')
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = '{}-{}'.format(panel, strip.zfill(2))

# ==============================================================================
# Visualize
# ==============================================================================

# plotter = MeshPlotter(None, figsize=(10, 7))

# mesh = RING_unrolled[3]

# points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
# polygon = offset_polygon(points, -0.020)

# polygons = []
# polygons.append({
#     'points': polygon
# })

# fkey = list(mesh.faces_where({'count': 0}))[0]
# normal = mesh.face_normal(fkey)

# facecolor = {}
# facecolor[fkey] = (255, 0, 0) if normal[2] > 0 else (0, 0, 255) 

# plotter.mesh = mesh
# plotter.draw_polygons(polygons)
# plotter.draw_faces(
#     text={fkey: "{}".format(str(attr['count']).zfill(2)) for fkey, attr in mesh.faces(True)},
#     facecolor=facecolor)
# plotter.draw_edges()

# plotter.show()

# ==============================================================================
# Export
# ==============================================================================

for mesh in RING_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)
