from __future__ import print_function

import os
import compas
import compas_fofin
from compas.geometry import add_vectors
from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'hypar.json')

shell = Shell.from_json(FILE_I)

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

artist = ShellArtist(shell, layer="FOFIN::shell")

artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.draw_lines(lines)
artist.redraw()
