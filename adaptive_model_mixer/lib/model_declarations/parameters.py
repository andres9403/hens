# Author: Miten Mistry
#         Department of Computing, Imperial College London
from .parameter_initialisation_functions import *

from pyomo.environ import *
from pyomo.environ import value

def declare_parameters(model):
    # --------------------------------------------------------------
    #  Global scalar data
    # --------------------------------------------------------------
    model.Alpha       = Param(within=NonNegativeReals, doc="factor for area cost")
    model.Beta        = Param(within=PercentFraction,  doc="exponent for the area cost")
    model.Cost_hx     = Param(within=NonNegativeReals, doc="fixed charge for exchangers")
    model.Cost_cu     = Param(within=NonNegativeReals, doc="cooling utility cost coefficient")
    model.Cost_hu     = Param(within=NonNegativeReals, doc="heating utility cost coefficient")
    model.Delta_t_min = Param(within=NonNegativeReals, doc="minimum temperature approach")

    # --------------------------------------------------------------
    #  Superstructure size
    # --------------------------------------------------------------
    model.Number_stages      = Param(within=PositiveIntegers, doc="number of stages")
    model.Number_hot_stream  = Param(within=PositiveIntegers, doc="number of hot streams")
    model.Number_cold_stream = Param(within=PositiveIntegers, doc="number of cold streams")
    model.First_stage        = Param(within=PositiveIntegers, default=1, doc="index of first stage")

    model.Last_stage = Param(within=PositiveIntegers,
                             initialize=lambda m: m.Number_stages + 1,
                             doc="index of last stage (= #stages + 1)")

    # --------------------------------------------------------------
    #  Index sets
    # --------------------------------------------------------------
    model.HP = Set(initialize=lambda m: range(1, value(m.Number_hot_stream + 1)), doc="hot streams i", ordered=True)
    model.CP = Set(initialize=lambda m: range(1, value(m.Number_cold_stream + 1)), doc="cold streams j", ordered=True)
    model.ST = Set(initialize=lambda m: range(value(m.First_stage), value(m.Number_stages + 1)), doc="stages k", ordered=True)
    model.K  = Set(initialize=lambda m: range(value(m.First_stage), value(m.Last_stage + 1)), doc="temperature locations K", ordered=True)

    model.First_Stage_Set = Set(initialize=lambda m: [value(m.First_stage)], doc="singleton {First_stage}", ordered=True)
    model.K_Take_First_Stage = Set(initialize=lambda m: [k for k in m.K if k != value(m.First_stage)],
                                   doc="K \\ {First_stage}", ordered=True)

    # --------------------------------------------------------------
    #  Stream-specific parameters
    # --------------------------------------------------------------
    model.Fh = Param(model.HP, doc="hot-stream flowrate Fh(i)")
    model.Fc = Param(model.CP, doc="cold-stream flowrate Fc(j)")
    model.Hh = Param(model.HP, doc="heat transfer coefficient hot stream i")
    model.Hc = Param(model.CP, doc="heat transfer coefficient cold stream j")
    model.H_cu = Param(doc="HTC cold utility")
    model.H_hu = Param(doc="HTC hot utility")

    model.Th_in  = Param(model.HP, doc="hot-stream inlet temperature")
    model.Th_out = Param(model.HP, doc="hot-stream outlet temperature")
    model.Tc_in  = Param(model.CP, doc="cold-stream inlet temperature")
    model.Tc_out = Param(model.CP, doc="cold-stream outlet temperature")

    model.T_cu_in  = Param(within=PositiveReals, doc="cold-utility inlet temp")
    model.T_cu_out = Param(within=PositiveReals, doc="cold-utility outlet temp")
    model.T_hu_in  = Param(within=PositiveReals, doc="hot-utility inlet temp")
    model.T_hu_out = Param(within=PositiveReals, doc="hot-utility outlet temp")

    # --------------------------------------------------------------
    #  Placeholder gradient point sets
    # --------------------------------------------------------------
    model.Reclmtd_gradient_points = Set(model.HP, model.CP, model.ST, dimen=2, initialize=[])
    model.Reclmtd_cu_gradient_points = Set(model.HP, dimen=1, initialize=[])
    model.Reclmtd_hu_gradient_points = Set(model.CP, dimen=1, initialize=[])

    # --------------------------------------------------------------
    #  U-value, exponents, Omega, Gamma
    # --------------------------------------------------------------
    model.U     = Param(model.HP, model.CP, within=PositiveReals, initialize=u_init)
    model.U_cu  = Param(model.HP, within=PositiveReals, initialize=u_cu_init)
    model.U_hu  = Param(model.CP, within=PositiveReals, initialize=u_hu_init)

    model.Ech = Param(model.HP, within=PositiveReals, initialize=ech_init)
    model.Ecc = Param(model.CP, within=PositiveReals, initialize=ecc_init)

    model.Omega_ij = Param(model.HP, model.CP, within=PositiveReals, initialize=Omega_ij_init)
    model.Omega_i  = Param(model.HP, within=PositiveReals, initialize=Omega_i_init)
    model.Omega_j  = Param(model.CP, within=PositiveReals, initialize=Omega_j_init)

    model.Gamma = Param(model.HP, model.CP, within=NonNegativeReals, initialize=Gamma_init)

    # --------------------------------------------------------------
    #  Breakpoint Sets (all must return fresh list copies)
    # --------------------------------------------------------------
    model.Th_breakpoints = Set(model.HP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, k: list(th_breakpoints_init(m, i)))

    model.Thx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, j, k: list(thx_breakpoints_init(m, i, j, k)))

    model.Tc_breakpoints = Set(model.CP, model.K_Take_First_Stage, dimen=1, ordered=True,
        initialize=lambda m, j, k: list(tc_breakpoints_init(m, j)))

    model.Tcx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, j, k: list(tcx_breakpoints_init(m, i, j, k)))

    model.Q_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, j, k: list(q_breakpoints_init(m, i, j)))
    model.Q_cu_breakpoints = Set(model.HP, dimen=1, ordered=True,
        initialize=lambda m, i: list(q_cu_breakpoints_init(m, i)))
    model.Q_hu_breakpoints = Set(model.CP, dimen=1, ordered=True,
        initialize=lambda m, j: list(q_hu_breakpoints_init(m, j)))

    model.Area_beta_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, j, k: list(area_beta_breakpoints_init(m, i, j, k)))

    model.Area_beta_exp = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=lambda m, i, j, k:
            [A ** value(m.Beta) for A in m.Area_beta_breakpoints[i, j, k]])

    model.Area_beta_gradients = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True,
        initialize=area_beta_gradients_init)

    model.Area_cu_beta_breakpoints = Set(model.HP, dimen=1, ordered=True,
        initialize=lambda m, i: list(area_cu_beta_breakpoints_init(m, i)))
    model.Area_cu_beta_exp = Set(model.HP, dimen=1, ordered=True,
        initialize=lambda m, i:
            [A ** value(m.Beta) for A in m.Area_cu_beta_breakpoints[i]])
    model.Area_cu_beta_gradients = Set(model.HP, dimen=1, ordered=True,
        initialize=area_cu_beta_gradients_init)

    model.Area_hu_beta_breakpoints = Set(model.CP, dimen=1, ordered=True,
        initialize=lambda m, j: list(area_hu_beta_breakpoints_init(m, j)))
    model.Area_hu_beta_exp = Set(model.CP, dimen=1, ordered=True,
        initialize=lambda m, j:
            [A ** value(m.Beta) for A in m.Area_hu_beta_breakpoints[j]])
    model.Area_hu_beta_gradients = Set(model.CP, dimen=1, ordered=True,
        initialize=area_hu_beta_gradients_init)




