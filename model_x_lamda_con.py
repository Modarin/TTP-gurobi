#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/6/21 10:05
#@Author: Pengli Mo
#@File  : model_x.py

from gurobipy import *
from data_input import *
from function_list import *

RP_x_lamda_con = Model(name="RP_x")
z_con=RP_x_lamda_con.addVars(1, ub=10000000, vtype=GRB.CONTINUOUS, name='z')
# RP_lamda_con.setObjective(z[0], GRB.MAXIMIZE)

P_chi_con={}
for k in range(num_K):
    for s in range(num_S):
        P_chi_con[k,s] = RP_x_lamda_con.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='chi_'+str(k)+"_"+str(s))

P_lamda_con={}
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            P_lamda_con[k,s,kk,ss]=RP_x_lamda_con.addVars(4, lb=0, ub=1.0,vtype=GRB.CONTINUOUS, name='lamda_'+str(k)+"_"+str(s)+'_'+str(kk)+"_"+str(ss))

# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        RP_x_lamda_con.addConstr(P_chi_con[k,s][0] == 1, name='unique_' + str(k) + '_' + str(s))

for k in range(num_K):
    for s in range(num_S):
        for t in range(1,len(candidate_T[str(k) + '_' + str(s)])):
            RP_x_lamda_con.addConstr(P_chi_con[k, s][t-1] >= P_chi_con[k, s][t], name='u' + str(k) + '_' + str(s))


# Con(2c)
for k in range(num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s - 1)])):
            tt=max(0,candidate_T[str(k) + '_' + str(s - 1)][t] + data.travel[
                s - 1] + dwell_lower-candidate_T[str(k) + '_' + str(s)][0])
            if tt<len(candidate_T[str(k) + '_' + str(s)]):
                RP_x_lamda_con.addConstr(P_chi_con[k,s-1][t]-P_chi_con[k,s][tt]<=0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_lamda_con.addConstr(P_chi_con[k, s - 1][t] == 0, name='2c_' + str(k) + '_' + str(s) + '_' + str(t))


# Con(3c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k - 1) + '_' + str(s)])):
            tt = max(0,candidate_T[str(k-1) + '_' + str(s)][t] - data.travel[
                s-1] + headway_lower - candidate_T[str(k) + '_' + str(s-1)][0])
            if tt < len(candidate_T[str(k) + '_' + str(s-1)]):
                RP_x_lamda_con.addConstr(P_chi_con[k-1, s][t] - P_chi_con[k,s-1][tt] <= 0, name='3c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_lamda_con.addConstr(P_chi_con[k - 1, s][t] == 0,name='3c_' + str(k) + '_' + str(s) + '_' + str(t))


# Con(4c)
for k in range(1, num_K):
    for s in set_S_op:
        for t in range(len(candidate_T[str(k) + '_' + str(s-1)])):
            tt = max(0,candidate_T[str(k) + '_' + str(s-1)][t] + data.travel[
                s-1] - headway_upper - candidate_T[str(k-1) + '_' + str(s)][0])
            if tt < len(candidate_T[str(k-1) + '_' + str(s)]):
                RP_x_lamda_con.addConstr(P_chi_con[k, s-1][t] - P_chi_con[k-1,s][tt] <= 0,
                               name='4c_' + str(k) + '_' + str(s) + '_' + str(t))
            else:
                RP_x_lamda_con.addConstr(P_chi_con[k, s-1][t] == 0, name='4c_' + str(k) + '_' + str(s) + '_' + str(t))



# Con(5.1)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-min(data.D_br[s],data.D_tr[ss])-candidate_T[str(kk) + '_' + str(ss)][0])
                if tt<len(candidate_T[str(kk) + '_' + str(ss)])-1:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t] - P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][0],
                                   name='51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t]<= 1-P_lamda_con[k,s,kk,ss][0],
                                   name='51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))

# Con(5.2)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                t = max(0, candidate_T[str(kk) + '_' + str(ss)][tt] - data.travel[s] - candidate_T[str(k) + '_' + str(s)][0])
                if t <len(candidate_T[str(k) + '_' + str(s)])-1:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] - P_chi_con[k, s][t] <= 1-P_lamda_con[k,s,kk,ss][0],
                                 name='52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][0],
                               name='52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))

