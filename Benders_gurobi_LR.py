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
    #     coeff_x=[[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)]
        lhs=LinExpr(0)
        # for s in range(len(set_S_sh)):
        #     for k in range(num_K):
        #         for kk in range(num_K):
        #             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
        #                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
        #                     coeff_x[k][set_S_sh_before[s]][t]+=LP_y.getConstrByName('xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)).pi
        #                     coeff_x[kk][set_S_sh[s]][tt]+=LP_y.getConstrByName('xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)).pi
        # for u in range(len(U)):
        #     for tau in range(num_T):
        #         for k in range(num_K):
        #             for s in U[u]:
        #                 for t in candidate_T[str(k) + '_' + str(s)]:
        #                     coeff_x[k][s][t]+=(LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).pi * E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
        #                                   LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).pi * E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau])
        for k in range(num_K):
            for s in range(num_S):
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi_integer[k, s][t])
                    # if t + 1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                    #     lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi_integer[k, s][t])
                    #     lhs.addTerms(-list_coeff_x[p - 1][k][s][t], chi_integer[k, s][t+1])
                    # else:
                    #     lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi_integer[k, s][t])
                    # lhs.addTerms(list_coeff_x[p-1][k][s][t], x_integer[k,s][t])
        lhs.addTerms(-1, z_integer[0])
        tem = 0
        # for s in range(len(set_S_sh)):
        #     for k in range(num_K):
        #         tem += LP_y.getConstrByName('onebefore_'+str(s)+'_'+str(k)).pi
        #         tem += LP_y.getConstrByName('oneafter_'+str(s)+'_'+str(k)).pi
        RP_x_slim.addConstr(lhs >= -tem, name='obj' + '_' + str(p))
        RP_x_slim.update()
        RP_x_slim.getConstrByName('obj' + '_' + str(p)).Lazy = 1
        # RP_x_slim.cbLazy(lhs >= -tem)
        # if p>1:
        #     RP_x_slim.getConstrByName('obj' + '_' + str(p-1)).Lazy=2
            # RP_x.getAttr('Lazy', {RP_x.getConstrByName('obj' + '_' + str(p-1))})[0]=1
            # print([int(RP_x.getAttr('Lazy', {RP_x.getConstrByName('obj' + '_' + str(i))})[0]) for i in range(1, p)])
            # RP_x.getConstrByName('obj' + '_' + str(p)).Lazy=1
            # RP_x.cbLazy(lhs >= -tem)
            # print('hello')

def callBendersOptimalCuts(RP_x_slim,where):
    if where == GRB.Callback.MIPSOL:
        for cut in range(len(list_coeff_x)):
            lhs = LinExpr(0)
            for k in range(num_K):
                for s in range(num_S):
                    for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                        if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                            lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi_integer[k,s][t]-chi_integer[k,s][t+1])
                        else:
                            lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi_integer[k, s][t])
            lhs.addTerms(-1, z_integer[0])
            tem = 0
            RP_x_slim.cbLazy(lhs >= -tem)


p=0
tem_UB=0
for s in set_S_op:
    tem_UB+=sum(E_rg['0_'+str(s)+'_0'])
UB=[100]
LB=[-10000000]
epsilon=0.0001
x_value=timetable2x(data,num_S,num_T)

RP_x = Model(name="RP_x")
# x={}
# for k in range(num_K):
#     for s in range(num_S):
#         x[k,s] = RP_x.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='x_'+str(k)+"_"+str(s))
chi={}
lamda={}
for k in range(num_K):
    for s in range(num_S):
        chi[k,s] = RP_x.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='chi_'+str(k)+"_"+str(s))
        lamda[k,s] = RP_x.addVars(len(candidate_service[str(k)+'_'+str(s)]),4, lb=0.0, ub=1.0, vtype=GRB.BINARY, name='lamda_'+str(k)+"_"+str(s))

