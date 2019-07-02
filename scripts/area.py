from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Compute volume of concrete per vertex
# ==============================================================================

thickness = 0.04

lines = []

for key in shell.vertices():
    area = shell.vertex_area(key)
    volume = area * thickness

    a = shell.vertex_coordinates(key)
    v = [0.0, 0.0, -volume]
    b = add_vectors(a, v)

    lines.append({
        'start' : a,
        'end'   : b,
        'name'  : "{}.{}.volume.{:.2f}".format(shell.name, key, volume),
        'color' : (0, 0, 255),
        'arrow' : 'end'
    })

# ==============================================================================
# Visualize
# ==============================================================================

artist = ShellArtist(shell, layer="Geometry::Area")

artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.draw_lines(lines)
artist.redraw()