# from pyomo.environ import (
#     Set, Param, RangeSet, PositiveReals, NonNegativeReals,
#     PositiveIntegers, PercentFraction
# )

# ## For pyomo 5.3 and below, use the following import
# # from pyomo.core.base.sets import Set
# # from pyomo.core.base.rangeset import RangeSet
# from pyomo.environ import (
#     PositiveReals,
#     NonNegativeReals,
#     PositiveIntegers,
#     PercentFraction,
#     Expression,
#     value,               
# )
# from .parameter_initialisation_functions import *
# from pyomo.environ import value



# ############################################################
# ############################################################
# ################### Assignment Functions ###################
# ############################################################
# ############################################################
# def declare_parameters(model):
#     model.Alpha       = Param(within=NonNegativeReals, doc="factor for area cost"                            )
#     model.Beta        = Param(within=PercentFraction , doc="exponent for the area cost"                      )
#     model.Cost_hx  = Param(within=NonNegativeReals, doc="fixed charge for exchangers"                     )
#     model.Cost_cu     = Param(within=NonNegativeReals, doc="utility cost coeffiecient for cooling utility j" )
#     model.Cost_hu     = Param(within=NonNegativeReals, doc="utility cost coeffiecient for heating utility k" )
#     model.Delta_t_min = Param(within=NonNegativeReals, doc="minimum temperature approach"                    )

