from pyomo.environ import Var, Binary, NonNegativeReals
from .bound_generators import *
from .index_generators import *

def declare_concrete_variables(model):
    if hasattr(model, 'area'):
        model.del_component('area')
    model.area = Var(model.HP, model.CP, model.ST, bounds=area_bounds, initialize = 0, doc="area of the heat exchanger ijk")

    if hasattr(model, 'area_cu'):
        model.del_component('area_cu')
    model.area_cu = Var(model.HP, bounds=area_cu_bounds, initialize = 0, doc="area of the cooling heat exchanger i")

    if hasattr(model, 'area_hu'):
        model.del_component('area_hu')
    model.area_hu = Var(model.CP, bounds=area_hu_bounds, initialize = 0, doc="area of the heating heat exchanger j")

    if hasattr(model, 'area_beta'):
        model.del_component('area_beta')
    model.area_beta    = Var(model.HP, model.CP, model.ST, initialize = 0, domain=NonNegativeReals)
    if hasattr(model, 'area_cu_beta'):
        model.del_component('area_cu_beta')
    model.area_cu_beta = Var(model.HP, initialize = 0, domain=NonNegativeReals)
    if hasattr(model, 'area_hu_beta'):
        model.del_component('area_hu_beta')
    model.area_hu_beta = Var(model.CP, initialize = 0, domain=NonNegativeReals)

    # Flow rates 
    if hasattr(model, 'fh'):
        model.del_component('fh')
    model.fh = Var(model.HP, model.CP, model.ST, bounds = fh_bounds, initialize = 0, doc="Flow rate entering heat exchanger ijk cold side")
    if hasattr(model, 'fc'):
        model.del_component('fc')
    model.fc = Var(model.HP, model.CP, model.ST, bounds = fc_bounds, initialize = 0, doc="Flow rate entering heat exchanger ijk hot side")

    # Per exchanger outlet
    if hasattr(model, 'thx'):
        model.del_component('thx')
    model.thx = Var(model.HP, model.CP, model.ST, bounds=thx_bounds,\
            doc="Outlet temperature of the heat exchanger ijk hot side"  )
    if hasattr(model, 'tcx'):
        model.del_component('tcx')
    model.tcx = Var(model.HP, model.CP, model.ST, bounds=tcx_bounds,\
            doc="Outlet temperature of the heat exchanger ijk cold side" )

    # Temperature approaches
    if hasattr(model, 'dt'):
        model.del_component('dt')
    model.dt    = Var(model.HP, model.CP, model.K, bounds=dt_bounds,\
            doc="Approach between i and j in location k"  )
    if hasattr(model, 'dt_cu'):
        model.del_component('dt_cu')
    model.dt_cu = Var(model.HP,                    bounds=dt_cu_bounds,\
            doc="Approach between i and the cold utility" )
    if hasattr(model, 'dt_hu'):
        model.del_component('dt_hu')
    model.dt_hu = Var(model.CP,                    bounds=dt_hu_bounds,\
            doc="Approach between j and the hot utility"  )

    # Log mean temperature differences
    if hasattr(model, 'reclmtd'):
        model.del_component('reclmtd')
    model.reclmtd    = Var(model.HP, model.CP, model.ST, bounds=reclmtd_bounds,\
            doc="Log mean temperature difference between hot stream i and cold stream j at stage k" )
    if hasattr(model, 'reclmtd_cu'):
        model.del_component('reclmtd_cu')
    model.reclmtd_cu = Var(model.HP,                     bounds=reclmtd_cu_bounds,\
            doc="Log mean temperature difference between hot stream i and cold utility"             )
    if hasattr(model, 'reclmtd_hu'):
        model.del_component('reclmtd_hu')
    model.reclmtd_hu = Var(model.CP,                     bounds=reclmtd_hu_bounds,\
            doc="Log mean temperature difference between cold stream j and hot utility"             )

    # Heat loads
    if hasattr(model, 'q'):
        model.del_component('q')
    model.q    = Var(model.HP, model.CP, model.ST, bounds=q_bounds, initialize = 0,\
            doc="heat load between hot stream i and cold stream j at stage k" )
    if hasattr(model, 'q_cu'):
        model.del_component('q_cu')
    model.q_cu = Var(model.HP,                     bounds=q_cu_bounds, initialize = 0,\
            doc="heat load between hot stream i and cold utility"             )
    if hasattr(model, 'q_hu'):
        model.del_component('q_hu')
    model.q_hu = Var(model.CP,                     bounds=q_hu_bounds, initialize = 0,\
            doc="heat load between cold stream j and hot utility"             )

    # Per stage temperatures
    if hasattr(model, 'th'):
        model.del_component('th')
    model.th = Var(model.HP, model.K, bounds=th_bounds,\
            doc="temperature of hot stream i at hot end of stage k"  )
    if hasattr(model, 'tc'):
        model.del_component('tc')
    model.tc = Var(model.CP, model.K, bounds=tc_bounds,\
            doc="temperature of cold stream j at hot end of stage k" )

    # Binary variables
    if hasattr(model, 'z'):
        model.del_component('z')
    model.z    = Var(model.HP, model.CP, model.ST, initialize = 0, domain=Binary,\
            doc="existence of the match between hot stream i and cold stream j at stage k" )
    if hasattr(model, 'z_cu'):
        model.del_component('z_cu')
    model.z_cu = Var(model.HP,                     initialize = 0, domain=Binary,\
            doc="existence of the match between hot stream i and cold utility"             )
    if hasattr(model, 'z_hu'):
        model.del_component('z_hu')
    model.z_hu = Var(model.CP,                     initialize = 0, domain=Binary,\
            doc="existence of the match between cold stream j and hot utility"             )

    if hasattr(model, 'z_area_beta'):
        model.del_component('z_area_beta')
    model.z_area_beta = Var(z_area_beta_index, domain=Binary)
    if hasattr(model, 'z_area_cu_beta'):
        model.del_component('z_area_cu_beta')
    model.z_area_cu_beta = Var(z_area_cu_beta_index, domain=Binary)
    if hasattr(model, 'z_area_hu_beta'):
        model.del_component('z_area_hu_beta')
    model.z_area_hu_beta = Var(z_area_hu_beta_index, domain=Binary)

    if hasattr(model, 'z_q'):
        model.del_component('z_q')
    model.z_q     = Var(z_q_index,      domain=Binary)
    if hasattr(model, 'z_q_cu'):
        model.del_component('z_q_cu')
    model.z_q_cu  = Var(z_q_cu_index,   domain=Binary)
    if hasattr(model, 'z_q_hu'):
        model.del_component('z_q_hu')
    model.z_q_hu  = Var(z_q_hu_index,   domain=Binary)

    if hasattr(model, 'var_delta_reclmtd'):
        model.del_component('var_delta_reclmtd')
    model.var_delta_reclmtd    = Var(z_q_index,    domain=NonNegativeReals)
    if hasattr(model, 'var_delta_reclmtd_cu'):
        model.del_component('var_delta_reclmtd_cu')
    model.var_delta_reclmtd_cu = Var(z_q_cu_index, domain=NonNegativeReals)
    if hasattr(model, 'var_delta_reclmtd_hu'):
        model.del_component('var_delta_reclmtd_hu')
    model.var_delta_reclmtd_hu = Var(z_q_hu_index, domain=NonNegativeReals)

    # New variables
    if hasattr(model, 'bh_in'):
        model.del_component('bh_in')
    model.bh_in  = Var(model.HP, model.CP, model.ST,  bounds=bh_bounds)
    if hasattr(model, 'bh_out'):
        model.del_component('bh_out')
    model.bh_out = Var(model.HP, model.CP, model.ST,  bounds=bh_bounds)
    if hasattr(model, 'bc_in'):
        model.del_component('bc_in')
    model.bc_in  = Var(model.HP, model.CP, model.ST,  bounds=bc_bounds)
    if hasattr(model, 'bc_out'):
        model.del_component('bc_out')
    model.bc_out = Var(model.HP, model.CP, model.ST,  bounds=bc_bounds)

    if hasattr(model, 'z_th'):
        model.del_component('z_th')
    model.z_th   = Var(z_th_index,  domain=Binary)
    if hasattr(model, 'z_thx'):
        model.del_component('z_thx')
    model.z_thx  = Var(z_thx_index, domain=Binary)
    if hasattr(model, 'z_tc'):
        model.del_component('z_tc')
    model.z_tc   = Var(z_tc_index,  domain=Binary)
    if hasattr(model, 'z_tcx'):
        model.del_component('z_tcx')
    model.z_tcx  = Var(z_tcx_index, domain=Binary)

    if hasattr(model, 'var_delta_fh'):
        model.del_component('var_delta_fh')
    model.var_delta_fh  = Var(var_delta_fh_index,  domain=NonNegativeReals)
    if hasattr(model, 'var_delta_fhx'):
        model.del_component('var_delta_fhx')
    model.var_delta_fhx = Var(var_delta_fhx_index, domain=NonNegativeReals)
    if hasattr(model, 'var_delta_fc'):
        model.del_component('var_delta_fc')
    model.var_delta_fc  = Var(var_delta_fc_index,  domain=NonNegativeReals)
    if hasattr(model, 'var_delta_fcx'):
        model.del_component('var_delta_fcx')
    model.var_delta_fcx = Var(var_delta_fcx_index, domain=NonNegativeReals)
