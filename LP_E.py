#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/25 17:25
#@Author: Pengli Mo
#@File  : LP_E.py

from gurobipy import *
from data_input import *

def LP_E(x):
    model = Model(name="LP_y")
    E = model.addVars(len(U), num_T, vtype=GRB.CONTINUOUS, name='E')
    obj = LinExpr(0)
    for u in range(len(U)):
        for t in range(num_T):
            obj.addTerms(1, E[u, t])
    model.setObjective(obj, GRB.MAXIMIZE)


    E_tr_x = [[0 for tau in range(num_T)] for u in range(len(U))]
    E_rg_x = [[0 for tau in range(num_T)] for u in range(len(U))]
    for u in range(len(U)):
        for tau in range(num_T):
            for k in range(num_K):
                for s in U[u]:
                    for t in candidate_T[str(k) + '_' + str(s)]:
                        E_tr_x[u][tau] += E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] * x[k][s][t]
                        E_rg_x[u][tau] += E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau] * x[k][s][t]


    # Con(6) nettr
    for u in range(num_U):
        for tau in range(num_T):
            # lhs = LinExpr(0)
            # lhs.addTerms(1, E[u, tau])
            # for k in range(num_K):
            #     for s in U[u]:
            #         # for t in range(num_T):
            #         for t in candidate_T[str(k) + '_' + str(s)]:
            #             lhs.addTerms(-E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau], x[k, s, t])
            model.addConstr(E[u, tau] <= E_tr_x[u][tau], name='nettr_' + str(u) + '_' + str(tau))

    # Con(7) netrg
    for u in range(num_U):
        for tau in range(num_T):
            # lhs = LinExpr(0)
            # lhs.addTerms(1, E[u, tau])
            # for k in range(num_K):
            #     for s in U[u]:
            #         # for t in range(num_T):
            #         for t in candidate_T[str(k) + '_' + str(s)]:
            #             lhs.addTerms(-E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau], x[k, s, t])
            model.addConstr(E[u, tau] <= E_rg_x[u][tau], name='netrg_' + str(u) + '_' + str(tau))
    model.Params.LogToConsole = False
    model.optimize()

    dual_lambda=[[0 for tau in range(num_T)] for u in range(num_U)]
    dual_mu=[[0 for tau in range(num_T)] for u in range(num_U)]
    for u in range(num_U):
        for tau in range(num_T):
            dual_lambda[u][tau]=model.getAttr('Pi', {model.getConstrByName('nettr_' + str(u) + '_' + str(tau))})[0]
            dual_mu[u][tau] = model.getAttr('Pi', {model.getConstrByName('netrg_' + str(u) + '_' + str(tau))})[0]
    return model.objVal, dual_lambda, dual_mu


