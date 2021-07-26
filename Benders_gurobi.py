#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/26 15:10
#@Author: Pengli Mo
#@File  : Benders_gurobi.py#!/usr/bin/env python

from gurobipy import *
from data_input import *
from function_list import *
import datetime

def addBendersOptimalCuts():
                # (RP_x,where):
    # if where == GRB.Callback.MIPSOL:
        coeff_x=[[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)]
        lhs=LinExpr(0)
        # for s in range(len(set_S_sh)):
        #     for k in range(num_K):
        #         for kk in range(num_K):
        #             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
        #                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
        #                     coeff_x[k][set_S_sh_before[s]][t]+=LP_y.getConstrByName('xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)).pi
        #                     coeff_x[kk][set_S_sh[s]][tt]+=LP_y.getConstrByName('xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)).pi
        for u in range(len(U)):
            for tau in range(num_T):
                for k in range(num_K):
                    for s in U[u]:
                        for t in candidate_T[str(k) + '_' + str(s)]:
                            coeff_x[k][s][t]+=(LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).pi * E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
                                          LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).pi * E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau])
        for k in range(num_K):
            for s in range(num_S):
                for t in range(num_T):
                    lhs.addTerms(coeff_x[k][s][t], x[k,s,t])
        lhs.addTerms(-1, z[0])
        tem = 0
        # for s in range(len(set_S_sh)):
        #     for k in range(num_K):
        #         tem += LP_y.getConstrByName('onebefore_'+str(s)+'_'+str(k)).pi
        #         tem += LP_y.getConstrByName('oneafter_'+str(s)+'_'+str(k)).pi
        RP_x.addConstr(lhs >= -tem, name='obj' + '_' + str(p))
        if p>1:
            RP_x.getConstrByName('obj' + '_' + str(p-1)).Lazy=2
            # RP_x.getAttr('Lazy', {RP_x.getConstrByName('obj' + '_' + str(p-1))})[0]=1
            # print([int(RP_x.getAttr('Lazy', {RP_x.getConstrByName('obj' + '_' + str(i))})[0]) for i in range(1, p)])
            # RP_x.getConstrByName('obj' + '_' + str(p)).Lazy=1
            # RP_x.cbLazy(lhs >= -tem)
            # print('hello')


p=0
UB=[10000000]
LB=[-10000000]
epsilon=0.0001
x_value=timetable2x(data,num_S,num_T)

RP_x = Model(name="RP_x")
x = RP_x.addVars(num_K, num_S, num_T, lb=0.0, ub=1.0, vtype=GRB.BINARY, name='x')
z = RP_x.addVars(1,lb=-GRB.INFINITY,vtype=GRB.CONTINUOUS,name='z')
RP_x.setObjective(z[0], GRB.MAXIMIZE)

# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        lhs = LinExpr(0)
        # for t in candidate_T[str(k) + '_' + str(s)]:
        for t in range(num_T):
            lhs.addTerms(1, x[k, s, t])
        RP_x.addConstr(lhs == 1, name='unique_' + str(k) + '_' + str(s))

# Con(2c)
for k in range(num_K):
    for s in set_S_op:
        for t in candidate_T[str(k) + '_' + str(s - 1)]:
            lhs = LinExpr(0)
            for ttt in candidate_T[str(k) + '_' + str(s - 1)]:
                if ttt >= t:
                    lhs.addTerms(1, x[k, s - 1, ttt])
            for tt in candidate_T[str(k) + '_' + str(s)]:
                if tt >= t + data.travel[s - 1] + dwell_lower:
                    lhs.addTerms(-1, x[k, s, tt])
            RP_x.addConstr(lhs <= 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))

# Con(3c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in candidate_T[str(k - 1) + '_' + str(s)]:
            lhs = LinExpr(0)
            for ttt in candidate_T[str(k - 1) + '_' + str(s)]:
                if ttt >= t:
                    lhs.addTerms(1, x[k - 1, s, ttt])
            for tt in candidate_T[str(k) + '_' + str(s - 1)]:
                if tt + data.travel[s - 1] - t >= headway_lower:
                    lhs.addTerms(-1, x[k, s - 1, tt])
            RP_x.addConstr(lhs <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))

# Con(4c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in candidate_T[str(k - 1) + '_' + str(s)]:
            lhs = LinExpr(0)
            for ttt in candidate_T[str(k - 1) + '_' + str(s)]:
                if ttt >= t:
                    lhs.addTerms(1, x[k - 1, s, ttt])
            for tt in candidate_T[str(k) + '_' + str(s - 1)]:
                if tt + data.travel[s - 1] - t <= headway_upper:
                    lhs.addTerms(-1, x[k, s - 1, tt])
            RP_x.addConstr(lhs <= 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))



LP_E = Model(name="LP_E")
E = LP_E.addVars(len(U), num_T, lb=-GRB.INFINITY, vtype=GRB.CONTINUOUS, name='E')

obj = LinExpr(0)
for u in range(len(U)):
    for t in range(num_T):
        obj.addTerms(1, E[u, t])
LP_E.setObjective(obj, GRB.MAXIMIZE)

E_tr_x = [[0 for tau in range(num_T)] for u in range(len(U))]
E_rg_x = [[0 for tau in range(num_T)] for u in range(len(U))]
for u in range(len(U)):
    for tau in range(num_T):
        for k in range(num_K):
            for s in U[u]:
                for t in candidate_T[str(k) + '_' + str(s)]:
                    E_tr_x[u][tau] += E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] * x_value[k][s][t]
                    E_rg_x[u][tau] += E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau] * x_value[k][s][t]

