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
# from compas_plotters import MeshPlotter
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellHelper
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Helpers
# ==============================================================================

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
FILE_I = os.path.join(DATA, 'fabric.json')

BASE = Shell.from_json(FILE_I)
mesh_flip_cycles(BASE)

SIDE = 'edos'
SEEM = -0.020

COLOR = (255, 0, 0) if SIDE == 'idos' else (0, 0, 255)
THICKNESS = -0.020 if SIDE == 'idos' else +0.020

# ==============================================================================
# Fabric layer from extended dual
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
# Identify strips
# ==============================================================================

SOUTH = [
    list(FABRIC.faces_where({'panel': 'SOUTH', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'SOUTH', 'strip': '01'})),
    list(FABRIC.faces_where({'panel': 'SOUTH', 'strip': '02'})),
    list(FABRIC.faces_where({'panel': 'SOUTH', 'strip': '03'})),
    list(FABRIC.faces_where({'panel': 'SOUTH', 'strip': '04'}))]

WEST = [
    list(FABRIC.faces_where({'panel': 'WEST', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'WEST', 'strip': '01'})),
    list(FABRIC.faces_where({'panel': 'WEST', 'strip': '02'})),
    list(FABRIC.faces_where({'panel': 'WEST', 'strip': '03'})),
    list(FABRIC.faces_where({'panel': 'WEST', 'strip': '04'}))]

NORTH = [
    list(FABRIC.faces_where({'panel': 'NORTH', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'NORTH', 'strip': '01'})),
    list(FABRIC.faces_where({'panel': 'NORTH', 'strip': '02'})),
    list(FABRIC.faces_where({'panel': 'NORTH', 'strip': '03'})),
    list(FABRIC.faces_where({'panel': 'NORTH', 'strip': '04'}))]

SW = [
    list(FABRIC.faces_where({'panel': 'SW', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'WS', 'strip': '00'}))]

NW = [
    list(FABRIC.faces_where({'panel': 'WN', 'strip': '00'})),
    list(FABRIC.faces_where({'panel': 'NW', 'strip': '00'}))]

# ==============================================================================
# Sort faces
# ==============================================================================

SOUTH_sorted = [sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count')) for faces in SOUTH]
WEST_sorted = [sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count')) for faces in WEST]
NORTH_sorted = [sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count')) for faces in NORTH]
SW_sorted = [sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count')) for faces in SW]
NW_sorted = [sorted(faces, key=lambda fkey: FABRIC.get_face_attribute(fkey, 'count')) for faces in NW]

# ==============================================================================
# Triangulate
# ==============================================================================

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

# ==============================================================================
# Rename
# ==============================================================================

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
# Plot (for checking)
# ==============================================================================

# mesh = WEST_unrolled[0]

# points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
# polygons = [{'points': offset_polygon(points, SEEM)}]

# fkey = list(mesh.faces_where({'count': 0}))[0]
# facecolor = {fkey: COLOR}

# PLOTTER = MeshPlotter(mesh, figsize=(10, 7))
# PLOTTER.draw_polygons(polygons)
# PLOTTER.draw_faces(
#     text={fkey: "{}".format(str(attr['count']).zfill(2)) for fkey, attr in mesh.faces(True)},
#     facecolor=facecolor)
# PLOTTER.draw_edges()
# PLOTTER.show()

# ==============================================================================
# Export
# ==============================================================================

# for mesh in SOUTH_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# for mesh in WEST_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# for mesh in NORTH_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# for mesh in SW_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# for mesh in NW_unrolled:
#     path = os.path.join(DATA, 'FABRIC', 'unrolled', SIDE, "{}.json".format(mesh.attributes['name']))
#     mesh.to_json(path)

# ==============================================================================
# Visualize
# ==============================================================================

ARTIST = ShellArtist(None)

for mesh in SOUTH_unrolled:
    points = [mesh.vertex_coordinates(key) for key in mesh.vertices_on_boundary(ordered=True)]
    polygon = offset_polygon(points, SEEM)
    polygons = [{'points': polygon + polygon[:1]}]

    ARTIST.mesh = mesh
    ARTIST.layer = "Unrolled::{}::{}".format(SIDE, mesh.attributes['name'])
    ARTIST.clear_layer()
    ARTIST.draw_faces()
    ARTIST.draw_facelabels(text={key: "{}".format(attr['count']) for key, attr in mesh.faces(True)})
    ARTIST.draw_polygons(polygons)
