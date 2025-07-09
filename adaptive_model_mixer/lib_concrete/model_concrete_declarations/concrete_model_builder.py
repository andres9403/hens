from pyomo.environ import ConcreteModel
from .parameters import declare_concrete_parameters
from .variables import declare_concrete_variables
from .constraints import declare_concrete_constraints
from .objective import declare_concrete_objective

def build_concrete_model(data):
    model = ConcreteModel()
    declare_concrete_parameters(model, data)
    declare_concrete_variables(model)
    declare_concrete_constraints(model)
    declare_concrete_objective(model)
    return model