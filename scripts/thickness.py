from __future__ import print_function

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas.geometry import scale_vector
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'box.json')

shell = Shell.from_json(FILE_I)

vertexcolor = {key: (255, 0, 0) for key in shell.vertices_where({'is_anchor': True})}

z = shell.get_vertices_attribute('z')
zmax = max(z)

lines = []
for key, attr in shell.vertices(True):
    z = attr['z']
    t = (1 - z/zmax) * 0.04 + 0.04
    a = shell.vertex_coordinates(key)
    n = shell.vertex_normal(key)
    b = add_vectors(a, scale_vector(n, 0.5 * t))
    c = add_vectors(a, scale_vector(n, -0.5 * t))

    lines.append({
        'start' : a,
        'end'   : b,
        'arrow' : 'end',
        'color' : (255, 0, 0),
        'name'  : "{}.{}.up".format(shell.name, key)
    })
    lines.append({
        'start' : a,
        'end'   : c,
        'arrow' : 'end',
        'color' : (0, 0, 255),
        'name'  : "{}.{}.down".format(shell.name, key)
    })

artist = ShellArtist(shell, layer="Thickness")
artist.clear_layer()
artist.draw_vertices(color=vertexcolor)
artist.draw_edges()
artist.draw_faces()
artist.draw_lines(lines)
artist.redraw()
