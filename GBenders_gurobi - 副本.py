#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/26 15:10
#@Author: Pengli Mo
#@File  : Benders_gurobi.py#!/usr/bin/env python

from gurobipy import *
from data_input import *
from function_list import *
import datetime
from model_x import *
# from model_lamda import *
from model_x_lamda import *
from model_x_lamda_con import *
import math


# def update_RP_x_lamda_initial(lamda_initial):
#     for k in range(num_K):
#         for s in set_S_op:
#             for service in candidate_service[str(k)+'_'+str(s)]:
#                 kk=service[0]
#                 ss=service[0]
#                 for t in range(len(candidate_T[str(k) + '_' + str(s)])):
#                     RP_x.getConstrByName('51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                 for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
#                     RP_x.getConstrByName('52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]
#                     RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]

def update_objective_x_initial(lamda_initial):
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    RP_x.getConstrByName('51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0])
                    RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1])
                    RP_x.getConstrByName('71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2])
                    RP_x.getConstrByName('82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3])
                for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                    RP_x.getConstrByName('52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0])
                    RP_x.getConstrByName('61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1])
                    RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2])
                    RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = int(1-lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3])

    matrix_chi=[[[0 for t in range(len(candidate_T[str(k) + '_' + str(s)]))] for s in range(num_S)] for k in range(num_K)]
    obj = LinExpr()
    obj_para=0
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    matrix_chi[k][s][t]+=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0]-\
                                        lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1])*candidate_T[str(k) + '_' + str(s)][t]
                    if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                        matrix_chi[k][s][t+1]-=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0]-\
                                            lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1])*candidate_T[str(k) + '_' + str(s)][t]
                for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                    matrix_chi[kk][ss][tt]+=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1]-\
                                        lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0])*candidate_T[str(kk) + '_' + str(ss)][tt]
                    if tt+1 in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                        matrix_chi[kk][ss][tt+1]-=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1]-\
                                            lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0])*candidate_T[str(kk) + '_' + str(ss)][tt]
                obj_para+=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1]+ \
                           lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][3])*data.D_br[s]
                obj_para+=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1] +\
                           lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][2]) * data.D_tr[ss]
                obj_para+=(lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][0]- \
                           lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)][1])*data.travel[s]

    for k in range(num_K):
        for s in set_S_over:
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                obj.addTerms(matrix_chi[k][s][t],chi[k,s][t])
    RP_x.setObjective(obj+obj_para,GRB.MAXIMIZE)


