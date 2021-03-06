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
        for tt in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-tt, x[k-1, s, tt])
        model.addConstr(lhs >= headway_lower, name='Lheadway_' + str(k) + '_' + str(s))

# Con(4) Uheadway
for k in range(1,num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k) + '_' + str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for tt in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-tt, x[k-1, s, tt])
        model.addConstr(lhs <= headway_upper, name='Uheadway_' + str(k) + '_' + str(s))

# Con(2) dwell
for k in range(num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k)+'_'+str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for tt in candidate_T[str(k) + '_' + str(s-1)]:
            lhs.addTerms(-tt, x[k, s-1, tt])
        model.addConstr(lhs == data.dwell[s-1]+data.travel[s-1], name='dwell_' + str(k) + '_' + str(s))

for k in range(num_K):
    for s in set_S_over:
        for t in range(num_T):
            lhs = LinExpr(0)
            for tt in range(num_T):
                if tt>=t:
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

# 目标函数
obj=QuadExpr(0)

for k in range(num_K):
    for s in range(num_S):
        for t in candidate_T[str(k)+'_'+str(s)]:
            p = 0
            for tt in range(t + 1):
                for ss in range(s + 1, num_S):
                    if str(s) + '-' + str(ss) in data.passenger:
                        p += data.passenger[str(s) + '-' + str(ss)][tt]
                obj.add(chi[k,s,t],p)
                if k>0:
                    obj.add(chi[k,s,t]*chi[k-1,s,tt],-p)

model.setObjective(obj, GRB.MINIMIZE)


model.optimize()

for k in range(num_K):
    print(candidate_T[str(k)+'_'+str(0)], [x[k,0,t].x for t in candidate_T[str(k)+'_'+str(0)]])
    # print(candidate_T[str(k) + '_' + str(0)], [chi[k, 0, t].x for t in range(num_T)])

if model.status == GRB.Status.INFEASIBLE:
    model.computeIIS()
    for c in model.getConstrs():
        if c.IISConstr:
            print('%s' % c.constrName)

tem_wait=0
tem_p=0

for s in range(num_S):
    p = [0 for t in range(num_T)]
    for t in range(candidate_T[str(0) + '_' + str(s)][0] + 1):
        for ss in range(s + 1, num_S):
            for tt in range(t+1):
                if str(s) + '-' + str(ss) in data.passenger:
                    p[t] += data.passenger[str(s) + '-' + str(ss)][tt]
                    # tem_p += data.passenger[str(s) + '-' + str(ss)][t]
        tem_wait+=chi[0,s,t].x*p[t]
for k in range(1,num_K):
    for s in range(num_S):
        p = [0 for t in range(num_T)]
        for t in range(candidate_T[str(k-1) + '_' + str(s)][0]+1,candidate_T[str(k) + '_' + str(s)][0]+1):
            for ss in range(s + 1, num_S):
                for tt in range(candidate_T[str(k-1) + '_' + str(s)][0]+1,t + 1):
                    if str(s) + '-' + str(ss) in data.passenger:
                        p[t] += data.passenger[str(s) + '-' + str(ss)][tt]
                        # tem_p += data.passenger[str(s) + '-' + str(ss)][t]
            tem_wait +=chi[k,s,t].x*p[t]

    # print(p)
# for k in range(1,2):
#     for s in range(num_S):
#         for t in range(candidate_T[str(k-1) + '_' + str(s)][0]+1,candidate_T[str(k) + '_' + str(s)][0]+1):
#             p = 0
#             for tt in range(candidate_T[str(k-1) + '_' + str(s)][0]+1,t+1):
#                 for ss in range(s + 1, num_S):
#                     if str(s) + '-' + str(ss) in data.passenger:
#                         p += data.passenger[str(s) + '-' + str(ss)][tt]
#             tem_wait += chi[k, s, t].x * p
# for s in range(num_S):
#     for ss in range(s + 1, num_S):
#         for t in range(candidate_T[str(0)+'_'+str(s)][0]+1):
#             if str(s) + '-' + str(ss) in data.passenger:
#                 tem_p+=data.passenger[str(s) + '-' + str(ss)][t]
print(tem_wait)