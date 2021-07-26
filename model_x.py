#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/6/21 10:05
#@Author: Pengli Mo
#@File  : model_x.py

from gurobipy import *
from data_input import *
from function_list import *

lamda_initial = get_lamda_inital(data, set_S_over, num_K, candidate_service)


RP_x = Model(name="RP_x")

chi={}
for k in range(num_K):
    for s in range(num_S):
        chi[k,s] = RP_x.addVars(len(candidate_T[str(k)+'_'+str(s)]), lb=0.0, ub=1.0, vtype=GRB.CONTINUOUS, name='chi_'+str(k)+"_"+str(s))



# Con(1) unique
for k in range(num_K):
    for s in range(num_S):
        RP_x.addConstr(chi[k,s][0] == 1, name='unique_' + str(k) + '_' + str(s))

# for k in range(num_K):
#     for s in range(num_S):
#         for t in range(1,len(candidate_T[str(k) + '_' + str(s)])):
#             RP_x.addConstr(chi[k, s][t-1] >= chi[k, s][t], name='u' + str(k) + '_' + str(s))


# Con(2c)
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



# Con(5.1)
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-min(data.D_br[s],data.D_tr[ss])-candidate_T[str(kk) + '_' + str(ss)][0])
                if tt<len(candidate_T[str(kk) + '_' + str(ss)])-1:
                    RP_x.addConstr(chi[k, s][t] - chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0],
                                   name='51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[k, s][t]<= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0],
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
                    RP_x.addConstr(chi[kk, ss][tt] - chi[k, s][t] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0],
                                 name='52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0],
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
                    RP_x.addConstr(chi[kk, ss][tt] - chi[k, s][t] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1],
                                 name='61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1],
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
                    RP_x.addConstr(chi[k, s][t] - chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1],
                                   name='62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[k, s][t]<= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1],
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
                    RP_x.addConstr(chi[k, s][t] - chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2],
                                   name='71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[k, s][t]<= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2],
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
                    RP_x.addConstr(chi[kk, ss][tt] - chi[k, s][t] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2],
                                 name='72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2],
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
                    RP_x.addConstr(chi[kk, ss][tt] - chi[k, s][t] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3],
                                 name='81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3],
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
                    RP_x.addConstr(chi[k, s][t] - chi[kk, ss][tt] <= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3],
                                   name='82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))
                else:
                    RP_x.addConstr(chi[k, s][t]<= 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3],
                                   name='82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss))


