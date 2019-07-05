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
FILE_I1 = os.path.join(DATA, 'data.json')
FILE_I2 = os.path.join(DATA, 'fabric.json')

SHELL = Mesh.from_json(FILE_I1)
FABRIC = Mesh.from_json(FILE_I2)

SHELL.name = 'Shell'
FABRIC.name = 'Fabric'

mesh_flip_cycles(FABRIC)

THICKNESS = 0.04

# ==============================================================================
# Offsets
# ==============================================================================

EDOS = FABRIC.copy()
IDOS = FABRIC.copy()

EDOS.name = 'Extrados'
IDOS.name = 'Intrados'

for key in FABRIC.vertices():
    normal = FABRIC.vertex_normal(key)
    xyz = FABRIC.vertex_coordinates(key)

    xyz_e = add_vectors(xyz, scale_vector(normal, +0.5 * THICKNESS))
    xyz_i = add_vectors(xyz, scale_vector(normal, -0.5 * THICKNESS))

    EDOS.set_vertex_attributes(key, 'xyz', xyz_e)
    IDOS.set_vertex_attributes(key, 'xyz', xyz_i)

mesh_flip_cycles(IDOS)

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

STRIPS = SOUTH + SW + WEST + NW + NORTH + RING

# ==============================================================================
# Visualise
# ==============================================================================

ARTIST = MeshArtist(FABRIC, layer="Fabric")
ARTIST.clear_layer()

# INTRADOS

ARTIST.mesh = IDOS

ARTIST.layer = "Fabric::Intrados"

for i, strip in enumerate(STRIPS):
    guid = ARTIST.draw_faces(keys=strip, join_faces=True)
    color = (255, 128, 128) if i % 2 else (255, 0, 0)
    rs.ObjectColor(guid, color)

ARTIST.layer = "Fabric::Normals"
ARTIST.draw_facenormals(color=(255, 0, 0), scale=0.05)

# EXTRADOS

ARTIST.mesh = EDOS

ARTIST.layer = "Fabric::Extrados"

for i, strip in enumerate(STRIPS):
    guid = ARTIST.draw_faces(keys=strip, join_faces=True)
    color = (128, 128, 255) if i % 2 else (0, 0, 255)
    rs.ObjectColor(guid, color)

ARTIST.layer = "Fabric::Normals"
ARTIST.draw_facenormals(color=(0, 0, 255), scale=0.05)
