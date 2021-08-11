# -*- coding: utf-8 -*-
"""
@author: SYJ
"""
import gurobipy as gp
from gurobipy import GRB

def addBendersCuts():
    '''
        
    '''
    if SP_Dual.status == GRB.Status.UNBOUNDED:       # feasible cut
        ray = SP_Dual.UnbdRay
        MP.addConstr(8*ray[0] + 3*ray[1] + 5*ray[2] + \
                     8*ray[3]*y[0] + 3*ray[4]*y[1] + 5*ray[5]*y[2] + \
                     5*ray[6]*y[3] + 3*ray[7]*y[4] <= 0)
    elif SP_Dual.status == GRB.Status.OPTIMAL:       # optimal cut
        MP.addConstr(8*Vdual1[0].x + 3*Vdual1[1].x + 5*Vdual1[2].x + \
                     8*Vdual2[0].x*y[0] + 3*Vdual2[1].x*y[1] + 5*Vdual2[2].x*y[2] + \
                     5*Vdual2[3].x*y[3] + 3*Vdual2[4].x*y[4] <= z)
        SP_Dual_obj.append(SP_Dual.ObjVal)              
        # x.append(x1.pi)                              
        # x.append(x2.pi)
        # x.append(x3.pi)
        # x.append(x4.pi)
        # x.append(x5.pi)
    else:                                            # sp error
        print (SP_Dual.status)
        

try:
    MP = gp.Model('MP')            # Benders Master Problem
    SP_Dual = gp.Model('SP_Dual')       # dual of Benders SubProblem
    
    # enable status consult
    SP_Dual.Params.InfUnbdInfo = 1
    
    # add Variables
    y= MP.addVars(5, obj=7, vtype=GRB.BINARY, name='y')
    z= MP.addVar(obj=1, vtype=GRB.CONTINUOUS, name='z')
    
    Vdual1 = SP_Dual.addVars(3, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='Vdual1')
    Vdual2 = SP_Dual.addVars(5, lb=-GRB.INFINITY, ub=0, vtype=GRB.CONTINUOUS, name='Vdual2')
    
    # sp constraints
    x1 = SP_Dual.addConstr(Vdual1[0] + Vdual2[0] <= 1)
    x2 = SP_Dual.addConstr(Vdual1[1] + Vdual2[1] <= 1)
    x3 = SP_Dual.addConstr(Vdual1[2] + Vdual2[2] <= 1)
    x4 = SP_Dual.addConstr(Vdual1[0] + Vdual1[2] + Vdual2[3] <= 1)
    x5 = SP_Dual.addConstr(Vdual1[0] + Vdual1[1] + Vdual2[4] <= 1)
    
    # initial
    iteration = 0
    SP_Dual_obj = [9999]
    x = []
    
    # initial solution
    MP.optimize()
    
    # main loop
    while SP_Dual_obj[-1] > z.x:

        if iteration == 0: 
             SP_Dual.setObjective(8*Vdual1[0] + 3*Vdual1[1] + 5*Vdual1[2] + \
                                  8*Vdual2[0]*y[0].x + 3*Vdual2[1]*y[1].x + 5*Vdual2[2]*y[2].x + \
                                  5*Vdual2[3]*y[3].x + 3*Vdual2[4]*y[4].x, GRB.MAXIMIZE)
             SP_Dual.optimize()
             addBendersCuts()
             iteration = 1
        else:
            # modify the coefficients
             Vdual2[0].obj = 8*y[0].x
             Vdual2[1].obj = 3*y[1].x
             Vdual2[2].obj = 5*y[2].x
             Vdual2[3].obj = 5*y[3].x
             Vdual2[4].obj = 3*y[4].x
             SP_Dual.optimize()
             addBendersCuts()
             iteration = iteration + 1
        
        MP.optimize()


     
except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')        
