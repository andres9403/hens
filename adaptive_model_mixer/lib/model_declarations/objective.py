# Author: Miten Mistry
#         Department of Computing, Imperial College London

# from pyomo.core.base.objective import Objective

from pyomo.environ import Objective, minimize

def TAC_rule(model):
    total_cu_load = sum(model.q_cu[i] for i in model.HP)
    total_hu_load = sum(model.q_hu[j] for j in model.CP)

    total_stream_hx = sum(model.z[i, j, k] for i in model.HP for j in model.CP for k in model.ST)
    total_cu_hx     = sum(model.z_cu[i]    for i in model.HP)
    total_hu_hx     = sum(model.z_hu[j]    for j in model.CP)
    total_hx        = total_stream_hx + total_cu_hx + total_hu_hx

    area_stream_hx = sum(model.area_beta[i, j, k] for i in model.HP for j in model.CP for k in model.ST)
    area_cu_hx     = sum(model.area_cu_beta[i]     for i in model.HP)
    area_hu_hx     = sum(model.area_hu_beta[j]     for j in model.CP)
    total_area     = area_stream_hx + area_cu_hx + area_hu_hx

    return (model.Cost_cu * total_cu_load +
            model.Cost_hu * total_hu_load +
            model.Cost_hx * total_hx +
            model.Alpha * total_area)

def declare_objective(model):
    model.TAC = Objective(rule=TAC_rule, sense=minimize)