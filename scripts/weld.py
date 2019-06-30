import os
import compas
import compas_rhino
import compas_fofin

from compas.geometry import add_vectors
from compas.geometry import scale_vector

from compas.datastructures import mesh_weld

from compas_fofin.datastructures import Shell
from compas_fofin.rhino import ShellArtist


HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', 'data'))
FILE_I = os.path.join(DATA, 'shajay.json')
FILE_O = os.path.join(DATA, 'shajay_welded.json')


shell = Shell.from_json(FILE_I)

shell = mesh_weld(shell)

shell.to_json(FILE_O)
