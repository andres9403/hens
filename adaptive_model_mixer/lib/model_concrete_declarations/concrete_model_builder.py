from pyomo.environ import ConcreteModel
from .parameters import declare_concrete_parameters

def build_concrete_model(data):
    model = ConcreteModel()
    declare_concrete_parameters(model, data)
    return model