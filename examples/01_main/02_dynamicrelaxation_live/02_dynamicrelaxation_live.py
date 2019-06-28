import os
import random

import compas

from compas.datastructures import Network
from compas.datastructures import network_dr

from compas_plotters import NetworkPlotter


HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, '02_dynamicrelaxation_live.obj')


# define a callback function
# for plotting the intermediate configurations of the DR process
def callback(k, xyz, crits, args):
    print(k)
    plotter.update_vertices()
    plotter.update_edges()
    plotter.update(pause=0.001)
    for key, attr in network.vertices(True):
        attr['x'] = xyz[key][0]
        attr['y'] = xyz[key][1]
        attr['z'] = xyz[key][2]


# make a network
network = Network.from_obj(FILE)

# identify the fixed vertices
leaves = network.vertices_where({'vertex_degree': 1})
network.set_vertices_attribute('is_fixed', True, keys=leaves)

# assign random prescribed force densities to the edges
for uv in network.edges():
    network.set_edge_attribute(uv, 'qpre', 1.0 * random.randint(1, 7))

# make a plotter for (dynamic) visualization
plotter = NetworkPlotter(network, figsize=(10, 7))

# plot the starting configuration
plotter.draw_vertices(facecolor={key: '#000000' for key in network.vertices_where({'is_fixed': True})})
plotter.draw_edges()
plotter.update(pause=1.0)

# run the DR
network_dr(network, kmax=50, callback=callback)

# plot the final configuration
plotter.draw_vertices(facecolor={key: '#000000' for key in network.vertices_where({'is_fixed': True})})
plotter.draw_edges()
plotter.update(pause=1.0)

# keep the plot alive
plotter.show()
