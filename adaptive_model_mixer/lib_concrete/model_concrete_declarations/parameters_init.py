from pyomo.environ import Param, Set, RangeSet, PositiveIntegers, PositiveReals, value
from ..model_concrete_declarations.parameter_initialisation_functions import *

def init_concrete_parameters(model):
    if hasattr(model, 'U'):
        model.del_component('U')
    model.U = Param(model.HP, model.CP, within=PositiveReals, initialize = u_init)
    if hasattr(model, 'U_cu'):
        model.del_component('U_cu')
    model.U_cu = Param(model.HP, within=PositiveReals, initialize = u_cu_init)
    if hasattr(model, 'U_hu'):
        model.del_component('U_hu')
    model.U_hu = Param(model.CP, within=PositiveReals, initialize = u_hu_init)

    if hasattr(model, 'Ech'):
        model.del_component('Ech')
    model.Ech = Param(model.HP, within=PositiveReals, initialize = ech_init)
    if hasattr(model, 'Ecc'):
        model.del_component('Ecc')
    model.Ecc = Param(model.CP, within=PositiveReals, initialize=ecc_init)

    if hasattr(model, 'Omega_ij'):
        model.del_component('Omega_ij')
    model.Omega_ij = Param(model.HP, model.CP, within=PositiveReals, initialize = Omega_ij_init)
    if hasattr(model, 'Omega_i'):
        model.del_component('Omega_i')
    model.Omega_i = Param(model.HP, within=PositiveReals, initialize = Omega_i_init)
    if hasattr(model, 'Omega_j'):
        model.del_component('Omega_j')
    model.Omega_j = Param(model.CP, within=PositiveReals, initialize = Omega_j_init)

    if hasattr(model, 'Gamma'):
        model.del_component('Gamma')
    model.Gamma = Param(model.HP, model.CP, within=PositiveReals, initialize = Gamma_init)