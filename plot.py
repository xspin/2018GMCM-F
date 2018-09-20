#!/usr/bin/python3
# -*- coding: utf-8 -*-
import util
import matplotlib.pyplot as plt
import numpy as np
import datetime
# from data import Hd

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
params = {'legend.fontsize': 'x-large',
          'figure.figsize': (8, 6),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large',}
         #'font.size': 12}
plt.rcParams.update(params)

def plot_alg1(Table, gatealloc, puckallock):
    narrow_count = 0
    wide_count = 0
    total_narrow_count = 0
    total_wide_count = 0
    for puck in Table['Puck'].dict:
        tp = util.bt(Table['Puck'][puck]['plane_type'])
        if tp == 'N': total_narrow_count += 1
        else: total_wide_count += 1
    for puck, gate in puckallock.items():
        if not gate: continue
        tp = util.bt(Table['Puck'][puck]['plane_type'])
        if tp == 'N': narrow_count += 1
        else: wide_count += 1

    plt.figure()
    plt.bar([0, 1], [wide_count, narrow_count], color='rb', tick_label=['Wide', 'Narrow'], align='center')
    plt.text(0, wide_count, '{}'.format(wide_count), fontsize=15)
    plt.text(1, narrow_count, '{}'.format(narrow_count), fontsize=15)
    plt.ylabel(u'数量')
    plt.savefig("output/alg1-1.pdf", bbox_inches='tight')
        
    plt.figure()
    plt.bar([0, 1], [wide_count/total_wide_count, narrow_count/total_narrow_count], color='rb', tick_label=['Wide', 'Narrow'], align='center')
    plt.text(0, wide_count/total_wide_count*1.01, '{}'.format(wide_count/total_wide_count), fontsize=15)
    plt.text(1, narrow_count/total_narrow_count*1.01, '{:.3f}'.format(narrow_count/total_narrow_count), fontsize=15)
    plt.ylabel(u'比例')
    plt.savefig("output/alg1-2.pdf", bbox_inches='tight')
    plt.show()

    T_count = 0
    S_count = 0
    T_time = 0
    S_time = 0
    start_date = datetime.datetime(2018,1,20)
    end_date = datetime.datetime(2018,1,21)
    ztime = datetime.time(0,0,0)
    start_time = util.gettime(start_date, ztime)
    end_time = util.gettime(end_date, ztime)
    for gate, pks in gatealloc.items():
        if len(pks)==0: continue
        for pk in pks:
            sdate = (Table['Puck'][pk]['in_date'])
            stime = (Table['Puck'][pk]['in_time'])
            edate = (Table['Puck'][pk]['out_date'])
            etime = (Table['Puck'][pk]['out_time'])
            st = util.gettime(sdate, stime)
            et = util.gettime(edate, etime)
            if st<start_time: t = et-start_time
            elif et>end_time: t = end_time-st
            else: t = et-st
        h = Table['Gate'][gate]['hall']
        if h=='T': 
            T_count += 1
            T_time += t
        elif h=='S': 
            S_count += 1
            S_time += t
        else: print('Error hall:', h)
    T_time  = T_time / (24*60) / T_count
    S_time  = S_time / (24*60) / S_count
    plt.figure()
    plt.bar([0, 1], [T_count, S_count], color='rb', tick_label=['T', 'S'], align='center')
    plt.text(0, T_count, '{}'.format(T_count), fontsize=15)
    plt.text(1, S_count, '{}'.format(S_count), fontsize=15)
    plt.ylabel(u'数量')
    plt.savefig("output/alg1-3.pdf", bbox_inches='tight')

    plt.figure()
    plt.bar([0, 1], [T_time, S_time], color='rb', tick_label=['T', 'S'], align='center')
    plt.text(0, T_time*1.01, '{:.2f}'.format(T_time), fontsize=15)
    plt.text(1, S_time*1.01, '{:.2f}'.format(S_time), fontsize=15)
    plt.ylabel(u'平均使用率')
    plt.savefig("output/alg1-4.pdf", bbox_inches='tight')


    # export to csv file
    # pucks_df = Table['Puck'].df.copy()
    # pucks_df.rename(columns=Hd, inplace=True)


def plot_alg23(Table, cgraph, tag):
    fail_count = cgraph.fail_count
    fail_rate = fail_count/cgraph.gust_count

    print('Fail Count: {}, Rate: {}'.format(fail_count, fail_rate))

    n_time = 360//5+1
    n_tens = 11
    time_cdf = np.zeros(n_time)
    tensity_cdf = np.zeros(n_tens)
    
    for inpuck in cgraph.adj:
        for outpuck in cgraph.adj[inpuck]:
                key = inpuck+'->'+outpuck
                cost = cgraph.cost[key]
                tensity = cgraph.tensity[key]
                time_cdf[cost//5] += cgraph.gust[key]
                if tensity<=1:
                    tensity_cdf[int(tensity*10)] += cgraph.gust[key]
    time_cdf /= cgraph.gust_count
    tensity_cdf /= cgraph.gust_count

    plt.figure(figsize=(12,4))
    plt.plot(np.arange(n_time)*5, time_cdf, 'r-s')
    plt.xlabel('换乘时间（分）')
    plt.ylabel(u'比率')
    plt.xlim([0, n_time*5])
    plt.grid(True)
    plt.savefig("output/alg{}-1.pdf".format(tag), bbox_inches='tight')

    plt.figure(figsize=(12,4))
    plt.plot(np.arange(n_time)*5,np.cumsum(time_cdf), 'r-s')
    plt.xlabel('换乘时间（分）')
    plt.ylabel(u'比率')
    plt.xlim([0, n_time*5])
    plt.grid(True)
    plt.savefig("output/alg{}-2.pdf".format(tag), bbox_inches='tight')

    plt.figure(figsize=(12,4))
    plt.plot(np.arange(n_tens)/10, tensity_cdf, 'b-o')
    plt.xlabel('紧张度')
    plt.ylabel(u'比率')
    plt.xticks(np.arange(n_tens)/10)
    plt.grid(True)
    plt.savefig("output/alg{}-3.pdf".format(tag), bbox_inches='tight')
    
    plt.figure(figsize=(12,4))
    plt.plot(np.arange(n_tens)/10, np.cumsum(tensity_cdf), 'b-o')
    plt.xlabel('紧张度')
    plt.ylabel(u'比率')
    plt.xticks(np.arange(n_tens)/10)
    plt.grid(True)
    plt.savefig("output/alg{}-4.pdf".format(tag), bbox_inches='tight')

