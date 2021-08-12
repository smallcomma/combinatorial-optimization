# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 15:54:24 2020

@author: asus-pc

example 3
background: Processing Scheduling Problem
《Effective continuous-time formulation for short-term scheduling.
 1. Multipurpose batch processes》
"""

import gurobipy as gp
from gurobipy import GRB
import prettytable as pt


# sets
N = ['n0','n1','n2','n3','n4','n5']
I = ['i1','i2','i3','i4','i5','i6']
J = ['j1','j2','j3','j4','j5','j6']
S = ['s1','s2','s3','s4','s5','s6']


# parameters
task_unit, alpha, beta = gp.multidict({
    ('i1','j1'): [52/3, 13/15],
    ('i2','j2'): [8/3, 2/15],
    ('i3','j3'): [8/3, 2/15],
    ('i4','j4'): [4, 1/5],
    ('i5','j5'): [16/3, 4/15],
    ('i6','j6'): [16/3, 4/15]
    })

unit, task, Max_C = gp.multidict({
    'j1': [['i1'],20],
    'j2': [['i2'],20],
    'j3': [['i3'],20],
    'j4': [['i4'],20],
    'j5': [['i5'],20],
    'j6': [['i6'],20]
    })


State, Max_S, STin = gp.multidict({
    's1': [9999,9999],
    's2': [9999,9999],
    's3': [100,0],
    's4': [100,0],
    's5': [100,0],
    's6': [9999,0]
    })

stask, raw, p1, product, p2, sunit = gp.multidict({
    'i1': [['s1'],[1],['s3'],[1],'j1'],
    'i2': [['s2','s3'],[1,1],['s4'],[1],'j2'],
    'i3': [['s2','s3'],[1,1],['s4'],[1],'j3'],
    'i4': [['s4'],[1],['s5'],[1],'j4'],
    'i5': [['s5'],[1],['s6'],[1],'j5'],
    'i6': [['s5'],[1],['s6'],[1],'j6']
    })

gongxu = [[['i1'],['i2','i3'],['i4'],['i5','i6']]]
T_H = 76
H = 9999


# models
ep = gp.Model('eventpoint_example2')
# variables
# continuous
ts = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'ts')
tf = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'tf')
b = ep.addVars(task_unit, N, vtype = GRB.CONTINUOUS, name = 'b')
st = ep.addVars(State, N, vtype = GRB.CONTINUOUS, name = 'st')
d = ep.addVars(State, N, vtype = GRB.CONTINUOUS, name = 'demand')
# binary
wv = ep.addVars(I, N, vtype = GRB.BINARY, name = 'wv')
yv = ep.addVars(J, N, vtype = GRB.BINARY, name = 'yv')


# constraints
ep.addConstrs(sum(wv[i, n] for i in task[j]) == yv[j, n] for j in J for n in N)

ep.addConstrs(b[i,j,n] <= Max_C[j]*wv[i,n] for j in J for i in task[j] for n in N)
 
ep.addConstrs(st[s, n] <= Max_S[s] for s in State for n in N)

ep.addConstrs(st[s,'n0'] == STin[s] - \
              sum(p1[i][raw[i].index(s)]*b[i,sunit[i],'n0']for i in I if s in raw[i]) - \
              d[s,'n0'] for s in State)

ep.addConstrs(d[s,n] == 0 for s in State[0:(len(State)-1)] for n in N)

ep.addConstrs(st[s,N[k+1]] == st[s,N[k]] + \
              sum(p2[i][product[i].index(s)]*b[i,sunit[i],N[k]]for i in I if s in product[i]) - \
              sum(p1[i][raw[i].index(s)]*b[i,sunit[i],N[k+1]]for i in I if s in raw[i]) - \
              d[s,N[k+1]] for s in State for k in range(len(N)-1))

ep.addConstrs(tf[i,sunit[i],n] == ts[i,sunit[i],n] + alpha[i,sunit[i]]*wv[i,n] + beta[i,sunit[i]]*b[i,sunit[i],n] for i in I for n in N)
# ep.addConstrs(ts[i,sunit[i],N[n+1]] >= tf[i,sunit[i],N[n]] - H*(2-wv[i,N[n]]-yv[sunit[i],N[n]]) for i in I for n in range((len(N)-1)))
ep.addConstrs(ts[task[j][i],j,N[n+1]] >= tf[task[j][ii],j,N[n]] - H*(2-wv[task[j][ii],N[n]]-yv[j,N[n]])\
              for j in J for n in range((len(N)-1)) for i in range(len(task[j])) for ii in range(len(task[j])))
ep.addConstrs(ts[i,sunit[i],N[n+1]] >= ts[i,sunit[i],N[n]] for i in I for n in range((len(N)-1)))
ep.addConstrs(tf[i,sunit[i],N[n+1]] >= tf[i,sunit[i],N[n]] for i in I for n in range((len(N)-1)))
for k in gongxu:
    for i in range(len(k)-1):
        for j1 in range(len(k[i])):
            for j2 in range(len(k[i+1])):
                ep.addConstrs(ts[k[i+1][j2],sunit[k[i+1][j2]],N[n+1]] >= tf[k[i][j1],sunit[k[i][j1]],N[n]] -\
                              H*(2 - wv[k[i][j1],N[n]] - yv[sunit[k[i][j1]],N[n]]) for n in range(len(N)-1))
                    
ep.addConstrs(ts[i,sunit[i],N[n+1]] >= sum(tf[i,sunit[i],N[nn]]-ts[i,sunit[i],N[nn]]for nn in range(n+1)) for i in I for n in range(len(N)-1))

ep.addConstrs(ts[i,sunit[i],n] <= T_H for i in I for n in N)
ep.addConstrs(tf[i,sunit[i],n] <= T_H for i in I for n in N)
# objective
# ep.setObjective(10*(sum(d['s8',n]+d['s9',n] for n in N))-sum(yv[j,n] for j in J for n in N), GRB.MAXIMIZE)

ep.setObjective(2*(sum(d['s6',n] for n in N)), GRB.MAXIMIZE)


# output
# ep.write('ep.lp')
ep.optimize()

tb = pt.PrettyTable()
R = N.copy()
R.insert(0,'')
tb.field_names = R

for i in I:
    wvrow = []
    wvrow.append('wv%s' % i)

    for j in N:
        wvrow.append(wv[i,j].x)
    tb.add_row(wvrow)
    
    
for i in I:    
    tsrow = []
    tfrow = []    
    tsrow.append('ts%s' % i)
    tfrow.append('tf%s' % i)
    for k in N:
        tsrow.append(round(ts[i,sunit[i],k].x,3))
        tfrow.append(round(tf[i,sunit[i],k].x,3))
    tb.add_row(tsrow)
    tb.add_row(tfrow)
    
print(tb)