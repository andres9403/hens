from pyomo.environ import *
from pyomo.dataportal import DataPortal
from lib.model_concrete_declarations.concrete_model_builder import build_concrete_model

def parse_dat_to_dict(dat_file):
    dp = DataPortal()
    dp.load(filename=dat_file)
    data_dict = {name: dp.data(name) for name in dp.data()}
    return data_dict

data = parse_dat_to_dict("/home/andresfel9403/hens/datafiles/model3.dat")
print(data)
model = build_concrete_model(data)
print(model.Fh._data)
