from pyomo.environ import *
from pyomo.dataportal import DataPortal
from lib_concrete.model_concrete_declarations.concrete_model_builder import build_concrete_model
from pyomo.opt import SolverFactory
from lib_concrete.iterations_helper import IterationState



def parse_dat_to_dict(dat_file):
    dp = DataPortal()
    dp.load(filename=dat_file)
    data_dict = {name: dp.data(name) for name in dp.data()}
    return data_dict

data = parse_dat_to_dict("/home/andresfel9403/hens/datafiles/model3.dat")
print(data)
model = build_concrete_model(data)

solver = 'gurobi'
opt = SolverFactory(solver)
opt.options[ 'MIPFocus' ] = 1
num_vars = len(list(model.component_data_objects(Var, active=True)))
num_cons = len(list(model.component_data_objects(Constraint, active=True)))
print(num_vars, 'variables')
print(num_cons, 'constraints')

state = IterationState()

_ = state.safe_initial_breakpoints(model)

model = state.add_tangent_points(model)


model = state.add_T_breakpoints(model)
#model = state.add_area_beta_breakpoints(model)

num_vars = len(list(model.component_data_objects(Var, active=True)))
num_cons = len(list(model.component_data_objects(Constraint, active=True)))
print(num_vars, 'variables')
print(num_cons, 'constraints')

results = opt.solve(model, tee=True)

