# -*- coding: utf-8 -*-
"""
@author: SYJ
"""
import gurobipy as gp
import prettytable as pt
from gurobipy import GRB

# sets
Source = ['i1','i2','i3','i4']
Destination = ['j1','j2','j3']

# cost
choose, fixed_cost, variable_cost = gp.multidict({
    ('i1','j1'):    [10, 2],
    ('i1','j2'):    [30, 3],
    ('i1','j3'):    [20, 4],
    ('i2','j1'):    [10, 3],
    ('i2','j2'):    [30, 2],
    ('i2','j3'):    [20, 1],
    ('i3','j1'):    [10, 1],
    ('i3','j2'):    [30, 4],
    ('i3','j3'):    [20, 3],
    ('i4','j1'):    [10, 4],
    ('i4','j2'):    [30, 5],
    ('i4','j3'):    [20, 2]})

# supply
supply={
        'i1':   10,
        'i2':   30,
        'i3':   40,
        'i4':   20}

# demand
demand={
        'j1':   20,
        'j2':   50,
        'j3':   30}





# #model
# mall = gp.Model('FCTP_all') #the MIP model of the whole problem
msp_dual = gp.Model('FCTP_SP_Dual')
mmp = gp.Model('FCTP_MP')
# #variables
# flowx = mall.addVars(Source, Destination, obj=variable_cost, lb=0, vtype=GRB.CONTINUOUS, \
#                      name = 'flowx')
# flowy = mall.addVars(Source, Destination, obj=fixed_cost, vtype=GRB.BINARY, \
#                      name = 'flowy')
    

# #constrains
# mall.addConstrs((flowx.sum('*',j) == demand[j] for j in Destination), "DemandBalance")
# mall.addConstrs((flowx.sum(i,'*') == supply[i] for i in Source), "SupplyBanlance")
# mall.addConstrs((flowx[i, j] <= min(supply[i], demand[j])*flowy[i, j] for i, j in choose), "XYCons")



# #optimize
# mall.optimize()


# #output
# if mall.status == GRB.OPTIMAL:
#     solution = mall.getAttr('x',flowx)
#     costvalue = mall.ObjVal
#     print('the minimum cost is %g' % costvalue)
#     for i, j in choose:
#         if solution[i,j] > 0:
#             print('%s -> %s:%g' % (i, j, solution[i, j]))


