# -*- coding: utf-8 -*-
"""
@author: SYJ
"""

import gurobipy as gp
from gurobipy import GRB
# Parameters
TypesDemand = [3, 7, 9, 16]           		# demand length
QuantityDemand = [25, 30, 14, 8]      		# demand numbers
LengthUsable = 20                    		# lenth of the pipe

try:
    MainProbRelax = gp.Model()                 # relaxed main problem
    SubProb = gp.Model()                       # subproblem

    # mainproblem
    # min total numbers of pipes
    Zp = MainProbRelax.addVars(len(TypesDemand), obj=1.0, vtype=GRB.CONTINUOUS, name = 'z')
    # add constraints
    # initial pattern: 3*6,7*2,9*2,16*1
    ColumnIndex = MainProbRelax.addConstrs(gp.quicksum(Zp[p] * (LengthUsable//TypesDemand[i]) \
    for p in range(len(TypesDemand)) if p==i) >= QuantityDemand[i] for i in range(len(TypesDemand)))  
    MainProbRelax.optimize()                # solve the main problem


    # subproblem
    # dual cost
    Dualsolution = MainProbRelax.getAttr(GRB.Attr.Pi, MainProbRelax.getConstrs())
    # objective
    Ci = SubProb.addVars(len(TypesDemand), obj=Dualsolution, vtype=GRB.INTEGER, name = 'c')
    # constraints
    SubProb.addConstr(gp.quicksum(Ci[i] * TypesDemand[i] for i in range(len(TypesDemand))) <= LengthUsable)
    SubProb.setAttr(GRB.Attr.ModelSense, -1) 	    # maximize           
    SubProb.optimize()                       		# solve the sub problem
    
    # main loop
    while SubProb.objval - 1 > 0:
           # get new pattern
           columnCoeff = SubProb.getAttr("X", SubProb.getVars())
           column = gp.Column(columnCoeff, MainProbRelax.getConstrs())
           # add column
           MainProbRelax.addVar(obj=1.0, vtype=GRB.CONTINUOUS, name="CG", column=column)
           MainProbRelax.optimize() 		# 求解
           # modify the objective function of the sub problem
           for i in range(len(TypesDemand)):
                Ci[i].obj = ColumnIndex[i].pi
           SubProb.optimize()
        
    # solve the interger problem
    for v in MainProbRelax.getVars():
         v.setAttr("VType", GRB.INTEGER)
    MainProbRelax.optimize()
    for v in MainProbRelax.getVars():
         if v.X != 0.0:
              print('%s %g' % (v.VarName, v.X))

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')     
