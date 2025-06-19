# Author: Miten Mistry
#         Department of Computing, Imperial College London

import pyomo.environ
import sys, os, copy, time, socket

from multiprocessing import Process, cpu_count

from pyomo.opt import SolverFactory
from pprint import pprint

from lib.iterations_helper import *
from lib.results_generator.results_builder import build_heat_exchanger_results
from lib.constants import *


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

termination_func = can_terminate_relative

start = time.time()

maxIters = 500

number_of_cores = cpu_count()

argparser = initialise_parser()
args = argparser.parse_args()

validate_and_assign_args(args)

folders = create_output_dir('.', args.model, args.run_name)

output_file = open(os.path.join(folders[append_folder], 'output.txt'), 'w')
results_file = open(os.path.join(folders[append_folder], 'results.csv'), 'w')

results_file.write('iteration, tac, time, total_time\n')

datafile = '/home/andresfel9403/hens/datafiles/' + args.model + '.dat'

#solver = args.solver
solver = 'gurobi_direct'

if solver == 'gurobi_direct':
    opt = SolverFactory(solver)
    if args.num_threads:
        opt.options[ 'threads' ] = min(number_of_cores, args.num_threads)
    opt.options['NonConvex'] = 2

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

experiment = args.model_type

model = initialise_hx_model(datafile, experiment)

if experiment == 'MINLP':
    instance = model.create_instance(datafile)
    results = opt.solve(instance, tee=True)
    instance.solutions.load_from(results)
    if args.print_instance:
        instance.pprint()
    output_file.close()
    results_file.close()
else:
    warmstart = False

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

    iterations = 1

    new_points = copy.deepcopy(get_all_points())

    output_file.write('Running:\n')
    output_file.write('\tAdaptive Model\n')
    output_file.write('\t' + args.model + '\n')
    output_file.write('on: '+ socket.gethostname() + '\n\n')

    iter_finish = start

    for run in range(1, maxIters):
        iter_start = iter_finish

        print('Running iteration ', run)

        instance = model.create_instance(datafile)

        # Print the number of nonlinear constraints
        from pyomo.core.expr.visitor import polynomial_degree
        from pyomo.environ import Constraint
        nonlinear_constraints = 0
        for c in instance.component_objects(Constraint, active=True):
            for idx in c:
                expr = c[idx].body
                deg = polynomial_degree(expr)
                if deg is None or deg > 1:
                    nonlinear_constraints += 1
        print(f"********************Model has {nonlinear_constraints} nonlinear constraints.")

        output_file.write('----------------------------------\n')
        output_file.write('---- Run: ' + str(run) + '\n')
        output_file.write('----------------------------------\n')

        opt.options[ 'LogFile' ] = os.path.join(folders[ logs_folder ], 'gur' + str(run).zfill(len(str(maxIters))) + '.log')

        results = opt.solve(instance, tee=True)
        
        instance.solutions.load_from(results)

        if experiment == 'Reformulation':

            old_points = new_points

            active_hx, inactive_hx         = get_active_hx(instance)

            new_tangent_points = get_new_tangent_points(instance, active_hx)
            added_tangents    = add_new_tangent_points(new_tangent_points)
            new_q_breakpoints = get_new_q_breakpoints(instance, active_hx)
            new_beta_breakpoints = get_new_beta_breakpoints(instance, active_hx)
            new_balancing_breakpoints = get_new_balancing_breakpoints(instance, active_hx, inactive_hx, args.weaken)

            new_points = copy.deepcopy(get_all_points())

        output_file.write('----------------------------------\n')
        output_file.write('---- TAC: ' + str(value(instance.TAC)) + '\n')
        output_file.write('----------------------------------\n')
        output_file.write('\n')

        if experiment == 'Reformulation':
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

        print('\tTAC: %f' % value(instance.TAC))
        print('\tTook: %.2fs' % local_time)
        print('\tTotal: %.2fs' % total_time)

        results_file.write('%d, %s, %s, %s\n' % (run, str(value(instance.TAC)), str(local_time), str(total_time)))

        results_file.flush()

        errors = summarise_errors(instance, active_hx, inactive_hx, args.weaken)
        max_errors = get_max_errors(errors, active_hx, inactive_hx, args.weaken)

        filename = 'iteration' + str(run).zfill(len(str(maxIters)))
        t = Process(target=build_heat_exchanger_results, args=(instance, folders, args.run_name, run, args.model, filename, active_hx, old_points, errors, local_time, total_time, epsilons, tolerances), kwargs={'iteration': True})
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
        instance.pprint()

    output_file.close()
    results_file.close()
