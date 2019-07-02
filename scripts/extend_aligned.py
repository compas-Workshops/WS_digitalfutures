from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.utilities import pairwise
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import Frame
from compas.geometry import bounding_box
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.rpc import Proxy

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

numerical = Proxy('compas.numerical')

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

keys = [268, 258, 115, 106, 114, 269, 281, 145]

p1 = shell.vertex_coordinates(keys[1])
p0 = shell.vertex_coordinates(keys[0])
xaxis = subtract_vectors(p1, p0)
zaxis = [0, 0, 1.0]
yaxis = cross_vectors(zaxis, xaxis)

offset = 0.5
normal = normalize_vector(yaxis)
origin = add_vectors(p0, scale_vector(normal, offset))
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

result = numerical.pca_numpy(points)

print(result[0])
print(result[1])
print(result[2])

lines = []
a = result[0][0]
for axis in result[1]:
    b = add_vectors(a, axis)
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