#     model.Number_stages      = Param(within=PositiveIntegers, doc="number of stages"       )
#     model.Number_hot_stream  = Param(within=PositiveIntegers, doc="number of hot streams"  )
#     model.Number_cold_stream = Param(within=PositiveIntegers, doc="number of cold streams" )

#     model.First_stage = Param(within=PositiveIntegers, default=1,                    doc='Index of the first stage')
   
#     model.Last_stage  = Param(within=PositiveIntegers, initialize = lambda m: value(m.Number_stages) + 1, doc='Index of the last stage' )
#     model.HP = Set(doc="set of hot process streams i", initialize=lambda m: list(range(1, value(m.Number_hot_stream) + 1)))
#     model.CP = Set(doc="set of cold process streams j", initialize=lambda m: list(range(1, value(m.Number_cold_stream) + 1)))
#     model.ST = Set(doc="set of stages in the superstructure", initialize=lambda m: list(range(value(m.First_stage), value(m.Number_stages) + 1)))
#     model.K = Set(doc="set of temperature locations", initialize=lambda m: list(range(value(m.First_stage), value(m.Last_stage) + 1)))
#     model.First_Stage_Set = Set(doc="singleton set with the first stage index",initialize=lambda m: [value(m.First_stage)])
#     model.K_Take_First_Stage = Set(doc="K excluding the first stage",initialize=lambda m: [k for k in list(m.K) if k != value(m.First_stage)])
   

#     model.Fh = Param(model.HP, doc="flow capicity of hot stream i"  )
#     model.Fc = Param(model.CP, doc="flow capacity of cold stream j" )

#     model.Hh   = Param(model.HP, doc="heat transfer coefficient for hot stream i"  )
#     model.Hc   = Param(model.CP, doc="heat transfer coefficient for cold stream j" )
#     model.H_cu = Param(          doc="heat transfer coefficient for cold utility"  )
#     model.H_hu = Param(          doc="heat transfer coefficient for hot utility"   )

#     model.Th_in  = Param(model.HP, doc="inlet temperature of hot stream i"   )
#     model.Tc_in  = Param(model.CP, doc="inlet temperature of cold stream j"  )
#     model.Th_out = Param(model.HP, doc="outlet temperature of hot stream i"  )
#     model.Tc_out = Param(model.CP, doc="outlet temperature of cold stream j" )

#     model.T_cu_in  = Param(within=PositiveReals, doc="inlet temperature of cold utility"  )
#     model.T_cu_out = Param(within=PositiveReals, doc="outlet temperature of cold utility" )
#     model.T_hu_in  = Param(within=PositiveReals, doc="inlet temperature of hot utility"   )
#     model.T_hu_out = Param(within=PositiveReals, doc="outlet temperature of hot utility"  )

#     ###############################
#     #   Initialised Parameters    #
#     ###############################
    
#     model.Reclmtd_gradient_points = Set(model.HP, model.CP, model.ST, dimen=2, initialize=[])
#     model.Reclmtd_cu_gradient_points = Set(model.HP, dimen=1, initialize=[])
#     model.Reclmtd_hu_gradient_points = Set(model.CP, dimen=1, initialize=[])



#     model.U    = Param(model.HP, model.CP, within=PositiveReals, initialize=u_init)
#     model.U_cu = Param(model.HP,           within=PositiveReals, initialize=u_cu_init)
#     model.U_hu = Param(model.CP,           within=PositiveReals, initialize=u_hu_init)

#     model.Ech = Param(model.HP, within=PositiveReals, initialize=ech_init)
#     model.Ecc = Param(model.CP, within=PositiveReals, initialize=ecc_init)

#     model.Omega_ij = Param(model.HP, model.CP, within=PositiveReals, initialize=Omega_ij_init)
#     model.Omega_i  = Param(model.HP,           within=PositiveReals, initialize=Omega_i_init)
#     model.Omega_j  = Param(model.CP,           within=PositiveReals, initialize=Omega_j_init)

