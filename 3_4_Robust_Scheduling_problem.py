# -*- coding: utf-8 -*-
"""
@author: SYJ

example2 with robust

background: Processing Scheduling Problem
《Effective continuous-time formulation for short-term scheduling.
 1. Multipurpose batch processes》
robust: 
《A Comparative Theoretical and Computational Study on Robust
Counterpart Optimization: I. Robust Linear Optimization and Robust
Mixed Integer Linear Optimization》
Example 7.2

"""

import gurobipy as gp
from gurobipy import GRB
# import prettytable as pt
import  matplotlib.pyplot as plt
# import math as mt

R_F = [1]

# 0.box
# 1.ellipsoidal
# 2.polyhedral
# 3.interval+ellipsoidal
# 4.interval+polyhedral
# 5.interval+ellipsoidal+polyhedral 0.5 + 0.5
# 6.interval+ellipsoidal+polyhedral 0.25 + 0.75
# 7.interval+ellipsoidal+polyhedral 0.75 + 0.25
# 8.interval+polyhedral
colorbar = ['red','blue','yellow','green','gray','purple','salmon','pink']
lb = ['box','ellipsoidal','polyhedral','interval+ellipsoidal','interval+polyhedral',\
      'interval+ellipsoidal+polyhedral(1)','interval+ellipsoidal+polyhedral(2)',\
          'interval+ellipsoidal+polyhedral(3)','interval+polyhedral(2)']
#sets
N = ['n0','n1','n2','n3','n4']
I = ['i1','i2','i3','i4','i5','i6','i7','i8']
J = ['j1','j2','j3','j4']
S = ['s1','s2','s3','s4','s5','s6','s7','s8','s9']


# parameters
task_unit, alpha, beta = gp.multidict({
    ('i1','j1'): [2/3, 1/150],
    ('i2','j2'): [4/3, 2/75],
    ('i4','j2'): [4/3, 2/75],
    ('i6','j2'): [2/3, 1/75],
    ('i3','j3'): [4/3, 1/60],
    ('i5','j3'): [4/3, 1/60],
    ('i7','j3'): [2/3, 1/120],
    ('i8','j4'): [4/3, 1/150]
    })
unit, task, Max_C = gp.multidict({
    'j1': [['i1'],100],
    'j2': [['i2','i4','i6'],50],
    'j3': [['i3','i5','i7'],80],
    'j4': [['i8'],200]
    })


State, Max_S, STin = gp.multidict({
    's1': [9999,9999],
    's2': [9999,9999],
    's3': [9999,9999],
    's4': [100,0],
    's5': [200,0],
    's6': [150,0],
    's7': [200,0],
    's8': [9999,0],
    's9': [9999,0]
    })

stask, raw, p1, product, p2, sunit = gp.multidict({
    'i1': [['s1'],[1],['s4'],[1],'j1'],
    'i2': [['s2','s3'],[0.5,0.5],['s6'],[1],'j2'],
    'i3': [['s2','s3'],[0.5,0.5],['s6'],[1],'j3'],
    'i4': [['s4','s6'],[0.4,0.6],['s8','s5'],[0.4,0.6],'j2'],
    'i5': [['s4','s6'],[0.4,0.6],['s8','s5'],[0.4,0.6],'j3'],
    'i6': [['s3','s5'],[0.2,0.8],['s7'],[1],'j2'],
    'i7': [['s3','s5'],[0.2,0.8],['s7'],[1],'j3'],
    'i8': [['s7'],[1],['s5','s9'],[0.1,0.9],'j4']
    })

gongxu = [[['i1'],['i4','i5'],['i6','i7'],['i8']],[['i2','i3'],['i4','i5']]]
T_H = 8
H = 9999
# omega = -0.1
# tao = -0.1 

# models
ep = gp.Model('eventpoint_example2')

# ep.Params.NonConvex = 2
ep.Params.OutputFlag = 0
# variables
# continuous
ts = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'ts')
tf = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'tf')
b = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'b')
st = ep.addVars(State, N, vtype = GRB.CONTINUOUS, name = 'st')
d = ep.addVars(State, N, vtype = GRB.CONTINUOUS, name = 'demand')
z = ep.addVar(vtype = GRB.CONTINUOUS, name = 'z')
# uncertainty
uc = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'uc')
uc2 = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'uc2')
u_wv = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'u_wv')
v_b = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'v_b')
u_wv2 = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'u_wv')
v_b2 = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'v_b')
q_wv = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'q_wv')
p_b = ep.addVars(I, N, vtype = GRB.CONTINUOUS, name = 'p_b')
# binary
wv = ep.addVars(I, N, vtype = GRB.BINARY, name = 'wv')
yv = ep.addVars(J, N, vtype = GRB.BINARY, name = 'yv')

