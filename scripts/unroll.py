import os
import compas
import compas_hilo

from collections import deque

from functools import partial
from compas.geometry import Frame
from compas.geometry import Transformation
from compas.geometry import cross_vectors
from compas.geometry import normalize_vector
from compas.geometry import Point
from compas.utilities import flatten
from compas.utilities import pairwise
from compas.datastructures import Mesh
from compas.datastructures import mesh_quads_to_triangles
from compas.geometry import oriented_bounding_box_xy_numpy
from compas_plotters import MeshPlotter
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellHelper
from compas_fofin.rhino import ShellArtist

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', '..', 'data')

FILE_I = os.path.join(DATA, 'fabric-extended.json')
FILE_O = os.path.join(DATA, 'fabric-extended.json')

fabric = Shell.from_json(FILE_I)

zones = {
    "SOUTH": [1448, 1447, 1446, 1445, 1444, 1443, 1442, 1441, 1440, 1439, 1438],
    "WEST" : [1468, 1467, 1466, 1465, 1464, 1463, 1462, 1461],
    "NW"   : [1393, 1392, 1391, 1390, 1389, 1388, 1387],
    "NE"   : [1407, 1406, 1405, 1404, 1403, 1402, 1401],
    "EAST" : [1426, 1425, 1419, 1418, 1417, 1416, 1415]
}

# ==============================================================================
# Predicates
# ==============================================================================

def startswith_NAME(name, key, attr):
    strip = attr['strip']
    if not strip:
        return False
    return strip.startswith(name)


def endswith_NAME(name, key, attr):
    strip = attr['strip']
    if not strip:
        return False
    return strip.endswith(name)


def split_strips(zone):
    strips = []
    current = None
    for fkey in zone:
        name = fabric.get_face_attribute(fkey, 'strip')
        parts = name.split('-')
        strip = "-".join(parts[:-1])
        if current is None:
            current = strip
            strips.append([])
        if strip != current:
            current = strip
            strips.append([])
        strips[-1].append(fkey)
    return strips


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
        fkeys = list(trimesh.faces_where_predicate(partial(endswith_NAME, '-00')))
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
        origin = trimesh.vertex_coordinates(corner)
        zaxis = trimesh.face_normal(root, unitized=True)
        xaxis = trimesh.edge_direction(corner, trimesh.face_vertex_descendant(root, corner))
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
                xaxis = trimesh.edge_direction(v, u)
                yaxis = normalize_vector(cross_vectors(xaxis, zaxis))
                frame = Frame(origin, xaxis, yaxis)
                origin = flatmesh.vertex_coordinates(v)
                zaxis = [0, 0, 1]
                xaxis = flatmesh.edge_direction(v, u)
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


def postprocess(meshes):
    sectioncount = {}
    for mesh in meshes:
        fkey = mesh.get_any_face()
        strip = mesh.get_face_attribute(fkey, 'strip')
        parts = strip.split("-")
        zone = parts[0]
        row = parts[1]
        section = parts[2]
        name = "-".join(parts[:-1])
        mesh.attributes.update({
            'name'    : name,
            'zone'    : zone,
            'row'     : int(row),
            'section' : int(section)
        })
        if int(row) not in sectioncount:
            sectioncount[int(row)] = 0
        sectioncount[int(row)] += 1

    for mesh in meshes:
        mesh.update_default_edge_attributes({'flap': None})
        mesh.set_edges_attribute('flap', None)
        boundary = list(mesh.edges_on_boundary())
        mesh.set_edges_attribute('flap', 'normal', keys=boundary)

        fkeys = sorted(mesh.faces(), key=lambda fkey: mesh.get_face_attribute(fkey, 'strip'))

        f0 = fkeys[0]
        f1 = fkeys[1]
        for u, v in mesh.face_halfedges(f0):
            nbr = mesh.halfedge[v][u]
            if nbr == f1:
                break
            u = None
            v = None
        if u is None or v is None:
            raise Exception('this should not happen.')
        vertices = mesh.face_vertices(f0)
        i = vertices.index(u)
        topleft = vertices[i - 2]
        bottomleft = vertices[i - 1]

        f0 = fkeys[-1]
        f1 = fkeys[-2]
        for u, v in mesh.face_halfedges(f0):
            nbr = mesh.halfedge[v][u]
            if nbr == f1:
                break
            u = None
            v = None
        if u is None or v is None:
            raise Exception('this should not happen.')
        vertices = mesh.face_vertices(f0)
        i = vertices.index(u)
        topright = vertices[i - 1]
        bottomright = vertices[i - 2]

        corners = [topleft, bottomleft, bottomright, topright]
        mesh.attributes.update({
            'corners' : corners
        })

        if mesh.attributes['row'] == 0:
            boundary = list(mesh.vertices_on_boundary(ordered=True))
            i = boundary.index(corners[0])
            j = boundary.index(corners[-1])
            if j < i:
                top = boundary[i:] + boundary[:j + 1]
            else:
                top = boundary[i:j + 1]
            for u, v in pairwise(top):
                mesh.set_edge_attribute((u, v), 'flap', 'coldjoint')

        if mesh.attributes['section'] == 0:
            mesh.set_edge_attribute((topleft, bottomleft), 'flap', 'boundary')

        if mesh.attributes['section'] == sectioncount[mesh.attributes['row']] - 1:
            mesh.set_edge_attribute((topright, bottomright), 'flap', 'boundary')