#     model.Gamma = Param(model.HP, model.CP, within=NonNegativeReals, initialize=Gamma_init)

#     model.Th_breakpoints = Set(model.HP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, k: list(th_breakpoints_init(model, i)))

#     model.Thx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: list(thx_breakpoints_init(model, i, j, k)))

#     model.Tc_breakpoints = Set(model.CP, model.K_Take_First_Stage, dimen=1, ordered=True, initialize=lambda model, j, k: list(tc_breakpoints_init(model, j)))

#     model.Tcx_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: list(tcx_breakpoints_init(model, i, j, k)))

#     model.Q_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: list(q_breakpoints_init(model, i, j)))
#     model.Q_cu_breakpoints = Set(model.HP, dimen=1, ordered=True, initialize=lambda model, i: list(q_cu_breakpoints_init(model, i)))
#     model.Q_hu_breakpoints = Set(model.CP, dimen=1, ordered=True, initialize=lambda model, j: list(q_hu_breakpoints_init(model, j)))

#     model.Area_beta_breakpoints = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model,i,j,k: list(area_beta_breakpoints_init(model,i,j,k)))

#     model.Area_beta_exp = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model, i, j, k: [pow(A, value(model.Beta)) for A in model.Area_beta_breakpoints[i, j, k]])
   
#     model.Area_beta_gradients = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=area_beta_gradients_init)

#     model.Area_cu_beta_breakpoints = Set(model.HP, dimen=1, ordered=True, initialize=lambda model,i: list(area_cu_beta_breakpoints_init(model,i)))
#     model.Area_cu_beta_exp = Set(model.HP, dimen=1, ordered=True, initialize=lambda model, i: [pow(A, value(model.Beta)) for A in model.Area_cu_beta_breakpoints[i]])
   
#     model.Area_cu_beta_gradients = Set(model.HP, dimen=1, ordered=True, initialize=area_cu_beta_gradients_init)

#     model.Area_hu_beta_breakpoints = Set(model.CP, dimen=1, ordered=True, initialize=lambda model,j: list(area_hu_beta_breakpoints_init(model,j)))
    
#     model.Area_hu_beta_exp = Set(model.CP, dimen=1, ordered=True, initialize=lambda model, j: [pow(A, value(model.Beta)) for A in model.Area_hu_beta_breakpoints[j]])
#     model.Area_hu_beta_gradients = Set(model.CP, dimen=1, ordered=True, initialize=area_hu_beta_gradients_init)

## Problem when using the last stage as a parameter

    
  
    
    #model.Last_stage = Param(within=PositiveIntegers, default=last_stage_rule, doc='Index of the last stage')
    #model.Last_stage = Param(within=PositiveIntegers, default=3, doc='Index of the last stage')
    
    #print("Last stage is set to: ", value(model.Last_stage))

    #model.Last_stage = Expression(expr=model.Number_stages + 1)
   
    # model.HP = RangeSet(1, model.Number_hot_stream,  doc="set of hot process streams i"          )
    # model.CP = RangeSet(1, model.Number_cold_stream, doc="set of cold process streams j"         )
    # model.ST = RangeSet(model.First_stage, model.Number_stages, doc="set of stages in the superstructure" )
    #model.K  = RangeSet(model.First_stage, model.Last_stage, doc="set of temperature locations"          )
    #model.K  = RangeSet(model.First_stage, value(model.Number_stages) + 1, doc="set of temperature locations")
    #model.First_Stage_Set = RangeSet(model.First_stage, model.First_stage)
    #model.K_Take_First_Stage = model.K - model.First_Stage_Set

    # model.Area_beta_exp = Set(model.HP, model.CP, model.ST, dimen=1, ordered=True, initialize=lambda model,i,j,k: map(lambda A: pow(A, model.Beta), model.Area_beta_breakpoints[i,j,k]))
     #model.Area_cu_beta_exp = Set(model.HP, dimen=1, ordered=True, initialize=lambda model,i: map(lambda A: pow(A, model.Beta), model.Area_cu_beta_breakpoints[i]))
     # model.Area_hu_beta_exp = Set(model.CP, dimen=1, ordered=True, initialize=lambda model,j: map(lambda A: pow(A, model.Beta), model.Area_hu_beta_breakpoints[j]))