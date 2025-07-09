from pyomo.environ import *

model = AbstractModel()
model.A = Set()
model.cost = Param(model.A, mutable=True)

instance = model.create_instance("/home/andresfel9403/hens/adaptive_model_mixer/lib/model_concrete_declarations/data.dat")

instance.A.clear()
instance.A.add('D')

print(instance.A.value)
