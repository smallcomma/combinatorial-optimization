# -*- coding: utf-8 -*-
"""

@author: SYJ

"""

import gurobipy as gp
from gurobipy import GRB
import prettytable as pt
# parameters
M = 3
N = 3
INF = 9999
Y = {}
G = {}
x_mp = {}
z_mp = {}
iteration = 0
#numpy.ndarray.tolist(np.random.random(10))
#np.random.rand(3,3)
Capacity = [800,800,800]
Demand_f = [206,274,220]
Demand_v = [40,40,40]

Cost_supply_f = [400,414,326]
Cost_supply_v = [18,25,20]

Cost_transportation = [[22,33,24],[33,23,30],[20,25,27]]

# models
transportation_mp = gp.Model('transportation_mp')
transportation_sp = gp.Model('transportation_sp')

# variables
y = transportation_mp.addVars(1,M,vtype = GRB.BINARY,name = 'y')
x_mp[iteration] = transportation_mp.addVars(M,N,vtype = GRB.CONTINUOUS,name = 'x_mp%d' % iteration)
z_mp[iteration] = transportation_mp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'z_mp%d' % iteration)
a = transportation_mp.addVar(vtype = GRB.CONTINUOUS,name = 'a')


z = transportation_sp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'z')
x = transportation_sp.addVars(M,N,vtype = GRB.CONTINUOUS,name = 'x')
d = transportation_sp.addVars(1,N,vtype = GRB.CONTINUOUS,name = 'd')
g = transportation_sp.addVars(1,N,vtype = GRB.CONTINUOUS,name = 'g')

w1 = transportation_sp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'w1')
w2 = transportation_sp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'w2')
w3 = transportation_sp.addVars(1,N,vtype = GRB.CONTINUOUS,name = 'w3')

B11 = transportation_sp.addVars(1,M,vtype = GRB.BINARY,name = 'b11')
B12 = transportation_sp.addVars(1,M,vtype = GRB.BINARY,name = 'b12')
B13 = transportation_sp.addVars(1,N,vtype = GRB.BINARY,name = 'b13')



# B2 = transportation_sp.addVars(1,12,vtype = GRB.BINARY,name = 'b2')
B21 = transportation_sp.addVars(1,M,vtype = GRB.BINARY,name = 'b21')
B22 = transportation_sp.addVars(M,N,vtype = GRB.BINARY,name = 'b22')



    
transportation_mp.setObjective(400*y[0,0] + 414*y[0,1] + 326*y[0,2] + a,GRB.MINIMIZE)    
transportation_sp.setObjective(18*z[0,0] + 25*z[0,1] + 20*z[0,2] +\
                               22*x[0,0] + 33*x[0,1] + 24*x[0,2] +\
                               33*x[1,0] + 23*x[1,1] + 30*x[1,2] +\
                               20*x[2,0] + 25*x[2,1] + 27*x[2,2], GRB.MAXIMIZE)      

LB = [-INF]
UB = [INF]

