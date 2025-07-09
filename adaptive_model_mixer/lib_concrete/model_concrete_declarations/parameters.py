from pyomo.environ import Param, Set, RangeSet, PositiveIntegers, PositiveReals, value
from ..model_concrete_declarations.parameter_initialisation_functions import *

def declare_concrete_parameters(model, data):
    model.Alpha = Param(initialize=data['Alpha'], mutable=True)
    model.Beta = Param(initialize=data['Beta'])
    model.Cost_hx = Param(initialize=data['Cost_hx'], mutable=True)
    model.Cost_cu = Param(initialize=data['Cost_cu'], mutable=True)
    model.Cost_hu = Param(initialize=data['Cost_hu'], mutable=True)
    model.Delta_t_min = Param(initialize=data['Delta_t_min'], mutable=True)
    model.Number_stages = Param(within=PositiveIntegers, initialize=data['Number_stages'])
    model.Number_hot_stream = Param(within=PositiveIntegers, initialize=data['Number_hot_stream'])
    model.Number_cold_stream = Param(within=PositiveIntegers, initialize=data['Number_cold_stream'])
    model.First_stage = Param(within=PositiveIntegers, default=1)
    model.Last_stage = Param(within=PositiveIntegers, initialize=data['Number_stages']+1)
    

    ## Sets that represents the hot and cold streams, stages and temperature locations
    model.HP = RangeSet(1, model.Number_hot_stream, doc="set of hot process streams i" )
    model.CP = RangeSet(1, model.Number_cold_stream, doc="set of cold process streams j" )
    model.ST = RangeSet(model.First_stage, model.Number_stages, doc="set of stages in the superstructure" )
    model.K = RangeSet(model.First_stage, model.Last_stage, doc="set of temperature locations")

    model.First_Stage_Set = RangeSet(model.First_stage, model.First_stage)
    model.K_Take_First_Stage = model.K - model.First_Stage_Set

    ## Parameters per sets
    model.Fh = Param(model.HP, initialize = data['Fh'], doc="flow rate of hot process streams i")
    model.Fc = Param(model.CP, initialize = data['Fc'], doc="flow rate of cold process streams j")
    
    model.Hh = Param(model.HP, initialize = data['Hh'], doc="enthalpy of hot process streams i")
    model.Hc = Param(model.CP, initialize = data['Hc'], doc="enthalpy of cold process streams j")
    model.H_cu = Param(initialize=data['H_cu'], doc="heat transfer coefficient for cooling utility j")
    model.H_hu = Param(initialize=data['H_hu'], doc="heat transfer coefficient for heating utility k")
    
    model.Th_in = Param(model.HP, initialize=data['Th_in'], doc="inlet temperature of hot process streams i")
    model.Tc_in = Param(model.CP, initialize=data['Tc_in'], doc="inlet temperature of cold process streams j")
    model.Th_out = Param(model.HP, initialize=data['Th_out'], doc="outlet temperature of hot process streams i")
    model.Tc_out = Param(model.CP, initialize=data['Tc_out'], doc="outlet temperature of cold process streams j")

    model.T_cu_in = Param(initialize=data['T_cu_in'], doc="inlet temperature of cooling utility j")
    model.T_cu_out = Param(initialize=data['T_cu_out'], doc="outlet temperature of cooling utility j")
    model.T_hu_in = Param(initialize=data['T_hu_in'], doc="inlet temperature of heating utility k")
    model.T_hu_out = Param(initialize=data['T_hu_out'], doc="outlet temperature of heating utility k")

    model.Reclmtd_gradient_points = Set(model.HP, model.CP, model.ST, dimen=2, initialize = [])
    model.Reclmtd_cu_gradient_points = Set(model.HP, dimen=1, initialize=[])
    model.Reclmtd_hu_gradient_points = Set(model.CP, dimen=1, initialize=[])

    model.U = Param(model.HP, model.CP, within=PositiveReals, initialize = u_init)
    model.U_cu = Param(model.HP, within=PositiveReals, initialize = u_cu_init)
    model.U_hu = Param(model.CP, within=PositiveReals, initialize = u_hu_init)

    model.Ech = Param(model.HP, within=PositiveReals, initialize = ech_init)
    model.Ecc = Param(model.CP, within=PositiveReals, initialize=ecc_init)

    model.Omega_ij = Param(model.HP, model.CP, within=PositiveReals, initialize = Omega_ij_init)
    model.Omega_i = Param(model.HP, within=PositiveReals, initialize = Omega_i_init)
    model.Omega_j = Param(model.CP, within=PositiveReals, initialize = Omega_j_init)

    model.Gamma = Param(model.HP, model.CP, within=PositiveReals, initialize = Gamma_init)

    ## RecLMTD Sets for the breakpoints

    model.Th_breakpoints = Set(model.HP, model.ST, dimen=1, ordered=True, initialize = lambda model, i, k: th_breakpoints_init(model, i))
    model.Thx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: thx_breakpoints_init(model, i, j, k))

    model.Tc_breakpoints = Set(model.CP, model.K_Take_First_Stage, dimen=1, ordered=True, initialize=lambda model, j, k: tc_breakpoints_init(model, j))
    model.Tcx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: tcx_breakpoints_init(model, i, j, k))

    model.Q_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: q_breakpoints_init(model, i, j))
    model.Q_cu_breakpoints = Set(model.HP, dimen=1, ordered=True, initialize=lambda model, i: q_cu_breakpoints_init(model, i))
    model.Q_hu_breakpoints = Set(model.CP, dimen=1, ordered=True, initialize=lambda model, j: q_hu_breakpoints_init(model, j))

    model.Area_beta_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model,i,j,k: area_beta_breakpoints_init(model,i,j))
    model.Area_beta_exp = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model,i,j,k: map(lambda A: pow(A, value(model.Beta)), model.Area_beta_breakpoints[i,j,k]))
    model.Area_beta_gradients = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=area_beta_gradients_init)

    model.Area_cu_beta_breakpoints = Set(model.HP, dimen=1, ordered=True, initialize=lambda model,i: area_cu_beta_breakpoints_init(model,i))
    model.Area_cu_beta_exp = Set(model.HP, dimen=1, ordered=True, initialize=lambda model,i: map(lambda A: pow(A, value(model.Beta)), model.Area_cu_beta_breakpoints[i]))
    model.Area_cu_beta_gradients = Set(model.HP, dimen=1, ordered=True, initialize=area_cu_beta_gradients_init)

    model.Area_hu_beta_breakpoints = Set(model.CP, dimen=1, ordered=True, initialize=lambda model,j: area_hu_beta_breakpoints_init(model,j))
    model.Area_hu_beta_exp = Set(model.CP, dimen=1, ordered=True, initialize=lambda model,j: map(lambda A: pow(A, value(model.Beta)), model.Area_hu_beta_breakpoints[j]))
    model.Area_hu_beta_gradients = Set(model.CP, dimen=1, ordered=True, initialize=area_hu_beta_gradients_init)
 







    # model.Fh = Param(initialize=data['Fh'], mutable=True)
    # model.Fc = Param(initialize=data['Fc'], mutable=True)
    # model.Hh = Param(initialize=data['Hh'], mutable=True)
    # model.Hc = Param(initialize=data['Hc'], mutable=True)
    # model.H_cu = Param(initialize=data['H_cu'], mutable=True)
    # model.H_hu = Param(initialize=data['H_hu'], mutable=True)
    # model.Th_in = Param(initialize=data['Th_in'], mutable=True)
    # model.Tc_in = Param(initialize=data['Tc_in'], mutable=True)
    # model.Th_out = Param(initialize=data['Th_out'], mutable=True)
    # model.Tc_out = Param(initialize=data['Tc_out'], mutable=True)
    # model.T_cu_in = Param(initialize=data['T_cu_in'], mutable=True)
    # model.T_cu_out = Param(initialize=data['T_cu_out'], mutable=True)
    # model.T_hu_in = Param(initialize=data['T_hu_in'], mutable=True)
    # model.T_hu_out = Param(initialize=data['T_hu_out'], mutable=True)
    # model.U = Param(initialize=data['U'], mutable=True)
    # model.



    # model.HP = Set(initialize=data['HP'], mutable=True)
    # model.CP = Set(initialize=data['CP'], mutable=True)
    # model.ST = Set(initialize=data['ST'], mutable=True)
    # model.K = Set(initialize=data['K'], mutable=True)