def update_objective_x():
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    RP_x.getConstrByName('51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][0].x
                    RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][1].x
                    RP_x.getConstrByName('71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][2].x
                    RP_x.getConstrByName('82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][3].x
                for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                    RP_x.getConstrByName('52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][0].x
                    RP_x.getConstrByName('61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][1].x
                    RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][2].x
                    RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1-P_lamda[k,s,kk,ss][3].x

        matrix_chi=[[[0 for t in range(len(candidate_T[str(k) + '_' + str(s)]))] for s in range(num_S)] for k in range(num_K)]
        obj = LinExpr()
        obj_para=0
        for k in range(num_K):
            for s in set_S_over:
                for service in candidate_service[str(k)+'_'+str(s)]:
                    kk=service[0]
                    ss=service[1]
                    for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                        matrix_chi[k][s][t]+=(P_lamda[k,s,kk,ss][0].x-P_lamda[k,s,kk,ss][1].x)*candidate_T[str(k) + '_' + str(s)][t]
                        if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                            matrix_chi[k][s][t+1]-=(P_lamda[k,s,kk,ss][0].x-P_lamda[k,s,kk,ss][1].x)*candidate_T[str(k) + '_' + str(s)][t]
                    for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                        matrix_chi[kk][ss][tt]+=(P_lamda[k,s,kk,ss][1].x-P_lamda[k,s,kk,ss][0].x)*candidate_T[str(kk) + '_' + str(ss)][tt]
                        if tt+1 in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                            matrix_chi[kk][ss][tt+1]-=(P_lamda[k,s,kk,ss][1].x-P_lamda[k,s,kk,ss][0].x)*candidate_T[str(kk) + '_' + str(ss)][tt]
                    obj_para+=(P_lamda[k,s,kk,ss][1].x + P_lamda[k,s,kk,ss][3].x) * data.D_br[s]
                    obj_para+=(P_lamda[k,s,kk,ss][1].x + P_lamda[k,s,kk,ss][2].x) * data.D_tr[ss]
                    obj_para+=(P_lamda[k,s,kk,ss][0].x-P_lamda[k,s,kk,ss][1].x) * data.travel[s]

        for k in range(num_K):
            for s in set_S_over:
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    obj.addTerms(matrix_chi[k][s][t],chi[k,s][t])
        RP_x.setObjective(obj+obj_para,GRB.MAXIMIZE)

def benders_optimal_cut():
    lhs = LinExpr()
    rhs = 0
    lhs_con = LinExpr()
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                tem = [0 for count in range(4)]
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    tem[0] += RP_x.getConstrByName('51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[1] += RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[2] += RP_x.getConstrByName('71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[3] += RP_x.getConstrByName('82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).pi
                for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                    tem[0] += RP_x.getConstrByName('52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[1] += RP_x.getConstrByName('61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[2] += RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).pi
                    tem[3] += RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).pi
                sub = [0 for count in range(4)]
                sub[0] += data.D_br[s]
                sub[1] += data.D_tr[ss]
                sub[2] += data.D_br[s]
                sub[3] += data.D_tr[ss]
                for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                    if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                        sub[0] += candidate_T[str(k) + '_' + str(s)][t]*(chi[k,s][t].x-chi[k,s][t+1].x)
                        sub[1] -= candidate_T[str(k) + '_' + str(s)][t]*(chi[k,s][t].x-chi[k,s][t+1].x)
                    else:
                        sub[0] += candidate_T[str(k) + '_' + str(s)][t]*chi[k,s][t].x
                        sub[1] -= candidate_T[str(k) + '_' + str(s)][t]*chi[k,s][t].x
                for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                    if tt+1 in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                        sub[0] -= candidate_T[str(kk) + '_' + str(ss)][tt]*(chi[kk,ss][tt].x-chi[kk,ss][tt+1].x)
                        sub[1] += candidate_T[str(kk) + '_' + str(ss)][tt]*(chi[kk,ss][tt].x-chi[kk,ss][tt+1].x)
                    else:
                        sub[0] -= candidate_T[str(kk) + '_' + str(ss)][tt]*chi[kk,ss][tt].x
                        sub[1] += candidate_T[str(kk) + '_' + str(ss)][tt]*chi[kk,ss][tt].x

                if p==1:
                    for co in range(4):
                        lhs.addTerms(sub[co]-tem[co], P_lamda[k, s, kk, ss][co])
                        rhs-=tem[co]*lamda_initial[str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)][co]
                        lhs_con.addTerms(sub[co]-tem[co], P_lamda_con[k, s, kk, ss][co])
                else:
                    for co in range(4):
                        lhs.addTerms(sub[co]-tem[co], P_lamda[k, s, kk, ss][co])
                        rhs-=tem[co]*P_lamda[k,s,kk,ss][co].x
                        lhs_con.addTerms(sub[co]-tem[co], P_lamda_con[k, s, kk, ss][co])

    lhs.addTerms(-1, z[0])
    RP_x_lamda.addConstr(lhs>=rhs,name="benders_"+str(p))
    RP_x_lamda.update()
    RP_x_lamda.getConstrByName("benders_"+str(p)).Lazy = 1

    lhs_con.addTerms(-1, z_con[0])
    RP_x_lamda_con.addConstr(lhs_con>=rhs,name="benders_"+str(p))
    RP_x_lamda_con.update()
    RP_x_lamda_con.getConstrByName("benders_"+str(p)).Lazy = 1

def benders_feasiblity_cut():
    lhs = LinExpr()
    P_lhs = LinExpr()
    lhs_con = LinExpr()
    P_lhs_con = LinExpr()
    count_rhs = 0
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                for co in range(4):
                    if P_lamda[k,s,kk,ss][co].x>0.5:
                        count_rhs+=1
                        lhs.addTerms(1,P_lamda[k,s,kk,ss][co])
                        P_lhs.addTerms(1, P_lamda[k, s, kk, ss][co])
                        lhs_con.addTerms(1,P_lamda_con[k,s,kk,ss][co])
                        P_lhs_con.addTerms(1, P_lamda_con[k, s, kk, ss][co])

    RP_x_lamda.setObjective(P_lhs, GRB.MAXIMIZE)
    RP_x_lamda.optimize()
    RP_x_lamda.addConstr(lhs <= min(count_rhs-1,math.floor(RP_x_lamda.ObjVal)), name="benders_" + str(p))
    RP_x_lamda.update()
    RP_x_lamda.getConstrByName("benders_" + str(p)).Lazy = 1

    RP_x_lamda_con.addConstr(lhs_con <= min(count_rhs-1,math.floor(RP_x_lamda.ObjVal)), name="benders_" + str(p))
    RP_x_lamda_con.update()
    RP_x_lamda_con.getConstrByName("benders_" + str(p)).Lazy = 1

    # for k in range(num_K):
    #     for s in set_S_over:
    #         for service in candidate_service[str(k)+'_'+str(s)]:
    #             kk=service[0]
    #             ss=service[1]
    #             for co in range(4):
    #                 lamda_initial[str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)][co]=0
    #                 if P_lamda[k,s,kk,ss][co].x>0.6:
    #                     lamda_initial[str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)][co]=1


    # for k in range(num_K):
    #     for s in set_S_over:
    #         for service in candidate_service[str(k)+'_'+str(s)]:
    #             kk=service[0]
    #             ss=service[1]
    #             for co in range(4):
    #                 lamda_initial[str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)][co]=0
    # lamda_initial['0_8_3_0'][2] = 1
    # lamda_initial['1_1_0_7'][2] = 1
    # lamda_initial['1_2_1_6'][2] = 1
    # lamda_initial['1_3_3_5'][2] = 1
    # lamda_initial['1_5_0_3'][2] = 1
    # lamda_initial['1_7_3_1'][2] = 1
    # lamda_initial['1_8_4_0'][2] = 1
    # lamda_initial['2_0_0_8'][3] = 1
    # lamda_initial['2_1_1_7'][2] = 1
    # lamda_initial['2_2_3_6'][2] = 1
    # lamda_initial['2_3_4_5'][2] = 1
    # lamda_initial['2_5_1_3'][2] = 1
    # lamda_initial['2_6_2_2'][3] = 1
    # lamda_initial['2_8_5_0'][2] = 1
    # lamda_initial['3_1_2_7'][2] = 1
    # lamda_initial['3_3_5_5'][2] = 1
    # lamda_initial['3_6_3_2'][3] = 1
    # lamda_initial['3_7_5_1'][3] = 1
    # lamda_initial['4_0_2_8'][3] = 1
    # lamda_initial['4_1_3_7'][2] = 1
    # lamda_initial['4_2_5_6'][2] = 1
    # lamda_initial['4_5_3_3'][2] = 1
    # lamda_initial['4_6_4_2'][3] = 1
    # lamda_initial['5_1_4_7'][2] = 1
    # lamda_initial['5_6_5_2'][3] = 1
    # lamda_initial['6_0_4_8'][3] = 1
    # lamda_initial['6_1_5_7'][2] = 1
    # lamda_initial['6_5_5_3'][2] = 1

#######################################################################################################################
#####################################################   初始化  ########################################################
#######################################################################################################################

p=0
tem_UB=0
UB=[1000000000]
LB=[-10000000]
epsilon=0.0001
x_value=timetable2x(data,num_S,num_T)

RP_x.update()
RP_x.Params.LogToConsole = False
# RP_lamda.update()
# RP_lamda.Params.LogToConsole = False
RP_x_lamda.Params.LogToConsole = False
RP_x_lamda.Params.lazyConstraints = 1
RP_x_lamda_con.Params.LogToConsole = False
RP_x_lamda_con.Params.lazyConstraints = 1
# RP_lamda.Params.lazyConstraints = 1


#######################################################################################################################
#####################################################   计算开始  ######################################################
#######################################################################################################################

time_1 = datetime.datetime.now()

##添加关于lamda的约束

max_lamda=[0 for i in range(5)]
P_lhs0 = LinExpr()
P_lhs1 = LinExpr()
P_lhs2 = LinExpr()
P_lhs3 = LinExpr()
lhs = LinExpr()
lhs0 = LinExpr()
lhs1 = LinExpr()
lhs2 = LinExpr()
lhs3 = LinExpr()
for k in range(num_K):
    for s in set_S_over:
        for service in candidate_service[str(k)+'_'+str(s)]:
            kk=service[0]
            ss=service[1]
            P_lhs0.addTerms(1, P_lamda[k, s, kk, ss][0])
            P_lhs1.addTerms(1, P_lamda[k, s, kk, ss][1])
            P_lhs2.addTerms(1, P_lamda[k, s, kk, ss][2])
            P_lhs3.addTerms(1, P_lamda[k, s, kk, ss][3])
            lhs0.addTerms(1, P_lamda[k, s, kk, ss][0])
            lhs1.addTerms(1, P_lamda[k, s, kk, ss][1])
            lhs2.addTerms(1, P_lamda[k, s, kk, ss][2])
            lhs3.addTerms(1, P_lamda[k, s, kk, ss][3])
            lhs.addTerms(min(data.D_br[s],data.D_tr[ss])-1, P_lamda[k, s, kk, ss][0])
            lhs.addTerms(min(data.D_br[s],data.D_tr[ss])-1, P_lamda[k, s, kk, ss][1])
            lhs.addTerms(min(data.D_br[s],data.D_tr[ss]), P_lamda[k, s, kk, ss][2])
            lhs.addTerms(min(data.D_br[s],data.D_tr[ss]), P_lamda[k, s, kk, ss][3])

# RP_x_lamda.addConstr(P_lamda[1,1,0,7][1]==1)
# RP_x_lamda.addConstr(P_lamda[1,2,1,6][1]==1)
# RP_x_lamda.addConstr(P_lamda[1,5,0,3][1]==1)
# RP_x_lamda.addConstr(P_lamda[2,1,1,7][1]==1)
# RP_x_lamda.addConstr(P_lamda[2,5,1,3][2]==1)

# fix=[[1,1,0,7,2],[1,2,1,6,2],[1,5,0,3,2],[2,1,1,7,2],[2,5,1,3,2]]
# for k in range(num_K):
#     for s in set_S_over:
#         for service in candidate_service[str(k)+'_'+str(s)]:
#             kk=service[0]
#             ss=service[1]
#             for co in range(4):
#                 if [k,s,kk,ss,co] in fix:
#                     RP_x_lamda.addConstr(P_lamda[k, s, kk, ss][co] == 1,name='fix_'+str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)+'_'+str(co))
#                 else:
#                     RP_x_lamda.addConstr(P_lamda[k, s, kk, ss][co] == 0,name='fix_'+str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)+'_'+str(co))

RP_x_lamda.setObjective(P_lhs0,GRB.MAXIMIZE)
RP_x_lamda.optimize()

max_lamda[0]=math.floor(RP_x_lamda.ObjVal)
RP_x_lamda.addConstr(lhs0<=max(0,math.floor(max_lamda[0])), name='max_lamda_'+str(0))


RP_x_lamda.setObjective(P_lhs1,GRB.MAXIMIZE)
RP_x_lamda.optimize()
max_lamda[1]=math.floor(RP_x_lamda.ObjVal)
max_lamda[1]=RP_x_lamda.ObjVal
RP_x_lamda.addConstr(lhs1<=max(0,math.floor(max_lamda[1])), name='max_lamda_'+str(1))

RP_x_lamda.setObjective(P_lhs2,GRB.MAXIMIZE)
RP_x_lamda.optimize()
max_lamda[2]=math.floor(RP_x_lamda.ObjVal)
max_lamda[2]=RP_x_lamda.ObjVal
RP_x_lamda.addConstr(lhs2<=max(0,math.floor(max_lamda[2])), name='max_lamda_'+str(2))


RP_x_lamda.setObjective(P_lhs3,GRB.MAXIMIZE)
RP_x_lamda.optimize()
max_lamda[3]=math.floor(RP_x_lamda.ObjVal)
max_lamda[3]=RP_x_lamda.ObjVal
RP_x_lamda.addConstr(lhs3<=max(0,math.floor(max_lamda[3])), name='max_lamda_'+str(3))

RP_x_lamda.setObjective(P_lhs0+P_lhs1+P_lhs2+P_lhs3,GRB.MAXIMIZE)
RP_x_lamda.optimize()
max_lamda[4]=math.floor(RP_x_lamda.ObjVal)
max_lamda[4]=RP_x_lamda.ObjVal
RP_x_lamda.addConstr(lhs0+lhs1+lhs2+lhs3<=math.floor(max_lamda[4]), name='max_lamda_'+str(4))

# for k in range(num_K):
#     for s in set_S_over:
#         for service in candidate_service[str(k) + '_' + str(s)]:
#             kk = service[0]
#             ss = service[1]
#             tem = [P_lamda[k,s,kk,ss][co] for co in range(4)]
#             lamda_initial[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)] = tem

#检测模型是否有效
# for k in range(num_K):
#     for s in set_S_over:
#         for service in candidate_service[str(k)+'_'+str(s)]:
#             kk=service[0]
#             ss=service[1]
#             if P_lamda[k, s, kk, ss][1].x > 0.5:
#             # if P_lamda[k,s,kk,ss][0].x>0.5 or P_lamda[k,s,kk,ss][1].x>0.5 or P_lamda[k,s,kk,ss][2].x>0.5 or P_lamda[k,s,kk,ss][3].x>0.5:
#                 for t in range(len(candidate_T[str(k)+'_'+str(s)])):
#                     if t+1 not in range(len(candidate_T[str(k)+'_'+str(s)])) or P_chi[k,s][t+1].x<0.5:
#                         break
#                 for tt in range(len(candidate_T[str(kk)+'_'+str(ss)])):
#                     if tt+1 not in range(len(candidate_T[str(kk)+'_'+str(ss)])) or P_chi[kk,ss][tt+1].x<0.5:
#                         break
#                 print(k,s,kk,ss,candidate_T[str(k)+'_'+str(s)][t],candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s],\
#                       candidate_T[str(k)+'_'+str(s)][t]+data.travel[s],candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss])
                # print('51')
                # for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                #     tt=max(0,candidate_T[str(k) + '_' + str(s)][t]+data.travel[s]-min(data.D_br[s],data.D_tr[ss])-candidate_T[str(kk) + '_' + str(ss)][0])
                #     if tt<len(candidate_T[str(kk) + '_' + str(ss)]):
                #         print(candidate_T[str(k) + '_' + str(s)][t], candidate_T[str(kk) + '_' + str(ss)][tt])
                #     else:
                #         print(candidate_T[str(k) + '_' + str(s)][t])
                # print('52')
                # for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
                #     t = max(0, candidate_T[str(kk) + '_' + str(ss)][tt] - data.travel[s] - candidate_T[str(k) + '_' + str(s)][0])
                #     if t <len(candidate_T[str(k) + '_' + str(s)]):
                #         print(candidate_T[str(kk) + '_' + str(ss)][tt], candidate_T[str(k) + '_' + str(s)][t])
                #     else:
                #         print(candidate_T[str(kk) + '_' + str(ss)][tt])

RP_x_lamda.addConstr(z[0]<=lhs, name='max_obj_')




##正式benders循环
RP_x_lamda.setObjective(z[0], GRB.MAXIMIZE)
RP_x_lamda.update()
RP_x_lamda_con.setObjective(z_con[0], GRB.MAXIMIZE)
RP_x_lamda_con.update()

while abs((UB[p] - LB[p])/UB[p])>=epsilon:
    p+=1

    ####子问题求解，先修改子问题右端项，再求解
    if p==1:
    # if p <= 1000:
        update_objective_x_initial(lamda_initial)
        RP_x.update()
        RP_x.optimize()
        # if RP_x.status == GRB.OPTIMAL:
        #     print(RP_x.ObjVal)
        # if RP_x.ObjVal>55:
        #     print([chi[3, 3][t].x for t in range(len(candidate_T[str(3) + '_' + str(3)]))])
        #     print([chi[5, 5][t].x for t in range(len(candidate_T[str(5) + '_' + str(5)]))])
        #     print('hello')

    else:
        update_objective_x()
        # for k in range(num_K):
        #     for s in set_S_over:
        #         for service in candidate_service[str(k) + '_' + str(s)]:
        #             kk = service[0]
        #             ss = service[1]
        #             for t in range(len(candidate_T[str(k) + '_' + str(s)])):
        #                 RP_x.getConstrByName('51_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('62_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('71_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('82_' + str(k) + '_' + str(s) + '_' + str(t) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #             for tt in range(len(candidate_T[str(kk) + '_' + str(ss)])):
        #                 RP_x.getConstrByName('52_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('61_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('72_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        #                 RP_x.getConstrByName('81_' + str(k) + '_' + str(s) + '_' + str(tt) + '_' + str(kk) + '_' + str(ss)).rhs = 1
        # RP_x.update()
        # for t in range(len(candidate_T[str(0) + '_' + str(8)])):
        #     RP_x.getConstrByName('71_' + str(0) + '_' + str(8) + '_' + str(t) + '_' + str(3) + '_' + str(0)).rhs = 0
        # for tt in range(len(candidate_T[str(3) + '_' + str(0)])):
        #     RP_x.getConstrByName('72_' + str(0) + '_' + str(8) + '_' + str(tt) + '_' + str(3) + '_' + str(0)).rhs = 0
        # for t in range(len(candidate_T[str(1) + '_' + str(1)])):
        #     RP_x.getConstrByName('71_' + str(1) + '_' + str(1) + '_' + str(t) + '_' + str(0) + '_' + str(7)).rhs = 0
        # for tt in range(len(candidate_T[str(0) + '_' + str(7)])):
        #     RP_x.getConstrByName('72_' + str(1) + '_' + str(1) + '_' + str(tt) + '_' + str(0) + '_' + str(7)).rhs = 0

        RP_x.update()
        RP_x.optimize()
        if RP_x.status == GRB.OPTIMAL:
            print(RP_x.ObjVal)
        print('hello')

    ##求解子问题之后向主问题中增加benders optimal cut或者feasibilty cut
    if RP_x.status == GRB.OPTIMAL:
        #检验结果是否正确
        # if p !=1:
        #     for k in range(num_K):
        #         for s in set_S_over:
        #             for service in candidate_service[str(k)+'_'+str(s)]:
        #                 kk=service[0]
        #                 ss=service[1]
        #                 tem_index=-1
        #                 if lamda[k,s,kk,ss][0].x>0.5:
        #                     tem_index=0
        #                     for t in range(len(candidate_T[str(k)+'_'+str(s)])):
        #                         if t+1 not in range(len(candidate_T[str(k)+'_'+str(s)])) or chi[k,s][t+1].x<0.5:
        #                             break
        #                     for tt in range(len(candidate_T[str(kk)+'_'+str(ss)])):
        #                         if tt+1 not in range(len(candidate_T[str(kk)+'_'+str(ss)])) or chi[kk,ss][tt+1].x<0.5:
        #                             break
        #                     print(k,s,kk,ss,tem_index, candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s]-candidate_T[str(kk)+'_'+str(ss)][tt],\
        #                           candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s],candidate_T[str(k)+'_'+str(s)][t]+data.travel[s],\
        #                           candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss])
        #
        #                 if lamda[k,s,kk,ss][1].x>0.5:
        #                     tem_index = 1
        #                     for t in range(len(candidate_T[str(k)+'_'+str(s)])):
        #                         if t+1 not in range(len(candidate_T[str(k)+'_'+str(s)])) or chi[k,s][t+1].x<0.5:
        #                             break
        #                     for tt in range(len(candidate_T[str(kk)+'_'+str(ss)])):
        #                         if tt+1 not in range(len(candidate_T[str(kk)+'_'+str(ss)])) or chi[kk,ss][tt+1].x<0.5:
        #                             break
        #                     print(k,s,kk,ss,tem_index, candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss]-(candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s]),\
        #                           candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s],candidate_T[str(k)+'_'+str(s)][t]+data.travel[s],\
        #                           candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss])
        #
        #                 if lamda[k,s,kk,ss][2].x>0.5:
        #                     tem_index = 2
        #                     for t in range(len(candidate_T[str(k)+'_'+str(s)])):
        #                         if t+1 not in range(len(candidate_T[str(k)+'_'+str(s)])) or chi[k,s][t+1].x<0.5:
        #                             break
        #                     for tt in range(len(candidate_T[str(kk)+'_'+str(ss)])):
        #                         if tt+1 not in range(len(candidate_T[str(kk)+'_'+str(ss)])) or chi[kk,ss][tt+1].x<0.5:
        #                             break
        #                     print(k,s,kk,ss,tem_index, data.D_tr[ss],\
        #                           candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s],candidate_T[str(k)+'_'+str(s)][t]+data.travel[s],\
        #                           candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss])
        #
        #                 if lamda[k,s,kk,ss][3].x>0.5:
        #                     tem_index = 3
        #                     for t in range(len(candidate_T[str(k)+'_'+str(s)])):
        #                         if t+1 not in range(len(candidate_T[str(k)+'_'+str(s)])) or chi[k,s][t+1].x<0.5:
        #                             break
        #                     for tt in range(len(candidate_T[str(kk)+'_'+str(ss)])):
        #                         if tt+1 not in range(len(candidate_T[str(kk)+'_'+str(ss)])) or chi[kk,ss][tt+1].x<0.5:
        #                             break
        #                     print(k,s,kk,ss,tem_index, data.D_br[s],\
        #                           candidate_T[str(k)+'_'+str(s)][t]+data.travel[s]-data.D_br[s],candidate_T[str(k)+'_'+str(s)][t]+data.travel[s],\
        #                           candidate_T[str(kk)+'_'+str(ss)][tt],candidate_T[str(kk)+'_'+str(ss)][tt]+data.D_tr[ss])

        benders_optimal_cut()
    else:
        benders_feasiblity_cut()



    # ##求解主问题
    RP_x_lamda.optimize()
    # #先求解松弛问题
    # RP_x_lamda_con.optimize()
    # #将松弛问题分支
    # for k in range(num_K):
    #     for s in set_S_over:
    #         for service in candidate_service[str(k) + '_' + str(s)]:
    #             kk = service[0]
    #             ss = service[1]
    #             for co in range(4):
    #                 if P_lamda_con[k,s,kk,ss][co].x>0.01:
    #                     RP_x_lamda.getConstrByName(
    #                         'domain_' + str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss) + '_' + str(co)).rhs = 1
    #                 else:
    #                     RP_x_lamda.getConstrByName(
    #                         'domain_' + str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss) + '_' + str(co)).rhs = 0
    # RP_x_lamda.update()
    # RP_x_lamda.optimize()
    # if RP_x_lamda.status == GRB.Status.INFEASIBLE:
    #     RP_x_lamda.computeIIS()
    #     for c in RP_x.getConstrs():
    #         if c.IISConstr:
    #             print('%s' % c.constrName)



    # fix=[[1,1,0,7,2],[1,2,1,6,2],[1,5,0,3,2],[2,1,1,7,2],[2,5,1,3,2]]

    # for k in range(num_K):
    #     for s in set_S_over:
    #         for service in candidate_service[str(k)+'_'+str(s)]:
    #             kk=service[0]
    #             ss=service[1]
    #             for co in range(4):
    #                 if [k,s,kk,ss,co] in fix:
    #                     RP_lamda.addConstr(lamda[k, s, kk, ss][co] == 1,name='fix_'+str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)+'_'+str(co))
    #                 else:
    #                     RP_lamda.addConstr(lamda[k, s, kk, ss][co] == 0,name='fix_'+str(k)+'_'+str(s)+'_'+str(kk)+'_'+str(ss)+'_'+str(co))
    # RP_lamda.update()
    # RP_lamda.getConstrByName('fix_1_1_0_7_2').rhs = 1
    # RP_lamda.getConstrByName('fix_1_2_1_6_2').rhs = 1
    # RP_lamda.getConstrByName('fix_1_5_0_3_2').rhs = 1
    # RP_lamda.getConstrByName('fix_2_1_1_7_2').rhs = 1
    # RP_lamda.getConstrByName('fix_2_5_1_3_2').rhs = 1

    # RP_lamda.addConstr(lamda[1, 2, 1, 6][2] == 1)
    # RP_lamda.addConstr(lamda[1, 5, 0, 3][2] == 1)
    # RP_lamda.addConstr(lamda[2, 1, 1, 7][2] == 1)
    # RP_lamda.addConstr(lamda[2, 5, 1, 3][2] == 1)

    # if RP_x.status == GRB.Status.INFEASIBLE:
    #     RP_x.computeIIS()
    #     for c in RP_x.getConstrs():
    #         if c.IISConstr:
    #             print('%s' % c.constrName)

    # 更新上界
    UB.append(min(UB[p-1],RP_x_lamda.ObjVal))
    # 更新下界
    if RP_x.status == GRB.OPTIMAL:
        LB.append(max(LB[p - 1], RP_x.Objval))
        print(p, LB[p], UB[p], abs((UB[p] - LB[p]) / UB[p]),'feasible')

    else:
        LB.append(LB[p - 1])
        print(p, LB[p], UB[p], abs((UB[p] - LB[p]) / UB[p]),'infeasible')

x_value=[[[0 for t in range(len(candidate_T[str(k) + '_' + str(s)]))] for s in range(num_S)] for k in range(num_K)]
# if p % segment ==0:
#     for k in range(num_K):
#         for s in range(num_S):
#             for t in range(len(candidate_T[str(k) + '_' + str(s)])):
#                 x_value[k][s][t]=chi_integer[k,s][t].x
#                 if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
#                     x_value[k][s][t] -= chi_integer[k, s][t+1].x
# else:
for k in range(num_K):
    for s in range(num_S):
        for t in range(len(candidate_T[str(k) + '_' + str(s)])):
            x_value[k][s][t]=chi[k,s][t].x
            if t+1 in range(len(candidate_T[str(k) + '_' + str(s)])):
                x_value[k][s][t] -= chi[k, s][t+1].x

timetable=xvalue2timetable(x_value, num_S, num_K, num_T,candidate_T)

time_2 = datetime.datetime.now()
if RP_x.status == GRB.OPTIMAL:
    print(time_2-time_1)
    for k in range(num_K):
        print(timetable[k])

    # for k in range(num_K):
    #     for s in range(num_S):
    #         print(k,s,x_value[k][s])

    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k)+'_'+str(s)]:
                kk=service[0]
                ss=service[1]
                for co in range(4):
                    if P_lamda[k, s, kk, ss][co].x==1:
                        print(k,s,kk,ss,co,\
                              timetable[k][s]+data.travel[s]-data.D_br[s], timetable[k][s]+data.travel[s],\
                              timetable[kk][ss], timetable[kk][ss]+data.D_tr[ss])
# for k in range(num_K):
#     for s in range(num_S):
#         print(x_value[k][s])


















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