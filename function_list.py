#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/24 14:48
#@Author: Pengli Mo
#@File  : function_list.py

import xlrd
from class_define import *

def get_data(num_S,num_T):
    book = xlrd.open_workbook('D:\study\paper9-P2_plus\data\data.xlsx')
    TE = book.sheet_by_index(0) # travel time and energy consumption
    PA = book.sheet_by_index(1) # passenger
    TU = book.sheet_by_index(2)  # timetable_up
    TD = book.sheet_by_index(3)  # timetable_dn
    data = Data()
    data.travel=[0 for i in range(num_S*2)]
    data.dwell = [0 for i in range(num_S * 2)]
    data.E_tr=[[] for i in range(num_S*2)]
    data.E_rg = [[] for i in range(num_S * 2)]
    data.D_tr = [[] for i in range(num_S * 2)]
    data.D_br = [[] for i in range(num_S * 2)]
    for l in range(num_S):
        data.dwell[l]=int(TU.cell_value(l+1,1))
        data.travel[l]=int(TU.cell_value(l+1,0))
        data.E_tr[l]=[max(0, int(TE.cell_value(l,i))) for i in range(1,data.travel[l]+1)]
        data.E_rg[l]=[max(0, -int(TE.cell_value(l, i))) for i in range(1, data.travel[l] + 1)]
        data.D_tr[l]=sum(i>0 for i in data.E_tr[l])
        data.D_br[l]=sum(i>0 for i in data.E_rg[l])
        data.travel[l+num_S] = int(TD.cell_value(l+1, 0))
        data.dwell[l+num_S] = int(TD.cell_value(l+1, 1))
        data.E_tr[l+num_S] = [max(0, int(TE.cell_value(l+20, i))) for i in range(1, data.travel[l+num_S] + 1)]
        data.E_rg[l+num_S] = [max(0, -int(TE.cell_value(l+20, i))) for i in range(1, data.travel[l+num_S] + 1)]
        data.D_tr[l+num_S] = sum(i > 0 for i in data.E_tr[l+num_S])
        data.D_br[l+num_S] = sum(i > 0 for i in data.E_rg[l+num_S])
    for l in range(1,PA.nrows):
        if int(PA.cell_value(l,0))<=num_S and int(PA.cell_value(l,1))<=num_S:
            data.passenger[str(int(PA.cell_value(l,0))-1)+'-'+str(int(PA.cell_value(l,1))-1)]=[int(PA.cell_value(l,i)) for i in range(2, 2+num_T)]
    num_k_1=0
    while int(TU.cell_value(num_S-1,num_k_1+2))<num_T and num_k_1<(TU.ncols-2):
        num_k_1+=1
    num_k_2=0
    while int(TD.cell_value(num_S-1,num_k_2+2))<num_T and num_k_2<(TD.ncols-2):
        num_k_2+=1
    num_K=min(num_k_1,num_k_2)
    data.num_K=num_K
    data.timetable=[[] for i in range(num_K)]
    for k in range(num_K):
        tem_line=[0 for i in range(2*num_S)]
        tem_line[0:num_S]=[int(TU.cell_value(i, k+2)-1) for i in range(num_S)]
        tem_line[num_S:2*num_S] = [int(TD.cell_value(i, k + 2)-1) for i in range(num_S)]
        data.timetable[k]=tem_line

    return data

def get_eff_rolling(num_rolling_S,num_K,num_T, T_1, T_2, T_3, M):
    eff_rolling={}
    for s in range(num_rolling_S):
        for k in range(num_K+1):
            for kk in range(num_K+1):
                for t in range(num_T):
                    for tt in range(num_T):
                        dt=tt-t
                        if k<num_K+1 and kk<num_K+1:
                            if dt<T_1:
                                eff_rolling[str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)]=M
                            elif dt<=T_2:
                                eff_rolling[str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)]=0
                            elif dt>=T_3:
                                eff_rolling[str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)]=6
                            else:
                                eff_rolling[str(s)+'_'+str(k)+'_'+str(kk)+'_'+str(t)+'_'+str(tt)]=M
                        else:
                            eff_rolling[str(s) + '_' + str(k) + '_' + str(kk) + '_' + str(t) + '_' + str(tt)] = 100
    return eff_rolling

def get_eff_E(num_K,set_S, num_T,data,candidate_T):
    dic_tr={}
    dic_rg={}
    for k in range(num_K):
        for s in set_S:
            for t in range(num_T):
                tem_energy_tr=[0 for tau in range(num_T)]
                for tt in range(t,min(num_T,t+len(data.E_tr[s]))):
                    tem_energy_tr[tt] = data.E_tr[s][tt - t]
                dic_tr[str(k) + '_' + str(s) + '_' + str(t-candidate_T[str(k)+'_'+str(s)][0])] = tem_energy_tr

    for k in range(num_K):
        for s in set_S:
            for t in range(num_T):
                tem_energy_rg = [0 for tau in range(num_T)]
                for tt in range(t,min(num_T,t+len(data.E_rg[s]))):
                    tem_energy_rg[tt] = data.E_rg[s][tt - t]
                dic_rg[str(k) + '_' + str(s) + '_' + str(t-candidate_T[str(k)+'_'+str(s)][0])] = tem_energy_rg
    return dic_tr,dic_rg

