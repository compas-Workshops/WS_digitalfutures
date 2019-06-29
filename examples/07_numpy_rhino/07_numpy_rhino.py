import compas
from compas.datastructures import Mesh
from compas.rpc import Proxy
from compas_rhino.artists import MeshArtist

# create a proxy for the numerical package of COMPAS
numerical = Proxy('compas.numerical', python='pythonw')

# make a mesh from a sample OBJ file
mesh = Mesh.from_obj(compas.get('faces.obj'))

# assign default values for loads and force densities
mesh.update_default_vertex_attributes({'px': 0.0, 'py': 0.0, 'pz': 0.0})
mesh.update_default_edge_attributes({'q': 1.0})

# make a map between vertex keys (dicts)
# and vertex indices (lists, arrays)
key_index = mesh.key_index()

# convert data to a numerical format
xyz   = mesh.get_vertices_attributes('xyz')
edges = [(key_index[u], key_index[v]) for u, v in mesh.edges()]
fixed = [key_index[key] for key in mesh.vertices_where({'vertex_degree': 2})]
q     = mesh.get_edges_attribute('q', 1.0)
loads = mesh.get_vertices_attributes(('px', 'py', 'pz'), (0.0, 0.0, 0.0))

# run the force density algorithm
# through the proxy
xyz, q, f, l, r = numerical.fd_numpy(xyz, edges, fixed, q, loads)

# update the mesh with the result
for key, attr in mesh.vertices(True):
    index = key_index[key]
    attr['x'] = xyz[index][0]
    attr['y'] = xyz[index][1]
    attr['z'] = xyz[index][2]

for index, (u, v, attr) in enumerate(mesh.edges(True)):
    attr['f'] = f[index][0]
    attr['l'] = l[index][0]

# visualise
artist = MeshArtist(mesh)
artist.draw_vertices()
artist.draw_edges()
artist.draw_faces()
artist.redraw()
