from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.utilities import pairwise
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import Frame
from compas.geometry import bounding_box

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

keys = [268, 258, 115, 106, 114, 269, 281, 145]
origin = [0, 2.5, 0]
normal = [0, 1.0, 0]
plane = (origin, normal)

points = []
rhinopoints = []
for key in keys:
    a = shell.vertex_coordinates(key)
    r = shell.get_vertex_attributes(key, ['rx', 'ry', 'rz'])
    b = add_vectors(a, r)
    line = a, b
    x = intersection_line_plane(line, plane)
    points.append(x)

    rhinopoints.append({
        'pos'   : x,
        'color' : (0, 0, 255),
        'name'  : "{}.{}.anchor".format(shell.name, key)
    })

box = bounding_box(points)

lines = []
for i, j in [(0, 1), (1, 5), (5, 4), (4, 0)]:
    a = box[i]
    b = box[j]
    d = distance_point_point(a, b)
    if d < 0.01:
        continue
    lines.append({
        'start' : a,
        'end'   : b,
        'color' : (0, 255, 255),
        'name'  : "box"
    })

artist = ShellArtist(shell, layer="Scaffolding::Points")
artist.clear_layer()
artist.draw_points(rhinopoints)
artist.draw_lines(lines)
artist.redraw()