# OUTER LOOP(diferent robust situation) 
for robust_flag in R_F:
    fi = -0.1
    obj_val = []
    OME = []
    TAO = []
    F = []
    # INNER
    for iteration in range(20):
        # notice:remove all the constrains including Q-constrains
        ep.remove(ep.getConstrs()) 
        ep.remove(ep.getQConstrs()) 
        # main parameter use fi
        fi = fi + 0.1
        F.append(fi)
        
        # robust constraints
        # robust_flag
        # 0.box
        # 1.ellipsoidal
        # 2.polyhedral
        # 3.interval+ellipsoidal
        # 4.interval+polyhedral
        # 5.interval+ellipsoidal+polyhedral
        
      # uncertainty on the processing time  
      # ep.addConstrs(tf[i,sunit[i],n] == ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] for i in I for n in N)
        if robust_flag == 1: # 1.ellipsoidal
            omega = fi*(2**0.5)
            # print(omega)
            OME.append(OME)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          uc[i,n] for i in I for n in N)
            for i in I:
                for n in N:
                    ep.addConstr(uc[i,n]*uc[i,n] >= omega*omega*(0.05*alpha[i,sunit[i]]*wv[i,n]*0.05*alpha[i,sunit[i]]*wv[i,n] +\
                                                           0.05*beta[i,sunit[i]]*b[i,sunit[i],n]*0.05*beta[i,sunit[i]]*b[i,sunit[i],n]))
        elif robust_flag == 2: # 2.polyhedral
            tao = fi*2
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] >= 0.05*alpha[i,sunit[i]]*u_wv[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] >= 0.05*beta[i,sunit[i]]*v_b[i,n] for i in I for n in N)
            ep.addConstrs(- u_wv[i,n] <= wv[i,n] for i in I for n in N)
            ep.addConstrs(u_wv[i,n] >= wv[i,n] for i in I for n in N)
            ep.addConstrs(- v_b[i,n] <= b[i,sunit[i],n] for i in I for n in N)
            ep.addConstrs(v_b[i,n] >= b[i,sunit[i],n] for i in I for n in N)
        elif robust_flag == 0: # 0.box
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          fi*(0.05*alpha[i,sunit[i]]*u_wv[i,n] + 0.05*beta[i,sunit[i]]*v_b[i,n]) for i in I for n in N)
            ep.addConstrs(- u_wv[i,n] <= wv[i,n] for i in I for n in N)
            ep.addConstrs(u_wv[i,n] >= wv[i,n] for i in I for n in N)
            ep.addConstrs(- v_b[i,n] <= b[i,sunit[i],n] for i in I for n in N)
            ep.addConstrs(v_b[i,n] >= b[i,sunit[i],n] for i in I for n in N)
        elif robust_flag == 3: # 3.interval+ellipsoidal
            omega = fi*(2**0.5)
            # print(omega)
            OME.append(OME)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          0.05*alpha[i,sunit[i]]*u_wv[i,n] + 0.05*beta[i,sunit[i]]*v_b[i,n] +\
                          uc[i,n] for i in I for n in N)
            for i in I:
                for n in N:
                    ep.addConstr(uc[i,n]*uc[i,n] >= omega*omega*(0.05*alpha[i,sunit[i]]*u_wv2[i,n]*0.05*alpha[i,sunit[i]]*u_wv2[i,n] +\
                                                           0.05*beta[i,sunit[i]]*v_b2[i,n]*0.05*beta[i,sunit[i]]*v_b2[i,n]))
            ep.addConstrs(wv[i,n] - u_wv2[i,n] <= u_wv[i,n] for i in I for n in N)
            ep.addConstrs(wv[i,n] - u_wv2[i,n] >= -u_wv[i,n] for i in I for n in N)
            ep.addConstrs(b[i,sunit[i],n] - v_b2[i,n] <= v_b[i,n] for i in I for n in N)
            ep.addConstrs(b[i,sunit[i],n] - v_b2[i,n] >= - v_b[i,n] for i in I for n in N)
        elif robust_flag == 4: # 4.interval+polyhedral
            tao = fi*2
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] + u_wv[i,n] +v_b[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] + u_wv[i,n] >= 0.05*alpha[i,sunit[i]]*u_wv2[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] + v_b[i,n] >= 0.05*beta[i,sunit[i]]*v_b2[i,n] for i in I for n in N)
            ep.addConstrs(- u_wv2[i,n] <= wv[i,n] for i in I for n in N)
            ep.addConstrs(u_wv2[i,n] >= wv[i,n] for i in I for n in N)
            ep.addConstrs(- v_b2[i,n] <= b[i,sunit[i],n] for i in I for n in N)
            ep.addConstrs(v_b2[i,n] >= b[i,sunit[i],n] for i in I for n in N)        
        elif robust_flag == 5: # 5.interval+ellipsoidal+polyhedral
            omega = fi*(2**0.5)
            OME.append(OME)
            tao = 0.5*omega + 0.5*fi*2
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] + u_wv[i,n] +v_b[i,n] + uc2[i,n] for i in I for n in N)
            ep.addConstrs(uc2[i,n]*uc2[i,n] >= omega*omega*(u_wv2[i,n]*u_wv2[i,n] + v_b2[i,n]*v_b2[i,n]) for i in I for n in N)
            ep.addConstrs(q_wv[i,n] <= u_wv[i,n] for i in I for n in N)
            ep.addConstrs(q_wv[i,n] >= -u_wv[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] <= v_b[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] >= -v_b[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] >= -uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] >= -uc[i,n] for i in I for n in N)
        elif robust_flag == 6: # 6.interval+ellipsoidal+polyhedral(different tao)
            omega = fi*(2**0.5)
            OME.append(OME)
            tao = 0.25*omega + 0.75*fi*2
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] + u_wv[i,n] +v_b[i,n] + uc2[i,n] for i in I for n in N)
            ep.addConstrs(uc2[i,n]*uc2[i,n] >= omega*omega*(u_wv2[i,n]*u_wv2[i,n] + v_b2[i,n]*v_b2[i,n]) for i in I for n in N)
            ep.addConstrs(q_wv[i,n] <= u_wv[i,n] for i in I for n in N)
            ep.addConstrs(q_wv[i,n] >= -u_wv[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] <= v_b[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] >= -v_b[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] >= -uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] >= -uc[i,n] for i in I for n in N)
        elif robust_flag == 7: # 7.interval+ellipsoidal+polyhedral(different tao)
            omega = fi*(2**0.5)
            OME.append(OME)
            tao = 0.75*omega + 0.25*fi*2
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] + u_wv[i,n] +v_b[i,n] + uc2[i,n] for i in I for n in N)
            ep.addConstrs(uc2[i,n]*uc2[i,n] >= omega*omega*(u_wv2[i,n]*u_wv2[i,n] + v_b2[i,n]*v_b2[i,n]) for i in I for n in N)
            ep.addConstrs(q_wv[i,n] <= u_wv[i,n] for i in I for n in N)
            ep.addConstrs(q_wv[i,n] >= -u_wv[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] <= v_b[i,n] for i in I for n in N)
            ep.addConstrs(p_b[i,n] >= -v_b[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*alpha[i,sunit[i]]*wv[i,n] - q_wv[i,n] -u_wv2[i,n] >= -uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] <= uc[i,n] for i in I for n in N)
            ep.addConstrs(0.05*beta[i,sunit[i]]*b[i,sunit[i],n] - p_b[i,n] - v_b2[i,n] >= -uc[i,n] for i in I for n in N) 
        elif robust_flag == 8: # 8.
            tao = fi
            TAO.append(tao)
            ep.addConstrs(tf[i,sunit[i],n] >= ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] +\
                          tao*uc[i,n] + u_wv[i,n] +v_b[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] + u_wv[i,n] >= 0.05*alpha[i,sunit[i]]*u_wv2[i,n] for i in I for n in N)
            ep.addConstrs(uc[i,n] + v_b[i,n] >= 0.05*beta[i,sunit[i]]*v_b2[i,n] for i in I for n in N)
            ep.addConstrs(- u_wv2[i,n] <= wv[i,n] for i in I for n in N)
            ep.addConstrs(u_wv2[i,n] >= wv[i,n] for i in I for n in N)
            ep.addConstrs(- v_b2[i,n] <= b[i,sunit[i],n] for i in I for n in N)
            ep.addConstrs(v_b2[i,n] >= b[i,sunit[i],n] for i in I for n in N)     
            
        # constraints
        # allocation constraints
        ep.addConstrs(sum(wv[i, n] for i in task[j]) == yv[j, n] for j in J for n in N)
        # capacity constraints
        ep.addConstrs(b[i,j,n] <= Max_C[j]*wv[i,n] for j in J for i in task[j] for n in N)
        # storage constraints
        ep.addConstrs(st[s, n] <= Max_S[s] for s in State for n in N)
        # material balances 'n0'
        ep.addConstrs(st[s,'n0'] == STin[s] - \
                      sum(p1[i][raw[i].index(s)]*b[i,sunit[i],'n0']for i in I if s in raw[i]) - \
                      d[s,'n0'] for s in State)
        # demand constraints
        ep.addConstrs(d[s,n] == 0 for s in State[0:7] for n in N)
        # material balances 
        ep.addConstrs(st[s,N[k+1]] == st[s,N[k]] + \
                      sum(p2[i][product[i].index(s)]*b[i,sunit[i],N[k]]for i in I if s in product[i]) - \
                      sum(p1[i][raw[i].index(s)]*b[i,sunit[i],N[k+1]]for i in I if s in raw[i]) - \
                      d[s,N[k+1]] for s in State for k in range(len(N)-1))
        # sequence constraints : STSU/DTSU
        # ep.addConstrs(ts[i,sunit[i],N[n+1]] >= tf[i,sunit[i],N[n]] - H*(2-wv[i,N[n]]-yv[sunit[i],N[n]]) for i in I for n in range((len(N)-1)))
        ep.addConstrs(ts[task[j][i],j,N[n+1]] >= tf[task[j][ii],j,N[n]] - H*(2-wv[task[j][ii],N[n]]-yv[j,N[n]])\
                      for j in J for n in range((len(N)-1)) for i in range(len(task[j])) for ii in range(len(task[j])))
        ep.addConstrs(ts[i,sunit[i],N[n+1]] >= ts[i,sunit[i],N[n]] for i in I for n in range((len(N)-1)))
        ep.addConstrs(tf[i,sunit[i],N[n+1]] >= tf[i,sunit[i],N[n]] for i in I for n in range((len(N)-1)))
        # sequence constraints : DTDU
        for k in gongxu:
            for i in range(len(k)-1):
                for j1 in range(len(k[i])):
                    for j2 in range(len(k[i+1])):
                        ep.addConstrs(ts[k[i+1][j2],sunit[k[i+1][j2]],N[n+1]] >= tf[k[i][j1],sunit[k[i][j1]],N[n]] -\
                                      H*(2 - wv[k[i][j1],N[n]] - yv[sunit[k[i][j1]],N[n]]) for n in range(len(N)-1))
        # completion of previous tasks                
        ep.addConstrs(ts[i,sunit[i],N[n+1]] >= sum(tf[i,sunit[i],N[nn]]-ts[i,sunit[i],N[nn]]for nn in range(n+1)) for i in I for n in range(len(N)-1))
        # time horizon
        ep.addConstrs(ts[i,sunit[i],n] <= T_H for i in I for n in N)
        ep.addConstrs(tf[i,sunit[i],n] <= T_H for i in I for n in N)
        # objective
        ep.addConstr(z <= 10*(sum(d['s8',n]+d['s9',n] for n in N)))    
    
        # objective
        # ep.setObjective(10*(sum(d['s8',n]+d['s9',n] for n in N))-sum(yv[j,n] for j in J for n in N), GRB.MAXIMIZE)
        
        ep.setObjective(z, GRB.MAXIMIZE)

        # optimize
        ep.optimize()
        obj_val.append(ep.ObjVal)  


# output        
    plt.plot(F, obj_val, color = colorbar[R_F.index(robust_flag)],label = lb[robust_flag])
    plt.scatter(F, obj_val, color='black', s=10)
    
    
plt.grid()
plt.legend()
plt.rcParams['savefig.dpi'] = 900
plt.rcParams['figure.dpi'] = 900
plt.show()
# tb = pt.PrettyTable()
# R = N.copy()
# R.insert(0,'')
# tb.field_names = R

# for i in I:
#     wvrow = []
#     wvrow.append('wv%s' % i)

#     for j in N:
#         wvrow.append(wv[i,j].x)
#     tb.add_row(wvrow)
    
    
# for i in I:    
#     tsrow = []
#     tfrow = []    
#     tsrow.append('ts%s' % i)
#     tfrow.append('tf%s' % i)
#     for k in N:
#         tsrow.append(round(ts[i,sunit[i],k].x,3))
#         tfrow.append(round(tf[i,sunit[i],k].x,3))
#     tb.add_row(tsrow)
#     tb.add_row(tfrow)
    
# print(tb)