import os
import compas
import compas_rhino
import compas_fofin

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist


HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'box.json')


shell = Shell.from_json(FILE_I)

thickness = 0.04

edos = shell.copy()
idos = shell.copy()

for key in shell.vertices():
    normal = shell.vertex_normal(key)
    xyz = shell.vertex_coordinates(key)

    up = scale_vector(normal, 0.5 * thickness)
    down = scale_vector(normal, -0.5 * thickness)

    xyz_up = add_vectors(xyz, up)
    xyz_down = add_vectors(xyz, down)

    edos.set_vertex_attributes(key, 'xyz', xyz_up)
    idos.set_vertex_attributes(key, 'xyz', xyz_down)


artist = ShellArtist(None)

artist.mesh = idos
artist.layer = "Offset::idos"
artist.clear_layer()
artist.draw_mesh(color=(255, 0, 0))

artist.mesh = edos
artist.layer = "Offset::edos"
artist.clear_layer()
artist.draw_mesh(color=(0, 0, 255))

artist.redraw()