RP_x_slim = Model(name="RP_x_slim")
# x_integer={}
# for k in range(num_K):
#     for s in range(num_S):
#         x_integer[k,s]=RP_x_slim.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.BINARY, name='x_integer_'+str(k)+"_"+str(s))
chi_integer={}
for k in range(num_K):
    for s in range(num_S):
        chi_integer[k,s]=RP_x_slim.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.BINARY, name='chi_integer_'+str(k)+"_"+str(s))

z_integer=RP_x_slim.addVars(1,lb=0.0,vtype=GRB.CONTINUOUS,name='z_integer')

RP_x_slim.setObjective(z_integer[0], GRB.MAXIMIZE)



# RP_x.setObjective(lhs, GRB.MAXIMIZE)
# lhs = LinExpr(0)
# # lhs.addTerms(1, z[0])
# for k in range(num_K):
#     for s in range(num_S):
#         for t in candidate_T[str(k) + '_' + str(s)]:
#             lhs.addTerms(0, x[k, s, t])
# RP_x.setObjective(lhs, GRB.MAXIMIZE)

RP_x_slim.addConstr(z_integer[0]<=UB[0])

# Con(1) unique
# for k in range(num_K):
#     for s in range(num_S):
#         lhs = LinExpr(0)
#         for t in range(len(candidate_T[str(k) + '_' + str(s)])):
#             lhs.addTerms(1, x[k,s][t])
#         RP_x.addConstr(lhs == 1, name='unique_' + str(k) + '_' + str(s))
for k in range(num_K):
    for s in range(num_S):
        RP_x.addConstr(chi[k,s][0] == 1, name='unique_' + str(k) + '_' + str(s))

for k in range(num_K):
    for s in range(num_S):
        for t in range(1,len(candidate_T[str(k) + '_' + str(s)])):
            RP_x.addConstr(chi[k, s][t-1] >= chi[k, s][t], name='u' + str(k) + '_' + str(s))


# Con(2c)
# for k in range(num_K):
#     for s in set_S_op:
#         for t in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
#             lhs = LinExpr(0)
#             for ttt in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
#                 if ttt >= t:
#                     lhs.addTerms(1, x[k,s - 1][ttt])
#             for tt in range(len(candidate_T[str(k) + '_' + str(s)])):
#                 if candidate_T[str(k) + '_' + str(s)][tt] >= candidate_T[str(k) + '_' + str(s - 1)][t] + data.travel[s - 1] + dwell_lower:
#                     lhs.addTerms(-1, x[k,s][tt])
#             RP_x.addConstr(lhs <= 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))

