from __future__ import print_function

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'torus4.json')

shell = Shell.from_json(FILE_I)

vertexcolor = {key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})}

lines = []
for key in shell.vertices():
    a = shell.vertex_coordinates(key)
    n = shell.vertex_normal(key)
    b = add_vectors(a, n)

    lines.append({
        'start' : a,
        'end'   : b,
        'arrow' : 'end',
        'color' : (0, 255, 0),
        'name'  : "{}.{}.normal".format(shell.name, key)
    })

artist = ShellArtist(shell, layer="Normals")
artist.clear_layer()
artist.draw_vertices(color=vertexcolor)
artist.draw_edges()
artist.draw_lines(lines)
artist.redraw()
