from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas


from compas.geometry import offset_polygon

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellHelper
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')
FOLDER = os.path.join(DATA, 'fabric', 'unrolled', 'edos')

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(None)

files = [
    'SOUTH-00', 'SOUTH-01', 'SOUTH-02', 'SOUTH-03', 'SOUTH-04',
    'WEST-00', 'WEST-01', 'WEST-02', 'WEST-03', 'WEST-04',
    'NORTH-00', 'NORTH-01', 'NORTH-02', 'NORTH-03', 'NORTH-04',
    'SW-00', 'WS-00',
    'NW-00', 'WN-00'
]

for filename in files:
    FILE_I = os.path.join(FOLDER, filename + '.json')
    fabric = Shell.from_json(FILE_I)

    points = [fabric.vertex_coordinates(key) for key in fabric.vertices_on_boundary(ordered=True)]
    polygon = offset_polygon(points, -0.020)

    polygons = []
    polygons.append({
        'points': polygon + polygon[:1]
    })

    artist.mesh = fabric
    artist.layer = "Fabric::Unrolled::Edos::{}".format(filename)
    artist.clear_layer()
    artist.draw_faces()
    artist.draw_facelabels(text={key: "{}".format(attr['count']) for key, attr in fabric.faces(True)})
    artist.draw_polygons(polygons)
    artist.redraw()
