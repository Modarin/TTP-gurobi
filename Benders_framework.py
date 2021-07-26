#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/25 10:27
#@Author: Pengli Mo
#@File  : Benders_framework.py

from data_input import *
from LP_y import *
from LP_E import *
from RP_x import *
from function_list import *

p=0
UB=[10000000]
LB=[-10000000]
epsilon=0.002
x=timetable2x(data,num_S,num_T)
# for k in range(num_K):
#     for s in range(num_S):
#         if data.timetable[k][s] not in candidate_T[str(k)+'_'+str(s)]:
#             print('error')
# test_x=[[0 for i in range(num_K)] for s in range(len(set_S_sh))]
# for s in range(len(set_S_sh)):
#     for k in range(num_K):
#         # for kk in range(num_K + 1):
#             for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
#                 # for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
#                     test_x[s][k]+=x[k][set_S_sh_before[s]][t]
# dual_omega = [[0 for k in range(num_K)] for s in range(len(set_S_sh))]
# dual_chi = [[0 for k in range(num_K)] for s in range(len(set_S_sh))]
# dual_alpha = [
#     [[[[0 for tt in range(num_T)] for t in range(num_T)] for kk in range(num_K + 1)] for k in range(num_K)] for s in
#     range(len(set_S_sh))]
# dual_beta = [[[[[0 for tt in range(num_T)] for t in range(num_T)] for kk in range(num_K)] for k in range(num_K + 1)]
#              for s in range(len(set_S_sh))]
# dual_lambda = [[0 for tau in range(num_T)] for u in range(num_U)]
# dual_mu = [[0 for tau in range(num_T)] for u in range(num_U)]
list_dual_omega = []
list_dual_chi = []
list_dual_alpha = []
list_dual_beta = []
list_dual_lambda = []
list_dual_mu = []
# while abs((UB[p]-LB[p])/UB[p]) >= epsilon:
while abs((UB[p] - LB[p])/UB[p])>=epsilon:
    p+=1
    LB_1, new_dual_alpha, new_dual_beta, new_dual_omega, new_dual_chi=LP_y(x)
    test_LB_1=0
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            for kk in range(num_K):
                for t in candidate_T[str(k) + '_' + str(set_S_sh_before[s])]:
                    for tt in candidate_T[str(kk) + '_' + str(set_S_sh[s])]:
                        test_LB_1+=(new_dual_alpha[s][k][kk][t][tt]*x[k][set_S_sh_before[s]][t])
                        test_LB_1+=(new_dual_beta[s][k][kk][t][tt]*x[kk][set_S_sh[s]][tt])
    for s in range(len(set_S_sh)):
        for k in range(num_K):
            test_LB_1 += new_dual_omega[s][k]
            test_LB_1 += new_dual_chi[s][k]
    LB_2, new_dual_lambda, new_dual_mu = LP_E(x)
    test_LB_2 = 0
    for u in range(len(U)):
        for tau in range(num_T):
            for k in range(num_K):
                for s in U[u]:
                    for t in candidate_T[str(k) + '_' + str(s)]:
                        test_LB_2+=((new_dual_lambda[u][tau] * E_tr[str(k) + '_' + str(s) + '_' + str(t)][tau] +
                                      new_dual_mu[u][tau] * E_rg[str(k) + '_' + str(s) + '_' + str(t)][tau]))*x[k][s][t]
    LB.append(max(LB[p-1],LB_1+LB_2))
    list_dual_omega.append(new_dual_omega)
    list_dual_chi.append(new_dual_chi)
    list_dual_alpha.append(new_dual_alpha)
    list_dual_beta.append(new_dual_beta)
    list_dual_lambda.append(new_dual_lambda)
    list_dual_mu.append(new_dual_mu)

    # for k in range(num_K):
    #     for s in range(len(set_S_sh)):
    #         dual_omega[s][k]+=new_dual_omega[s][k]
    #         dual_chi[s][k] += new_dual_chi[s][k]
    # for s in range(len(set_S_sh)):
    #     for k in range(num_K):
    #         for kk in range(num_K+1):
    #             for t in range(num_T):
    #                 for tt in range(num_T):
    #                     dual_alpha[s][k][kk][t][tt]+=new_dual_alpha[s][k][kk][t][tt]
    # for s in range(len(set_S_sh)):
    #     for k in range(num_K+1):
    #         for kk in range(num_K):
    #             for t in range(num_T):
    #                 for tt in range(num_T):
    #                     dual_beta[s][k][kk][t][tt]+=new_dual_beta[s][k][kk][t][tt]
    # for u in range(num_U):
    #     for tau in range(num_T):
    #         dual_lambda[u][tau]+=new_dual_lambda[u][tau]
    #         dual_mu[u][tau] += new_dual_mu[u][tau]

    UB_1, x=RP_x(list_dual_alpha, list_dual_beta, list_dual_lambda, list_dual_mu, list_dual_omega, list_dual_chi, p,x)
    timetable=x2timetable(x, num_S, num_K, num_T)
    # for s in range(len(set_S_sh)):
    #     for k in range(num_K):
    #         UB_1+=  dual_omega[s][k]
    #         UB_1 += dual_chi[s][k]
    # UB_1=UB_1/p
    UB.append(min(UB[p-1],UB_1))
    print(LB_1+LB_2,UB_1,LB[p],UB[p],abs((UB[p] - LB[p])/UB[p]))
    # print('hello')