# Con(6) nettr
for u in range(num_U):
    for tau in range(num_T):
        LP_E.addConstr(E[u, tau] <= E_tr_x[u][tau], name='nettr_' + str(u) + '_' + str(tau))

# Con(7) netrg
for u in range(num_U):
    for tau in range(num_T):
        LP_E.addConstr(E[u, tau] <= E_rg_x[u][tau], name='netrg_' + str(u) + '_' + str(tau))


# LP_y = Model(name="LP_y")
# y = LP_y.addVars(len(set_S_sh), num_K + 1, num_K + 1, num_T, num_T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='y')
# obj = LinExpr(0)
# for s in range(len(set_S_sh)):
#     for k in range(num_K+1):
#         for kk in range(num_K+1):
#             for t in range(num_T):
#                 for tt in range(num_T):
#                     obj.addTerms(-eff_rolling[str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)],
#                                  y[s, k, kk, t, tt])
# LP_y.setObjective(obj, GRB.MAXIMIZE)
#
# # Con(8) onebefore
# for s in range(len(set_S_sh)):
#     for k in range(num_K):
#         lhs = LinExpr(0)
#         for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#             for kk in range(num_K + 1):
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     lhs.addTerms(1, y[s, k, kk, t, tt])
#         LP_y.addConstr(lhs == 1, name='onebefore_' + str(s) + '_' + str(k))
#
# # Con(9) oneafter
# for s in range(len(set_S_sh)):
#     for kk in range(num_K):
#         lhs = LinExpr(0)
#         for k in range(num_K + 1):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     lhs.addTerms(1, y[s, k, kk, t, tt])
#         LP_y.addConstr(lhs == 1, name='oneafter_' + str(s) + '_' + str(kk))
#
# # Con(10) xbefore
# for s in range(len(set_S_sh)):
#     for k in range(num_K):
#         for kk in range(num_K + 1):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     LP_y.addConstr(y[s, k, kk, t, tt] <= x_value[k][set_S_sh_before[s]][t],
#                                     name='xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
#                                         t) + '_' + str(tt))
# #
# # # Con(11) xafter
# for s in range(len(set_S_sh)):
#     for k in range(num_K + 1):
#         for kk in range(num_K):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     LP_y.addConstr(y[s, k, kk, t, tt]<= x_value[kk][set_S_sh[s]][tt],
#                                     name='xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
#                                         t) + '_' + str(tt))

RP_x.Params.LogToConsole = False
RP_x.Params.lazyConstraints = 1
# LP_y.Params.LogToConsole = False
LP_E.Params.LogToConsole = False

time_1 = datetime.datetime.now()
while abs((UB[p] - LB[p])/UB[p])>=epsilon:
    # and p<=100:
    p+=1
    if p == 1:
        LP_E.optimize()
        # LP_y.optimize()
    else:
        E_tr_x = [[0 for tau in range(num_T)] for u in range(len(U))]
        E_rg_x = [[0 for tau in range(num_T)] for u in range(len(U))]
        for u in range(len(U)):
            for tau in range(num_T):
                for k in range(num_K):
                    for s in U[u]:
                        for t in candidate_T[str(k) + '_' + str(s)]:
                            E_tr_x[u][tau] += E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] * x_value[k][s][t]
                            E_rg_x[u][tau] += E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau] * x_value[k][s][t]
                # if E_tr_x[u][tau] < 0:
                #     print('error')
        # print(E_tr_x[3][38])
        for u in range(num_U):
            for tau in range(num_T):
                # print(LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)))
                LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).rhs = E_tr_x[u][tau]
                LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).rhs = E_rg_x[u][tau]
        LP_E.optimize()
        if LP_E.status == GRB.Status.INFEASIBLE:
            print('Optimization was stopped with status %d' % LP_E.status)
            # do IIS, find infeasible constraints
            LP_E.computeIIS()
            for c in LP_E.getConstrs():
                if c.IISConstr:
                    print('%s' % c.constrName)
                    print(E_tr_x[3][38])
        # for s in range(len(set_S_sh)):
        #     for k in range(num_K):
        #         for kk in range(num_K):
        #             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
        #                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
        #                     LP_y.getConstrByName('xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
        #                         t) + '_' + str(tt)).rhs = x_value[k][set_S_sh_before[s]][t]
        #                     LP_y.getConstrByName('xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
        #                         t) + '_' + str(tt)).rhs = x_value[kk][set_S_sh[s]][tt]
        # LP_y.optimize()

    # LB_1=LP_y.Objval
    LB_1=0
    LB_2=LP_E.Objval
    LB.append(max(LB[p - 1], LB_1 + LB_2))

    addBendersOptimalCuts()
    RP_x.optimize()
    UB_1=RP_x.ObjVal

    UB.append(min(UB[p-1],UB_1))
    for k in range(num_K):
        for s in range(num_S):
            for t in range(num_T):
                x_value[k][s][t]=x[k,s,t].x
    # timetable=x2timetable(x, num_S, num_K, num_T)
    print(p, LB_1+LB_2,UB_1,LB[p],UB[p],abs((UB[p] - LB[p])/UB[p]))
    # print('hello')
time_2 = datetime.datetime.now()
print(time_2-time_1)

