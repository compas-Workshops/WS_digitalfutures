from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.datastructures import Mesh
from compas.datastructures import mesh_subdivide

from compas_rhino.artists import MeshArtist
from compas_rhino.selectors import VertexSelector
from compas_rhino.modifiers import VertexModifier


# make a drawing function for the control mesh
# fixed vertices will be shown in red
def draw():
    artist.clear_layer()
    artist.draw_vertices(color={key: '#ff0000' for key in mesh.vertices_where({'is_fixed': True})})
    artist.draw_edges()
    artist.redraw()


# make a control mesh
mesh = Mesh.from_polyhedron(6)

# give the mesh a name
mesh.attributes['name'] = 'Control'

# set default vertex attributes
mesh.update_default_vertex_attributes({'is_fixed': False})

# make an artist for visualisation
artist = MeshArtist(mesh, layer='SubdModeling::Control')

# draw the control mesh
draw()

# allow the user to change the attributes of the vertices
while True:
    keys = VertexSelector.select_vertices(mesh)
    if not keys:
        break
    VertexModifier.update_vertex_attributes(mesh, keys)
    draw()

# make a subd mesh (using catmullclark)
subd = mesh_subdivide(mesh, scheme='catmullclark', k=4, fixed=mesh.vertices_where({'is_fixed': True}))

# give the subdivision mesh a different name
subd.attributes['name'] = 'Mesh'

# draw the result
artist.mesh = subd
artist.layer = 'SubdModeling::Mesh'
artist.clear_layer()
artist.draw_mesh()
