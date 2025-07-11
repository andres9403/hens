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
from pprint import pprint
from lib_concrete.results_generator.results_builder import build_heat_exchanger_results
import matplotlib.pyplot as plt
import csv


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

## Create a folder to save the results

if not os.path.exists(os.path.join('.', args.model, args.run_name)):
    folders = state.create_output_dir('.', args.model, args.run_name)
else:
    print(f"Folder '{os.path.join('.', args.model, args.run_name)}' already exists.")
    folders = {
        'model_folder': os.path.join('.', args.model),
        'append_folder': os.path.join('.', args.model, args.run_name),
        'iterations_folder': os.path.join('.', args.model, args.run_name, 'iterations'),
        'logs_folder': os.path.join('.', args.model, args.run_name, 'iterations', 'logs'),
    }

output_file = open(os.path.join(folders[append_folder], 'output.txt'), 'w')
results_file = open(os.path.join(folders[append_folder], 'results.csv'), 'w')

results_file.write('iteration, tac, time, total_time\n')


datafile = os.path.join('datafiles', f"{args.model}.dat")
data = parse_dat_to_dict(datafile)

## Optimization solver options
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

iterations = 1
max_iterations = 22

new_points = copy.deepcopy(state.get_all_points())

output_file.write('Running:\n')
output_file.write('\tAdaptive Model\n')
output_file.write('\t' + args.model + '\n')
output_file.write('on: '+ socket.gethostname() + '\n\n')

iter_finish = start

tac_history = {}
relative_error_history = {balancing_ref: [], reclmtd_ref: [], area_ref: [], beta_ref: []}
error_history = {balancing_ref: [], reclmtd_ref: [], area_ref: [], beta_ref: []}    

for run in range(1, max_iterations):

    iter_start = iter_finish
    print('Running iteration ', run)

    output_file.write('----------------------------------\n')
    output_file.write('---- Run: ' + str(run) + '\n')
    output_file.write('----------------------------------\n')

    if run == 1:
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
        #new_model = copy.deepcopy(model)



    results = opt.solve(model, tee=True)
    model.solutions.load_from(results)

    old_points = new_points

    active_hx, inactive_hx = state.get_active_hx(model)
    new_tangent_points = state.get_new_tangent_points(model, active_hx) 
    added_tangents    = state.add_new_tangent_points(new_tangent_points)
    new_q_breakpoints = state.get_new_q_breakpoints(model, active_hx)
    new_beta_breakpoints = state.get_new_beta_breakpoints(model, active_hx)
    new_balancing_breakpoints = state.get_new_balancing_breakpoints(model, active_hx, inactive_hx, args.weaken)

    new_points = copy.deepcopy(state.get_all_points())

    output_file.write('----------------------------------\n')
    output_file.write('---- TAC: ' + str(value(model.TAC)) + '\n')
    output_file.write('----------------------------------\n')
    output_file.write('\n')
    output_file.write('Found ActiveHx:\n')
    pprint(active_hx, output_file)
    output_file.write('\n')
    output_file.write('Adding Tangents at:\n')
    pprint(added_tangents, output_file)
    output_file.write('\n')
    output_file.write('Adding Balancing breakpoints at:\n')
    pprint(new_balancing_breakpoints, output_file)
    output_file.write('\n')
    output_file.write('Adding q breakpoints at:\n')
    pprint(new_q_breakpoints, output_file)
    output_file.write('\n')
    output_file.write('Adding area beta breakpoints at:\n')
    pprint(new_beta_breakpoints, output_file)
    output_file.write('\n')

    output_file.flush()

    iter_finish = time.time()

    local_time = iter_finish-iter_start
    total_time = iter_finish-start

    print('\tTAC: %f' % value(model.TAC))
    print('\tTook: %.2fs' % local_time)
    print('\tTotal: %.2fs' % total_time)

    results_file.write('%d, %s, %s, %s\n' % (run, str(value(model.TAC)), str(local_time), str(total_time)))

    results_file.flush()

    errors = state.summarise_errors(model, active_hx, inactive_hx, args.weaken)
    max_errors = state.get_max_errors(errors, active_hx, inactive_hx, args.weaken)

 

    for key in max_errors:
        # Use absolute error for plotting; change to relative if needed
        error_history[key].append(max_errors[key][absolute_error])
        relative_error_history[key].append(max_errors[key][relative_error])

    tac_history[run] = value(model.TAC)

    filename = 'iteration' + str(run).zfill(len(str(max_iterations)))
    t = Process(target=build_heat_exchanger_results, args=(model, folders, args.run_name, run, args.model, filename, active_hx, old_points, errors, local_time, total_time, epsilons, tolerances), kwargs={'iteration': True})
    t.start()

    if termination_func(epsilons, max_errors):
        print('/*/*/*/*//*/*/*/*//*/*/*/*//*/*/*/')
        print('----------------------------------')
        print('---- Completed Within Error')
        print('----------------------------------')
        print('/*/*/*/*//*/*/*/*//*/*/*/*//*/*/*/')
        break

    if  len(added_tangents) == 0 \
        and len(new_beta_breakpoints) == 0\
        and len(new_q_breakpoints) == 0\
        and len(new_balancing_breakpoints) == 0:
        print('/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/')
        print('---------------------------------------------------')
        print('---- Completed No new tangents or breakpoints -----')
        print('---------------------------------------------------')
        print('/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/')
        break

    if args.cont:
        if iterations == 1:
            var = raw_input('Ran %d iterations. How many more?\n' % run)
            while True:
                try:
                    iters = int(var)
                except ValueError:
                    var = raw_input('\'%s\' is not an integer. How many more?\n' % var)
                else:
                    break

            if iters <= 0:
                print('/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/')
                print('-----------------------------------')
                print('---- Completed Not Continuing -----')
                print('-----------------------------------')
                print('/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/')
                break
            else:
                iterations = iters + 1
        iterations = iterations - 1

if args.print_instance:
    model.pprint()


plt.figure(figsize=(10, 6))
plt.suptitle('Max Relative Errors per Iteration')
plt.xlabel('Iteration')
plt.ylabel('Max Relative Error')
plt.grid(True)

for key, errors in relative_error_history.items():
    plt.plot(range(1, len(errors) + 1), errors, label=str(key))
plt.legend()
plt.show()


if args.print_instance:
    instance.pprint()
    # Store tac_history in a CSV file

tac_csv_path = os.path.join(folders[append_folder], 'tac_history.csv')
with open(tac_csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['iteration', 'tac'])
    for iter_num, tac_val in tac_history.items():
        writer.writerow([iter_num, tac_val])

plt.figure(figsize=(10, 6))
plt.plot(list(tac_history.keys()), list(tac_history.values()), marker='o')
plt.title('TAC per Iteration')
plt.xlabel('Iteration')
plt.ylabel('TAC')
plt.grid(True)
plt.show()



output_file.close()
results_file.close()


  

   


