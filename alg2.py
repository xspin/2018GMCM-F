#!/usr/bin/python3
# -*- coding: utf-8 -*-

from util import *
import datetime
import copy
print('Import alg2 module at', datetime.datetime.now())

def algorithmA(Table, flight, graph, graphPi, allocation, tag=2):

    check_allocation(Table, allocation)
    allocation = copy.deepcopy(allocation)

    config = {}
    # search depth
    config['depth'] = 5
    # recusive depth
    config['rec_depth'] = 3000
    #config['width'] = 2
    #config['time'] = 6
    config['ignore'] = set()
    config['reduce_cost'] = True
    config['Table'] = Table 
    config['flight'] = flight
    config['tag'] = tag 

    config['cost'] = getCost(Table, flight, allocation, config['tag']) 

    #print(allocation.items())
    k = 0
    n = len(allocation)
    cnt = 0

    print(config['cost'])
    for gate in allocation:
        k += 1
        print('{}/{}'.format(k, n))
        if len(allocation[gate]) == 0: 
            continue
        #config['ignore'].add(gate)
        for puck in allocation[gate].copy():
            if not puck in allocation[gate]: continue
            allocation[gate].remove(puck)
            remain = allocate(graph, graphPi, allocation, {puck}, config)
            if len(remain) == 0:
                print('  Reduced cost:', puck, config['cost'])
                cnt += 1
            else:
                allocation[gate].add(puck)
                #config['ignore'].remove(gate)
    print('\nTotal reduced:',cnt)
    print('Final cost:',config['cost'])
    check_allocation(Table, allocation)
    return allocation

def algorithmB(Table, flight, graph, graphPi, allocation, tag=2):
    check_allocation(Table, allocation)
    allocation = copy.deepcopy(allocation)

    config = {}
    # search depth
    config['depth'] = 5
    # recusive depth
    config['rec_depth'] = 3000
    #config['width'] = 2
    #config['time'] = 6
    config['ignore'] = set()
    config['reduce_cost'] = True
    config['Table'] = Table 
    config['flight'] = flight
    config['tag'] = tag 

    config['cost'] = getCost(Table, flight, allocation, config['tag']) 


    #print(allocation.items())
    sorted_gate = sorted(allocation.items(), key=lambda x:len(x[1]))
    k = 0
    n = len(sorted_gate)
    cnt = 0
    for gate, _ in sorted_gate:
        k+=1 
        print('{}/{}'.format(k, n))
        config['ignore'].add(gate)
        if len(allocation[gate]) == 0: continue
        pucks = allocation[gate]
        #allocation[gate] = {}
        alloc_bk = copy.deepcopy(allocation)
        remain = allocate(graph, graphPi, allocation, pucks, config)
        if len(remain) == 0:
            print('  Reduced gate:', gate)
            allocation[gate] = set()
            cnt += 1
            #print(config['ignore'])
            #break
        else:
            config['ignore'].remove(gate)
            allocation = alloc_bk
    print('\nTotal reduced gates:',cnt)
    check_allocation(Table, allocation)
    return allocation