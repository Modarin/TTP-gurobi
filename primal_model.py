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
x = model.addVars(num_K, num_S, num_T, vtype=GRB.BINARY, name='x')
lamda = model.addVars(num_K, num_S, num_K, num_S, lb=0, vtype=GRB.BINARY, name='lamda')
delta = model.addVars(num_K, num_S, num_K, num_S, vtype=GRB.CONTINUOUS, name='delta')

# 目标函数
obj = LinExpr(0)
# for u in range(len(U)):
#     for t in range(num_T):
#         obj.addTerms(1,E[u,t])
# for s in range(len(set_S_sh)):
#     for k in range(num_K+1):
#         for kk in range(num_K+1):
#             if k != num_K+1 or kk!= num_K+1:
#                 for t in range(num_T):
#                     for tt in range(num_T):
#                         obj.addTerms(-eff_rolling[str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)], y[s, k, kk ,t, tt])
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
        # for kk in range(num_K):
        #     for ss in range(num_S):
            obj.addTerms(1, delta[k,s,kk,ss])
model.setObjective(obj, GRB.MAXIMIZE)

# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        lhs=LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k)+'_'+str(s)]:
            lhs.addTerms(1,x[k,s,t])
        model.addConstr(lhs==1, name='unique_'+str(k)+'_'+str(s))

# Con(2) dwell
for k in range(num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k)+'_'+str(s)]:
            lhs.addTerms(t, x[k,s,t])
        for t in candidate_T[str(k) + '_' + str(s-1)]:
            lhs.addTerms(-t, x[k, s-1, t])
        model.addConstr(lhs >= dwell_lower+data.travel[s-1], name='dwell_' + str(k) + '_' + str(s))
# Con(3) Lheadway
for k in range(1,num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k) + '_' + str(s-1)]:
            lhs.addTerms(t, x[k,s-1,t])
        for t in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-t, x[k-1, s, t])
        model.addConstr(lhs >= headway_lower - data.travel[s - 1], name='Lheadway_' + str(k) + '_' + str(s))
# Con(4) Uheadway
for k in range(1,num_K):
    for s in set_S_op:
        lhs = LinExpr(0)
        # for t in range(num_T):
        for t in candidate_T[str(k) + '_' + str(s-1)]:
            lhs.addTerms(t, x[k,s-1,t])
        for t in candidate_T[str(k-1) + '_' + str(s)]:
            lhs.addTerms(-t, x[k-1, s, t])
        model.addConstr(lhs <= headway_upper - data.travel[s - 1], name='Uheadway_' + str(k) + '_' + str(s))

# # Con(6) nettr
# for u in range(num_U):
#     for tau in range(num_T):
#         lhs=LinExpr(0)
#         lhs.addTerms(1,E[u,tau])
#         for k in range(num_K):
#             for s in U[u]:
#                 # for t in range(num_T):
#                 for t in candidate_T[str(k) + '_' + str(s)]:
#                     lhs.addTerms(-E_tr[str(k)+'_'+str(s)+'_'+str(t-candidate_T[str(k) + '_' + str(s)][0])][tau],x[k,s,t])
#         model.addConstr(lhs<=0,name='nettr_'+str(u)+'_'+str(tau))
#
# # Con(7) netrg
# for u in range(num_U):
#     for tau in range(num_T):
#         lhs=LinExpr(0)
#         lhs.addTerms(1,E[u,tau])
#         for k in range(num_K):
#             for s in U[u]:
#                 # for t in range(num_T):
#                 for t in candidate_T[str(k) + '_' + str(s)]:
#                     lhs.addTerms(-E_rg[str(k)+'_'+str(s)+'_'+str(t-candidate_T[str(k) + '_' + str(s)][0])][tau],x[k,s,t])
#         model.addConstr(lhs<=0,name='netrg_'+str(u)+'_'+str(tau))

for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
        # for kk in range(num_K):
        #     for ss in range(num_S):
            model.addConstr(delta[k,s,kk,ss]>=0)

            lhs = LinExpr(0)
            lhs.addTerms(1,delta[k, s, kk, ss])
            lhs.addTerms(-min(data.D_tr[ss],data.D_br[s]), lamda[k,s,kk,ss])
            model.addConstr(lhs <= 0)

            lhs2 = LinExpr(0)
            lhs2.addTerms(1, delta[k, s, kk, ss])
            for tt in candidate_T[str(kk)+'_'+str(ss)]:
                lhs2.addTerms(-tt, x[kk, ss, tt])
            for t in candidate_T[str(k)+'_'+str(s)]:
                lhs2.addTerms(t, x[k, s, t])
            lhs2.addTerms(num_T, lamda[k, s, kk, ss])
            model.addConstr(lhs2 <= data.D_tr[ss]-data.travel[s]+data.D_br[s]+num_T)

            lhs3 = LinExpr(0)
            lhs3.addTerms(1, delta[k, s, kk, ss])
            for tt in candidate_T[str(kk)+'_'+str(ss)]:
                lhs3.addTerms(tt, x[kk, ss, tt])
            for t in candidate_T[str(k)+'_'+str(s)]:
                lhs3.addTerms(-t, x[k, s, t])
            lhs3.addTerms(num_T, lamda[k, s, kk, ss])
            model.addConstr(lhs3 <= data.travel[s] + num_T)