startswith_SOUTH = partial(startswith_NAME, 'SOUTH')
startswith_WEST  = partial(startswith_NAME, 'WEST')
startswith_NW    = partial(startswith_NAME, 'NW')
startswith_NE    = partial(startswith_NAME, 'NE')
startswith_EAST  = partial(startswith_NAME, 'EAST')

SOUTH = list(fabric.faces_where_predicate(startswith_SOUTH))
WEST  = list(fabric.faces_where_predicate(startswith_WEST))
NW    = list(fabric.faces_where_predicate(startswith_NW))
NE    = list(fabric.faces_where_predicate(startswith_NE))
EAST  = list(fabric.faces_where_predicate(startswith_EAST))

fabric.set_faces_attribute(SOUTH, 'zone', 'SOUTH')
fabric.set_faces_attribute(WEST, 'zone', 'WEST')
fabric.set_faces_attribute(NW, 'zone', 'NW')
fabric.set_faces_attribute(NE, 'zone', 'NE')
fabric.set_faces_attribute(EAST, 'zone', 'EAST')

sorted_SOUTH = sorted(SOUTH, key=lambda fkey: fabric.get_face_attribute(fkey, 'strip'))
sorted_WEST  = sorted(WEST, key=lambda fkey: fabric.get_face_attribute(fkey, 'strip'))
sorted_NW    = sorted(NW, key=lambda fkey: fabric.get_face_attribute(fkey, 'strip'))
sorted_NE    = sorted(NE, key=lambda fkey: fabric.get_face_attribute(fkey, 'strip'))
sorted_EAST  = sorted(EAST, key=lambda fkey: fabric.get_face_attribute(fkey, 'strip'))

strips_SOUTH = split_strips(sorted_SOUTH)
strips_WEST = split_strips(sorted_WEST)
strips_NW = split_strips(sorted_NW)
strips_NE = split_strips(sorted_NE)
strips_EAST = split_strips(sorted_EAST)

meshes_SOUTH = triangulate_strips(strips_SOUTH)
meshes_WEST = triangulate_strips(strips_WEST)
meshes_NW = triangulate_strips(strips_NW)
meshes_NE = triangulate_strips(strips_NE)
meshes_EAST = triangulate_strips(strips_EAST)

unrolled_SOUTH = unroll(meshes_SOUTH)
unrolled_WEST = unroll(meshes_WEST)
unrolled_NW = unroll(meshes_NW)
unrolled_NE = unroll(meshes_NE)
unrolled_EAST = unroll(meshes_EAST)

# ==============================================================================
# Post-process
# ==============================================================================

postprocess(unrolled_SOUTH)
postprocess(unrolled_WEST)
postprocess(unrolled_NW)
postprocess(unrolled_NE)
postprocess(unrolled_EAST)

# ==============================================================================
# Visualize
# ==============================================================================

plotter = MeshPlotter(None, figsize=(10, 7))

mesh = unrolled_SOUTH[0]
bbox = oriented_bounding_box_xy_numpy(mesh.get_vertices_attributes('xyz'))
points = []
lines = []
for index, (x, y) in enumerate(bbox[0]):
    point = Point(x, y, 0)
    points.append({
        'pos'    : point,
        'radius' : 0.01,
    })
for u, v in pairwise(bbox[0] + bbox[0][:1]):
    lines.append({
        'start' : u,
        'end'   : v,
        'width' : 0.1
    })

plotter.mesh = mesh
plotter.draw_vertices(
    keys=mesh.attributes['corners'],
    radius=0.05,
    text='key')
plotter.draw_faces()
plotter.draw_points(points)
plotter.draw_lines(lines)

coldjoint = list(mesh.edges_where({'flap' : 'coldjoint'}))
boundary = list(mesh.edges_where({'flap' : 'boundary'}))
edges =  coldjoint + boundary

plotter.draw_edges(
    keys=edges,
    color={key: '#ff0000' for key in boundary})

plotter.show()

# ==============================================================================
# Export
# ==============================================================================

for mesh in unrolled_SOUTH:
    path = os.path.join(DATA, 'unrolled', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in unrolled_WEST:
    path = os.path.join(DATA, 'unrolled', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in unrolled_NW:
    path = os.path.join(DATA, 'unrolled', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in unrolled_NE:
    path = os.path.join(DATA, 'unrolled', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)

for mesh in unrolled_EAST:
    path = os.path.join(DATA, 'unrolled', "{}.json".format(mesh.attributes['name']))
    mesh.to_json(path)
