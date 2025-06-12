from pyomo.environ import SolverFactory, Var, Constraint
from pyomo.core.expr.current import identify_variables
from pyomo.core.expr.visitor import polynomial_degree
from adaptive_model_mixer.lib.model_declarations.model_builder import create_model

# Step 1: Initialize the model
model = create_model()

# Step 2: Load the data file
datafile = '/home/andresfel9403/hens/datafiles/model1.dat'  # Change as needed
instance = model.create_instance(datafile)

# Step 3: Set up the solver for BARON via GAMS
solver = SolverFactory('gams')
solver.options['solver'] = 'baron'
# solver.options['threads'] = 4  # Adjust as needed

# Optional: Set BARON-specific options
# solver.options['optcr'] = 0.0  # Relative optimality gap
# solver.options['maxtime'] = 600  # Maximum time in seconds

# Print model features (number of variables, constraints, etc.)
print(f"Model has {len(list(instance.component_objects()))} components.")
print(f"Model has {len(list(instance.component_objects(Var)))} variables.")
print(f"Model has {len(list(instance.component_objects(Constraint)))} constraints.")
# Print how many nonlinear constraints the model has
nonlinear_constraints = 0
for c in instance.component_objects(Constraint, active=True):
    for idx in c:
        expr = c[idx].body
        deg = polynomial_degree(expr)
        if deg is None or deg > 1:
            nonlinear_constraints += 1
print(f"Model has {nonlinear_constraints} nonlinear constraints.")

# Step 4: Solve the model
# results = solver.solve(instance, tee=True)

# Step 5: Display results
# instance.display()