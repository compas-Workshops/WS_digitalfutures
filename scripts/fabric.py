from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import rhinoscriptsyntax as rs

from compas.datastructures import Mesh
from compas.datastructures import mesh_flip_cycles
from compas_rhino.artists import MeshArtist
from compas.geometry import add_vectors
from compas.geometry import scale_vector

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'fabric.json')

fabric = Mesh.from_json(FILE_I)
fabric.name = 'Fabric'

mesh_flip_cycles(fabric)

# ==============================================================================
# Offsets
# ==============================================================================

thickness = 0.04

edos = fabric.copy()
idos = fabric.copy()

edos.name = 'Extrados'
idos.name = 'Intrados'

for key in fabric.vertices():
    normal = fabric.vertex_normal(key)
    xyz = fabric.vertex_coordinates(key)

    xyz_e = add_vectors(xyz, scale_vector(normal, +0.5 * thickness))
    xyz_i = add_vectors(xyz, scale_vector(normal, -0.5 * thickness))

    edos.set_vertex_attributes(key, 'xyz', xyz_e)
    idos.set_vertex_attributes(key, 'xyz', xyz_i)

mesh_flip_cycles(idos)

# ==============================================================================
# Identify strips
# ==============================================================================

SOUTH = [
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'SOUTH', 'strip': '04'}))]

WEST = [
    list(fabric.faces_where({'panel': 'WEST', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'WEST', 'strip': '04'}))]

NORTH = [
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '01'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '02'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '03'})),
    list(fabric.faces_where({'panel': 'NORTH', 'strip': '04'}))]

SW = [
    list(fabric.faces_where({'panel': 'SW', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'WS', 'strip': '00'}))]

NW = [
    list(fabric.faces_where({'panel': 'WN', 'strip': '00'})),
    list(fabric.faces_where({'panel': 'NW', 'strip': '00'}))]

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

# ==============================================================================
# Visualise
# ==============================================================================

artist = MeshArtist(fabric, layer="Fabric")
artist.clear_layer()

strips = SOUTH + SW + WEST + NW + NORTH + RING

artist.layer = "Fabric::Intrados"
artist.mesh = idos

for i in range(0, len(strips), 2):
    guid = artist.draw_faces(keys=strips[i], join_faces=True)
    rs.ObjectColor(guid, (255, 0, 0))

for i in range(1, len(strips), 2):
    guid = artist.draw_faces(keys=strips[i], join_faces=True)
    rs.ObjectColor(guid, (255, 128, 128))

artist.layer = "Fabric::Normals"
artist.draw_facenormals(color=(255, 0, 0), scale=0.05)

artist.layer = "Fabric::Extrados"
artist.mesh = edos

for i in range(0, len(strips), 2):
    guid = artist.draw_faces(keys=strips[i], join_faces=True)
    rs.ObjectColor(guid, (0, 0, 255))

for i in range(1, len(strips), 2):
    guid = artist.draw_faces(keys=strips[i], join_faces=True)
    rs.ObjectColor(guid, (128, 128, 255))

artist.layer = "Fabric::Normals"
artist.draw_facenormals(color=(0, 0, 255), scale=0.05)
