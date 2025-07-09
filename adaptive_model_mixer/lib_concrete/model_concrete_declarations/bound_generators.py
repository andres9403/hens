# Author: Miten Mistry
#         Department of Computing, Imperial College London

from .helper_functions import lmtd_inv
from pyomo.environ import value

def area_bounds(model, i, j, *k):
    _, q_upper    = q_bounds(model, i, j)
    _, reclmtd_upper = reclmtd_bounds(model, i, j)

    area_lower = 0
    area_upper = value(q_upper*reclmtd_upper*model.U[i,j])

    return (area_lower, area_upper)

def area_cu_bounds(model, i):
    _, q_cu_upper    = q_cu_bounds(model, i)
    _, reclmtd_cu_upper = reclmtd_cu_bounds(model, i)

    area_cu_lower = 0
    area_cu_upper = value(q_cu_upper*reclmtd_cu_upper*model.U_cu[i])

    return (area_cu_lower, area_cu_upper)

def area_hu_bounds(model, j):
    _, q_hu_upper    = q_hu_bounds(model, j)
    _, reclmtd_hu_upper = reclmtd_hu_bounds(model, j)

    area_hu_lower = 0
    area_hu_upper = value(q_hu_upper*reclmtd_hu_upper*model.U_hu[j])

    return (area_hu_lower, area_hu_upper)

def fh_bounds(model, i, j, k):
    return (0, value(model.Fh[i]))

def fc_bounds(model, i, j, k):
    return (0, value(model.Fc[j]))

def thx_bounds(model, i, j, k):
    return (value(model.Th_out[i]), value(model.Th_in[i]))

def tcx_bounds(model, i, j, k):
    return (value(model.Tc_in[j]), value(model.Tc_out[j]))

def dt_bounds(model, i, j, k):
    return (value(model.Delta_t_min), value(model.Th_in[i]-model.Tc_in[j]))

def dt_cu_bounds(model, i):
    return (value(model.Delta_t_min), value(model.Th_in[i]-model.T_cu_in))

def dt_hu_bounds(model, j):
    return (value(model.Delta_t_min), value(model.T_hu_in - model.Tc_in[j]))

def reclmtd_bounds(model, i, j, *k):
    reclmtd_lower = value(1/(model.Th_in[i] - model.Tc_in[j]))
    reclmtd_upper = value(1/model.Delta_t_min)
    return (reclmtd_lower, reclmtd_upper)

def reclmtd_cu_bounds(model, i):
    x_min = value(model.Delta_t_min)
    x_max = value(model.Th_in[i] - model.T_cu_out)
    y    = value(model.Th_out[i] - model.T_cu_in)
    reclmtd_cu_lower = lmtd_inv(x_max,y)
    reclmtd_cu_upper = lmtd_inv(x_min,y)

    return (reclmtd_cu_lower, reclmtd_cu_upper)

def reclmtd_hu_bounds(model, j):
    x_min = value(model.Delta_t_min)
    x_max = value(model.T_hu_out - model.Tc_in[j])
    y    = value(model.T_hu_in - model.Tc_out[j])
    reclmtd_hu_lower = lmtd_inv(x_max,y)
    reclmtd_hu_upper = lmtd_inv(x_min,y)

    return (reclmtd_hu_lower, reclmtd_hu_upper)

def q_bounds(model, i, j, *k):
    q_lower = 0

    q_upper_hot_side  = value(model.Fh[i]*(model.Th_in[i] - model.Th_out[i]))
    q_upper_cold_side = value(model.Fc[j]*(model.Tc_out[j] - model.Tc_in[j]))
    q_upper = min( q_upper_hot_side, q_upper_cold_side )
    return (q_lower, q_upper)

def q_cu_bounds(model, i):
    q_cu_lower = 0
    q_cu_upper = value(model.Fh[i]*(model.Th_in[i] - model.Th_out[i]))
    return (q_cu_lower, q_cu_upper)

def q_hu_bounds(model, j):
    q_hu_lower = 0
    q_hu_upper = value(model.Fc[j]*(model.Tc_out[j] - model.Tc_in[j]))
    return (q_hu_lower, q_hu_upper)

def th_bounds(model, i, *k):
    return (value(model.Th_out[i]), value(model.Th_in[i]))

def tc_bounds(model, j, *k):
    return (value(model.Tc_in[j]), value(model.Tc_out[j]))

def bh_bounds(model, i, j, k):
    return (0, value(model.Th_in[i]*model.Fh[i]))

def bc_bounds(model, i, j, k):
    return (0, value(model.Tc_out[j]*model.Fc[j]))
