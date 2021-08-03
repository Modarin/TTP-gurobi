#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/6/21 10:05
#@Author: Pengli Mo
#@File  : model_x.py

from gurobipy import *
from data_input import *
from function_list import *



TTLP = Model(name="TTLP")

chi={}
gamma={}
for k in range(num_K):
    chi[k] = TTLP.addVars(len(candidate_T[str(k)+'_'+str(0)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='chi_'+str(k))
    if k >0:
        gamma[k] = TTLP.addVars(len(candidate_T[str(k)+'_'+str(0)]), len(candidate_T[str(k-1)+'_'+str(0)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS,name='chi_'+str(k))


# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        TTLP.addConstr(chi[k][0] == 1, name='unique_' + str(k) + '_' + str(s))


# Con(3c)
for k in range(1, num_K):
    for t in range(len(candidate_T[str(k - 1) + '_' + str(0)])):
        tt = max(0,candidate_T[str(k-1) + '_' + str(0)][t]+ headway_lower - candidate_T[str(k) + '_' + str(0)][0])
        if tt < len(candidate_T[str(k) + '_' + str(0)]):
            TTLP.addConstr(chi[k-1][t] - chi[k][tt] <= 0, name='3c_' + str(k) + '_' + str(t))
        else:
            TTLP.addConstr(chi[k-1][t] == 0,name='3c_' + str(k) + '_' + str(t))


# Con(4c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(0)])):
            tt = max(0,candidate_T[str(k) + '_' + str(0)][t]- headway_upper - candidate_T[str(k-1) + '_' + str(0)][0])
            if tt < len(candidate_T[str(k-1) + '_' + str(0)]):
                TTLP.addConstr(chi[k][t] - chi[k-1][tt] <= 0,
                               name='4c_' + str(k) + '_' + str(t))
            else:
                TTLP.addConstr(chi[k][t] == 0, name='4c_' + str(k) + '_'  + str(t))

# Con(11c)
for k in range(0, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(0)])):
            if k > 0:
                for tt in range(len(candidate_T[str(k-1) + '_' + str(0)])):
                    TTLP.addConstr(chi[k][t] >= gamma[k][t,tt], name='11c_' + str(k) + '_' + str(t)+ '_' + str(tt))

# Con(12c)
for k in range(0, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(0)])):
            if k > 0:
                for tt in range(len(candidate_T[str(k-1) + '_' + str(0)])):
                    TTLP.addConstr(chi[k-1][tt] >= gamma[k][t,tt], name='12c_' + str(k) + '_' + str(t)+ '_' + str(tt))


obj=LinExpr(0)
tem_para=0
for k in range(num_K):
    for s in range(num_S):
        for ss in range(s+1,num_S):
            if str(s) + '-' + str(ss) in data.passenger:
                if k == 0:
                    for t in range(0,candidate_T[str(k) + '_' + str(s)][0]-candidate_T[str(k) + '_' + str(0)][0]+1):
                        for tt in range(0,t+1):
                            if tt <=candidate_T[str(k) + '_' + str(s)][0]:
                                tem_para += data.passenger[str(s) + '-' + str(ss)][tt]
                            else:
                                obj.addTerms(data.passenger[str(s) + '-' + str(ss)][tt], chi[k][tt - candidate_T[str(k) + '_' + str(s)][0]])
                else:
                    for t in range(candidate_T[str(k - 1) + '_' + str(0)][0],
                                   candidate_T[str(k) + '_' + str(0)][len(candidate_T[str(k) + '_' + str(0)]) - 1] + 1):
                        ttt = t - (candidate_T[str(k) + '_' + str(s)][0] - candidate_T[str(k) + '_' + str(0)][0]) + \
                              (candidate_T[str(k - 1) + '_' + str(s)][0] - candidate_T[str(k - 1) + '_' + str(0)][0])
                        for tt in range(candidate_T[str(k - 1) + '_' + str(0)][0],ttt+1):
                            tem_tt=tt+(candidate_T[str(k) + '_' + str(s)][0]-candidate_T[str(k) + '_' + str(0)][0])
                            if tt<candidate_T[str(k) + '_' + str(0)][0]:
                                tem_para+=data.passenger[str(s) + '-' + str(ss)][tem_tt]
                            else:
                                obj.addTerms(data.passenger[str(s) + '-' + str(ss)][tem_tt], chi[k][tt-candidate_T[str(k) + '_' + str(0)][0]])

                            if t<candidate_T[str(k) + '_' + str(0)][0] or tt<candidate_T[str(k-1) + '_' + str(0)][0]:
                                tem_para-=data.passenger[str(s) + '-' + str(ss)][tem_tt]
                            elif tt<=candidate_T[str(k-1) + '_' + str(0)][len(candidate_T[str(k-1) + '_' + str(0)])-1]:
                                obj.addTerms(data.passenger[str(s) + '-' + str(ss)][tem_tt], gamma[k][t-candidate_T[str(k) + '_' + str(0)][0],tt-candidate_T[str(k-1) + '_' + str(0)][0]])

TTLP.setObjective(obj+tem_para, GRB.MINIMIZE)
TTLP.optimize()

for k in range(num_K):
    print([chi[k][t].x for t in range(len(candidate_T[str(k)+'_'+str(0)]))])

# tem_wait=0
# for s in range(num_S):
#     for ss in range(s+1,num_S):
#         if str(s) + '-' + str(ss) in data.passenger:
#             for t in range(0, candidate_T[str(k) + '_' + str(s)][0] + 1):
#                 tem_wait+=data.passenger[str(s) + '-' + str(ss)][t]*(candidate_T[str(k) + '_' + str(s)][0] + 1-t)
# print(tem_wait)



