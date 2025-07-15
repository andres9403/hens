# Author: Miten Mistry
#         Department of Computing, Imperial College London

from .bound_generators import area_bounds, area_cu_bounds, area_hu_bounds, q_bounds, q_cu_bounds, q_hu_bounds, th_bounds, thx_bounds, tc_bounds, tcx_bounds

def u_init(model, i, j):
    print("u_init called")
    return (1/model.Hh[i]) + (1/model.Hc[j])

def u_cu_init(model, i):
    print("u_cu_init called")
    return (1/model.Hh[i]) + (1/model.H_cu)

def u_hu_init(model, j):
    print("u_hu_init called")
    return (1/model.Hc[j]) + (1/model.H_hu)

def ech_init(model, i):
    print("ech_init called")
    return model.Fh[i]*(model.Th_in[i] - model.Th_out[i])

def ecc_init(model, j):
    print("ecc_init called")
    return model.Fc[j]*(model.Tc_out[j] - model.Tc_in[j])

def Omega_ij_init(model, i, j):
    print("Omega_ij_init called")
    return min(model.Ech[i], model.Ecc[j])

def Omega_i_init(model, i):
    print("Omega_i_init called")
    return model.Ech[i]

def Omega_j_init(model, j):
    print("Omega_j_init called")
    return model.Ecc[j]

def Gamma_init(model, i, j):
    print("Gamma_init called")
    return  max(\
                0,\
                model.Tc_in[j] - model.Th_in[i],\
                model.Tc_in[j] - model.Th_out[i],\
                model.Tc_out[j] - model.Th_in[i],\
                model.Tc_out[j] - model.Th_out[i]\
            )

def th_breakpoints_init(model, i):
    print("th_breakpoints_init called")
    return list(th_bounds(model, i))

def thx_breakpoints_init(model, i, j, k):
    print("thx_breakpoints_init called")
    return list(thx_bounds(model, i, j, k))

def tc_breakpoints_init(model, j):
    print("tc_breakpoints_init called")
    return list(tc_bounds(model, j))

def tcx_breakpoints_init(model, i, j, k):
    print("tcx_breakpoints_init called")
    return list(tcx_bounds(model, i, j, k))

def q_breakpoints_init(model, i, j, *k):
    print("q_breakpoints_init called")
    return list(q_bounds(model, i, j))

def q_cu_breakpoints_init(model, i):
    print("q_cu_breakpoints_init called")
    return list(q_cu_bounds(model, i))

def q_hu_breakpoints_init(model, j):
    print("q_hu_breakpoints_init called")
    return list(q_hu_bounds(model, j))

def area_beta_breakpoints_init(model, i, j, *k):
    print("area_beta_breakpoints_init called")
    return list(area_bounds(model, i, j))

def area_beta_gradients_init(model, i, j, k):
    # Print statement for debugging area_beta_gradients_init
    print("area_beta_gradients_init called")
    gradients = [0]*(len(model.Area_beta_breakpoints[i,j,k])-1)
    for m in range(1,len(model.Area_beta_breakpoints[i,j,k])):
        numerator = model.Area_beta_exp[i,j,k][m+1] - model.Area_beta_exp[i,j,k][m]
        denominator = model.Area_beta_breakpoints[i,j,k][m+1] - model.Area_beta_breakpoints[i,j,k][m]
        gradients[m-1] = numerator/denominator
    return gradients

def area_cu_beta_breakpoints_init(model, i):
    print("area_cu_beta_breakpoints_init called")
    return list(area_cu_bounds(model, i))

def area_cu_beta_gradients_init(model, i):
    print("area_cu_beta_gradients_init called")
    gradients = [0]*(len(model.Area_cu_beta_breakpoints[i])-1)
    for m in range(1,len(model.Area_cu_beta_breakpoints[i])):
        numerator = model.Area_cu_beta_exp[i][m+1] - model.Area_cu_beta_exp[i][m]
        denominator = model.Area_cu_beta_breakpoints[i][m+1] - model.Area_cu_beta_breakpoints[i][m]
        gradients[m-1] = numerator/denominator
    return gradients

def area_hu_beta_breakpoints_init(model, j):
    print("area_hu_beta_breakpoints_init called")
    return list(area_hu_bounds(model, j))

def area_hu_beta_gradients_init(model, j):
    print("area_hu_beta_gradients_init called")
    gradients = [0]*(len(model.Area_hu_beta_breakpoints[j])-1)
    for m in range(1,len(model.Area_hu_beta_breakpoints[j])):
        numerator = model.Area_hu_beta_exp[j][m+1] - model.Area_hu_beta_exp[j][m]
        denominator = model.Area_hu_beta_breakpoints[j][m+1] - model.Area_hu_beta_breakpoints[j][m]
        gradients[m-1] = numerator/denominator
    return gradients
