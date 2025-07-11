from pyomo.environ import Param, Set, RangeSet, PositiveIntegers, PositiveReals, value
from ..model_concrete_declarations.parameter_initialisation_functions import *

def init_concrete_parameters(model):
    model.U = Param(model.HP, model.CP, within=PositiveReals, initialize = u_init)
    model.U_cu = Param(model.HP, within=PositiveReals, initialize = u_cu_init)
    model.U_hu = Param(model.CP, within=PositiveReals, initialize = u_hu_init)

    model.Ech = Param(model.HP, within=PositiveReals, initialize = ech_init)
    model.Ecc = Param(model.CP, within=PositiveReals, initialize=ecc_init)

    model.Omega_ij = Param(model.HP, model.CP, within=PositiveReals, initialize = Omega_ij_init)
    model.Omega_i = Param(model.HP, within=PositiveReals, initialize = Omega_i_init)
    model.Omega_j = Param(model.CP, within=PositiveReals, initialize = Omega_j_init)

    model.Gamma = Param(model.HP, model.CP, within=PositiveReals, initialize = Gamma_init)