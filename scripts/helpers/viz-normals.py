from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas.geometry import scale_vector
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
# Compute normals
# ==============================================================================

vertexcolor = {key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})}

lines = []
for key in shell.vertices():
    a = shell.vertex_coordinates(key)
    n = shell.vertex_normal(key)
    b = add_vectors(a, scale_vector(n, 0.1))

    lines.append({
        'start' : a,
        'end'   : b,
        'arrow' : 'end',
        'color' : (0, 255, 0),
        'name'  : "{}.{}.normal".format(shell.name, key)
    })

# ==============================================================================
# Visualise
# ==============================================================================

artist = ShellArtist(shell, layer="Geometry::Normals")
artist.clear_layer()
artist.draw_vertices(color=vertexcolor)
artist.draw_edges()
artist.draw_lines(lines)
artist.redraw()
