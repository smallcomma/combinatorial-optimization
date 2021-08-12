# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 09:33:51 2021

@author: asus-pc
"""



import gurobipy as gp
from gurobipy import GRB
import numpy as np
import prettytable as pt
#parameters
M = 30
N = 30
INF = 9999
OBJ_INF = 99999999
Y = {}
G = {}
for n in range(N):
    G[0,n] = 0.6
x_mp = {}
z_mp = {}
t_Y = {}
t_G = {}
iteration = 0

#numpy.ndarray.tolist(np.random.random(10))
#np.random.rand(3,3)
'''
initial parameter
'''
# Capacity = [165.0, 165.0, 165.0, 165.0, 165.0, 165.0, 165.0, 165.0, 165.0, 165.0]
# Demand_f = [106, 101, 101, 101, 100, 105, 103, 108, 106, 103]
# Demand_v = [26.0, 35.0, 10.0, 10.0, 29.0, 39.0, 25.0, 28.0, 48.0, 48.0]
# Cost_supply_f = [907, 951, 927, 944, 988, 933, 998, 935, 905, 977]
# Cost_supply_v = [99, 90, 94, 94, 91, 96, 94, 99, 90, 92]
# Cost_transportation = [[96.0, 4.0, 36.0, 69.0, 57.0, 81.0, 19.0, 37.0, 9.0, 12.0],
#                       [52.0, 30.0, 80.0, 57.0, 40.0, 45.0, 37.0, 59.0, 43.0, 4.0],
#                       [38.0, 67.0, 7.0, 53.0, 13.0, 19.0, 37.0, 54.0, 35.0, 42.0],
#                       [35.0, 97.0, 77.0, 23.0, 61.0, 42.0, 20.0, 78.0, 57.0, 20.0],
#                       [18.0, 87.0, 53.0, 53.0, 21.0, 45.0, 43.0, 43.0, 70.0, 76.0],
#                       [33.0, 89.0, 20.0, 12.0, 50.0, 50.0, 47.0, 28.0, 63.0, 19.0],
#                       [3.0, 73.0, 89.0, 46.0, 72.0, 72.0, 26.0, 11.0, 12.0, 56.0],
#                       [30.0, 21.0, 82.0, 3.0, 37.0, 51.0, 85.0, 1.0, 15.0, 2.0],
#                       [55.0, 14.0, 58.0, 8.0, 34.0, 69.0, 94.0, 74.0, 49.0, 72.0],
#                       [37.0, 7.0, 15.0, 61.0, 16.0, 16.0, 61.0, 91.0, 4.0, 91.0]]

# Capacity = [165.0, 165.0, 165.0]
# Demand_f = [102, 106, 107]
# Demand_v = [31.0, 24.0, 21.0]
# Cost_supply_f = [993, 908, 947]
# Cost_supply_v = [92, 98, 91]
# Cost_transportation = [[37.0, 61.0, 8.0], [63.0, 2.0, 30.0], [49.0, 31.0, 22.0]]


'''
random parameters
'''
low = 10
high = 500
Demand_floor = np.random.randint(low,high,size = N)
Demand_f = np.ndarray.tolist(Demand_floor)
Demand_v = np.ndarray.tolist(np.floor(0.5*np.random.random(N)*Demand_floor))

Capacity = np.ndarray.tolist(np.ceil((high+0.5*high)*N/M*np.ones(M)))
# Capacity = np.ndarray.tolist(np.ceil(8000*np.ones(M)))
Cost_supply_f = np.ndarray.tolist(np.random.randint(100,1000,size = M))
Cost_supply_v = np.ndarray.tolist(np.random.randint(10,100,size = M))
Cost_transportation = np.ndarray.tolist(np.ceil(1000*np.random.rand(M,N)))

#models
transportation_mp = gp.Model('transportation_mp')
transportation_sp = gp.Model('transportation_sp')

#variables
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


B21 = transportation_sp.addVars(1,M,vtype = GRB.BINARY,name = 'b21')
B22 = transportation_sp.addVars(M,N,vtype = GRB.BINARY,name = 'b22')


 
transportation_mp.setObjective(sum(Cost_supply_f[m]*y[0,m] for m in range(M)) + a,GRB.MINIMIZE) 
   
transportation_sp.setObjective(sum(Cost_supply_v[m]*z[0,m] for m in range(M)) +\
                               sum(Cost_transportation[m][n]*x[m,n] for m in range(M) for n in range(N)), GRB.MAXIMIZE)
    
LB = [- OBJ_INF]
UB = [+ OBJ_INF]
transportation_mp.Params.OutputFlag = 0
transportation_sp.Params.OutputFlag = 1
while UB[-1]-LB[-1]>=0.1:
    if iteration == 0:   
        #initial the main problem
        transportation_mp.addConstr(a >= sum(Cost_supply_v[m]*z_mp[iteration][0,m]for m in range(M)) + \
                                    sum(Cost_transportation[m][n]*x_mp[iteration][m,n]for m in range(M) for n in range(N)))

        transportation_mp.addConstrs(z_mp[iteration][0,m] <= Capacity[m]*y[0,m] for m in range(M))
        
        transportation_mp.addConstrs(-sum(x_mp[iteration][m,j] for j in range(N)) + z_mp[iteration][0,m] >= 0 for m in range(M))
        #use a random scenario satisfy the uncertain set constraint
        transportation_mp.addConstrs(sum(x_mp[iteration][i,n] for i in range(M)) - Demand_f[n] - Demand_v[n]*G[0,n]>= 0 for n in range(N))
            
        transportation_mp.optimize()
    else:
        x_mp[iteration] = transportation_mp.addVars(M,N,vtype = GRB.CONTINUOUS,name = 'x_mp%d' % iteration)
        z_mp[iteration] = transportation_mp.addVars(1,M,vtype = GRB.CONTINUOUS,name = 'z_mp%d' % iteration)
        #add constraints with the worst scenario from the subproblem
        transportation_mp.addConstr(a >= sum(Cost_supply_v[m]*z_mp[iteration][0,m]for m in range(M)) + \
                                    sum(Cost_transportation[m][n]*x_mp[iteration][m,n]for m in range(M) for n in range(N)))
        transportation_mp.addConstrs(z_mp[iteration][0,m] <= Capacity[m]*y[0,m] for m in range(M))
        transportation_mp.addConstrs(-sum(x_mp[iteration][m,j] for j in range(N)) + z_mp[iteration][0,m] >= 0 for m in range(M))
        transportation_mp.addConstrs(sum(x_mp[iteration][i,n] for i in range(M)) - Demand_f[n] - Demand_v[n]*G[0,n]>= 0 for n in range(N))
        transportation_mp.optimize()
    #update the lower bound    
    LB.append(transportation_mp.ObjVal)
    #deliver the value of the discrete variables
    for m in range(M):
        Y[0,m] = y[0,m].x
        t_Y[iteration,m] = y[0,m].x
        
    #update the constraints of the subproblem
    transportation_sp.remove(transportation_sp.getConstrs())

    transportation_sp.addConstrs(-z[0,m] + Capacity[m]*Y[0,m] >= 0 for m in range(M))
    
    transportation_sp.addConstrs(-sum(x[m,j] for j in range(N)) + z[0,m] >= 0 for m in range(M))
    
    transportation_sp.addConstrs(sum(x[i,n] for i in range(M)) - d[0,n] >= 0 for n in range(N))
    #the constraints of dual problem
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] <= Cost_supply_v[m] for m in range(M)) 

    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] <= Cost_transportation[m][n] for m in range(M) for n in range(N))
    #KKT condition    
    transportation_sp.addConstrs(w1[0,m] <= INF*B11[0,m] for m in range(M))
    transportation_sp.addConstrs(w2[0,m] <= INF*B12[0,m] for m in range(M))
    transportation_sp.addConstrs(w3[0,n] <= INF*B13[0,n] for n in range(N))
    
    

    transportation_sp.addConstrs(-z[0,m] + Capacity[m]*Y[0,m] <= INF*(1-B11[0,m]) for m in range(M))   
    transportation_sp.addConstrs(-sum(x[m,j] for j in range(N)) + z[0,m] <=INF*(1-B12[0,m]) for m in range(M))
    transportation_sp.addConstrs(sum(x[i,n] for i in range(M)) - d[0,n] <= INF*(1-B13[0,n]) for n in range(N))
    
    

    transportation_sp.addConstrs(z[0,m] <= INF*B21[0,m] for m in range(M))
    transportation_sp.addConstrs(x[m,n] <= INF*B22[m,n] for m in range(M) for n in range(N))
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] - Cost_supply_v[m] <= INF*(1-B21[0,m]) for m in range(M))
    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] - Cost_transportation[m][n] <= INF*(1 - B22[m,n]) for m in range(M) for n in range(N))
    
    
    
    transportation_sp.addConstrs(-w1[0,m] + w2[0,m] - Cost_supply_v[m] >= INF*(B21[0,m]-1) for m in range(M))
    transportation_sp.addConstrs(-w2[0,m] + w3[0,n] - Cost_transportation[m][n] >= INF*(B22[m,n] - 1) for m in range(M) for n in range(N))
    
    # uncertain set
    # transportation_sp.addConstr(d[0,0] == 206 + 40*g[0,0])
    # transportation_sp.addConstr(d[0,1] == 274 + 40*g[0,1])
    # transportation_sp.addConstr(d[0,2] == 220 + 40*g[0,2])
    transportation_sp.addConstrs(d[0,n] == Demand_f[n] + Demand_v[n]*g[0,n] for n in range(N))
    
    # transportation_sp.addConstr(g[0,0] <= 1)
    # transportation_sp.addConstr(g[0,1] <= 1)
    # transportation_sp.addConstr(g[0,2] <= 1)
    transportation_sp.addConstrs(g[0,n] <= 1 for n in range(N))
    
    # transportation_sp.addConstr(g[0,0] + g[0,1] + g[0,2] <= 1.8)
    # transportation_sp.addConstr(g[0,0] + g[0,1] <= 1.2)
    
    
    transportation_sp.addConstrs(sum(g[0,n] for n in range(nn+1)) <= (nn+1)*0.6 for nn in range(N) if nn >= 1 )
    # transportation_sp.addConstr(sum(g[0,n] for n in range(N)) <= N*0.6)
    
    
    transportation_sp.optimize()
    #update the upper bound
    # UB.append(min(UB[-1],sum(Cost_supply_f[m]*Y[0,m] for m in range(M)) +\
    #      sum(Cost_supply_v[m]*z[0,m].x for m in range(M)) +\
    #      sum(Cost_transportation[m][n]*x[m,n].x for m in range(M) for n in range(N))))
    UB.append(sum(Cost_supply_f[m]*Y[0,m] for m in range(M)) +\
          sum(Cost_supply_v[m]*z[0,m].x for m in range(M)) +\
          sum(Cost_transportation[m][n]*x[m,n].x for m in range(M) for n in range(N)))   
    #deliver the worst scenario  
    for i in range(N):
        G[0,i] = g[0,i].x
        t_G[iteration,i] = g[0,i].x
    # G[0,0] = g[0,0].x
    # G[0,1] = g[0,1].x
    # G[0,2] = g[0,2].x
    # transportation_sp.reset()
    iteration = iteration + 1
    
t_y = pt.PrettyTable()
t_g = pt.PrettyTable()
ss = []
yy = []
gg = []
for i in range(M):
    ss.append(i+1)
t_y.add_column('site',ss)    
for j in range(iteration):
    for i in range(M):
        yy.append(t_Y[j,i])
    t_y.add_column('y',yy)
    yy=[]
print(t_y)    
ss = []
for i in range(N):
    ss.append(i+1)
t_g.add_column('destination',ss)    
for j in range(iteration):        
    for i in range(N):
        gg.append(t_G[j,i])
    t_g.add_column('g',gg)
    gg=[]        
print(t_g)
print('iteration:%d' % iteration)

   
    
    
    
    
    