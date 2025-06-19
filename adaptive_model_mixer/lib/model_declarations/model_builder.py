# Author: Miten Mistry
#         Department of Computing, Imperial College London

from pyomo.core.base.PyomoModel import AbstractModel
from pyomo.core import Set

from .parameters  import declare_parameters
from .variables   import declare_variables
from .objective   import declare_objective
from .constraints import declare_constraints

def create_model(run_type):
    model = AbstractModel()
    model.run_type = run_type
    declare_parameters(model)
    declare_variables(model)
    declare_objective(model)
    declare_constraints(model)
    return model

