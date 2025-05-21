from pyomo.environ import SolverFactory
from adaptive_model_mixer.lib.model_declarations.model_builder import create_model

# Step 1: Initialize the model
model = create_model()

# Step 2: Load the data file
datafile = '/home/andresfel9403/hens/datafiles/model3.dat'  # Replace 'model1.dat' with your desired data file
instance = model.create_instance(datafile)

# Step 3: Set up the solver
solver = SolverFactory('gurobi')  # Replace 'gurobi' with your solver of choice
solver.options['threads'] = 4  # Example: Set the number of threads
solver.options['Presolve'] = 2 
solver.options['Cuts'] = 0
# Step 4: Solve the model
results = solver.solve(instance, tee=True)

# Step 5: Display results
# instance.display()