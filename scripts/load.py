import os
from numpy import array
from numpy import float64

import compas
import compas_fofin

from compas.numerical import dr_numpy

from compas_fofin.datastructures import Shell
from compas_fofin.utilities import SelfweightCalculator


HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, '..', 'data')

FILE_I = os.path.join(DATA, 'geometry.json')
FILE_O = os.path.join(DATA, 'cablenet.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# load
# ==============================================================================

key_index = shell.key_index()
uv_index  = {(u, v): index for index, (u, v) in enumerate(shell.edges_where({'is_edge': True}))}

fixed  = [key_index[key] for key in shell.vertices_where({'is_anchor': True})]
xyz    = array(shell.get_vertices_attributes('xyz'), dtype=float64)
p      = array(shell.get_vertices_attributes(('px', 'py', 'pz')), dtype=float64)

edges  = [(key_index[u], key_index[v]) for u, v in shell.edges_where({'is_edge': True})]
qpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
fpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
lpre   = array([0.0] * len(edges), dtype=float64).reshape((-1, 1))
l0     = array([attr['l0'] for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
E      = array([attr['E'] * 1e+6 for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))
radius = array([attr['r'] for u, v, attr in shell.edges_where({'is_edge': True}, True)], dtype=float64).reshape((-1, 1))

# compute the weight of the frist layer of concrete
# note: this should be based on the designed geometry
#       not the geometry of the unloaded state

density = 25

shell.set_vertices_attribute('t', 0.04)

calculate_sw = SelfweightCalculator(shell, density=density, thickness_attr_name='c1')
sw = calculate_sw(xyz)
p[:, 2] = - 1.0 * sw[:, 0]

# ==============================================================================
# relax
# ==============================================================================

xyz, q, f, l, r = dr_numpy(xyz, edges, fixed, p, qpre, fpre, lpre, l0, E, radius, kmax=15000, tol1=0.01)

# ==============================================================================
# update
# ==============================================================================

for key, attr in shell.vertices(True):
    index = key_index[key]
    attr['x'] = xyz[index, 0]
    attr['y'] = xyz[index, 1]
    attr['z'] = xyz[index, 2]
    attr['rx'] = r[index, 0]
    attr['ry'] = r[index, 1]
    attr['rz'] = r[index, 2]

for u, v, attr in shell.edges_where({'is_edge': True}, True):
    index = uv_index[(u, v)]
    attr['f'] = f[index, 0]
    attr['l'] = l[index, 0]

# ==============================================================================
# 
# ==============================================================================

shell.to_json(FILE_O)
