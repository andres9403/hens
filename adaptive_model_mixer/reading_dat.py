from pyomo.environ import *
from pyomo.dataportal import DataPortal
from lib_concrete.model_concrete_declarations.concrete_model_builder import build_concrete_model
from pyomo.opt import SolverFactory
from lib_concrete.iterations_helper import IterationState
from lib_concrete.model_concrete_declarations.constraints import declare_concrete_constraints
from lib_concrete.model_concrete_declarations.parameters_init import init_concrete_parameters
from lib_concrete.model_concrete_declarations.variables import declare_concrete_variables
from lib_concrete.model_concrete_declarations.objective import declare_concrete_objective
from lib_concrete.constants import * 
import sys, os, copy, time, socket
from multiprocessing import Process, cpu_count

def can_terminate_absolute(epsilons, max_errors):
    if epsilons[balancing_ref] <= max_errors[balancing_ref][absolute_error]:
        return False
    if epsilons[reclmtd_ref] <= max_errors[reclmtd_ref][absolute_error]:
        return False
    if epsilons[area_ref] <= max_errors[area_ref][absolute_error]:
        return False
    if epsilons[beta_ref] <= max_errors[beta_ref][absolute_error]:
        return False
    return True

def can_terminate_relative(epsilons, max_errors):
    if epsilons[balancing_ref] <= max_errors[balancing_ref][relative_error]:
        print('balancing: %s, %s' % (str(max_errors[balancing_ref][relative_error]),str(epsilons[balancing_ref])))
        return False
    if epsilons[reclmtd_ref] <= max_errors[reclmtd_ref][relative_error]:
        print('lmtd: %s, %s' % (str(max_errors[reclmtd_ref][relative_error]),str(epsilons[reclmtd_ref])))
        return False
    if epsilons[area_ref] <= max_errors[area_ref][relative_error]:
        print('area: %s, %s' % (str(max_errors[area_ref][relative_error]),str(epsilons[area_ref])))
        return False
    if epsilons[beta_ref] <= max_errors[beta_ref][relative_error]:
        print('beta: %s, %s' % (str(max_errors[beta_ref][relative_error]),str(epsilons[beta_ref])))
        return False
    return True


def parse_dat_to_dict(dat_file):
    dp = DataPortal()
    dp.load(filename=dat_file)
    data_dict = {name: dp.data(name) for name in dp.data()}
    return data_dict

termination_func = can_terminate_relative
start = time.time()
number_of_cores = cpu_count()
state = IterationState()

argparser = state.initialise_parser()
args = argparser.parse_args()
state.validate_and_assign_args(args)

data = parse_dat_to_dict("/home/andresfel9403/hens/datafiles/model3.dat")
print(data)

solver = 'gurobi'
opt = SolverFactory(solver)
opt.options[ 'MIPFocus' ] = 1

tolerances = {
    'IntFeasTol': -1,
    'FeasibilityTol': -1,
    'OptimalityTol': -1
}

if args.tighten_tol:
    opt.options[ 'IntFeasTol' ]     = 0.000000001
    opt.options[ 'FeasibilityTol' ] = 0.000000001
    opt.options[ 'OptimalityTol' ]  = 0.000000001
    tolerances['IntFeasTol'] = 0.000000001
    tolerances['FeasibilityTol'] = 0.000000001
    tolerances['OptimalityTol'] = 0.000000001
else:
    if args.IntFeasTol:
        opt.options[ 'IntFeasTol' ] = args.IntFeasTol
        tolerances[ 'IntFeasTol' ] = args.IntFeasTol
    if args.FeasibilityTol:
        opt.options[ 'FeasibilityTol' ] = args.FeasibilityTol
        tolerances[ 'FeasibilityTol' ] = args.FeasibilityTol
    if args.OptimalityTol:
        opt.options[ 'OptimalityTol' ] = args.OptimalityTol
        tolerances[ 'OptimalityTol' ] = args.OptimalityTol
    if args.MarkowitzTol:
        opt.options[ 'MarkowitzTol' ] = args.MarkowitzTol
        tolerances[ 'MarkowitzTol' ] = args.MarkowitzTol

warmstart = False

# Tolerances and epsilons
default_eps = 0.0001

epsilons = {
    balancing_ref: default_eps,
    reclmtd_ref: default_eps,
    area_ref: default_eps,
    beta_ref: default_eps
}

if args.all_error:
    eps = args.all_error
    epsilons[balancing_ref] = eps
    epsilons[reclmtd_ref] = eps
    epsilons[area_ref] = eps
    epsilons[beta_ref] = eps
else:
    if args.bal_eps:
        epsilons[balancing_ref] = args.bal_eps
    if args.lmtd_eps:
        epsilons[reclmtd_ref] = args.lmtd_eps
    if args.area_eps:
        epsilons[area_ref] = args.area_eps
    if args.beta_eps:
        epsilons[beta_ref] = args.beta_eps

if args.absolute:
    termination_func = can_terminate_absolute


model = build_concrete_model(data)
_ = state.safe_initial_breakpoints(model)

max_iterations = 3

new_points = copy.deepcopy(state.get_all_points())

for i in range(1, max_iterations):
    if i == 1:
        model = state.add_tangent_points(model)
        _ = declare_concrete_constraints(model)
        num_vars = len(list(model.component_data_objects(Var, active=True)))
        num_cons = len(list(model.component_data_objects(Constraint, active=True)))
        print(num_vars, 'variables')
        print(num_cons, 'constraints')
    else:
        model = state.add_tangent_points(model)
        model = state.add_T_breakpoints(model)
        model = state.add_q_breakpoints(model)
        model = state.add_area_beta_breakpoints(model)
        _ = init_concrete_parameters(model)
        _ = declare_concrete_variables(model)
        _ = declare_concrete_constraints(model)
        _ = declare_concrete_objective(model)
        num_vars = len(list(model.component_data_objects(Var, active=True)))
        num_cons = len(list(model.component_data_objects(Constraint, active=True)))
        print(num_vars, 'variables')
        print(num_cons, 'constraints')
        new_model = copy.deepcopy(model)



    results = opt.solve(model, tee=True)
    model.solutions.load_from(results)

    active_hx, inactive_hx = state.get_active_hx(model)
    new_tangent_points = state.get_new_tangent_points(model, active_hx) 
    added_tangents    = state.add_new_tangent_points(new_tangent_points)
    new_q_breakpoints = state.get_new_q_breakpoints(model, active_hx)
    new_beta_breakpoints = state.get_new_beta_breakpoints(model, active_hx)
    new_balancing_breakpoints = state.get_new_balancing_breakpoints(model, active_hx, inactive_hx, args.weaken)

    new_points = copy.deepcopy(state.get_all_points())

    errors = state.summarise_errors(model, active_hx, inactive_hx, args.weaken)
    max_errors = state.get_max_errors(errors, active_hx, inactive_hx, args.weaken)

 


  

   