for k in range(num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
            tt=max(0,candidate_T[str(k) + '_' + str(s - 1)][t] + data.travel[
                s - 1] + dwell_lower-candidate_T[str(k) + '_' + str(s)][0])
            if tt<len(candidate_T[str(k) + '_' + str(s)]):
                RP_x.addConstr(chi[k,s-1][t]-chi[k,s][tt]<=0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x.addConstr(chi[k, s - 1][t] == 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))


# Con(3c)
# for k in range(1, num_K):
#     for s in set_S_op:
#         for t in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
#             lhs = LinExpr(0)
#             for ttt in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
#                 if ttt >= t:
#                     lhs.addTerms(1, x[k - 1,s][ttt])
#             for tt in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
#                 if candidate_T[str(k) + '_' + str(s - 1)][tt] + data.travel[s - 1] - candidate_T[str(k - 1) + '_' + str(s)][t] >= headway_lower:
#                     lhs.addTerms(-1, x[k,s - 1][tt])
#             RP_x.addConstr(lhs <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))

for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
            tt = max(0,candidate_T[str(k-1) + '_' + str(s)][t] - data.travel[
                s-1] + headway_lower - candidate_T[str(k) + '_' + str(s-1)][0])
            if tt < len(candidate_T[str(k) + '_' + str(s-1)]):
                RP_x.addConstr(chi[k-1, s][t] - chi[k,s-1][tt] <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x.addConstr(chi[k - 1, s][t] == 0,name='3c_' + str(k) + '_' + str(s) + '_' + str(t))


# Con(4c)
# for k in range(1, num_K):
#     for s in set_S_op:
#         for t in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
#             lhs = LinExpr(0)
#             for ttt in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
#                 if ttt <= t:
#                     lhs.addTerms(1, x[k - 1,s][ttt])
#             for tt in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
#                 if candidate_T[str(k) + '_' + str(s - 1)][tt] + data.travel[s - 1] - candidate_T[str(k - 1) + '_' + str(s)][t] <= headway_upper:
#                     lhs.addTerms(-1, x[k,s - 1][tt])
#             RP_x.addConstr(lhs <= 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s-1)])):
            tt = max(0,candidate_T[str(k) + '_' + str(s-1)][t] + data.travel[
                s-1] - headway_upper - candidate_T[str(k-1) + '_' + str(s)][0])
            if tt < len(candidate_T[str(k-1) + '_' + str(s)]):
                RP_x.addConstr(chi[k, s-1][t] - chi[k-1,s][tt] <= 0,
                               name='4c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x.addConstr(chi[k, s-1][t] == 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))


# Con(1) unique_slim
for k in range(num_K):
    for s in range(num_S):
        RP_x_slim.addConstr(chi_integer[k,s][0] == 1, name='unique_' + str(k) + '_' + str(s))

for k in range(num_K):
    for s in range(num_S):
        for t in range(1,len(candidate_T[str(k) + '_' + str(s)])):
            RP_x_slim.addConstr(chi_integer[k, s][t-1] >= chi_integer[k, s][t], name='u' + str(k) + '_' + str(s))

# Con(2c)_slim
for k in range(num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
            tt=max(0,candidate_T[str(k) + '_' + str(s - 1)][t] + data.travel[
                s - 1] + dwell_lower-candidate_T[str(k) + '_' + str(s)][0])
            if tt<len(candidate_T[str(k) + '_' + str(s)]):
                RP_x_slim.addConstr(chi_integer[k,s-1][t]-chi_integer[k,s][tt] <= 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_slim.addConstr(chi_integer[k, s - 1][t] == 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))

# Con(3c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
            tt = max(0,candidate_T[str(k-1) + '_' + str(s)][t] - data.travel[
                s-1] + headway_lower - candidate_T[str(k) + '_' + str(s-1)][0])
            if tt < len(candidate_T[str(k) + '_' + str(s-1)]):
                RP_x_slim.addConstr(chi_integer[k-1, s][t] - chi_integer[k,s-1][tt] <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_slim.addConstr(chi_integer[k - 1, s][t] == 0,name='3c_' + str(k) + '_' + str(s) + '_' + str(t))

# Con(4c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s-1)])):
            tt = max(0,candidate_T[str(k) + '_' + str(s-1)][t] + data.travel[
                s-1] - headway_upper - candidate_T[str(k-1) + '_' + str(s)][0])
            if tt < len(candidate_T[str(k-1) + '_' + str(s)]):
                RP_x_slim.addConstr(chi_integer[k, s-1][t] - chi_integer[k-1,s][tt] <= 0,
                               name='4c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_slim.addConstr(chi_integer[k, s-1][t] == 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))




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
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
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
# RP_x_slim.Params.LogToConsole = False
RP_x_slim.Params.lazyConstraints = 1
# RP_x_slim.setParam('VarBranch', 0)
# LP_y.Params.LogToConsole = False
LP_E.Params.LogToConsole = False
list_coeff_x=[]
multiper = []
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
                        for t in range(len(candidate_T[str(k) + '_' + str(s)])):
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
        # if LP_E.status == GRB.Status.INFEASIBLE:
        #     print('Optimization was stopped with status %d' % LP_E.status)
        #     # do IIS, find infeasible constraints
        #     LP_E.computeIIS()
        #     for c in LP_E.getConstrs():
        #         if c.IISConstr:
        #             print('%s' % c.constrName)
        #             print(E_tr_x[3][38])
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

    list_coeff_x.append([[[0 for t in range(len(candidate_T[str(k) + '_' + str(s)]))] for s in range(num_S)] for k in range(num_K)])
    for u in range(len(U)):
        for tau in range(num_T):
            for k in range(num_K):
                for s in U[u]:
                    for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                        list_coeff_x[p - 1][k][s][t] += (
                                LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).pi *
                                E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
                                LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).pi *
                                E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau])
                        if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                            list_coeff_x[p - 1][k][s][t+1] -= (
                                    LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).pi *
                                    E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
                                    LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).pi *
                                    E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau])
    #RP_x的相关准备：改目标函数
    if p==1:
        lhs = LinExpr(0)
        for k in range(num_K):
            for s in range(num_S):
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    lhs.addTerms(list_coeff_x[p - 1][k][s][t], chi[k,s][t])
        RP_x.setObjective(lhs, GRB.MAXIMIZE)
    else:
        for k in range(num_K):
            for s in range(num_S):
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    RP_x.getVarByName('chi_' + str(k) + '_' + str(s) + '[' + str(t) + ']').obj += list_coeff_x[p-1][k][s][t]

    #RP_x_slim的相关准备：加约束
    addBendersOptimalCuts()

    if p % segment ==0:
        RP_x_slim.optimize()
        new_UB =RP_x_slim.ObjVal
    else:
        RP_x.optimize()
        new_UB=RP_x.ObjVal/p



    # new_UB=UB[0]
    # for cut in range(len(list_coeff_x)):
    #     tem_sum = 0
    #     for k in range(num_K):
    #         for s in range(num_S):
    #             for t in candidate_T[str(k) + '_' + str(s)]:
    #                 tem_sum += list_coeff_x[p - 1][k][s][t] * RP_x.getVarByName(
    #                     'x[' + str(k) + ',' + str(s) + ',' + str(t) + ']').x
    #     new_UB = min(new_UB, tem_sum)
    # UB_1=new_UB


    UB.append(min(UB[p-1],new_UB))
    x_value=[[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)]
    # UB.append(min(UB[p - 1], UB_1))
    if p % segment ==0:
        for k in range(num_K):
            for s in range(num_S):
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    x_value[k][s][t]=chi_integer[k,s][t].x
                    if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                        x_value[k][s][t] -= chi_integer[k, s][t+1].x
    else:
        for k in range(num_K):
            for s in range(num_S):
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    x_value[k][s][t]=chi[k,s][t].x
                    if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                        x_value[k][s][t] -= chi[k, s][t+1].x

    timetable=x2timetable(x_value, num_S, num_K, num_T,candidate_T)
    print(p,LB[p],UB[p],abs((UB[p] - LB[p])/UB[p]), LB_1+LB_2,RP_x.ObjVal/p)
    # print(p, LB[p], UB[p], abs((UB[p] - LB[p]) / UB[p]), LB_1 + LB_2, UB_1)
    # print('hello')
