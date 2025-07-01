# Author: Miten Mistry
#         Department of Computing, Imperial College London

from pyomo.environ import value
from functools import wraps

# ------------------------------------------------------------------
#  Helper decorator: attach .dimen automatically
# ------------------------------------------------------------------
def index_set(dimen):
    """Decorator to set the .dimen attribute on a generator function."""
    def decorator(f):
        f.dimen = dimen
        return f
    return decorator


# ------------------------------------------------------------------
#  Break-point index helpers
# ------------------------------------------------------------------
@index_set(3)
def z_th_index(model):
    """(i, k, point)  –  break-points on Th(i,k)  (skip point 0)."""
    for i in model.HP:
        for k in model.ST:
            if (i, k) in model.Th_breakpoints:
                n = len(model.Th_breakpoints[i, k])
                yield from ((i, k, p) for p in range(1, n))


@index_set(4)
def z_thx_index(model):
    """(i, j, k, point) – break-points on Thx(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Thx_breakpoints:
                    n = len(model.Thx_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(3)
def z_tc_index(model):
    """(j, k, point) – break-points on Tc(j,k) (k≠first stage)."""
    for j in model.CP:
        for k in model.K_Take_First_Stage:
            if (j, k) in model.Tc_breakpoints:
                n = len(model.Tc_breakpoints[j, k])
                yield from ((j, k, p) for p in range(1, n))


@index_set(4)
def z_tcx_index(model):
    """(i, j, k, point) – break-points on Tcx(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Tcx_breakpoints:
                    n = len(model.Tcx_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


# ------------------------------------------------------------------
#  Δ-flow indices
# ------------------------------------------------------------------
@index_set(4)
def var_delta_fh_index(model):
    """(i, j, k, point) – Δfh break-points tied to Th(i,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, k) in model.Th_breakpoints:
                    n = len(model.Th_breakpoints[i, k])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(4)
def var_delta_fhx_index(model):
    """(i, j, k, point) – Δfhx break-points tied to Thx(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Thx_breakpoints:
                    n = len(model.Thx_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(4)
def var_delta_fc_index(model):
    """(i, j, k, point) – Δfc break-points tied to Tc(j,k+1)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                key = (j, k + 1)
                if key in model.Tc_breakpoints:
                    n = len(model.Tc_breakpoints[key])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(4)
def var_delta_fcx_index(model):
    """(i, j, k, point) – Δfcx break-points tied to Tcx(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Tcx_breakpoints:
                    n = len(model.Tcx_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


# ------------------------------------------------------------------
#  Reclmtd gradient indices
# ------------------------------------------------------------------
@index_set(5)
def reclmtd_index(model):
    """(i, j, k, x, y) – 2-D gradient points for each (i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                for (x, y) in model.Reclmtd_gradient_points[i, j, k]:
                    yield (i, j, k, x, y)


@index_set(2)
def reclmtd_cu_index(model):
    """(i, point) – gradient points for CU exchanger i."""
    for i in model.HP:
        yield from ((i, pt) for pt in model.Reclmtd_cu_gradient_points[i])


@index_set(2)
def reclmtd_hu_index(model):
    """(j, point) – gradient points for HU exchanger j."""
    for j in model.CP:
        yield from ((j, pt) for pt in model.Reclmtd_hu_gradient_points[j])


# ------------------------------------------------------------------
#  Q-break-point indices
# ------------------------------------------------------------------
@index_set(4)
def z_q_index(model):
    """(i, j, k, point) – break-points on q(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Q_breakpoints:
                    n = len(model.Q_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(2)
def z_q_cu_index(model):
    """(i, point) – break-points on q_cu(i)."""
    for i in model.HP:
        n = len(model.Q_cu_breakpoints[i])
        yield from ((i, p) for p in range(1, n))


@index_set(2)
def z_q_hu_index(model):
    """(j, point) – break-points on q_hu(j)."""
    for j in model.CP:
        n = len(model.Q_hu_breakpoints[j])
        yield from ((j, p) for p in range(1, n))


# ------------------------------------------------------------------
#  Area-beta break-point indices
# ------------------------------------------------------------------
@index_set(4)
def z_area_beta_index(model):
    """(i, j, k, point) – break-points on area^β for HX(i,j,k)."""
    for i in model.HP:
        for j in model.CP:
            for k in model.ST:
                if (i, j, k) in model.Area_beta_breakpoints:
                    n = len(model.Area_beta_breakpoints[i, j, k])
                    yield from ((i, j, k, p) for p in range(1, n))


@index_set(2)
def z_area_cu_beta_index(model):
    """(i, point) – break-points on area_cu^β."""
    for i in model.HP:
        n = len(model.Area_cu_beta_breakpoints[i])
        yield from ((i, p) for p in range(1, n))


@index_set(2)
def z_area_hu_beta_index(model):
    """(j, point) – break-points on area_hu^β."""
    for j in model.CP:
        n = len(model.Area_hu_beta_breakpoints[j])
        yield from ((j, p) for p in range(1, n))




# def z_th_index(model):
#     for i in model.HP:
#         for k in model.ST:
#             for point in range(1, len(model.Th_breakpoints[i,k])):
#                 yield (i,k, point)

# z_th_index.dimen = 3

# def z_thx_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Thx_breakpoints[i,j,k])):
#                     yield (i,j,k,point)

# z_thx_index.dimen = 4

# def z_tc_index(model):
#     for j in model.CP:
#         for k in model.K_Take_First_Stage:
#             for point in range(1, len(model.Tc_breakpoints[j,k])):
#                 yield (j,k, point)

# z_tc_index.dimen = 3

# def z_tcx_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Tcx_breakpoints[i,j,k])):
#                     yield (i,j,k,point)

# z_tcx_index.dimen = 4

# def var_delta_fh_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Th_breakpoints[i,k])):
#                     yield (i,j,k, point)

# var_delta_fh_index.dimen = 4

# def var_delta_fhx_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Thx_breakpoints[i,j,k])):
#                     yield (i,j,k, point)

# var_delta_fhx_index.dimen = 4

# def var_delta_fc_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Tc_breakpoints[j,k+1])):
#                     yield (i,j,k, point)

# var_delta_fc_index.dimen = 4

# def var_delta_fcx_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Tcx_breakpoints[i,j,k])):
#                     yield (i,j,k, point)

# var_delta_fcx_index.dimen = 4

# def reclmtd_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in model.Reclmtd_gradient_points[i,j,k]:
#                     yield (i,j,k) + point

# reclmtd_index.dimen = 5

# def reclmtd_cu_index(model):
#     for i in model.HP:
#         for point in model.Reclmtd_cu_gradient_points[i]:
#             yield (i,point)

# reclmtd_cu_index.dimen = 2

# def reclmtd_hu_index(model):
#     for j in model.CP:
#         for point in model.Reclmtd_hu_gradient_points[j]:
#             yield (j,point)

# reclmtd_hu_index.dimen = 2

# def z_q_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1, len(model.Q_breakpoints[i,j,k])):
#                     yield (i,j,k,point)

# z_q_index.dimen = 4

# def z_q_cu_index(model):
#     for i in model.HP:
#         for point in range(1, len(model.Q_cu_breakpoints[i])):
#             yield (i,point)

# z_q_cu_index.dimen = 2

# def z_q_hu_index(model):
#     for j in model.CP:
#         for point in range(1, len(model.Q_hu_breakpoints[j])):
#             yield (j,point)

# z_q_hu_index.dimen = 2

# def z_area_beta_index(model):
#     for i in model.HP:
#         for j in model.CP:
#             for k in model.ST:
#                 for point in range(1,len(model.Area_beta_breakpoints[i,j,k])):
#                     yield (i,j,k,point)

# z_area_beta_index.dimen = 4

# def z_area_cu_beta_index(model):
#     for i in model.HP:
#         for point in range(1,len(model.Area_cu_beta_breakpoints[i])):
#             yield (i,point)

# z_area_cu_beta_index.dimen = 2

# def z_area_hu_beta_index(model):
#     for j in model.CP:
#         for point in range(1,len(model.Area_hu_beta_breakpoints[j])):
#             yield (j,point)

# z_area_hu_beta_index.dimen = 2
