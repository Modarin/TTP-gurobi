#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/24 13:26
#@Author: Pengli Mo
#@File  : primal_model.py
# import gurobipy as gp

from gurobipy import *
from data_input import *

model = Model(name="Primal")

# 定理变量
x = model.addVars(num_K, num_S, num_T, lb=0, vtype=GRB.BINARY, name='x')
chi = model.addVars(num_K, num_S, num_T, lb=0, vtype=GRB.BINARY, name='chi')

# 目标函数
obj=QuadExpr(0)

for k in range(num_K):
    for s in range(num_S):
        for t in range(num_T):
            p=0
            for ss in range(s):
                if str(ss)+'-'+str(s) in data.passenger:
                    p+=data.passenger[str(ss)+'-'+str(s)][t]
            for tt in range(t):
                if k==0:
                    obj.add(chi[k,s,t]*chi[k,s,tt],p)
                else:
                    obj.add((chi[k,s,t]-chi[k-1,s,t])*(chi[k,s,tt]-chi[k-1,s,tt]),p)

model.setObjective(obj, GRB.MINIMIZE)

# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        lhs=LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k)+'_'+str(s)]:
            lhs.addTerms(1,x[k,s,t])
        model.addConstr(lhs==1, name='unique_'+str(k)+'_'+str(s))


# Con(3) Lheadway
for k in range(1,num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k) + '_' + str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for t in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-t, x[k-1, s, t])
        model.addConstr(lhs >= headway_lower, name='Lheadway_' + str(k) + '_' + str(s))

# Con(4) Uheadway
for k in range(1,num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k) + '_' + str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for t in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-t, x[k-1, s, t])
        model.addConstr(lhs <= headway_upper, name='Uheadway_' + str(k) + '_' + str(s))

# Con(2) dwell
for k in range(num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k)+'_'+str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for t in candidate_T[str(k) + '_' + str(s-1)]:
            lhs.addTerms(-t, x[k, s-1, t])
        model.addConstr(lhs == data.dwell[s-1]+data.travel[s-1], name='dwell_' + str(k) + '_' + str(s))

for k in range(num_K):
    for s in set_S_over:
        for t in range(num_T):
            lhs = LinExpr(0)
            for tt in range(num_T):
                if tt<=t:
                    lhs.addTerms(1,x[k,s,tt])
            model.addConstr(lhs==chi[k,s,t])

for k in range(num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        for ss in range(s):
            for sss in range(s,num_S):
                for t in range(num_T):
                    if str(ss)+'-'+str(sss) in data.passenger:
                        if k ==0:
                            lhs.addTerms(data.passenger[str(ss)+'-'+str(sss)][t], chi[k,ss,t])
                        else:
                            lhs.addTerms(data.passenger[str(ss) + '-' + str(sss)][t], chi[k, ss, t])
                            lhs.addTerms(-data.passenger[str(ss) + '-' + str(sss)][t], chi[k - 1, ss, t])
        model.addConstr(lhs <= capacity_train, name='capacity_' + str(k) + '_' + str(s))





model.optimize()

if model.status == GRB.Status.INFEASIBLE:
    model.computeIIS()
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)
