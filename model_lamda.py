#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/6/21 10:05
#@Author: Pengli Mo
#@File  : model_lamda.py

from gurobipy import *
from data_input import *
from function_list import *

RP_lamda = Model(name="RP_lamda")
lamda={}
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            lamda[k,s,kk,ss]=RP_lamda.addVars(4, lb=0, vtype=GRB.BINARY, name='lamda_'+str(k)+"_"+str(s)+'_'+str(kk)+"_"+str(ss))
z=RP_lamda.addVars(1, ub=10000000, vtype=GRB.CONTINUOUS, name='z')
RP_lamda.setObjective(z[0], GRB.MAXIMIZE)

for k in range(num_K):
    for s in set_S_over:
        lhs = LinExpr()
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk = service[0]
            ss=service[1]
            lhs.addTerms(1,lamda[k,s,kk,ss][0])
            lhs.addTerms(1,lamda[k,s,kk,ss][1])
            lhs.addTerms(1,lamda[k,s,kk,ss][2])
            lhs.addTerms(1,lamda[k,s,kk,ss][3])
            # RP_lamda.addConstr(lamda[k,s,kk,ss][0]+lamda[k,s,kk,ss][1]+lamda[k,s,kk,ss][2]+lamda[k,s,kk,ss][3] <= 1, name='9_' + str(k) + '_' + str(s)+'_'+str(kk)+"_"+str(ss))
            if data.D_br[s]<data.D_tr[ss]:
                RP_lamda.addConstr(lamda[k, s, kk, ss][2] == 0, name='1011_' + str(k) + '_' + str(s) + '_' + str(kk) + "_" + str(ss))
            else:
                RP_lamda.addConstr(lamda[k, s, kk, ss][3] == 0, name='1011_' + str(k) + '_' + str(s) + '_' + str(kk) + "_" + str(ss))
        RP_lamda.addConstr(lhs <= 1, name='9_' + str(k) + '_' + str(s)+'_'+ str(kk) + '_' + str(ss))