def get_candidta_T(data, num_S, headway_lower, headway_upper, dwell_lower):
    num_K=data.num_K
    candidate_T={}
    #首末车固定
    for s in range(num_S):
        candidate_T[str(0) + '_' + str(s)]=[data.timetable[0][s]]
        candidate_T[str(num_K-1) + '_' + str(s)] = [data.timetable[num_K-1][s]]
        candidate_T[str(num_K) + '_' + str(s)] = [0]
    #中间的车推导
    for k in range(1, num_K-1):
        for s in range(num_S):
            t_left=max(data.timetable[0][s]+k*(headway_lower+dwell_lower), data.timetable[num_K-1][s]-(num_K-1-k)*(headway_upper+dwell_lower))
            t_right=min(data.timetable[0][s]+k*(headway_upper+dwell_lower), data.timetable[num_K-1][s]-(num_K-1-k)*(headway_lower+dwell_lower))
            candidate_T[str(k)+'_'+str(s)]=[i for i in range(max(t_left,data.timetable[k][s]-5), min(t_right+1, data.timetable[k][s]+5))]

    return candidate_T

def get_candidate_service(data, candidate_T, num_K, set_S_over,set_S_fan):
    candidate_service={}
    for k in range(num_K):
        for s in set_S_over:
            tem=[]
            for kk in range(num_K):
                # for ss in set_S_op:
                for ss in [s,set_S_fan[s]]:
                    #如果牵引最大<=制动最小，牵引最小>=制动最大，则无反馈，反之则归入candidate
                    if max(candidate_T[str(kk)+'_'+str(ss)])+data.D_tr[ss]>=min(candidate_T[str(k)+'_'+str(s)])+data.travel[s]-data.D_br[s] and min(candidate_T[str(kk) + '_' + str(ss)]) + data.D_tr[ss] <= max(
                            candidate_T[str(k) + '_' + str(s)]) + data.travel[s] - data.D_br[s]:
                        tem.append([kk,ss])
            candidate_service[str(k)+'_'+str(s)]=tem
    return candidate_service



def timetable2x(data,num_S,num_T):
    x=[[[0 for i in range(num_T)] for s in range(num_S)] for k in range(data.num_K)]
    for k in range(data.num_K):
        for s in range(num_S):
            x[k][s][data.timetable[k][s]]=1
    return x
def x2timetable(x,num_S, num_K, num_T, candidate_T):
    timetable=[[0 for s in range(num_S)] for k in range(num_K)]
    for k in range(num_K):
        for s in range(num_S):
            for t in range(num_T):
                if x[k][s][t]==1:
                    timetable[k][s]+=t
    return timetable
def xvalue2timetable(x,num_S, num_K, num_T, candidate_T):
    timetable=[[0 for s in range(num_S)] for k in range(num_K)]
    for k in range(num_K):
        for s in range(num_S):
            for t in range(len(candidate_T[str(k) + '_' + str(s)])):
                if x[k][s][t]==1:
                    timetable[k][s]+=t+candidate_T[str(k) + '_' + str(s)][0]
    return timetable

def get_lamda_inital(data,set_S_over,num_K, candidate_service):
    lamda_inital={}
    for k in range(num_K):
        for s in set_S_over:
            for service in candidate_service[str(k) + '_' + str(s)]:
                kk = service[0]
                ss = service[1]
                tem=[0 for i in range(4)]
                #condition 3
                if data.timetable[k][s] + data.travel[s] - data.D_br[s] <= data.timetable[kk][ss] and \
                        data.timetable[k][s] + data.travel[s] - data.D_tr[ss] >= data.timetable[kk][ss]:
                    tem[2]=1
                    if tem[2]==0:
                        if data.timetable[k][s] + data.travel[s] - data.D_br[s] >= data.timetable[kk][ss] and \
                                data.timetable[k][s] + data.travel[s] - data.D_tr[ss] <= data.timetable[kk][ss]:
                            tem[3] = 1
                            if tem[3]==0:
                                if data.timetable[k][s] + data.travel[s] - data.D_br[s] + max(data.D_br[s]- data.D_tr[ss],0) < \
                                        data.timetable[kk][ss] and data.timetable[k][s] + data.travel[s] > \
                                        data.timetable[kk][ss]:
                                    tem[0] = 1
                                    if tem[0]==0:
                                        if data.timetable[k][s] + data.travel[s] - data.D_br[s] + min(data.D_br[s]- data.D_tr[ss],0) > \
                                                data.timetable[kk][ss] and data.timetable[k][s] + data.travel[s] - \
                                                data.D_br[s] - data.D_tr[ss] < data.timetable[kk][ss]:
                                            tem[1] = 1
                lamda_inital[str(k) + '_' + str(s) + '_' + str(kk) + '_' + str(ss)]=tem

    return lamda_inital