# # Con(8) onebefore
# for s in range(len(set_S_sh)):
#     for k in range(num_K):
#         lhs = LinExpr(0)
#         # for t in range(num_T):
#         for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#             for kk in range(num_K+1):
#                 # for tt in range(num_T):
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     lhs.addTerms(1, y[s,k,kk,t,tt])
#         model.addConstr(lhs==1, name='onebefore_'+str(s)+'_'+str(k))
#
# # Con(9) oneafter
# for s in range(len(set_S_sh)):
#     for kk in range(num_K):
#         lhs = LinExpr(0)
#         for k in range(num_K + 1):
#             # for t in range(num_T):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 # for tt in range(num_T):
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     lhs.addTerms(1, y[s, k, kk, t, tt])
#         model.addConstr(lhs == 1, name='oneafter_' + str(s) + '_' + str(kk))
#
# # Con(10) xbefore
# for s in range(len(set_S_sh)):
#     for k in range(num_K):
#         for kk in range(num_K+1):
#             # for t in range(num_T):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 # for tt in range(num_T):
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     model.addConstr(y[s,k,kk,t,tt]-x[k,set_S_sh_before[s],t]<=0, name='xbefore_'+str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)+'_')
#
#
# # Con(11) xafter
# for s in range(len(set_S_sh)):
#     for k in range(num_K+1):
#         for kk in range(num_K):
#             # for t in range(num_T):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 # for tt in range(num_T):
#                 for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     model.addConstr(y[s,k,kk,t,tt]-x[kk,set_S_sh[s],tt]<=0, name='xafter_'+str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)+'_')

model.optimize()
x_value=[[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)]
for k in range(num_K):
    for s in range(num_S):
        for t in candidate_T[str(k) + '_' + str(s)]:
            x_value[k][s][t] = x[k, s,t].x

timetable = x2timetable(x_value, num_S, num_K, num_T, candidate_T)
lamda_value=[[[[0 for ss in range(num_S)] for kk in range(num_K)] for s in range(num_S)] for k in range(num_K)]
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k) + '_' + str(s)]:
            kk = service[0]
            ss = service[1]
            if lamda[k,s,kk,ss].x>0.1:
                print(k,s,kk,ss,timetable[k][s]+data.travel[s]-data.D_br[s],timetable[k][s]+data.travel[s],timetable[kk][ss],timetable[kk][ss]+data.D_tr[ss],delta[k,s,kk,ss].x)
                # lamda_value[k][s][kk][ss]=lamda[k,s,kk,ss].x
for k in range(num_K):
    print(timetable[k])
print('hello')
# obj = []
# for s in set_s:
#     for ss in set_s:
#         for j in set_i:
#             obj.append(delta[s, ss, j])
# model.setObjective(quicksum(obj), GRB.MINIMIZE)
#
# # 约束（10），旅行时间约束，包含两个约束
# for s in set_s:
#     for v in solution[s]:
#         for r in range(len(v.route) + 1):
#             if r == 0:
#                 tem_node = v.route[r]
#                 model.addConstr(a[s, tem_node] <= (max_work_time - A[str(tem_node) + '-0'].travel))
#                 model.addConstr(a[s, tem_node] >= A['0-' + str(tem_node)].travel)
#             elif r == len(v.route):
#                 tem_node = v.route[r - 1]
#                 model.addConstr(a[s, tem_node] <= (max_work_time - A[str(tem_node) + '-0'].travel))
#                 model.addConstr(a[s, tem_node] >= A['0-' + str(tem_node)].travel)
#             else:
#                 node_before = v.route[r - 1]
#                 tem_node = v.route[r]
#                 model.addConstr((a[s, tem_node] - a[s, node_before] <= max_work_time - A[
#                     '0-' + str(node_before)].travel - A[str(tem_node) + '-0'].travel))
#                 model.addConstr(
#                     (a[s, tem_node] - a[s, node_before] >= A[str(node_before) + '-' + str(tem_node)].travel))
# # 约束（12）
# for i in range(1, num_node):
#     for s in range(num_scenarios):
#         for ss in range(num_scenarios):
#             model.addConstr((a[s, i] - a[ss, i]) <= (time_window_width + max_work_time * delta[s, ss, i]))
#             model.addConstr((a[s, i] - a[ss, i]) >= (-time_window_width - max_work_time * delta[s, ss, i]))
#
# # model.setParam('OutputFlag', 0)
# model.optimize()
#
# if model.status == GRB.OPTIMAL:
#     infeasible_request = []
#     feasible_objective = model.objVal
#     delta_value = [[[0 for i in set_i] for ss in set_s] for s in set_s]
#     for s in set_s:
#         for ss in set_s:
#             for i in set_i:
#                 delta_value[s][ss][i] = model.getVarByName("delta[" + str(s) + ',' + str(ss) + ',' + str(i) + ']').x
#                 if delta_value[s][ss][i] >= 0.9:
#                     if i not in infeasible_request:
#                         infeasible_request.append(i)
# else:
#     infeasible_request = []
#     feasible_objective = num_customers