while UB[-1]-LB[-1]>=0.1:
    if iteration == 0:
        # transportation_mp.addConstr(a >= 18*z_mp[iteration][0,0] + 25*z_mp[iteration][0,1] + 20*z_mp[iteration][0,2] +\
        #                           22*x_mp[iteration][0,0] + 33*x_mp[iteration][0,1] + 24*x_mp[iteration][0,2] +\
        #                           33*x_mp[iteration][1,0] + 23*x_mp[iteration][1,1] + 30*x_mp[iteration][1,2] +\
        #                           20*x_mp[iteration][2,0] + 25*x_mp[iteration][2,1] + 27*x_mp[iteration][2,2])
        transportation_mp.addConstr(a >= sum(Cost_supply_v[m]*z_mp[iteration][0,m]for m in range(M)) + \
                                    sum(Cost_transportation[m][n]*x_mp[iteration][m,n]for m in range(M) for n in range(N)))

        # transportation_mp.addConstr(z_mp[iteration][0,0] <= 800*y[0,0])
        # transportation_mp.addConstr(z_mp[iteration][0,1] <= 800*y[0,1])
        # transportation_mp.addConstr(z_mp[iteration][0,2] <= 800*y[0,2])
        transportation_mp.addConstrs(z_mp[iteration][0,m] <= Capacity[m]*y[0,m] for m in range(M))
        
        
        # transportation_mp.addConstr(-sum(x_mp[iteration][0,j] for j in range(N)) + z_mp[iteration][0,0] >= 0)
        # transportation_mp.addConstr(-sum(x_mp[iteration][1,j] for j in range(N)) + z_mp[iteration][0,1] >= 0)
        # transportation_mp.addConstr(-sum(x_mp[iteration][2,j] for j in range(N)) + z_mp[iteration][0,2] >= 0)
        transportation_mp.addConstrs(-sum(x_mp[iteration][m,j] for j in range(N)) + z_mp[iteration][0,m] >= 0 for m in range(M))
        
        # transportation_mp.addConstr(sum(x_mp[iteration][i,0] for i in range(M)) - 206 >= 0)
        # transportation_mp.addConstr(sum(x_mp[iteration][i,1] for i in range(M)) - 274 >= 0)
        # transportation_mp.addConstr(sum(x_mp[iteration][i,2] for i in range(M)) - 220 >= 0)
        transportation_mp.addConstrs(sum(x_mp[iteration][i,n] for i in range(M)) - Demand_f[n] >= 0 for n in range(N))
            
        transportation_mp.optimize()
    else:
        x_mp[iteration] = transportation_mp.addVars(M,N,vtype = GRB.CONTINUOUS,name = 'x_mp%d' % iteration)
        z_mp[iteration] = transportation_mp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'z_mp%d' % iteration)
        # transportation_mp.addConstr(a >= 18*z_mp[iteration][0,0] + 25*z_mp[iteration][0,1] + 20*z_mp[iteration][0,2] +\
        #                           22*x_mp[iteration][0,0] + 33*x_mp[iteration][0,1] + 24*x_mp[iteration][0,2] +\
        #                           33*x_mp[iteration][1,0] + 23*x_mp[iteration][1,1] + 30*x_mp[iteration][1,2] +\
        #                           20*x_mp[iteration][2,0] + 25*x_mp[iteration][2,1] + 27*x_mp[iteration][2,2])
        # transportation_mp.addConstr(z_mp[iteration][0,0] <= 800*y[0,0])
        # transportation_mp.addConstr(z_mp[iteration][0,1] <= 800*y[0,1])
        # transportation_mp.addConstr(z_mp[iteration][0,2] <= 800*y[0,2])
        # transportation_mp.addConstr(-sum(x_mp[iteration][0,j] for j in range(N)) + z_mp[iteration][0,0] >= 0)
        # transportation_mp.addConstr(-sum(x_mp[iteration][1,j] for j in range(N)) + z_mp[iteration][0,1] >= 0)
        # transportation_mp.addConstr(-sum(x_mp[iteration][2,j] for j in range(N)) + z_mp[iteration][0,2] >= 0)
        # transportation_mp.addConstr(sum(x_mp[iteration][i,0] for i in range(M)) - 206 - 40*G[0,0] >= 0)
        # transportation_mp.addConstr(sum(x_mp[iteration][i,1] for i in range(M)) - 274 - 40*G[0,1] >= 0)
        # transportation_mp.addConstr(sum(x_mp[iteration][i,2] for i in range(M)) - 220 - 40*G[0,2] >= 0)
        transportation_mp.addConstr(a >= sum(Cost_supply_v[m]*z_mp[iteration][0,m]for m in range(M)) + \
                                    sum(Cost_transportation[m][n]*x_mp[iteration][m,n]for m in range(M) for n in range(N)))
        transportation_mp.addConstrs(z_mp[iteration][0,m] <= Capacity[m]*y[0,m] for m in range(M))
        transportation_mp.addConstrs(-sum(x_mp[iteration][m,j] for j in range(N)) + z_mp[iteration][0,m] >= 0 for m in range(M))
        transportation_mp.addConstrs(sum(x_mp[iteration][i,n] for i in range(M)) - Demand_f[n] - Demand_v[n]*G[0,n]>= 0 for n in range(N))
        transportation_mp.optimize()
        
    LB.append(transportation_mp.ObjVal)
    for m in range(M):
        Y[0,m] = y[0,m].x
    
        
    
    transportation_sp.remove(transportation_sp.getConstrs())

    # transportation_sp.addConstr(-z[0,0] + 800*Y[0,0] >= 0)
    # transportation_sp.addConstr(-z[0,1] + 800*Y[0,1] >= 0)
    # transportation_sp.addConstr(-z[0,2] + 800*Y[0,2] >= 0)
    transportation_sp.addConstrs(-z[0,m] + Capacity[m]*Y[0,m] >= 0 for m in range(M))
    
    # transportation_sp.addConstr(-sum(x[0,j] for j in range(N)) + z[0,0] >= 0)
    # transportation_sp.addConstr(-sum(x[1,j] for j in range(N)) + z[0,1] >= 0)
    # transportation_sp.addConstr(-sum(x[2,j] for j in range(N)) + z[0,2] >= 0)
    transportation_sp.addConstrs(-sum(x[m,j] for j in range(N)) + z[0,m] >= 0 for m in range(M))
    
    # transportation_sp.addConstr(sum(x[i,0] for i in range(M)) - d[0,0] >= 0)
    # transportation_sp.addConstr(sum(x[i,1] for i in range(M)) - d[0,1] >= 0)
    # transportation_sp.addConstr(sum(x[i,2] for i in range(M)) - d[0,2] >= 0)
    transportation_sp.addConstrs(sum(x[i,n] for i in range(M)) - d[0,n] >= 0 for n in range(N))
    
    
    # transportation_sp.addConstr(-w1[0,0] + w2[0,0] <= 18)
    # transportation_sp.addConstr(-w1[0,1] + w2[0,1] <= 25)
    # transportation_sp.addConstr(-w1[0,2] + w2[0,2] <= 20) 
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] <= Cost_supply_v[m] for m in range(M)) 

    # transportation_sp.addConstr(-w2[0,0] + w3[0,0] <= 22)#00
    # transportation_sp.addConstr(-w2[0,0] + w3[0,1] <= 33)#01
    # transportation_sp.addConstr(-w2[0,0] + w3[0,2] <= 24)#02
    
    # transportation_sp.addConstr(-w2[0,1] + w3[0,1] <= 23)#11
    # transportation_sp.addConstr(-w2[0,1] + w3[0,0] <= 33)#10
    # transportation_sp.addConstr(-w2[0,1] + w3[0,2] <= 30)#12
    
    # transportation_sp.addConstr(-w2[0,2] + w3[0,2] <= 27)#22
    # transportation_sp.addConstr(-w2[0,2] + w3[0,0] <= 20)#20
    # transportation_sp.addConstr(-w2[0,2] + w3[0,1] <= 25)#21 
    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] <= Cost_transportation[m][n] for m in range(M) for n in range(N))
    
    # transportation_sp.addConstr(w1[0,0] <= INF*B1[0,0])
    # transportation_sp.addConstr(w1[0,1] <= INF*B1[0,1])
    # transportation_sp.addConstr(w1[0,2] <= INF*B1[0,2])
    # transportation_sp.addConstr(w2[0,0] <= INF*B1[0,3])
    # transportation_sp.addConstr(w2[0,1] <= INF*B1[0,4])
    # transportation_sp.addConstr(w2[0,2] <= INF*B1[0,5])
    # transportation_sp.addConstr(w3[0,0] <= INF*B1[0,6])
    # transportation_sp.addConstr(w3[0,1] <= INF*B1[0,7])
    # transportation_sp.addConstr(w3[0,2] <= INF*B1[0,8])
    transportation_sp.addConstrs(w1[0,m] <= INF*B11[0,m] for m in range(M))
    transportation_sp.addConstrs(w2[0,m] <= INF*B12[0,m] for m in range(M))
    transportation_sp.addConstrs(w3[0,n] <= INF*B13[0,n] for n in range(N))
    
    
    # transportation_sp.addConstr(-z[0,0] + 800*Y[0,0] <= INF*(1-B1[0,0]))
    # transportation_sp.addConstr(-z[0,1] + 800*Y[0,1] <= INF*(1-B1[0,1]))
    # transportation_sp.addConstr(-z[0,2] + 800*Y[0,2] <= INF*(1-B1[0,2]))
    transportation_sp.addConstrs(-z[0,m] + Capacity[m]*Y[0,m] <= INF*(1-B11[0,m]) for m in range(M))
    
    # transportation_sp.addConstr(-sum(x[0,j] for j in range(N)) + z[0,0] <= INF*(1-B1[0,3]))
    # transportation_sp.addConstr(-sum(x[1,j] for j in range(N)) + z[0,1] <= INF*(1-B1[0,4]))
    # transportation_sp.addConstr(-sum(x[2,j] for j in range(N)) + z[0,2] <= INF*(1-B1[0,5]))
    transportation_sp.addConstrs(-sum(x[m,j] for j in range(N)) + z[0,m] <=INF*(1-B12[0,m]) for m in range(M))
    
    # transportation_sp.addConstr(sum(x[i,0] for i in range(M)) - d[0,0] <= INF*(1-B1[0,6]))
    # transportation_sp.addConstr(sum(x[i,1] for i in range(M)) - d[0,1] <= INF*(1-B1[0,7]))
    # transportation_sp.addConstr(sum(x[i,2] for i in range(M)) - d[0,2] <= INF*(1-B1[0,8]))
    transportation_sp.addConstrs(sum(x[i,n] for i in range(M)) - d[0,n] <= INF*(1-B13[0,n]) for n in range(N))
    
    
    # transportation_sp.addConstr(z[0,0] <= INF*B2[0,0])
    # transportation_sp.addConstr(z[0,1] <= INF*B2[0,1])
    # transportation_sp.addConstr(z[0,2] <= INF*B2[0,2])
    transportation_sp.addConstrs(z[0,m] <= INF*B21[0,m] for m in range(M))
    
    # transportation_sp.addConstr(x[0,0] <= INF*B2[0,3])
    # transportation_sp.addConstr(x[0,1] <= INF*B2[0,4])
    # transportation_sp.addConstr(x[0,2] <= INF*B2[0,5])
    # transportation_sp.addConstr(x[1,0] <= INF*B2[0,6])
    # transportation_sp.addConstr(x[1,1] <= INF*B2[0,7])
    # transportation_sp.addConstr(x[1,2] <= INF*B2[0,8])
    # transportation_sp.addConstr(x[2,0] <= INF*B2[0,9])
    # transportation_sp.addConstr(x[2,1] <= INF*B2[0,10])
    # transportation_sp.addConstr(x[2,2] <= INF*B2[0,11])
    transportation_sp.addConstrs(x[m,n] <= INF*B22[m,n] for m in range(M) for n in range(N))
    
    # transportation_sp.addConstr(-w1[0,0] + w2[0,0] - 18 <= INF*(1-B2[0,0]))
    # transportation_sp.addConstr(-w1[0,1] + w2[0,1] - 25 <= INF*(1-B2[0,1]))
    # transportation_sp.addConstr(-w1[0,2] + w2[0,2] - 20 <= INF*(1-B2[0,2])) 
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] - Cost_supply_v[m] <= INF*(1-B21[0,m]) for m in range(M))
    
    # transportation_sp.addConstr(-w2[0,0] + w3[0,0] - 22 <= INF*(1-B2[0,3]))#00
    # transportation_sp.addConstr(-w2[0,0] + w3[0,1] - 33 <= INF*(1-B2[0,4]))#01
    # transportation_sp.addConstr(-w2[0,0] + w3[0,2] - 24 <= INF*(1-B2[0,5]))#02
    
    # transportation_sp.addConstr(-w2[0,1] + w3[0,1] - 23 <= INF*(1-B2[0,7]))#11
    # transportation_sp.addConstr(-w2[0,1] + w3[0,0] - 33 <= INF*(1-B2[0,6]))#10
    # transportation_sp.addConstr(-w2[0,1] + w3[0,2] - 30 <= INF*(1-B2[0,8]))#12
    
    # transportation_sp.addConstr(-w2[0,2] + w3[0,2] - 27 <= INF*(1-B2[0,11]))#22
    # transportation_sp.addConstr(-w2[0,2] + w3[0,0] - 20 <= INF*(1-B2[0,9]))#20
    # transportation_sp.addConstr(-w2[0,2] + w3[0,1] - 25 <= INF*(1-B2[0,10]))#21 
    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] - Cost_transportation[m][n] <= INF*(1 - B22[m,n]) for m in range(M) for n in range(N))
    
    
    
    # transportation_sp.addConstr(-w1[0,0] + w2[0,0] - 18 >= INF*(B2[0,0]-1))
    # transportation_sp.addConstr(-w1[0,1] + w2[0,1] - 25 >= INF*(B2[0,1]-1))
    # transportation_sp.addConstr(-w1[0,2] + w2[0,2] - 20 >= INF*(B2[0,2]-1)) 
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] - Cost_supply_v[m] >= INF*(B21[0,m]-1) for m in range(M))
    
    # transportation_sp.addConstr(-w2[0,0] + w3[0,0] - 22 >= INF*(B2[0,3]-1))#00
    # transportation_sp.addConstr(-w2[0,0] + w3[0,1] - 33 >= INF*(B2[0,4]-1))#01
    # transportation_sp.addConstr(-w2[0,0] + w3[0,2] - 24 >= INF*(B2[0,5]-1))#02
    
    # transportation_sp.addConstr(-w2[0,1] + w3[0,1] - 23 >= INF*(B2[0,7]-1))#11
    # transportation_sp.addConstr(-w2[0,1] + w3[0,0] - 33 >= INF*(B2[0,6]-1))#10
    # transportation_sp.addConstr(-w2[0,1] + w3[0,2] - 30 >= INF*(B2[0,8]-1))#12
    
    # transportation_sp.addConstr(-w2[0,2] + w3[0,2] - 27 >= INF*(B2[0,11]-1))#22
    # transportation_sp.addConstr(-w2[0,2] + w3[0,0] - 20 >= INF*(B2[0,9]-1))#20
    # transportation_sp.addConstr(-w2[0,2] + w3[0,1] - 25 >= INF*(B2[0,10]-1))#21 
    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] - Cost_transportation[m][n] >= INF*(B22[m,n] - 1) for m in range(M) for n in range(N))
    
    # u
    transportation_sp.addConstr(d[0,0] == 206 + 40*g[0,0])
    transportation_sp.addConstr(d[0,1] == 274 + 40*g[0,1])
    transportation_sp.addConstr(d[0,2] == 220 + 40*g[0,2])
    transportation_sp.addConstr(g[0,0] <= 1)
    transportation_sp.addConstr(g[0,1] <= 1)
    transportation_sp.addConstr(g[0,2] <= 1)
    transportation_sp.addConstr(g[0,0] + g[0,1] + g[0,2] <= 1.8)
    transportation_sp.addConstr(g[0,0] + g[0,1] <= 1.2)

    transportation_sp.optimize()
    
    UB.append(400*Y[0,0] + 414*Y[0,1] + 326*Y[0,2] +\
         18*z[0,0].x + 25*z[0,1].x + 20*z[0,2].x +\
         22*x[0,0].x + 33*x[0,1].x + 24*x[0,2].x +\
         33*x[1,0].x + 23*x[1,1].x + 30*x[1,2].x +\
         20*x[2,0].x + 25*x[2,1].x + 27*x[2,2].x)
         
    G[0,0] = g[0,0].x
    G[0,1] = g[0,1].x
    G[0,2] = g[0,2].x
    
    iteration = iteration + 1
    
    
    
tb = pt.PrettyTable()    
# tb.field_names = ['iteration','LB','UB']

tb.add_column('iteration',[i for i in range(iteration + 1)])
tb.add_column('LB',LB)
tb.add_column('UB',UB)

print(tb)
    
    
    
    
    
    
    