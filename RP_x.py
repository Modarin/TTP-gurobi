#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/25 18:52
#@Author: Pengli Mo
#@File  : RP_x.py

from gurobipy import *
from data_input import *

def RP_x(list_dual_alpha, list_dual_beta, list_dual_lambda, list_dual_mu, list_dual_omega, list_dual_chi, P,x_value):
    model = Model(name="RP_x")
    # x = model.addVars(num_K, num_S, num_T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='x')
    x = model.addVars(num_K, num_S, num_T, lb=0.0, ub=1.0, vtype=GRB.BINARY, name='x')
    z = model.addVars(1,lb=-GRB.INFINITY,vtype=GRB.CONTINUOUS,name='z')

    # obj = LinExpr(0)
    for p in range(P):
        lhs=LinExpr(0)
        for s in range(len(set_S_sh)):
            for k in range(num_K):
                for kk in range(num_K):
                    for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                        for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                            # print(alpha[s][k][kk][t][tt])
                            lhs.addTerms(list_dual_alpha[p][s][k][kk][t][tt], x[k,set_S_sh_before[s],t])
                            # print(s,k,kk,t,tt,set_S_sh[s])
                            lhs.addTerms(list_dual_beta[p][s][k][kk][t][tt], x[kk,set_S_sh[s], tt])
        for u in range(len(U)):
            for tau in range(num_T):
                for k in range(num_K):
                    for s in U[u]:
                        for t in candidate_T[str(k)+'_'+str(s)]:
                            lhs.addTerms((list_dual_lambda[p][u][tau]*E_tr[str(k)+'_'+str(s)+'_'+str(t)][tau]+list_dual_mu[p][u][tau]*E_rg[str(k)+'_'+str(s)+'_'+str(t)][tau]), x[k,s,t])
        lhs.addTerms(-1, z[0])
        tem=0
        for s in range(len(set_S_sh)):
            for k in range(num_K):
                tem += list_dual_omega[p][s][k]
                tem += list_dual_chi[p][s][k]
        model.addConstr(lhs >= -tem, name='obj'+'_'+str(p))
    # model.setObjective(obj, GRB.MAXIMIZE)
    # 目标函数
    # model.addConstr(z[0] <= -1, name='testz1')
    # model.addConstr(z[0] >= -2, name='testz2')
    # obj.addTerms(1, z[0])
    model.setObjective(z[0], GRB.MAXIMIZE)


    # Con(1) unique
    for k in range(num_K):
        for s in range(num_S):
            lhs = LinExpr(0)
            # for t in range(num_T):
            for t in candidate_T[str(k) + '_' + str(s)]:
                lhs.addTerms(1, x[k, s, t])
            model.addConstr(lhs == 1, name='unique_' + str(k) + '_' + str(s))

    # Con(2c)
    for k in range(num_K):
        for s in set_S_op:
            for t in candidate_T[str(k)+'_'+str(s-1)]:
                lhs = LinExpr(0)
                for ttt in candidate_T[str(k)+'_'+str(s-1)]:
                    if ttt>=t:
                        lhs.addTerms(1, x[k,s-1,ttt])
                for tt in candidate_T[str(k)+'_'+str(s)]:
                    if tt>=t+data.travel[s-1]+dwell_lower:
                        lhs.addTerms(-1, x[k, s, tt])
                model.addConstr(lhs<=0, name='2c_'+str(k)+'_'+str(s)+'_'+str(t))

    # Con(3c)
    for k in range(1, num_K):
        for s in set_S_op:
            for t in candidate_T[str(k-1)+'_'+str(s)]:
                lhs = LinExpr(0)
                for ttt in candidate_T[str(k-1)+'_'+str(s)]:
                    if ttt>=t:
                        lhs.addTerms(1, x[k-1, s, ttt])
                for tt in candidate_T[str(k)+'_'+str(s-1)]:
                    if tt+data.travel[s-1]-t>=headway_lower:
                        lhs.addTerms(-1, x[k,s-1,tt])
                model.addConstr(lhs <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))

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
                model.addConstr(lhs <= 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))
    # for k in range(1, num_K):
    #     for s in set_S_op:
    #         # for t in candidate_T[str(k) + '_' + str(s)]:
    #         for t in range(num_T):
    #             model.addConstr(x[k,s,t] == x_value[k][s][t], name='test_' + str(k) + '_' + str(s) + '_' + str(t))

    model.Params.LogToConsole = False
    # model.setParam(GRB.Param.DualReductions, 0)
    model.optimize()
    if model.status == GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % model.status)
        # do IIS, find infeasible constraints
        model.computeIIS()
        for c in model.getConstrs():
            if c.IISConstr:
                print('%s' % c.constrName)
    # 获得决策变量值
    value_x=[[[0 for t in range(num_T)] for s in range(num_S)] for k in range(num_K)]
    for k in range(num_K):
        for s in range(num_S):
            for t in candidate_T[str(k)+'_'+str(s)]:
                value_x[k][s][t]=model.getAttr('X', {model.getVarByName('x['+str(k)+','+str(s)+','+str(t)+']')})[0]

    return model.objVal, value_x







