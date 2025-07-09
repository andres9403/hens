from pyomo.environ import *

m = ConcreteModel()
m.A = Set(initialize=['A', 'B'])
m.cost = Param(m.A, initialize={'A': 5, 'B': 10}, mutable=True)

# This works:
m.A.add('C')
m.cost['A'] = 7

print(m.A.value)