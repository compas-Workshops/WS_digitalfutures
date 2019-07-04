from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs

import os
import compas
import compas_fofin
from compas.utilities import pairwise
from compas.geometry import add_vectors
from compas.datastructures import mesh_dual
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist
from compas_fofin.rhino import ShellHelper

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data-extended-strips-split.json')
FILE_O = os.path.join(DATA, 'data-extended-strips-split.json')

fabric = Shell.from_json(FILE_I)

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(fabric, layer="Fabric::SplitCorners")
artist.clear_layer()
artist.draw_vertices()
artist.draw_faces()
artist.draw_edges()
artist.redraw()

# ==============================================================================
# Assign strips
# ==============================================================================

while True:
    edge = ShellHelper.select_edge(fabric)
    if not edge:
        break
    u, v = edge
    fkey = fabric.halfedge[u][v]
    if fkey is None:
        fkey = fabric.halfedge[v][u]
    if fkey is None:
        print('Edge not on the boundary.')
        continue
    faces = ShellHelper.select_face_strip(fabric, fkey)
    panel = rs.GetString('Panel')
    number = rs.GetString('Strip number')
    for i, fkey in enumerate(faces):
        fabric.set_face_attribute(fkey, 'panel', panel)
        fabric.set_face_attribute(fkey, 'strip', number)
        fabric.set_face_attribute(fkey, 'count', i)

# ==============================================================================
# Export
# ==============================================================================

fabric.to_json(FILE_O)