# Con(6.1)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                t = max(0, candidate_T[str(kk) + '_' + str(ss)][tt] - data.travel[s] +max(data.D_br[s], data.D_tr[ss])- candidate_T[str(k) + '_' + str(s)][0])
                if t <len(candidate_T[str(k) + '_' + str(s)])-1:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] - P_chi_con[k, s][t] <= 1-P_lamda_con[k,s,kk,ss][1],
                                 name='61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][1],
                               name='61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))

# Con(6.2)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-data.D_br[s]-data.D_tr[ss]-candidate_T[str(kk) + '_' + str(ss)][0])
                if tt<len(candidate_T[str(kk) + '_' + str(ss)])-1:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t] - P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][1],
                                   name='62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t]<= 1-P_lamda_con[k,s,kk,ss][1],
                                   name='62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))

# Con(7.1)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-data.D_br[s]-candidate_T[str(kk) + '_' + str(ss)][0])
                if tt<len(candidate_T[str(kk) + '_' + str(ss)]):
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t] - P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][2],
                                   name='71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t]<= 1-P_lamda_con[k,s,kk,ss][2],
                                   name='71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))

# Con(7.2)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                t = max(0, candidate_T[str(kk) + '_' + str(ss)][tt] - data.travel[s] +data.D_tr[ss]- candidate_T[str(k) + '_' + str(s)][0])
                if t <len(candidate_T[str(k) + '_' + str(s)]):
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] - P_chi_con[k, s][t] <= 1-P_lamda_con[k,s,kk,ss][2],
                                 name='72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][2],
                               name='72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))

# Con(8.1)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                t = max(0, candidate_T[str(kk) + '_' + str(ss)][tt] - data.travel[s] +data.D_br[s]- candidate_T[str(k) + '_' + str(s)][0])
                if t <len(candidate_T[str(k) + '_' + str(s)]):
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] - P_chi_con[k, s][t] <= 1-P_lamda_con[k,s,kk,ss][3],
                                 name='81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][3],
                               name='81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))


# Con(8.2)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-data.D_tr[ss]-candidate_T[str(kk) + '_' + str(ss)][0])
                if tt<len(candidate_T[str(kk) + '_' + str(ss)]):
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t] - P_chi_con[kk, ss][tt] <= 1-P_lamda_con[k,s,kk,ss][3],
                                   name='82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x_lamda_con.addConstr(P_chi_con[k, s][t]<= 1-P_lamda_con[k,s,kk,ss][3],
                                   name='82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))



for k in range(num_K):
    for s in set_S_over:
        lhs = LinExpr()
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk = service[0]
            ss = service[1]
            lhs.addTerms(1,P_lamda_con[k,s,kk,ss][0])
            lhs.addTerms(1,P_lamda_con[k,s,kk,ss][1])
            lhs.addTerms(1,P_lamda_con[k,s,kk,ss][2])
            lhs.addTerms(1,P_lamda_con[k,s,kk,ss][3])
            # RP_lamda_con.addConstr(lamda[k,s,kk,ss][0]+lamda[k,s,kk,ss][1]+lamda[k,s,kk,ss][2]+lamda[k,s,kk,ss][3] <= 1, name='9_' + str(k) + '_' + str(s)+'_'+str(kk)+"_"+str(ss))
            if data.D_br[s]<data.D_tr[ss]:
                RP_x_lamda_con.addConstr(P_lamda_con[k, s, kk, ss][2] == 0, name='1011_' + str(k) + '_' + str(s) + '_' + str(kk) + "_" + str(ss))
            else:
                RP_x_lamda_con.addConstr(P_lamda_con[k, s, kk, ss][3] == 0, name='1011_' + str(k) + '_' + str(s) + '_' + str(kk) + "_" + str(ss))


        RP_x_lamda_con.addConstr(lhs <= 1, name='9_' + str(k) + '_' + str(s)+'_'+ str(kk) + '_' + str(ss))