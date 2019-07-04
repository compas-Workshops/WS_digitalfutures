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


def unroll(zone):
    unrolled = []
    for quadmesh, trimesh in zone:
        flatmesh = trimesh.copy()
        fkeys = list(trimesh.faces_where({'count': 0}))

        for fkey in fkeys:
            nbrs = trimesh.face_neighbors(fkey)
            if len(nbrs) == 1:
                root = fkey
                break
            root = None

        for key in trimesh.face_vertices(root):
            if trimesh.vertex_degree(key) == 2:
                corner = key
                break
            corner = None

        u = corner
        v = trimesh.face_vertex_descendant(root, u)

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

        tovisit = deque([root])
        visited = set([root])
        while tovisit:
            fkey = tovisit.popleft()
            for u, v in trimesh.face_halfedges(fkey):
                nbr = trimesh.halfedge[v][u]
                if nbr is None:
                    continue
                if nbr in visited:
                    continue
                tovisit.append(nbr)
                visited.add(nbr)

                origin = trimesh.vertex_coordinates(v)
                zaxis = trimesh.face_normal(nbr, unitized=True)
                xaxis = normalize_vector(trimesh.edge_direction(v, u))
                yaxis = normalize_vector(cross_vectors(xaxis, zaxis))
                frame = Frame(origin, xaxis, yaxis)

                origin = flatmesh.vertex_coordinates(v)
                zaxis = [0, 0, 1.0]
                xaxis = normalize_vector(flatmesh.edge_direction(v, u))
                yaxis = normalize_vector(cross_vectors(xaxis, zaxis))
                frame_to = Frame(origin, xaxis, yaxis)

                T = Transformation.from_frame_to_frame(frame, frame_to)
                w = trimesh.face_vertex_ancestor(nbr, v)
                x, y, z = trimesh.vertex_coordinates(w)
                point = Point(x, y, z)
                point.transform(T)
                flatmesh.set_vertex_attributes(w, 'xyz', point)

        for key, attr in quadmesh.vertices(True):
            x, y, z = flatmesh.vertex_coordinates(key)
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

        unrolled.append(quadmesh)

    return unrolled


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

SOUTH = [
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '04'})),
]

WEST = [
    list(fabric.faces_where({'panel': 'WEST', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '04'})),
]

NORTH = [
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '04'})),
]

SW = [
    list(fabric.faces_where({'panel': 'SW', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'WS', 'strip': '00'})),
]

NW = [
    list(fabric.faces_where({'panel': 'WN', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'NW', 'strip': '00'})),
]

print(len(SW[0]))
print(len(NW[0]))

SOUTH_sorted = []
WEST_sorted = []
NORTH_sorted = []
SW_sorted = []
NW_sorted = []

for faces in SOUTH:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
    SOUTH_sorted.append(strip)

for faces in WEST:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
    WEST_sorted.append(strip)

for faces in NORTH:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
    NORTH_sorted.append(strip)

for faces in SW:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
    SW_sorted.append(strip)

for faces in NW:
    strip = sorted(faces, key=lambda fkey: fabric.get_face_attribute(fkey, 'count'))
    NW_sorted.append(strip)

SOUTH_triangulated = triangulate_strips(SOUTH_sorted)
WEST_triangulated = triangulate_strips(WEST_sorted)
NORTH_triangulated = triangulate_strips(NORTH_sorted)
SW_triangulated = triangulate_strips(SW_sorted)
NW_triangulated = triangulate_strips(NW_sorted)

# ==============================================================================
# Unroll
# ==============================================================================

SOUTH_unrolled = unroll(SOUTH_triangulated)
WEST_unrolled = unroll(WEST_triangulated)
NORTH_unrolled = unroll(NORTH_triangulated)
SW_unrolled = unroll(SW_triangulated)
NW_unrolled = unroll(NW_triangulated)

for mesh in SOUTH_unrolled:
    fkey = mesh.get_any_face()
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = 'SOUTH-{}'.format(strip.zfill(2))

for mesh in WEST_unrolled:
    fkey = mesh.get_any_face()
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = 'WEST-{}'.format(strip.zfill(2))

for mesh in NORTH_unrolled:
    fkey = mesh.get_any_face()
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = 'NORTH-{}'.format(strip.zfill(2))

for mesh in SW_unrolled:
    fkey = mesh.get_any_face()
    panel = mesh.get_face_attribute(fkey, 'panel')
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = '{}-{}'.format(panel, strip.zfill(2))

for mesh in NW_unrolled:
    fkey = mesh.get_any_face()
    strip = mesh.get_face_attribute(fkey, 'strip')
    panel = mesh.get_face_attribute(fkey, 'panel')
    strip = mesh.get_face_attribute(fkey, 'strip')
    mesh.attributes['name'] = '{}-{}'.format(panel, strip.zfill(2))

# ==============================================================================
# Visualize
# ==============================================================================

plotter = MeshPlotter(None, figsize=(10, 7))

mesh = WEST_unrolled[0]

points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
polygon = offset_polygon(points, -0.020)

polygons = []
polygons.append({
    'points': polygon
})

fkey = list(mesh.faces_where({'count': 0}))[0]
normal = mesh.face_normal(fkey)

facecolor = {}
facecolor[fkey] = (255, 0, 0) if normal[2] > 0 else (0, 0, 255) 

plotter.mesh = mesh
plotter.draw_polygons(polygons)
plotter.draw_faces(
    text={fkey: "{}".format(str(attr['count']).zfill(2)) for fkey, attr in mesh.faces(True)},
    facecolor=facecolor)
plotter.draw_edges()

plotter.show()

# ==============================================================================
# Export
# ==============================================================================

for mesh in SOUTH_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in WEST_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in NORTH_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in SW_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in NW_unrolled:
    path = os.path.join(DATA, 'fabric', 'unrolled', 'idos', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)
