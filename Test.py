#!/usr/bin/python

import sys
import argparse

try:
    from gurobipy import *
except ImportError:
    raise Exception('gurobipy not found.\nthis code requires gurobi to be installed in python')

from parse_matpower import *
from qc_lib import *
import time
import sys
import pandas as pd

version = '1.0.0'

def build_parser():
    parser = argparse.ArgumentParser(
        description='''compute-bounds is a python/gurobi based script for 
            computing tight bounds on voltage magnitudes and line phase angle 
            differences in matpower Optimal Power Flow datasets.  
            The theory behind this code can be found in 'Strengthening 
            Convex Relaxations with Bound Tightening for Power Network 
            Optimization', Carleton Coffrin, Hassan L. Hijazi, and 
            Pascal Van Hentenryck.''',

        epilog='''Please file bugs at https://github.com/ccoffrin/ac-opf-bounds''',
    )
    parser.add_argument('file', help='a matpower case file to process (.m)')
    parser.add_argument('-loa', '--linear_oa', help='use a linear outer-approximation of the QC model (more scalable)', action='store_true')
    parser.add_argument('-i', '--iterations', help='limit the number of iterations (0 computes the base relaxation without tightening)', type=int, default=sys.maxsize )
    parser.add_argument('-l', '--large', help='configures the algorithm for processing cases with over 1000 buses', action='store_true')
    parser.add_argument('-pad', help='override test case phase angle difference bounds with given value (in radians)', type=float)

    # rough output levels
    # 0 minimal
    # 1-3 tbd
    # 4 add all algorithm output
    # 5 add qc-model output
    # 6 add gurobi solve output
    parser.add_argument('-o', '--output', help='controls the output level (0-6)', type=int, default=0)
    parser.add_argument('-v', '--version', action='version', version=version)

    return parser

# args = pglib_opf_case14_ieee.m
#
# case = parse_mp_case(args.file)

case = parse_mp_case('pglib_opf_case14_ieee.m')
case = case.make_per_unit()
case = case.make_radians()

# dfBus    = pd.DataFrame(case.bus, columns= ['cols'])
# dfBranch = pd.DataFrame(case.branch)
# dfGen    = pd.DataFrame(case.gen)
# dfGenCost= pd.DataFrame(case.gencost)
#
# # dfBus['bus_i','type','Pd','Qd','Gs','Bs','area','Vm','Va','baseKV','zone','Vmax','Vmin'] = pd.DataFrame(dfBus.cols.tolist(), index = dfBus.index)
# # dfBus = dfBus.drop(['cols'], axis = 1)
# # dfBus.columns = ['bus_i','type','Pd','Qd','Gs','Bs','area','Vm','Va','baseKV','zone','Vmax','Vmin']

import time
import pandas        as pd
from   pyomo.environ import DataPortal, Set, Param, Var, Binary, NonNegativeReals, Reals, UnitInterval, Boolean

print('Input data                  ****')

StartTime = time.time()

#%% reading data from CSV
dfOption             = pd.read_csv(CaseName+'/oT_Data_Option_'                  +CaseName+'.csv', index_col=[0    ])
dfParameter          = pd.read_csv(CaseName+'/oT_Data_Parameter_'               +CaseName+'.csv', index_col=[0    ])
dfScenario           = pd.read_csv(CaseName+'/oT_Data_Scenario_'                +CaseName+'.csv', index_col=[0    ])
dfDuration           = pd.read_csv(CaseName+'/oT_Data_Duration_'                +CaseName+'.csv', index_col=[0    ])
# dfDemand             = pd.read_csv(CaseName+'/oT_Data_Demand_'                  +CaseName+'.csv', index_col=[0,1,2])
# dfUpOperatingReserve = pd.read_csv(CaseName+'/oT_Data_UpwardOperatingReserve_'  +CaseName+'.csv', index_col=[0,1,2])
# dfDwOperatingReserve = pd.read_csv(CaseName+'/oT_Data_DownwardOperatingReserve_'+CaseName+'.csv', index_col=[0,1,2])
# dfGeneration         = pd.read_csv(CaseName+'/oT_Data_Generation_'              +CaseName+'.csv', index_col=[0    ])
# dfVariableMaxPower   = pd.read_csv(CaseName+'/oT_Data_VariableGeneration_'      +CaseName+'.csv', index_col=[0,1,2])
# dfVariableMinStorage = pd.read_csv(CaseName+'/oT_Data_MinimumStorage_'          +CaseName+'.csv', index_col=[0,1,2])
# dfVariableMaxStorage = pd.read_csv(CaseName+'/oT_Data_MaximumStorage_'          +CaseName+'.csv', index_col=[0,1,2])
# dfEnergyInflows      = pd.read_csv(CaseName+'/oT_Data_EnergyInflows_'           +CaseName+'.csv', index_col=[0,1,2])
# dfNodeLocation       = pd.read_csv(CaseName+'/oT_Data_NodeLocation_'            +CaseName+'.csv', index_col=[0    ])
# dfNetwork            = pd.read_csv(CaseName+'/oT_Data_Network_'                 +CaseName+'.csv', index_col=[0,1,2])