# Author: Miten Mistry
#         Department of Computing, Imperial College London

def z_th_index(model):
    print("z_th_index called")
    for i in model.HP:
        for k in model.ST:
            for point in range(1, len(model.Th_breakpoints[i,k])):
                yield (i,k, point)

z_th_index.dimen = 3

def z_thx_index(model):
    print("z_thx_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Thx_breakpoints[i,j,k])):
                    yield (i,j,k,point)

z_thx_index.dimen = 4

def z_tc_index(model):
    print("z_tc_index called")
    for j in model.CP:
        for k in model.K_Take_First_Stage:
            for point in range(1, len(model.Tc_breakpoints[j,k])):
                yield (j,k, point)

z_tc_index.dimen = 3

def z_tcx_index(model):
    print("z_tcx_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Tcx_breakpoints[i,j,k])):
                    yield (i,j,k,point)

z_tcx_index.dimen = 4

def var_delta_fh_index(model):
    print("var_delta_fh_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Th_breakpoints[i,k])):
                    yield (i,j,k, point)

var_delta_fh_index.dimen = 4

def var_delta_fhx_index(model):
    print("var_delta_fhx_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Thx_breakpoints[i,j,k])):
                    yield (i,j,k, point)

var_delta_fhx_index.dimen = 4

def var_delta_fc_index(model):
    print("var_delta_fc_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Tc_breakpoints[j,k+1])):
                    yield (i,j,k, point)

var_delta_fc_index.dimen = 4

def var_delta_fcx_index(model):
    print("var_delta_fcx_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Tcx_breakpoints[i,j,k])):
                    yield (i,j,k, point)

var_delta_fcx_index.dimen = 4

def reclmtd_index(model):
    print("reclmtd_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in model.Reclmtd_gradient_points[i,j,k]:
                    yield (i,j,k) + point

reclmtd_index.dimen = 5

def reclmtd_cu_index(model):
    print("reclmtd_cu_index called")
    for i in model.HP:
        for point in model.Reclmtd_cu_gradient_points[i]:
            yield (i,point)

reclmtd_cu_index.dimen = 2

def reclmtd_hu_index(model):
    print("reclmtd_hu_index called")
    for j in model.CP:
        for point in model.Reclmtd_hu_gradient_points[j]:
            yield (j,point)

reclmtd_hu_index.dimen = 2

def z_q_index(model):
    print("z_q_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1, len(model.Q_breakpoints[i,j,k])):
                    yield (i,j,k,point)

z_q_index.dimen = 4

def z_q_cu_index(model):
    print("z_q_cu_index called")
    for i in model.HP:
        for point in range(1, len(model.Q_cu_breakpoints[i])):
            yield (i,point)

z_q_cu_index.dimen = 2

def z_q_hu_index(model):
    print("z_q_hu_index called")
    for j in model.CP:
        for point in range(1, len(model.Q_hu_breakpoints[j])):
            yield (j,point)

z_q_hu_index.dimen = 2

def z_area_beta_index(model):
    print("z_area_beta_index called")
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for point in range(1,len(model.Area_beta_breakpoints[i,j,k])):
                    yield (i,j,k,point)

z_area_beta_index.dimen = 4

def z_area_cu_beta_index(model):
    print("z_area_cu_beta_index called")
    for i in model.HP:
        for point in range(1,len(model.Area_cu_beta_breakpoints[i])):
            yield (i,point)

z_area_cu_beta_index.dimen = 2

def z_area_hu_beta_index(model):
    print("z_area_hu_beta_index called")
    for j in model.CP:
        for point in range(1,len(model.Area_hu_beta_breakpoints[j])):
            yield (j,point)

z_area_hu_beta_index.dimen = 2
