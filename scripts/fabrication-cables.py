from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from openpyxl import Workbook

from compas.utilities import pairwise
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import intersection_line_plane
from compas.geometry import Frame
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import offset_polygon

from compas_fofin.datastructures import Shell


def append_to_sheet(sheet, beamA, beamB):
    for u in beamA:
        nbrs = shell.vertex_neighbors(u)
        v = None
        for nbr in nbrs:
            if nbr in boundary:
                continue
            v = nbr
            break
        if v is None:
            continue
        edges = shell.get_continuous_edges((u, v), directed=False)
        last = edges[-1][1]
        if last in beamB:
            values = LENGTHS[u][:]
            values += [shell.edge_length(u, v) for u, v in edges]
            values += LENGTHS[last][::-1]
            accumulated = []
            value = 0
            for v in values:
                value += v
                accumulated.append(value)
            sheet.append([u] + [round(1e3 * v, 1) for v in accumulated])
        else:
            values = LENGTHS[u][:]
            values += [shell.edge_length(u, v) for u, v in edges[:-1]]
            values += [shell.edge_length(* edges[-1]) - 0.100]
            values += [0.100, 0.100]
            accumulated = []
            value = 0
            for v in values:
                value += v
                accumulated.append(value)
            sheet.append([u] + [round(1e3 * v, 1) for v in accumulated])


# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')
FILE_O = os.path.join(DATA, 'data-fabrication-cables.xlsx')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Beam vertices
# ==============================================================================

beams = [
    [268, 258, 115, 106, 114, 269, 281, 145],
    [57, 4, 259, 278, 54],
    [116, 261, 282, 60, 79, 52, 260, 5],
    [146, 270, 117, 107],
    [8, 144, 272, 175],
]

offset = 0.5
zaxis = [0, 0, 1.0]

p1 = shell.vertex_coordinates(beams[0][1])
p0 = shell.vertex_coordinates(beams[0][0])
xaxis = subtract_vectors(p1, p0)
yaxis = cross_vectors(zaxis, xaxis)
normal = normalize_vector(yaxis)
origin = add_vectors(p0, scale_vector(normal, offset))
NORTH = (origin, normal)

p1 = shell.vertex_coordinates(beams[1][1])
p0 = shell.vertex_coordinates(beams[1][0])
xaxis = subtract_vectors(p1, p0)
yaxis = cross_vectors(zaxis, xaxis)
normal = normalize_vector(yaxis)
origin = add_vectors(p0, scale_vector(normal, offset))
WEST = (origin, normal)

p1 = shell.vertex_coordinates(beams[2][1])
p0 = shell.vertex_coordinates(beams[2][0])
xaxis = subtract_vectors(p1, p0)
yaxis = cross_vectors(zaxis, xaxis)
normal = normalize_vector(yaxis)
origin = add_vectors(p0, scale_vector(normal, offset))
SOUTH = (origin, normal)

planes = [
    NORTH,
    WEST,
    SOUTH,
    SOUTH,
    NORTH
]

# ==============================================================================
# Horizontal beams
# ==============================================================================

LENGTHS = {}

for i, keys in enumerate(beams):
    plane = planes[i]

    points = []
    for key in keys:
        a = shell.vertex_coordinates(key)
        r = shell.get_vertex_attributes(key, ['rx', 'ry', 'rz'])
        b = add_vectors(a, r)

        line = a, b
        x = intersection_line_plane(line, plane)
        direction = normalize_vector(subtract_vectors(a, x))

        points.append(x)

        x0 = x
        x1 = add_vectors(x0, scale_vector(direction, 0.040))
        x2 = add_vectors(x1, scale_vector(direction, 0.300))
        x3 = add_vectors(x2, scale_vector(direction, 0.100))
        x4 = a

        LENGTHS[key] = [
            0.1,
            distance_point_point(x2, x3),
            distance_point_point(x3, x4),
        ]

# ==============================================================================
# Export
# ==============================================================================

wb = Workbook()

boundary = set(shell.vertices_on_boundary())

beamS = [116, 261, 282, 60, 79, 52, 260, 5]
beamW = [57, 4, 259, 278, 54]
beamN = [268, 258, 115, 106, 114, 269, 281, 145]
beamSE = [146, 270, 117, 107]
beamNE = [8, 144, 272, 175]

ws_S = wb.active
ws_S.title = "SOUTH"
ws_W = wb.create_sheet()
ws_W.title = "WEST"
ws_N = wb.create_sheet()
ws_N.title = "NORTH"
ws_E = wb.create_sheet()
ws_E.title = "EAST"

append_to_sheet(ws_S, beamS, beamN)
append_to_sheet(ws_W, beamW, [])
append_to_sheet(ws_N, beamN, beamS)
append_to_sheet(ws_E, beamSE, beamNE)

wb.save(FILE_O)
