#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/25 11:02
#@Author: Pengli Mo
#@File  : LP_y.py

from gurobipy import *
from data_input import *

def LP_y(x):
    model = Model(name="LP_y")
    # y_lb=[[[[0 for tt in range(num_T)] for t in range(num_T)] for kk in range(num_K)] for k in range(num_K)]
    # y_ub = [[[[1 for tt in range(num_T)] for t in range(num_T)] for kk in range(num_K)] for k in range(num_K)]
    y = model.addVars(len(set_S_sh), num_K + 1, num_K + 1, num_T, num_T, lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='y')
    obj = LinExpr(0)
    for s in range(len(set_S_sh)):
        for k in range(num_K+1):
            for kk in range(num_K+1):
                for t in range(num_T):
                    for tt in range(num_T):
                        obj.addTerms(-eff_rolling[str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)],
                                     y[s, k, kk, t, tt])
    model.setObjective(obj, GRB.MAXIMIZE)

    # Con(8) onebefore
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            lhs = LinExpr(0)
            # for t in range(num_T):
            for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                for kk in range(num_K + 1):
                    # for tt in range(num_T):
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        lhs.addTerms(1, y[s, k, kk, t, tt])
            model.addConstr(lhs == 1, name='onebefore_' + str(s) + '_' + str(k))

    # Con(9) oneafter
    for s in range(len(set_S_sh)):
        for kk in range(num_K):
            lhs = LinExpr(0)
            for k in range(num_K + 1):
                # for t in range(num_T):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    # for tt in range(num_T):
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        lhs.addTerms(1, y[s, k, kk, t, tt])
            model.addConstr(lhs == 1, name='oneafter_' + str(s) + '_' + str(kk))

    # Con(10) xbefore
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            for kk in range(num_K + 1):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        model.addConstr(y[s, k, kk, t, tt] <= x[k][set_S_sh_before[s]][t],
                                        name='xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
                                            t) + '_' + str(tt))
    #
    # # Con(11) xafter
    for s in range(len(set_S_sh)):
        for k in range(num_K + 1):
            for kk in range(num_K):
                # for t in range(num_T):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    # for tt in range(num_T):
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        model.addConstr(y[s, k, kk, t, tt]<= x[kk][set_S_sh[s]][tt],
                                        name='xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(
                                            t) + '_' + str(tt))
    model.Params.LogToConsole = False
    model.optimize()

    #获得决策变量值
    # value_y=[[[[[0 for s in range(len(set_S_sh))]for k in range(num_K+1)]for kk in range(num_K+1)]for t in range(num_T)]for tt in range(num_T)]
    # value_y = [[[[[0 for s in range(num_T)] for k in range(num_T)] for kk in range(num_K + 1)] for t in
    #             range(num_K+1)] for tt in range(len(set_S_sh))]
    # for s in range(len(set_S_sh)):
    #     for k in range(num_K+1):
    #         for kk in range(num_K+1):
    #             for t in range(num_T):
    #                 for tt in range(num_T):
    #                     value_y[s][k][kk][t][tt]=model.getAttr('X', {model.getVarByName('y['+str(s)+','+str(k)+','+str(kk)+','+str(t)+','+str(tt)+']')})

    #获得对偶值
    dual_omega=[[0 for k in range(num_K)] for s in range(len(set_S_sh))]
    dual_chi = [[0 for k in range(num_K)] for s in range(len(set_S_sh))]
    dual_alpha=[[[[[0 for tt in range(num_T)] for t in range(num_T)]for kk in range(num_K + 1)]for k in range(num_K)]for s in range(len(set_S_sh))]
    dual_beta=[[[[[0 for tt in range(num_T)]for t in range(num_T)]for kk in range(num_K)]for k in range(num_K + 1)]for s in range(len(set_S_sh))]
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            dual_omega[s][k]=model.getAttr('Pi', {model.getConstrByName('onebefore_'+str(s)+'_'+str(k))})[0]
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            dual_chi[s][k]=model.getAttr('Pi', {model.getConstrByName('oneafter_'+str(s)+'_'+str(k))})[0]
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            for kk in range(num_K + 1):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        dual_alpha[s][k][kk][t][tt] = model.getAttr('Pi', {model.getConstrByName(
                            'xbefore_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt))})[0]
    for s in range(len(set_S_sh)):
        for k in range(num_K + 1):
            for kk in range(num_K):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        dual_beta[s][k][kk][t][tt] = model.getAttr('Pi', {model.getConstrByName(
                            'xafter_' + str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt))})[0]

    # Dualsolution = model.getAttr('Pi', {model.getConstrByName('onebefore_0_0')})
    # model.getP
    # value=model.getVarByName('y[0,0,0,0]').x
    return model.objVal, dual_alpha, dual_beta, dual_omega, dual_chi