time_2 = datetime.datetime.now()
print(time_2-time_1)
for k in range(num_K):
    for s in range(num_S):
        print(x_value[k][s])



















# ##################################LR，失败
# # 开始LR
# # 将新约束添加进list中
# list_coeff_x.append([[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)])
# for u in range(len(U)):
#     for tau in range(num_T):
#         for k in range(num_K):
#             for s in U[u]:
#                 for t in candidate_T[str(k) + '_' + str(s)]:
#                     list_coeff_x[p - 1][k][s][t] += (LP_E.getConstrByName('nettr_' + str(u) + '_' + str(tau)).pi *
#                                                      E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
#                                                      LP_E.getConstrByName('netrg_' + str(u) + '_' + str(tau)).pi *
#                                                      E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau])
# multiper.append(0)
# # 先计算步长和次梯度（旧约束必定满足了，只检验新约束）
# LR_p = 0
# index_feasible = 0
# coeff_z = -1
# UB_1 = 0
# # bt = tem_UB
# while index_feasible == 0:
#     index_feasible = 1
#     LR_p += 1
#     coeff_z = 0
#     step = 1 / LR_p
#     step_distance = 0.0
#
#     if LR_p == 1:
#         # 新加的cut是可以帮助求解的，因此原解不能满足新解，否则benders不能收敛
#         index_feasible = 0
#         tem_sum = 0
#         for k in range(num_K):
#             for s in range(num_S):
#                 for t in candidate_T[str(k) + '_' + str(s)]:
#                     tem_sum += list_coeff_x[p - 1][k][s][t] * RP_x.getVarByName(
#                         'x[' + str(k) + ',' + str(s) + ',' + str(t) + ']').x
#         # step=((tem_UB-tem_sum)/(step_distance+(tem_sum-tem_UB)**2)**(1/2))*bt
#         multiper[p - 1] = max(0, multiper[p - 1] + step * (tem_UB - tem_sum))
#         for k in range(num_K):
#             for s in range(num_S):
#                 for t in candidate_T[str(k) + '_' + str(s)]:
#                     tem_coeff = 0
#                     for cut in range(len(list_coeff_x)):
#                         tem_coeff += multiper[cut] * list_coeff_x[cut][k][s][t]
#                     RP_x.getVarByName('x[' + str(k) + ',' + str(s) + ',' + str(t) + ']').obj = tem_coeff
#         RP_x.getVarByName('z[0]').obj = 1 - sum(multiper)
#         RP_x.optimize()
#         UB_1 = RP_x.getVarByName('z[0]').x
#         if RP_x.ObjVal < last_RP_obj:
#             bt = 0
#         else:
#             bt = 0.02
#         last_RP_obj = RP_x.ObjVal
#     else:
#         # 考虑新cut后解发生变动，这时候需要检测已有约束的状态，并考虑是否需要求解
#         new_lb_LR = tem_UB
#         subgradient = [0 for cut in range(len(list_coeff_x))]
#         step_distance = 0
#         for cut in range(len(list_coeff_x)):
#             tem_sum = 0
#             for k in range(num_K):
#                 for s in range(num_S):
#                     for t in candidate_T[str(k) + '_' + str(s)]:
#                         tem_sum += list_coeff_x[p - 1][k][s][t] * RP_x.getVarByName(
#                             'x[' + str(k) + ',' + str(s) + ',' + str(t) + ']').x
#             new_lb_LR = min(new_lb_LR, tem_sum)
#             subgradient[cut] = RP_x.getVarByName('z[0]').x - tem_sum
#             step_distance += (tem_sum - RP_x.getVarByName('z[0]').x) ** 2
#         if step_distance == 0:
#             index_feasible = 1
#         else:
#             # step = ((UB_1 - new_lb_LR) / (step_distance**(1/2))) * bt
#             for cut in range(len(list_coeff_x)):
#                 multiper[cut] = max(0, multiper[cut] + step * subgradient[cut])
#             for k in range(num_K):
#                 for s in range(num_S):
#                     for t in candidate_T[str(k) + '_' + str(s)]:
#                         tem_coeff = 0
#                         for cut in range(len(list_coeff_x)):
#                             tem_coeff += multiper[cut] * list_coeff_x[cut][k][s][t]
#                         RP_x.getVarByName('x[' + str(k) + ',' + str(s) + ',' + str(t) + ']').obj = tem_coeff
#             RP_x.getVarByName('z[0]').obj = 1 - sum(multiper)
#             if abs(RP_x.getVarByName('z[0]').x - new_lb_LR) > 0.0001:
#                 # print(RP_x.ObjVal, new_lb_LR)
#                 index_feasible = 0
#                 RP_x.optimize()
#                 UB_1 = min(UB_1, RP_x.ObjVal)
#                 # if RP_x.ObjVal < last_RP_obj:
#                 #     bt = 0
#                 # else:
#                 #     bt = 0.02
#                 last_RP_obj = RP_x.ObjVal
#             else:
#                 index_feasible = 1