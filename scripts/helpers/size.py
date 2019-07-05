from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

from compas_fofin.datastructures import Shell

# ==============================================================================
# Initialise
# ==============================================================================

HERE = os.path.dirname(__file__)
DATA = os.path.abspath(os.path.join(HERE, '..', '..', 'data'))
FILE_I = os.path.join(DATA, 'data.json')

shell = Shell.from_json(FILE_I)

# ==============================================================================
# Compute volume of concrete per vertex
# ==============================================================================

thickness = 0.04
A = 0

for fkey in shell.faces():
    area = shell.face_area(fkey)
    A += area

print(A)
print(A * thickness)