"""
Use Benders Decomposition
"""
# the function to add Benders cut
def addBendersCuts():
    '''
    Add optimal cuts and feasible cuts to main problem.
    '''
    if msp_dual.status == GRB.Status.UNBOUNDED:       # subproblem unbounded
        # global ray
        ray = msp_dual.UnbdRay
        # mmp.addConstr(-sum(supply[i]*ray[t] for i in Source for t in range(0,4)) + \
        #                 sum(demand[j]*ray[tt] for j in Destination for tt in range(4,7)) - \
        #                 sum(min(supply[i], demand[j])*ray[ttt]*y[i, j] for i, j in choose for ttt in range(7,19)) <= 0)
        mmp.addConstr(-supply['i1']*ray[0] - supply['i2']*ray[1] - supply['i3']*ray[2] - \
                      supply['i4']*ray[3] + demand['j1']*ray[4] + demand['j2']*ray[5] + \
                      demand['j3']*ray[6] - min(supply['i1'], demand['j1'])*ray[7]*y['i1','j1'] - \
                      min(supply['i1'], demand['j2'])*ray[8]*y['i1','j2'] - \
                      min(supply['i1'], demand['j3'])*ray[9]*y['i1','j3'] - \
                      min(supply['i2'], demand['j1'])*ray[10]*y['i2','j1'] - \
                      min(supply['i2'], demand['j2'])*ray[11]*y['i2','j2'] - \
                      min(supply['i2'], demand['j3'])*ray[12]*y['i2','j3'] - \
                      min(supply['i3'], demand['j1'])*ray[13]*y['i3','j1'] - \
                      min(supply['i3'], demand['j2'])*ray[14]*y['i3','j2'] - \
                      min(supply['i3'], demand['j3'])*ray[15]*y['i3','j3'] - \
                      min(supply['i4'], demand['j1'])*ray[16]*y['i4','j1'] - \
                      min(supply['i4'], demand['j2'])*ray[17]*y['i4','j2'] - \
                      min(supply['i4'], demand['j3'])*ray[18]*y['i4','j3'] <= 0)
        ub.append(ub[-1])
    elif msp_dual.status == GRB.Status.OPTIMAL:       # subproblem optimal
        mmp.addConstr(-sum(supply[i]*u[i].x for i in Source) + \
                       sum(demand[j]*v[j].x for j in Destination) - \
                       sum(min(supply[i], demand[j])*w[i, j].x*y[i, j] for i, j in choose) + \
                       sum(fixed_cost[i,j]*y[i,j] for i,j in choose) <= z)
        # mmp.addConstr(-supply['i1']*u['i1'].x - supply['i2']*u['i2'].x - supply['i3']*u['i3'].x - \
        #              supply['i4']*u['i4'].x + demand['j1']*v['j1'].x + demand['j2']*v['j2'].x + \
        #              demand['j3']*v['j3'].x - (-10 + min(supply['i1'], demand['j1'])*w['i1','j1'].x)*y['i1','j1'] - \
        #              (-30 + min(supply['i1'], demand['j2'])*w['i1','j2'].x)*y['i1','j2'] - \
        #              (-20 + min(supply['i1'], demand['j3'])*w['i1','j3'].x)*y['i1','j3'] - \
        #              (-10 + min(supply['i2'], demand['j1'])*w['i2','j1'].x)*y['i2','j1'] - \
        #              (-30 + min(supply['i2'], demand['j2'])*w['i2','j2'].x)*y['i2','j2'] - \
        #              (-20 + min(supply['i2'], demand['j3'])*w['i2','j3'].x)*y['i2','j3'] - \
        #              (-10 + min(supply['i3'], demand['j1'])*w['i3','j1'].x)*y['i3','j1'] - \
        #              (-30 + min(supply['i3'], demand['j2'])*w['i3','j2'].x)*y['i3','j2'] - \
        #              (-20 + min(supply['i3'], demand['j3'])*w['i3','j3'].x)*y['i3','j3'] - \
        #              (-10 + min(supply['i4'], demand['j1'])*w['i4','j1'].x)*y['i4','j1'] - \
        #              (-30 + min(supply['i4'], demand['j2'])*w['i4','j2'].x)*y['i4','j2'] - \
        #              (-20 + min(supply['i4'], demand['j3'])*w['i4','j3'].x)*y['i4','j3'] <= z)
        SP_Dual_obj = msp_dual.ObjVal + sum(fixed_cost[i,j]*y[i,j].x for i,j in choose) 
        ub.append(min(SP_Dual_obj, ub[-1]))
    else:                                            #其他状态
        print (msp_dual.status)
        
#variables
y = mmp.addVars(Source, Destination, vtype=GRB.BINARY, name = 'y')      
z = mmp.addVar(obj=1, vtype=GRB.CONTINUOUS, name = 'z')  
u = msp_dual.addVars(Source, lb=0, vtype=GRB.CONTINUOUS, name='u')     
v = msp_dual.addVars(Destination, lb=0, vtype=GRB.CONTINUOUS, name='v') 
w = msp_dual.addVars(Source, Destination, lb=0, vtype=GRB.CONTINUOUS, name='w') 

# constrains
msp_dual.addConstrs((- u[i] + v[j] - w[i, j] <= variable_cost[i, j] for i, j in choose), name='cons')
# x11 = msp_dual.addConstr(- u['i1'] + v['j1'] - w['i1','j1'] <= variable_cost['i1','j1'])
# x12 = msp_dual.addConstr(- u['i1'] + v['j2'] - w['i1','j2'] <= variable_cost['i1','j2'])
# x13 = msp_dual.addConstr(- u['i1'] + v['j3'] - w['i1','j3'] <= variable_cost['i1','j3'])
# x21 = msp_dual.addConstr(- u['i2'] + v['j1'] - w['i2','j1'] <= variable_cost['i2','j1'])
# x22 = msp_dual.addConstr(- u['i2'] + v['j2'] - w['i2','j2'] <= variable_cost['i2','j2'])
# x23 = msp_dual.addConstr(- u['i2'] + v['j3'] - w['i2','j3'] <= variable_cost['i2','j3'])
# x31 = msp_dual.addConstr(- u['i3'] + v['j1'] - w['i3','j1'] <= variable_cost['i3','j1'])
# x32 = msp_dual.addConstr(- u['i3'] + v['j2'] - w['i3','j2'] <= variable_cost['i3','j2'])
# x33 = msp_dual.addConstr(- u['i3'] + v['j3'] - w['i3','j3'] <= variable_cost['i3','j3'])
# x41 = msp_dual.addConstr(- u['i4'] + v['j1'] - w['i4','j1'] <= variable_cost['i4','j1'])
# x42 = msp_dual.addConstr(- u['i4'] + v['j2'] - w['i4','j2'] <= variable_cost['i4','j2'])
# x43 = msp_dual.addConstr(- u['i4'] + v['j3'] - w['i4','j3'] <= variable_cost['i4','j3'])

