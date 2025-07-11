# Author: Miten Mistry
#         Department of Computing, Imperial College London

import os, sys, bisect

from argparse import ArgumentParser, RawTextHelpFormatter

from pprint import pprint

from pyomo.core.base.numvalue import value
from .model_declarations.model_builder import create_model
from .model_declarations.helper_functions import two_point_generator, three_point_generator, lmtd_inv

from .constants import *

class IterationState:
    def __init__(self):
        self.stream_tangent_points = {}
        self.cu_tangent_points     = {}
        self.hu_tangent_points     = {}

        self.stream_q_points = {}
        self.cu_q_points     = {}
        self.hu_q_points     = {}

        self.stream_area_betas = {}
        self.cu_area_betas     = {}
        self.hu_area_betas     = {}

        self.th_breakpoints  = {}
        self.thx_breakpoints = {}
        self.tc_breakpoints  = {}
        self.tcx_breakpoints = {}

    def create_output_dir(self, root, model, append):
        model_dir  = root + os.sep + model
        append_dir = model_dir + os.sep + append
        iterations_dir = append_dir + os.sep + iterations
        log_dir = iterations_dir + os.sep + logs

        if not os.path.exists(model_dir):
            os.makedirs(model_dir)

        if not os.path.exists(append_dir):
            os.makedirs(append_dir)

        if not os.path.exists(iterations_dir):
            os.makedirs(iterations_dir)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        return {\
            model_folder     : model_dir,\
            append_folder    : append_dir,\
            iterations_folder: iterations_dir,\
            logs_folder      : log_dir,\
        }

    @staticmethod
    def initialise_parser():
        parser = ArgumentParser()
        parser.add_argument('model', nargs='?', default='model1', help='The model you wish to run e.g. model1 for datafile: ../datafiles/model1.dat')
        parser.add_argument('run_name', nargs='?', default='test', help='The name of the run you are running the results will be placed in a directory with this name')
        parser.add_argument('-i', '--print-instance', help='print instance of final run', action='store_true')
        parser.add_argument('-t', '--num-threads', type=int, help='Number of cpu cores used.', default=1)
        parser.add_argument('-c', '--cont', help='Get continuation message.', action='store_true')
        parser.add_argument('-w', '--weaken', help='Skip breakpoints for inactive balancing constraints.', action='store_true')
        parser.add_argument('-a', '--absolute', help='Use absolute error', action='store_true')
        parser.add_argument('--lmtd-eps', type=float, default=0.001, help='Max absolute lmtd error. DEFAULT=0.0001')
        parser.add_argument('--bal-eps', type=float, default=0.001, help='Max absolute error for balancing bilinearities. DEFAULT=0.0001')
        parser.add_argument('--area-eps', type=float, default=0.01, help='Max absolute error for area bilinearities. DEFAULT=0.0001')
        parser.add_argument('--beta-eps', type=float, default=0.1, help='Max absolute error for area betas. DEFAULT=0.0001')
        parser.add_argument('-e', '--all-error', type=float, default=0.001, help='Max absolute error for all approximations. DEFAULT=0.0001')
        parser.add_argument('-m', '--tighten-tol', action='store_true', help='Tighten solver tolerances.')
        parser.add_argument('--IntFeasTol', type=float, default=1e-5, help='Integer feasibility tolerance.')
        parser.add_argument('--FeasibilityTol', type=float, default=1e-6, help='Primal feasibility tolerance.')
        parser.add_argument('--OptimalityTol', type=float, default=1e-6, help='Dual feasibility tolerance.')
        parser.add_argument('--MarkowitzTol', type=float, default=0.0078125, help='Pivoting tolerance.')
        return parser

    @staticmethod
    def validate_and_assign_args(args):
        if args.num_threads:
            if args.num_threads <= 0:
                raise ValueError('The number of threads must be positive')

    def add_initial_th_breakpoints(self, instance):
        for i in instance.HP:
            for k in instance.ST:
                self.th_breakpoints[i,k] = [m for m in instance.Th_breakpoints[i,k]]

    def add_initial_thx_breakpoints(self, instance):
        for i in instance.HP:
            for j in instance.CP:
                for k in instance.ST:
                    self.thx_breakpoints[i,j,k] = [m for m in instance.Thx_breakpoints[i,j,k]]

    def add_initial_tc_breakpoints(self, instance):
        for j in instance.CP:
            for k in instance.K_Take_First_Stage:
                self.tc_breakpoints[j,k] = [m for m in instance.Tc_breakpoints[j,k]]

    def add_initial_tcx_breakpoints(self, instance):
        for i in instance.HP:
            for j in instance.CP:
                for k in instance.ST:
                    self.tcx_breakpoints[i,j,k] = [m for m in instance.Tcx_breakpoints[i,j,k]]

    def add_initial_stream_tangent_points(self, instance):
        for i in instance.HP:
            for j in instance.CP:
                for k in instance.ST:
                    self.stream_tangent_points[i,j,k] = three_point_generator(defaultTangentWeights[stream_hx], instance.dt[i,j,k].bounds)

    def add_initial_cu_tangent_points(self, instance):
        for i in instance.HP:
            self.cu_tangent_points[i] = two_point_generator(defaultTangentWeights[cu_hx], instance.dt_cu[i].bounds)

    def add_initial_hu_tangent_points(self, instance):
        for j in instance.CP:
            self.hu_tangent_points[j] = two_point_generator(defaultTangentWeights[hu_hx], instance.dt_hu[j].bounds)

    def add_initial_stream_area_beta_points(self, instance):
        for i in instance.HP:
            for j in instance.CP:
                for k in instance.ST:
                    self.stream_area_betas[i,j,k] = [m for m in instance.Area_beta_breakpoints[i,j,k]]

    def add_initial_cu_area_beta_points(self, instance):
        for i in instance.HP:
            self.cu_area_betas[i] = [m for m in instance.Area_cu_beta_breakpoints[i]]

    def add_initial_hu_area_beta_points(self, instance):
        for j in instance.CP:
            self.hu_area_betas[j] = [m for m in instance.Area_hu_beta_breakpoints[j]]

    def add_initial_stream_q_points(self, instance):
        for i in instance.HP:
            for j in instance.CP:
                for k in instance.ST:
                    self.stream_q_points[i,j,k] = [m for m in instance.Q_breakpoints[i,j,k]]

    def add_initial_cu_q_points(self, instance):
        for i in instance.HP:
            self.cu_q_points[i] = [m for m in instance.Q_cu_breakpoints[i]]

    def add_initial_hu_q_points(self, instance):
        for j in instance.CP:
            self.hu_q_points[j] = [m for m in instance.Q_hu_breakpoints[j]]

    def declare_th_breakpoints(self, model, i, k):
        return self.th_breakpoints[i,k]

    def declare_thx_breakpoints(self, model, i, j, k):
        return self.thx_breakpoints[i,j,k]

    def declare_tc_breakpoints(self, model, j, k):
        return self.tc_breakpoints[j,k]

    def declare_tcx_breakpoints(self, model, i, j, k):
        return self.tcx_breakpoints[i,j,k]

    def declare_stream_tangent_points(self, model, i, j, k):
        return self.stream_tangent_points[i,j,k]

    def declare_cu_tangent_points(self, model, i):
        return self.cu_tangent_points[i]

    def declare_hu_tangent_points(self, model, j):
        return self.hu_tangent_points[j]

    def declare_stream_q_breakpoints(self, model, i, j, k):
        return self.stream_q_points[i,j,k]

    def declare_cu_q_breakpoints(self, model, i):
        return self.cu_q_points[i]

    def declare_hu_q_breakpoints(self, model, j):
        return self.hu_q_points[j]

    def declare_stream_area_beta_breakpoints(self, model, i, j, k):
        return self.stream_area_betas[i,j,k]

    def declare_cu_area_beta_breakpoints(self, model, i):
        return self.cu_area_betas[i]

    def declare_hu_area_beta_breakpoints(self, model, j):
        return self.hu_area_betas[j]

    def initialise_hx_model(self, datafile):
        model = create_model()
        instance = model.create_instance(datafile)

        self.add_initial_th_breakpoints(instance)
        self.add_initial_thx_breakpoints(instance)
        self.add_initial_tc_breakpoints(instance)
        self.add_initial_tcx_breakpoints(instance)

        self.add_initial_stream_tangent_points(instance)
        self.add_initial_cu_tangent_points(instance)
        self.add_initial_hu_tangent_points(instance)

        self.add_initial_stream_q_points(instance)
        self.add_initial_cu_q_points(instance)
        self.add_initial_hu_q_points(instance)

        self.add_initial_stream_area_beta_points(instance)
        self.add_initial_cu_area_beta_points(instance)
        self.add_initial_hu_area_beta_points(instance)

        # Use lambdas to wrap the methods for Pyomo initialize
        model.Th_breakpoints.initialize  = lambda model, i, k: self.declare_th_breakpoints(model, i, k)
        model.Thx_breakpoints.initialize = lambda model, i, j, k: self.declare_thx_breakpoints(model, i, j, k)
        model.Tc_breakpoints.initialize  = lambda model, j, k: self.declare_tc_breakpoints(model, j, k)
        model.Tcx_breakpoints.initialize = lambda model, i, j, k: self.declare_tcx_breakpoints(model, i, j, k)

        model.Reclmtd_gradient_points.initialize    = lambda model, i, j, k: self.declare_stream_tangent_points(model, i, j, k)
        model.Reclmtd_cu_gradient_points.initialize = lambda model, i: self.declare_cu_tangent_points(model, i)
        model.Reclmtd_hu_gradient_points.initialize = lambda model, j: self.declare_hu_tangent_points(model, j)

        model.Q_breakpoints.initialize = lambda model, i, j, k: self.declare_stream_q_breakpoints(model, i, j, k)
        model.Q_cu_breakpoints.initialize = lambda model, i: self.declare_cu_q_breakpoints(model, i)
        model.Q_hu_breakpoints.initialize = lambda model, j: self.declare_hu_q_breakpoints(model, j)

        model.Area_beta_breakpoints.initialize = lambda model, i, j, k: self.declare_stream_area_beta_breakpoints(model, i, j, k)
        model.Area_cu_beta_breakpoints.initialize = lambda model, i: self.declare_cu_area_beta_breakpoints(model, i)
        model.Area_hu_beta_breakpoints.initialize = lambda model, j: self.declare_hu_area_beta_breakpoints(model, j)

        return model

    def get_active_hx(self, instance):
        active_hx = {
            stream_hx    : [],
            cu_hx        : [],
            hu_hx        : []
        }
        inactive_hx = {
            stream_hx    : [],
            cu_hx        : [],
            hu_hx        : []
        }
        for index in instance.z:
            if value(instance.z[index]) >= active_lb:
                active_hx[stream_hx].append(index)
            else:
                inactive_hx[stream_hx].append(index)

        for index in instance.z_cu:
            if value(instance.z_cu[index]) >= active_lb:
                active_hx[cu_hx].append(index)
            else:
                inactive_hx[cu_hx].append(index)

        for index in instance.z_hu:
            if value(instance.z_hu[index]) >= active_lb:
                active_hx[hu_hx].append(index)
            else:
                inactive_hx[hu_hx].append(index)

        return active_hx, inactive_hx

    def get_new_tangent_points(self, instance, active_hx):
        new_tangents = {
            stream_hx    : {},
            cu_hx        : {},
            hu_hx        : {}
        }
        for index in active_hx[stream_hx]:
            x_index = index
            y_index = (index[0], index[1], index[2]+1)
            x = instance.dt[x_index].value
            y = instance.dt[y_index].value
            new_tangent_point = (x,y) if x >= y else (y,x)
            new_tangents[stream_hx][index] = new_tangent_point

        for index in active_hx[cu_hx]:
            x = instance.dt_cu[index].value
            new_tangents[cu_hx][index] = x

        for index in active_hx[hu_hx]:
            x = instance.dt_hu[index].value
            new_tangents[hu_hx][index] = x

        return new_tangents

    def get_new_balancing_breakpoints(self, instance, active_hx, inactive_hx, weaken):
        new_th_breakpoints = {}
        new_thx_breakpoints = {}
        new_tc_breakpoints = {}
        new_tcx_breakpoints = {}

        active_th_indices = list(set((i, k) for i, _, k in active_hx[stream_hx]))
        active_tc_indices = list(set((j, k+1) for _, j, k in active_hx[stream_hx]))

        for index in active_th_indices:
            breakpoint = instance.th[index].value
            if breakpoint not in self.th_breakpoints[index]:
                bisect.insort(self.th_breakpoints[index], breakpoint)
                new_th_breakpoints[index] = breakpoint

        for index in active_hx[stream_hx]:
            breakpoint = instance.thx[index].value
            if breakpoint not in self.thx_breakpoints[index]:
                bisect.insort(self.thx_breakpoints[index], breakpoint)
                new_thx_breakpoints[index] = breakpoint

        for index in active_tc_indices:
            breakpoint = instance.tc[index].value
            if breakpoint not in self.tc_breakpoints[index]:
                bisect.insort(self.tc_breakpoints[index], breakpoint)
                new_tc_breakpoints[index] = breakpoint

        for index in active_hx[stream_hx]:
            breakpoint = instance.tcx[index].value
            if breakpoint not in self.tcx_breakpoints[index]:
                bisect.insort(self.tcx_breakpoints[index], breakpoint)
                new_tcx_breakpoints[index] = breakpoint

        if not weaken:
            for index in inactive_hx[stream_hx]:
                if instance.bh_out[index].value > 0.000001:
                    breakpoint = instance.thx[index].value
                    if breakpoint not in self.thx_breakpoints[index]:
                        bisect.insort(self.thx_breakpoints[index], breakpoint)
                        new_thx_breakpoints[index] = breakpoint
                if instance.bc_out[index].value > 0.000001:
                    breakpoint = instance.tcx[index].value
                    if breakpoint not in self.tcx_breakpoints[index]:
                        bisect.insort(self.tcx_breakpoints[index], breakpoint)
                        new_tcx_breakpoints[index] = breakpoint

        new_balancing_breakpoints = {}
        if not len(new_th_breakpoints) == 0:
            new_balancing_breakpoints['th'] = new_th_breakpoints

        if not len(new_thx_breakpoints) == 0:
            new_balancing_breakpoints['thx'] = new_thx_breakpoints

        if not len(new_tc_breakpoints) == 0:
            new_balancing_breakpoints['tc'] = new_tc_breakpoints

        if not len(new_tcx_breakpoints) == 0:
            new_balancing_breakpoints['tcx'] = new_tcx_breakpoints

        return new_balancing_breakpoints

    def get_new_q_breakpoints(self, instance, active_hx):
        new_stream_breakpoints = {}
        new_cu_breakpoints = {}
        new_hu_breakpoints = {}

        for index in active_hx[stream_hx]:
            breakpoint = instance.q[index].value
            if breakpoint not in self.stream_q_points[index]:
                bisect.insort(self.stream_q_points[index], breakpoint)
                new_stream_breakpoints[index] = breakpoint

        for index in active_hx[cu_hx]:
            breakpoint = instance.q_cu[index].value
            if breakpoint not in self.cu_q_points[index]:
                bisect.insort(self.cu_q_points[index], breakpoint)
                new_cu_breakpoints[index] = breakpoint

        for index in active_hx[hu_hx]:
            breakpoint = instance.q_hu[index].value
            if breakpoint not in self.hu_q_points[index]:
                bisect.insort(self.hu_q_points[index], breakpoint)
                new_hu_breakpoints[index] = breakpoint

        new_q_breakpoints = {}
        if not len(new_stream_breakpoints) == 0:
            new_q_breakpoints[stream_hx] = new_stream_breakpoints

        if not len(new_cu_breakpoints) == 0:
            new_q_breakpoints[cu_hx] = new_cu_breakpoints

        if not len(new_hu_breakpoints) == 0:
            new_q_breakpoints[hu_hx] = new_hu_breakpoints

        return new_q_breakpoints

    def get_new_beta_breakpoints(self, instance, active_hx):
        new_stream_breakpoints = {}
        new_cu_breakpoints = {}
        new_hu_breakpoints = {}

        for index in active_hx[stream_hx]:
            breakpoint = instance.area[index].value
            if breakpoint not in self.stream_area_betas[index]:
                bisect.insort(self.stream_area_betas[index], breakpoint)
                new_stream_breakpoints[index] = breakpoint

        for index in active_hx[cu_hx]:
            breakpoint = instance.area_cu[index].value
            if breakpoint not in self.cu_area_betas[index]:
                bisect.insort(self.cu_area_betas[index], breakpoint)
                new_cu_breakpoints[index] = breakpoint

        for index in active_hx[hu_hx]:
            breakpoint = instance.area_hu[index].value
            if breakpoint not in self.hu_area_betas[index]:
                bisect.insort(self.hu_area_betas[index], breakpoint)
                new_hu_breakpoints[index] = breakpoint

        new_beta_breakpoints = {}
        if not len(new_stream_breakpoints) == 0:
            new_beta_breakpoints[stream_hx] = new_stream_breakpoints

        if not len(new_cu_breakpoints) == 0:
            new_beta_breakpoints[cu_hx] = new_cu_breakpoints

        if not len(new_hu_breakpoints) == 0:
            new_beta_breakpoints[hu_hx] = new_hu_breakpoints

        return new_beta_breakpoints

    def add_new_tangent_points(self, new_tangent_points):
        added_tangents = {
        }
        for index, tangent_point in new_tangent_points[stream_hx].items():
            if not tangent_point in self.stream_tangent_points[index]:
                if not stream_hx in added_tangents:
                    added_tangents[stream_hx] = {}
                self.stream_tangent_points[index].append(tangent_point)
                added_tangents[stream_hx][index] = [tangent_point]
                if not tangent_point[0] == tangent_point[1]:
                    self.stream_tangent_points[index].append((tangent_point[1], tangent_point[0]))
                    added_tangents[stream_hx][index].append((tangent_point[1], tangent_point[0]))

        for index, tangent_point in new_tangent_points[cu_hx].items():
            if not tangent_point in self.cu_tangent_points[index]:
                if not cu_hx in added_tangents:
                    added_tangents[cu_hx] = {}
                self.cu_tangent_points[index].append(tangent_point)
                added_tangents[cu_hx][index] = [tangent_point]

        for index, tangent_point in new_tangent_points[hu_hx].items():
            if not tangent_point in self.hu_tangent_points[index]:
                if not hu_hx in added_tangents:
                    added_tangents[hu_hx] = {}
                self.hu_tangent_points[index].append(tangent_point)
                added_tangents[hu_hx][index] = [tangent_point]

        return added_tangents

    def get_all_points(self):
        return {\
            stream_hx: {\
                tangent_points: self.stream_tangent_points,\
                q_points: self.stream_q_points,\
                area_beta_points: self.stream_area_betas,\
                th_points: self.th_breakpoints,\
                thx_points: self.thx_breakpoints,\
                tc_points: self.tc_breakpoints,\
                tcx_points: self.tcx_breakpoints,\
            },\
            cu_hx: {\
                tangent_points: self.cu_tangent_points,\
                q_points: self.cu_q_points,\
                area_beta_points: self.cu_area_betas,\
            },\
            hu_hx: {\
                tangent_points: self.hu_tangent_points,\
                q_points: self.hu_q_points,\
                area_beta_points: self.hu_area_betas,\
            },\
        }

    def calculate_reclmtd_error(self, x, y, reclmtd_estimate):
        reclmtd_correct = lmtd_inv(x, y)
        error = reclmtd_correct - reclmtd_estimate
        rel_error = error/reclmtd_correct
        abs_error = abs(error)
        return {\
            absolute_error: abs_error,\
            relative_error: rel_error,\
        }

    def calculate_stream_reclmtd_error(self, instance, i, j, k):
        dt_hot  = instance.dt[(i,j,k)].value
        dt_cold = instance.dt[(i,j,k+1)].value
        reclmtd_estimate = instance.reclmtd[(i,j,k)].value
        return self.calculate_reclmtd_error(dt_hot, dt_cold, reclmtd_estimate)

    def calculate_cu_reclmtd_error(self, instance, i):
        dt  = instance.dt_cu[i].value
        dt2 = instance.Th_out[i] - instance.T_cu_in
        reclmtd_estimate = instance.reclmtd_cu[i].value
        return self.calculate_reclmtd_error(dt, dt2, reclmtd_estimate)

    def calculate_hu_reclmtd_error(self, instance, j):
        dt  = instance.dt_hu[j].value
        dt2 = instance.T_hu_in - instance.Tc_out[j]
        reclmtd_estimate = instance.reclmtd_hu[j].value
        return self.calculate_reclmtd_error(dt, dt2, reclmtd_estimate)

    def calculate_area_beta_errors(self, area, beta, area_beta_estimate):
        area_beta_correct = pow(area, beta)
        error = area_beta_correct - area_beta_estimate
        rel_error = error/area_beta_correct
        abs_error = abs(error)
        return {\
            absolute_error: abs_error,\
            relative_error: rel_error,\
        }

    def calculate_stream_area_beta_error(self, instance, i, j, k):
        area = instance.area[i,j,k].value
        beta = instance.Beta
        area_beta_estimate = instance.area_beta[i,j,k].value
        return self.calculate_area_beta_errors(area, beta, area_beta_estimate)

    def calculate_cu_area_beta_error(self, instance, i):
        area = instance.area_cu[i].value
        beta = instance.Beta
        area_beta_estimate = instance.area_cu_beta[i].value
        return self.calculate_area_beta_errors(area, beta, area_beta_estimate)

    def calculate_hu_area_beta_error(self, instance, j):
        area = instance.area_hu[j].value
        beta = instance.Beta
        area_beta_estimate = instance.area_hu_beta[j].value
        return self.calculate_area_beta_errors(area, beta, area_beta_estimate)

    def calculate_area_errors(self, q, reclmtd, u, area_estimate):
        area_correct = u*q*reclmtd
        error = area_correct - area_estimate
        rel_error = error/area_correct
        abs_error = abs(error)
        return {\
            absolute_error: abs_error,\
            relative_error: rel_error,\
        }

    def calculate_stream_area_error(self, instance, i, j, k):
        q = instance.q[i,j,k].value
        reclmtd = instance.reclmtd[i,j,k].value
        u = instance.U[i,j]
        area_estimate = instance.area[i,j,k].value
        return self.calculate_area_errors(q, reclmtd, u, area_estimate)

    def calculate_cu_area_error(self, instance, i):
        q = instance.q_cu[i].value
        reclmtd = instance.reclmtd_cu[i].value
        u = instance.U_cu[i]
        area_estimate = instance.area_cu[i].value
        return self.calculate_area_errors(q, reclmtd, u, area_estimate)

    def calculate_hu_area_error(self, instance, j):
        q = instance.q_hu[j].value
        reclmtd = instance.reclmtd_hu[j].value
        u = instance.U_hu[j]
        area_estimate = instance.area_hu[j].value
        return self.calculate_area_errors(q, reclmtd, u, area_estimate)

    def calculate_bilinear_errors(self, f, t, bilinear_estimate):
        bilinear_correct = f*t
        if bilinear_correct < 0.000001:
            return {\
                absolute_error: 0,\
                relative_error: 0,\
            }
        error = bilinear_estimate - bilinear_correct
        rel_error = error/bilinear_correct if not t == 0 else 0
        abs_error = abs(error)
        return {\
            absolute_error: abs_error,\
            relative_error: rel_error,\
        }

    def calculate_bhin(self, instance, i, j, k):
        f = instance.fh[i,j,k].value
        t = instance.th[i,k].value
        bhin = instance.bh_in[i,j,k].value
        return self.calculate_bilinear_errors(f, t, bhin)

    def calculate_bhout(self, instance, i, j, k):
        f = instance.fh[i,j,k].value
        t = instance.thx[i,j,k].value
        bhout = instance.bh_out[i,j,k].value
        return self.calculate_bilinear_errors(f, t, bhout)

    def calculate_bcin(self, instance, i, j, k):
        f = instance.fc[i,j,k].value
        t = instance.tc[j,k+1].value
        bcin = instance.bc_in[i,j,k].value
        return self.calculate_bilinear_errors(f, t, bcin)

    def calculate_bcout(self, instance, i, j, k):
        f = instance.fc[i,j,k].value
        t = instance.tcx[i,j,k].value
        bcout = instance.bc_out[i,j,k].value
        return self.calculate_bilinear_errors(f, t, bcout)

    def summarise_errors(self, instance, active_hx, inactive_hx, weaken):
        errors = {}

        errors[stream_hx] = {}
        errors[cu_hx]     = {}
        errors[hu_hx]     = {}

        errors[stream_hx][reclmtd_error] = {}
        errors[cu_hx][reclmtd_error]     = {}
        errors[hu_hx][reclmtd_error]     = {}

        errors[stream_hx][area_error] = {}
        errors[cu_hx][area_error]     = {}
        errors[hu_hx][area_error]     = {}

        errors[stream_hx][area_beta_error] = {}
        errors[cu_hx][area_beta_error]     = {}
        errors[hu_hx][area_beta_error]     = {}

        errors[stream_hx][bhin_error]  = {}
        errors[stream_hx][bhout_error] = {}
        errors[stream_hx][bcin_error]  = {}
        errors[stream_hx][bcout_error] = {}

        for (i,j,k) in active_hx[stream_hx]:
            errors[stream_hx][reclmtd_error][i,j,k] = self.calculate_stream_reclmtd_error(instance, i, j, k)
            errors[stream_hx][area_error][i,j,k] = self.calculate_stream_area_error(instance, i, j, k)
            errors[stream_hx][area_beta_error][i,j,k] = self.calculate_stream_area_beta_error(instance, i, j, k)
            errors[stream_hx][bhin_error][i,j,k] = self.calculate_bhin(instance, i, j, k)
            errors[stream_hx][bhout_error][i,j,k] = self.calculate_bhout(instance, i, j, k)
            errors[stream_hx][bcin_error][i,j,k] = self.calculate_bcin(instance, i, j, k)
            errors[stream_hx][bcout_error][i,j,k] = self.calculate_bcout(instance, i, j, k)

        if not weaken:
            for (i,j,k) in inactive_hx[stream_hx]:
                errors[stream_hx][bhout_error][i,j,k] = self.calculate_bhout(instance, i, j, k)
                errors[stream_hx][bcout_error][i,j,k] = self.calculate_bcout(instance, i, j, k)

        for i in active_hx[cu_hx]:
            errors[cu_hx][reclmtd_error][i] = self.calculate_cu_reclmtd_error(instance, i)
            errors[cu_hx][area_error][i] = self.calculate_cu_area_error(instance, i)
            errors[cu_hx][area_beta_error][i] = self.calculate_cu_area_beta_error(instance, i)

        for j in active_hx[hu_hx]:
            errors[hu_hx][reclmtd_error][j] = self.calculate_hu_reclmtd_error(instance, j)
            errors[hu_hx][area_error][j] = self.calculate_hu_area_error(instance, j)
            errors[hu_hx][area_beta_error][j] = self.calculate_hu_area_beta_error(instance, j)

        return errors

    def get_max_errors(self, errors, active_hx, inactive_hx, weaken):
        max_errors = {
            balancing_ref: {
                absolute_error: -1, \
                relative_error: -1, \
            },
            reclmtd_ref: {
                absolute_error: -1, \
                relative_error: -1, \
            },
            area_ref: {
                absolute_error: -1, \
                relative_error: -1, \
            },
            beta_ref: {
                absolute_error: -1, \
                relative_error: -1, \
            },
        }

        for (i,j,k) in active_hx[stream_hx]:
            max_bilinear_error_abs = max( \
                errors[stream_hx][bhin_error][i,j,k][absolute_error], \
                errors[stream_hx][bhout_error][i,j,k][absolute_error], \
                errors[stream_hx][bcin_error][i,j,k][absolute_error], \
                errors[stream_hx][bcout_error][i,j,k][absolute_error], \
            )

            max_bilinear_error_rel = max( \
                    abs(errors[stream_hx][bhin_error][i,j,k][relative_error]), \
                    abs(errors[stream_hx][bhout_error][i,j,k][relative_error]), \
                    abs(errors[stream_hx][bcin_error][i,j,k][relative_error]), \
                    abs(errors[stream_hx][bcout_error][i,j,k][relative_error]), \
                )

            if max_errors[balancing_ref][absolute_error] < max_bilinear_error_abs:
                max_errors[balancing_ref][absolute_error] = max_bilinear_error_abs

            if max_errors[balancing_ref][relative_error] < max_bilinear_error_rel:
                max_errors[balancing_ref][relative_error] = max_bilinear_error_rel

        if not weaken:
            for (i,j,k) in inactive_hx[stream_hx]:
                max_bilinear_error_abs = max( \
                    errors[stream_hx][bhout_error][i,j,k][absolute_error], \
                    errors[stream_hx][bcout_error][i,j,k][absolute_error], \
                )

                max_bilinear_error_rel = max( \
                        abs(errors[stream_hx][bhout_error][i,j,k][relative_error]), \
                        abs(errors[stream_hx][bcout_error][i,j,k][relative_error]), \
                    )

                if max_errors[balancing_ref][absolute_error] < max_bilinear_error_abs:
                    max_errors[balancing_ref][absolute_error] = max_bilinear_error_abs

                if max_errors[balancing_ref][relative_error] < max_bilinear_error_rel:
                    max_errors[balancing_ref][relative_error] = max_bilinear_error_rel

        for check_set in [stream_hx, cu_hx, hu_hx]:
            for index in active_hx[check_set]:
                if max_errors[reclmtd_ref][absolute_error] < errors[check_set][reclmtd_error][index][absolute_error]:
                    max_errors[reclmtd_ref][absolute_error] = errors[check_set][reclmtd_error][index][absolute_error]

                if max_errors[reclmtd_ref][relative_error] < errors[check_set][reclmtd_error][index][relative_error]:
                    max_errors[reclmtd_ref][relative_error] = errors[check_set][reclmtd_error][index][relative_error]

                if max_errors[area_ref][absolute_error] < errors[check_set][area_error][index][absolute_error]:
                    max_errors[area_ref][absolute_error] = errors[check_set][area_error][index][absolute_error]

                if max_errors[area_ref][relative_error] < errors[check_set][area_error][index][relative_error]:
                    max_errors[area_ref][relative_error] = errors[check_set][area_error][index][relative_error]

                if max_errors[beta_ref][absolute_error] < errors[check_set][area_beta_error][index][absolute_error]:
                    max_errors[beta_ref][absolute_error] = errors[check_set][area_beta_error][index][absolute_error]

                if max_errors[beta_ref][relative_error] < errors[check_set][area_beta_error][index][relative_error]:
                    max_errors[beta_ref][relative_error] = errors[check_set][area_beta_error][index][relative_error]

        return max_errors

# The rest of the file (stateless functions) remains unchanged
