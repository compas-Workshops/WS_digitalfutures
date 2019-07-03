from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas.utilities import pairwise
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import cross_vectors

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist


def framelines(origin, xaxis, yaxis, zaxis, name):
    lines = []
    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(xaxis, 0.1)),
        'color' : (255, 0, 0),
        'name'  : "{}.X".format(name)
    })
    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(yaxis, 0.1)),
        'color' : (0, 255, 0),
        'name'  : "{}.Y".format(name)
    })
    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(zaxis, 0.1)),
        'color' : (0, 0, 255),
        'name'  : "{}.Z".format(name)
    })
    return lines


# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Beam vertices
# ==============================================================================

beams = [
    [268, 258, 115, 106, 114, 269, 281, 145],
    [5, 57, 4, 259, 278, 54, 268],
    [116, 261, 282, 60, 79, 52, 260, 5],
    [145, 8, 144, 272, 175, 13, 164],
    [147, 9, 146, 270, 117, 107, 116],
    [177, 273, 234, 36, 235, 280, 7, 164],
    [147, 279, 276, 226, 32, 227, 275, 192],
    [192, 30, 223, 274, 176, 14, 177]
]

POINTS = []
LINES = []

# ==============================================================================
# Horizontal clamps
# ==============================================================================

# for keys in horizontal:
#     p1 = shell.vertex_coordinates(keys[1])
#     p0 = shell.vertex_coordinates(keys[0])
#     xaxis = subtract_vectors(p1, p0)
#     zaxis = [0, 0, 1.0]
#     yaxis = cross_vectors(zaxis, xaxis)

#     offset = 0.040
#     normal = normalize_vector(yaxis)
#     origin = add_vectors(p0, scale_vector(normal, offset))
#     plane = (origin, normal)

#     points = []
#     for key in keys:
#         a = shell.vertex_coordinates(key)
#         r = shell.get_vertex_attributes(key, ['rx', 'ry', 'rz'])
#         b = add_vectors(a, r)

#         line = a, b
#         x = intersection_line_plane(line, plane)

#         points.append(x)
#         POINTS.append({
#             'pos'   : x,
#             'color' : (0, 0, 255),
#             'name'  : "{}.{}.extensions".format(shell.name, key)
#         })

# ==============================================================================
# Vetical clamps
# ==============================================================================

for keys in beams:
    vectors = [shell.get_vertex_attributes(key, ['rx', 'ry', 'rz']) for key in keys[1:-1]]
    average = [-sum(axis) / len(vectors) for axis in zip(*vectors)]
    average = normalize_vector(average)
    print(average)

    a = shell.vertex_coordinates(keys[0])
    b = shell.vertex_coordinates(keys[1])

    xaxis = normalize_vector(subtract_vectors(b, a))
    zaxis = normalize_vector(cross_vectors(xaxis, average))
    yaxis = normalize_vector(cross_vectors(zaxis, xaxis))

    origin = shell.vertex_coordinates(keys[0])

    LINES += framelines(origin, xaxis, yaxis, zaxis, 'frame')

    offset = 0.040
    normal = yaxis
    origin = add_vectors(origin, scale_vector(normal, offset))
    plane = (origin, normal)

    points = []
    for key in keys:
        a = shell.vertex_coordinates(key)
        r = shell.get_vertex_attributes(key, ['rx', 'ry', 'rz'])
        b = add_vectors(a, r)

        line = a, b
        x = intersection_line_plane(line, plane)

        points.append(x)
        POINTS.append({
            'pos'   : x,
            'color' : (0, 0, 255),
            'name'  : "{}.{}.extensions".format(shell.name, key)
        })

# ==============================================================================
# Export
# ==============================================================================

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(shell, layer="Scaffolding::Clamp::Points")
artist.clear_layer()
artist.draw_points(POINTS)
artist.draw_lines(LINES)
artist.redraw()