# change parameter: InfUnbdInfo
msp_dual.Params.InfUnbdInfo = 1

iteration = 0
SP_Dual_obj = 9999
x = []
ub=[9999]
lb=[0]
# initial Y
mmp.optimize()    
# main loop
while ub[-1] > lb[-1]:   
    if iteration == 0:
         msp_dual.setObjective(-sum(supply[i]*u[i] for i in Source) + \
                               sum(demand[j]*v[j] for j in Destination) - \
                               sum(min(supply[i], demand[j])*w[i, j]*y[i, j].x for i, j in choose), GRB.MAXIMIZE)
         # msp_dual.setObjective(-supply['i1']*u['i1'] - supply['i2']*u['i2'] - supply['i3']*u['i3'] - \
         #             supply['i4']*u['i4'] + demand['j1']*v['j1'] + demand['j2']*v['j2'] + \
         #             demand['j3']*v['j3'] - min(supply['i1'], demand['j1'])*w['i1','j1']*y['i1','j1'].x - \
         #             min(supply['i1'], demand['j2'])*w['i1','j2']*y['i1','j2'].x - \
         #             min(supply['i1'], demand['j3'])*w['i1','j3']*y['i1','j3'].x - \
         #             min(supply['i2'], demand['j1'])*w['i2','j1']*y['i2','j1'].x - \
         #             min(supply['i2'], demand['j2'])*w['i2','j2']*y['i2','j2'].x - \
         #             min(supply['i2'], demand['j3'])*w['i2','j3']*y['i2','j3'].x - \
         #             min(supply['i3'], demand['j1'])*w['i3','j1']*y['i3','j1'].x - \
         #             min(supply['i3'], demand['j2'])*w['i3','j2']*y['i3','j2'].x - \
         #             min(supply['i3'], demand['j3'])*w['i3','j3']*y['i3','j3'].x - \
         #             min(supply['i4'], demand['j1'])*w['i4','j1']*y['i4','j1'].x - \
         #             min(supply['i4'], demand['j2'])*w['i4','j2']*y['i4','j2'].x - \
         #             min(supply['i4'], demand['j3'])*w['i4','j3']*y['i4','j3'].x, GRB.MAXIMIZE)

    else:
        for i,j in choose:
            w[i,j].obj = - min(supply[i], demand[j])*y[i, j].x
        # w['i1','j1'].obj = - min(supply['i1'], demand['j1'])*y['i1','j1'].x
        # w['i1','j2'].obj = - min(supply['i1'], demand['j2'])*y['i1','j2'].x
        # w['i1','j3'].obj = - min(supply['i1'], demand['j3'])*y['i1','j3'].x
        # w['i2','j1'].obj = - min(supply['i2'], demand['j1'])*y['i2','j1'].x
        # w['i2','j2'].obj = - min(supply['i2'], demand['j2'])*y['i2','j2'].x
        # w['i2','j3'].obj = - min(supply['i2'], demand['j3'])*y['i2','j3'].x
        # w['i3','j1'].obj = - min(supply['i3'], demand['j1'])*y['i3','j1'].x
        # w['i3','j2'].obj = - min(supply['i3'], demand['j2'])*y['i3','j2'].x
        # w['i3','j3'].obj = - min(supply['i3'], demand['j3'])*y['i3','j3'].x
        # w['i4','j1'].obj = - min(supply['i4'], demand['j1'])*y['i4','j1'].x
        # w['i4','j2'].obj = - min(supply['i4'], demand['j2'])*y['i4','j2'].x
        # w['i4','j3'].obj = - min(supply['i4'], demand['j3'])*y['i4','j3'].x
        
    msp_dual.optimize()
    addBendersCuts()
    iteration = iteration + 1 
    mmp.optimize()
    lb.append(mmp.ObjVal)

# output
print ('use %g times to converge' % iteration)
print('the best value is %g' % lb[-1])
table=pt.PrettyTable()
table.add_column('iteration',[i for i in range(len(lb))])
table.add_column('lower_bound',lb)
table.add_column('upper_bound',ub)
print(table)
































