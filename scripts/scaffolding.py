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
from compas.geometry import bounding_box_xy
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import offset_polygon
from compas.rpc import Proxy

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

NUMERICAL = Proxy('compas.numerical')

# ==============================================================================
# Helpers
# ==============================================================================

def framelines(origin, xaxis, yaxis, zaxis, name):
    lines = []

    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(xaxis, 0.1)),
        'color' : (255, 0, 0),
        'name'  : "{}.X".format(name)})

    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(yaxis, 0.1)),
        'color' : (0, 255, 0),
        'name'  : "{}.Y".format(name)})

    lines.append({
        'start' : origin,
        'end'   : add_vectors(origin, scale_vector(zaxis, 0.1)),
        'color' : (0, 0, 255),
        'name'  : "{}.Z".format(name)})

    return lines


def beam_plane(beam):
    p1 = SHELL.vertex_coordinates(beam[1])
    p0 = SHELL.vertex_coordinates(beam[0])
    xaxis = subtract_vectors(p1, p0)
    yaxis = cross_vectors(ZAXIS, xaxis)
    normal = normalize_vector(yaxis)
    origin = add_vectors(p0, scale_vector(normal, OFFSET))
    return origin, normal

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

SHELL = Shell.from_json(FILE_I)

# ==============================================================================
# Beam vertices
# ==============================================================================

BEAMS = [
    [268, 258, 115, 106, 114, 269, 281, 145],
    [57, 4, 259, 278, 54],
    [116, 261, 282, 60, 79, 52, 260, 5],
    [146, 270, 117, 107],
    [8, 144, 272, 175]]

OFFSET = 0.5
ZAXIS = [0, 0, 1.0]

NORTH = beam_plane(BEAMS[0])
WEST = beam_plane(BEAMS[1])
SOUTH = beam_plane(BEAMS[2])

PLANES = [
    NORTH,
    WEST,
    SOUTH,
    SOUTH,
    NORTH]

# ==============================================================================
# Horizontal BEAMS
# ==============================================================================

LINES = []
POINTS = []
POLYGONS = []
FRAMES = []

for i, keys in enumerate(BEAMS):
    plane = PLANES[i]

    points = []
    for key in keys:
        a = SHELL.vertex_coordinates(key)
        r = SHELL.get_vertex_attributes(key, ['rx', 'ry', 'rz'])
        b = add_vectors(a, r)

        line = a, b
        x = intersection_line_plane(line, plane)
        direction = normalize_vector(subtract_vectors(a, x))

        points.append(x)

        POINTS.append({
            'pos'   : x,
            'color' : (0, 0, 0),
            'name'  : "{}.{}.anchor".format(SHELL.name, key)})

        x0 = x
        x1 = add_vectors(x0, scale_vector(direction, 0.040))
        x2 = add_vectors(x1, scale_vector(direction, 0.300))
        x3 = add_vectors(x2, scale_vector(direction, 0.100))
        x4 = a

        LINES.append({
            'start' : x0,
            'end'   : x1,
            'color' : (0, 0, 0),
            'name'  : "{}.anchor-ring".format(key)})

        LINES.append({
            'start' : x1,
            'end'   : x2,
            'color' : (255, 255, 255),
            'name'  : "{}.turn-buckle".format(key)})

        LINES.append({
            'start' : x2,
            'end'   : x3,
            'color' : (0, 0, 0),
            'name'  : "{}.sock".format(key)})

        LINES.append({
            'start' : x3,
            'end'   : x4,
            'color' : (255, 255, 255),
            'name'  : "{}.extra".format(key)})

    result = NUMERICAL.pca_numpy(points)

    origin = result[0][0]
    xaxis  = normalize_vector(result[1][0])
    yaxis  = normalize_vector(result[1][1])
    zaxis  = normalize_vector(result[1][2])
    frame = Frame(origin, xaxis, yaxis)

    if yaxis[2] > 0:
        offset = scale_vector(zaxis, -0.050)
    else:
        offset = scale_vector(zaxis, +0.050)

    points_xy = [frame.represent_point_in_local_coordinates(point) for point in points]
    box_xy = bounding_box_xy(points_xy)
    box = [frame.represent_point_in_global_coordinates(corner_xy)[:] for corner_xy in box_xy]
    box1 = offset_polygon(box, -0.025)
    box2 = [add_vectors(point, offset) for point in box1]

    POLYGONS.append({
        'points': box1 + box1[:1],
        'color' : (0, 0, 0)})

    POLYGONS.append({
        'points': box2 + box2[:1],
        'color' : (0, 0, 0)})

    POLYGONS.append({
        'points': [box1[0], box1[3], box2[3], box2[0], box1[0]],
        'color' : (0, 0, 0)})

    POLYGONS.append({
        'points': [box1[1], box2[1], box2[2], box1[2], box1[1]],
        'color' : (0, 0, 0)})

    FRAMES += framelines(origin, xaxis, yaxis, zaxis, 'box')

# ==============================================================================
# Visualize
# ==============================================================================

ARTIST = ShellArtist(SHELL, layer="Scaffolding")
ARTIST.clear_layer()

ARTIST.layer = "Scaffolding::Anchors"
ARTIST.clear_layer()
ARTIST.draw_points(POINTS)

ARTIST.layer = "Scaffolding::Connectors"
ARTIST.clear_layer()
ARTIST.draw_lines(LINES)

ARTIST.layer = "Scaffolding::Beams"
ARTIST.clear_layer()
ARTIST.draw_polygons(POLYGONS)

ARTIST.layer = "Scaffolding::Frames"
ARTIST.clear_layer()
ARTIST.draw_lines(FRAMES)
