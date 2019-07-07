from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
from compas_fofin.datastructures import Shell
from compas_fofin.fofin import fofin_numpy
from compas_plotters import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'mesh.obj')

shell = Shell.from_obj(FILE)

anchors = list(shell.vertices_where({'vertex_degree': 2}))
shell.set_vertices_attribute('is_anchor', True, keys=anchors)

fofin_numpy(shell)

plotter = MeshPlotter(shell, figsize=(10, 7))
plotter.draw_vertices(facecolor={key: (255, 0, 0) for key in anchors})
plotter.draw_edges()
plotter.draw_faces()
plotter.show()
