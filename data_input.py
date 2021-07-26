#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2021/5/25 10:26
#@Author: Pengli Mo
#@File  : data_input.py

# data input
from function_list import *

num_S=10
set_S_sh=[0,5]
set_S_sh_before=[9,4]
set_S_op=[1,2,3,4,6,7,8,9]
set_S_over=[0,1,2,3,5,6,7,8]
set_S_fan_list=[8,7,6,5,3,2,1,0]
set_S_fan={}
for s in range(len(set_S_over)):
    set_S_fan[set_S_over[s]]=set_S_fan_list[s]
num_T=100
U=[[1,9],[2,8],[3,7],[4,6]]
num_U=4
dwell_lower=1
headway_lower=4
headway_upper=20
T_1=3
T_2=T_1+2*(headway_lower+dwell_lower)
T_3=30
data=get_data(int(num_S/2),num_T)
num_K=data.num_K
candidate_T=get_candidta_T(data, num_S, headway_lower, headway_upper, dwell_lower)
# eff_rolling=get_eff_rolling(len(set_S_sh),num_K,num_T,T_1,T_2,T_3,1000)
E_tr,E_rg=get_eff_E(num_K,set_S_op,num_T,data,candidate_T)
candidate_service=get_candidate_service(data, candidate_T, num_K, set_S_over,set_S_fan)

segment=100

# lamda_initial={}