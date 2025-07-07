from pyomo.environ import Param, Set, RangeSet, PositiveIntegers, value

def declare_concrete_parameters(model, data):
    model.Alpha = Param(initialize=data['Alpha'], mutable=True)
    model.Beta = Param(initialize=data['Beta'], mutable=True)
    model.Cost_hx = Param(initialize=data['Cost_hx'], mutable=True)
    model.Cost_cu = Param(initialize=data['Cost_cu'], mutable=True)
    model.Cost_hu = Param(initialize=data['Cost_hu'], mutable=True)
    model.Delta_t_min = Param(initialize=data['Delta_t_min'], mutable=True)
    model.Number_stages = Param(within=PositiveIntegers, initialize=data['Number_stages'])
    model.Number_hot_stream = Param(within=PositiveIntegers, initialize=data['Number_hot_stream'])
    model.Number_cold_stream = Param(within=PositiveIntegers, initialize=data['Number_cold_stream'])
    model.First_stage = Param(within=PositiveIntegers, default=1)
    model.Last_stage = Param(within=PositiveIntegers, initialize=data['Number_stages']+1)
    

    ## Sets that represents the hot and cold streams, stages and temperature locations
    model.HP = RangeSet(1, model.Number_hot_stream, doc="set of hot process streams i" )
    model.CP = RangeSet(1, model.Number_cold_stream, doc="set of cold process streams j" )
    model.ST = RangeSet(model.First_stage, model.Number_stages, doc="set of stages in the superstructure" )
    model.K = RangeSet(model.First_stage, model.Last_stage, doc="set of temperature locations")

    model.First_Stage_Set = RangeSet(model.First_stage, model.First_stage)
    model.K_Take_First_Stage = model.K - model.First_Stage_Set

    ## Parameters per sets
    model.Fh = Param(model.HP, initialize = data['Fh'], doc="flow rate of hot process streams i")
    model.Fc = Param(model.CP, initialize = data['Fc'], doc="flow rate of cold process streams j")
    model.Hh = Param(model.HP, initialize = data['Hh'], doc="enthalpy of hot process streams i")
    model.Hc = Param(model.CP, initialize = data['Hc'], doc="enthalpy of cold process streams j")








    # model.Fh = Param(initialize=data['Fh'], mutable=True)
    # model.Fc = Param(initialize=data['Fc'], mutable=True)
    # model.Hh = Param(initialize=data['Hh'], mutable=True)
    # model.Hc = Param(initialize=data['Hc'], mutable=True)
    # model.H_cu = Param(initialize=data['H_cu'], mutable=True)
    # model.H_hu = Param(initialize=data['H_hu'], mutable=True)
    # model.Th_in = Param(initialize=data['Th_in'], mutable=True)
    # model.Tc_in = Param(initialize=data['Tc_in'], mutable=True)
    # model.Th_out = Param(initialize=data['Th_out'], mutable=True)
    # model.Tc_out = Param(initialize=data['Tc_out'], mutable=True)
    # model.T_cu_in = Param(initialize=data['T_cu_in'], mutable=True)
    # model.T_cu_out = Param(initialize=data['T_cu_out'], mutable=True)
    # model.T_hu_in = Param(initialize=data['T_hu_in'], mutable=True)
    # model.T_hu_out = Param(initialize=data['T_hu_out'], mutable=True)
    # model.U = Param(initialize=data['U'], mutable=True)
    # model.



    # model.HP = Set(initialize=data['HP'], mutable=True)
    # model.CP = Set(initialize=data['CP'], mutable=True)
    # model.ST = Set(initialize=data['ST'], mutable=True)
    # model.K = Set(initialize=data['K'], mutable=True)