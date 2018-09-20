from util import *
import datetime
import copy

def algorithm1A(Table, graph, graphPi):
    graph = graph.copy()
    graphPi = graphPi.copy()
    
    allocate = {}
    rd = 0
    
    while graph.size(0)>0 and graph.size(1)>0:
        rd += 1
        print('Round', rd)
        #print('  copy graphs')
        #gT = graphT.copy()
        gP = graph.copy()
        #gPi = graphP_inv
        
        # Find gate with maximum conflict in gP
        #print('  find the gate with maximum conflict')
        gate = None 
        for v in gP.vertex[1]:
            if gate is None or gP.deg(v)>gP.deg(gate):
                gate = v
        #print('  conflicts:', gP.deg(gate))
        # Remove gate from gP and gPi
        #print("  remove gate {} NBs from Graph".format(gate))
        gP.remove_nb(gate)
        #graphPi.remove_nb(gate)
        allocate[gate] = set()
        
        #print('  find maximal non-conflict puck set')
        while gP.size(0)>0:
            # Find puck with minimum gate choices
            puck = None
            for v in gP.vertex[0]:
                #if puck is None or graphPi.deg(v)+gP.deg(v)<graphPi.deg(puck)+gP.deg(puck):
                if puck is None or gP.deg(v)<gP.deg(puck):
                    puck = v
            if puck is None: break
            #print('  gT remove')
            #gT.remove_nb(puck)
            #print('  gP remove')
            gP.remove_nb(puck)
            #print('  gPi remove')
            #graphPi.remove(puck)
            allocate[gate].add(puck)
            
        # Remove the pucks and gate from graph graphT graphP graphPi
        #print('  remove the allocation from Graph')
        # graphT.remove(gate)
        graph.remove(gate)
        graphPi.remove(gate)
        for p in allocate[gate]:
            #graphT.remove(p)
            graph.remove(p)
            #graphPi.remove(p)
        print('  allocate gate {} with {} pucks'.format(gate, len(allocate[gate])))
        print('  remain {} gates and {} pucks'.format(graph.size(1), graph.size(0)))
    print('='*40)
    alt = 0
    cnt = 0
    for gate in allocate:
        if len(allocate[gate])>0:
            print('Gate {} [{}]: {}'.format(gate,get_gate_type(Table['Gate'][gate]), len(allocate[gate])))
            alt += 1
            cnt += len(allocate[gate])
    score = cnt - 0.5*alt
    print('\nTotal rounds:', rd)
    print('Used gates:', alt)
    print('Allocated pucks:', cnt)
    print('Remain pucks:', graph.size(0))
    print('Number of pucks:', graphPi.size(0))
    print('Score:', score)
    
    return allocate, graph.vertex[0]


# step 2: allocate more pucks
 
def algorithm1B(Table, graph, graphPi, allocation, pucks):
    # 将未分配航班尽量分配出去
    # 先尝试将未分配puck插入登机口，可能会
    check_allocation(Table, allocation)
    allocation = copy.deepcopy(allocation)
    #pucks = set(sorted(remain)[0:6])
    #print(pucks)
    #pucks = {'PK399'}
    config = {}
    # search depth
    config['depth'] = 5
    # recusive depth
    config['rec_depth'] = 3000
    #config['width'] = 2
    config['time'] = 6
    config['ignore'] = {}
    config['cost'] = 0

    remain = allocate(graph, graphPi, allocation, pucks, config)

    cnt = len(pucks)-len(remain)
    if cnt==0: print('No re-allocation!')
    else: print('Success allocation:', cnt)

    print('Remain {} pucks'.format(len(remain)))
    check_allocation(Table, allocation)
    return allocation, remain

    #diff(allocation, alloc)
def algorithm1C(Table, graph, graphPi, allocation):
    # 尽量减少使用的登机口数
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
    config['cost'] = 0

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
    

print('Import Alg1 module at', datetime.datetime.now())