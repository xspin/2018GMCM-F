import datetime
import copy
import time
import numpy as np
#from data import Time
print('Import util module at', datetime.datetime.now())

Body = {'W': {'332', '333', '33E', '33H', '33L', '773'}, 
        'N': {'319', '320', '321', '323', '325', '738', '73A', '73E', '73H', '73L'}}

class Time:
    process_time = [[15, 20, 35, 40],
                    [20, 15, 40, 35],
                    [35, 40, 20, 30],
                    [40, 45, 30, 20]]
    trans_time = [[0,1,0,1],[1,0,1,0],[0,1,0,1],[1,2,1,0]]
    Time_process = np.array(process_time).reshape([2,2,2,2])     
    Time_trans = np.array(trans_time).reshape([2,2,2,2])     
    Idx = {'D':0, 'I':1, 'T':0, 'S':1}
    area_type = ['T-North','T-Center','T-South','S-North','S-Center','S-South','S-East']
    for i, v in enumerate(area_type):
        Idx[v] = i
    Time_move = [[10],[15,10],[20,15,10],[25,20,25,10], [20,15,20,15,10],[25,20,25,20,15,10],[25,20,25,20,15,20,10]]    

    def Time(self, tag, in_type=None, in_gate=None, out_type=None, out_gate=None, in_area=None, out_area=None):
        penalty = 360
        if tag == 'walk':
            i, j = self.Idx[in_area], self.Idx[out_area]
            if i>j: return self.Time_move[i][j]
            else: return self.Time_move[j][i]
        if not all([in_type, in_gate, out_type, out_gate]): 
            #print('penalty')
            return penalty
        it = self.Idx[in_type]
        ig = self.Idx[in_gate]
        ot = self.Idx[out_type]
        og = self.Idx[out_gate]
        if tag == 'process':
            return self.Time_process[it,ig,ot,og] 
        elif tag == 'trans':
            return self.Time_trans[it,ig,ot,og]*8 
    def Time_test(self):
        for i, ina in enumerate(self.area_type):
            for outa in self.area_type[i:]:
                print('{} {}: {}'.format(ina,outa,Time('walk', in_area=ina, out_area=outa)))
            print()

        for i, di in enumerate('DI'):
            for u, tu in enumerate('TS'):
                for j, dj in enumerate('DI'):
                    for v, tv in enumerate('TS'):
                        print('{}{}-{}{}: {} {}'.format(di,tu,dj,tv,
                                self.Time_process[i,u,j,v],
                                self.Time('trans',in_type=di,in_gate=tu,out_type=dj,out_gate=tv)))
 
def bt(plane_type):
    plane_type = str(plane_type)
    if plane_type in Body['N']: return 'N'
    elif plane_type in Body['W']: return 'W'
    else: print('Error plane type:', plane_type)
    
def get_puck_type(pk):
    return pk['in_type']+pk['out_type']+bt(pk['plane_type'])
def get_gate_type(gt):
    return gt['in_type'].replace(', ','') +'|'+ gt['out_type'].replace(', ','')+gt['body_type']
    
def gettime(date, time):
    d = int(date.strftime('%d'))
    if type(time) is str:
        hm = tuple(map(int, time.split(':')))
    else:
        hm = (int(time.strftime("%H")), int(time.strftime("%M")))
    return (d-19)*24*60 + hm[0]*60 + hm[1]
    #return (d, hm[0], hm[1])

def conflict_time(pucka, puckb): #(series, series)
    timea = [gettime(pucka['in_date'], pucka['in_time'])-45,
            gettime(pucka['out_date'], pucka['out_time'])+45]
    timeb = [gettime(puckb['in_date'], puckb['in_time'])-45,
            gettime(puckb['out_date'], puckb['out_time'])+45]
    for ta in timea:
        if timeb[0]<=ta<=timeb[1]: return True
    for tb in timeb:
        if timea[0]<=tb<=timea[1]: return True
    return False

def conflict_type(puck, gate):
    in_type = gate['in_type']
    out_type = gate['out_type']
    body_type = str(gate['body_type'])
    puck_in_type = puck['in_type']
    puck_out_type = puck['out_type']
    puck_body = str(puck['plane_type'])
    if not in_type in ['I', 'D', 'D, I']:
        print('Error: in_type Error!', in_type)
    if not out_type in ['I', 'D', 'D, I']:
        print('Error: out_type Error!', out_type)
    if not puck_in_type in 'ID':
        print('Error: puck_in_Type Error!', puck_in_type)
    if not puck_out_type in 'ID':
        print('Error: puck_out_Type Error!', puck_out_type)
    if not puck_body in Body['N'] and not puck_body in Body['W']:
        print('Error: Body Type Error!', puck_body)
        
    if not puck_in_type in in_type: return True
    if not puck_out_type in out_type: return True
    if not puck_body in Body[body_type]: return True
    return False

def allocate(graph, gpi, allocation, pucks, config):
    debug = False
    if not 'width' in config:
        config['width'] = 10
    if not 'rec_depth' in config:
        config['rec_depth'] = 1024
    if not 'time' in config:
        config['time'] = 600
    remains = set()
    #allocation = copy.deepcopy(allocation)
    pucks = sorted(pucks, key=lambda p:graph.deg(p))
    for i, puck in enumerate(pucks):
        config['max_width'] = 0
        config['start_time'] = time.time()
        config['max_depth'] = 0
        if debug:
            print('{}/{} {}'.format(i+1,len(pucks), puck))
        stack = [(puck, None, config['depth'], 0)]
        ok = allocate_puck(graph, gpi, allocation, stack, config)
        #print('  stack:', len(stack))
        if debug:
            print('  max stack size:', config['max_width'])
            print('  max recusive depth:', config['max_depth'])
        if ok:
            gate = ''
            for g in allocation:
                if puck in allocation[g]: gate = g
            print('  Allocation success: {} -> {}'.format(puck, gate))
        else: 
            remains.add(puck)
            #print('Allocation fail:', puck)
            pass
    return remains
    
def allocate_puck(graph, gpi, allocation, stack, config):
    debug = False
    config['max_depth'] += 1
    config['max_width'] = max(config['max_width'], len(stack))
    # graph: time-type-conflict graph
    # gpi: type-nonconflict graph
    if len(stack)==0: #全部分配成功
        if 'cost_reduce' in config and config['cost_reduce']:
            cost = getCost(config['Table'], config['flight'], allocation, config['tag'])
            if cost >= config['cost']: return False
            else: config['cost'] = cost
        return True
    # 最小冲突的puck优先分配
    puck, ignore_gate, depth, index = stack.pop()
    ok = False
    # 遍历与puck兼容的gate
    for gate in gpi.adj[puck]:
        if gate == ignore_gate or gate in config['ignore']: continue
        # 与puck冲突的pks
        pks = sorted([pk for pk in allocation[gate] if pk in graph.adj[puck]], key=lambda p:-graph.deg(p))
        #pks = [pk for pk in allocation[gate] if pk in graph.adj[puck]]
        # 达到限制深度，且不能分配则退出
        if depth<=0 and len(pks)>0: continue
        if len(pks)>0:
            # 超过时间限制
            if time.time()-config['start_time']>config['time']: 
                print('  {:.2f}s'.format(time.time()-config['start_time']))
                break
            if config['max_depth']>config['rec_depth']:
                #print('reach max depth')
                break
        # 如果宽度超限了则不再向下搜索
        if len(stack)+len(pks)>config['width']: continue
        # 按冲突排序放入栈中
        for pk in pks: stack.append((pk, gate, depth-1, index+1))
        # 将puck分配到gate
        if puck in allocation[gate]: print('#Error: duplicated add')
        allocation[gate].add(puck)

        # 将冲突的pk从gate删除
        for pk in pks: 
            allocation[gate].remove(pk)
        if debug:
            print('Add: {} x {}'.format(len(pks),index+1))
            print('[{}]: '.format(index), end='')
            for _,_,_, i in stack: print(i, end=',')
            print('\n')
        # 递归分配stack中待分配的pucks
        ok = allocate_puck(graph, gpi, allocation, stack, config)
        # 如果不成功，回溯到之前状态
        if not ok:
            chg = 0
            if puck in allocation[gate]:
                allocation[gate].remove(puck)
            else:
                print('#Error: alloc remove', puck)
            for pk in pks: 
                allocation[gate].add(pk)
            # remove the pks from stack
            while len(stack)>0 and stack[-1][3] > index: 
                p,_,_,_ = stack.pop()
                #s += '  rm {}\n'.format(p)
            if debug:
                print('Remove:', index+1)
                print('[{}]: '.format(index), end='')
                for _,_,_, i in stack: print(i, end=',')
                print('\n')
                for _,_,_, i in stack: 
                    if i > index: print('#Error: index error!')
        #del pks
        # 如果分配成功（没有剩余）则返回True
        if ok: 
            break
    if not ok:
        stack.append((puck, ignore_gate, depth, index))
    return ok
    
def diff(alloc1, alloc2):
    print('='*40)
    print('Diff:')
    for gate in alloc1:
        d1 = [pk for pk in alloc1[gate] if not pk in alloc2[gate]]
        d2 = [pk for pk in alloc2[gate] if not pk in alloc1[gate]]
        if len(d1)>0 or len(d2)>0:
            print(gate)
            print('  alloc1:', d1)
            print('  alloc2:', d2)
    print('='*40)
  
def check_allocation(Table, allocate, remains=None):
    cnt = 0
    allocated_pucks = set()
    used_gates = set()
    isconf = False
    print('='*40)
    for gate, pks in allocate.items():
        allocated_pucks |= pks
        pks = list(pks)
        cnt += len(pks)
        if len(pks)==0: continue
        used_gates.add(gate)
        cf = [0] * len(pks)
        for i in range(len(pks)):
            if cf[i] == 1: continue
            for j in range(i+1, len(pks)):
                if conflict_time(Table['Puck'][pks[i]], Table['Puck'][pks[j]]):
                    cf[i], cf[j] = 1, 1
                    isconf = True
        if sum(cf)>0:
            print('  Gate {}: {}/{} conflict'.format(gate, sum(cf), len(pks)))
    if isconf: print('#Error: Find conflict!')
    else: print('No conflict found!')
    print('Total allocation:', cnt)
    print('Real Total allocation:', len(allocated_pucks))
    print('Used gates:', len(used_gates))
    if len(allocated_pucks)!=cnt:
        print('#Error: Duplicated allocation found!')
    if remains:
        wrong = False
        for pk in remains:
            if pk in allocated_pucks:
                print('#Error: Wrong remain puck', pk)
                wrong = True
        if not wrong: print('No wrong remain puck!')
    print('='*40)



Time = Time()
class CostGraph:
    def __init__(self, Table, flight, puckalloc, tag=2):
        self.Table = Table
        self.puckalloc = puckalloc
        self.pucks = set(Table['Puck'].dict.keys())
        self.gates = set(Table['Gate'].dict.keys()) 
        self.gust = {} # edge weight of puck-gate or puck-puck
        self.adj = {}
        self.cost = {}
        self.process_time = {}
        self.tensity = {}
        self.avg_tensity = 0 
        self.total_cost = 0
        self.penalty_count = 0
        self.fail_count = 0
        self.ticket_count = 0
        self.gust_count = 0

        for p in self.pucks: self.adj[p] = set() 
        for g in self.gates: self.adj[g] = set() 
        for _, row in Table['Ticket'].df.iterrows():
            inflight = 'in' + row['in_date'].strftime('%d') + row['in_flight']
            outflight = 'out' + row['out_date'].strftime('%d') + row['out_flight'] 
            num_gust = int(row['#gust'])
            if not inflight in flight: continue
            if not outflight in flight: continue
            inpuck = flight[inflight].puck['pk_no']
            outpuck = flight[outflight].puck['pk_no']
            key = inpuck+'->'+outpuck
            if key in self.gust: self.gust[key] += num_gust
            else: self.gust[key] = num_gust
            self.gust_count += num_gust 
            self.adj[inpuck].add(outpuck)
            self.ticket_count += 1
        self._get_cost()
        if tag == 3:
            self.total_cost = self.avg_tensity

    def _get_type(self, inpuck, outpuck):
        it = self.Table['Puck'][inpuck]['in_type']
        ot = self.Table['Puck'][outpuck]['out_type']
        if not inpuck in self.puckalloc: ingate = None
        else: ingate = self.puckalloc[inpuck]
        if not outpuck in self.puckalloc: outgate = None
        else: outgate = self.puckalloc[outpuck]
        if ingate is None or outgate is None:
            return None, None, None, None, None, None 
        ig = self.Table['Gate'][ingate]['hall']
        og = self.Table['Gate'][outgate]['hall']
        ia = ig + '-' + self.Table['Gate'][ingate]['area']
        oa = og + '-' + self.Table['Gate'][outgate]['area']
        return it, ig, ot, og, ia, oa

    def _get_cost(self):
        self.total_cost = 0
        for inpuck in self.adj:
            for outpuck in self.adj[inpuck]:
                sdate = (self.Table['Puck'][inpuck]['in_date'])
                stime = (self.Table['Puck'][inpuck]['in_time'])
                edate = (self.Table['Puck'][outpuck]['out_date'])
                etime = (self.Table['Puck'][outpuck]['out_time'])
                st = gettime(sdate, stime)
                et = gettime(edate, etime)
                dtime = et-st
                key = inpuck+'->'+outpuck
                it, ig, ot, og, ia, oa = self._get_type(inpuck, outpuck)
                #print(it,ig,ot,og)
                cost = Time.Time(tag='process',in_type=it,in_gate=ig,out_type=ot,out_gate=og)
                self.process_time[key] = cost
                self.total_cost += self.process_time[key]* self.gust[key]
                if it is None:
                    self.penalty_count += self.gust[key]
                else:
                    cost += Time.Time(tag='trans', in_type=it,in_gate=ig,out_type=ot,out_gate=og)
                    cost += Time.Time(tag='walk', in_area=ia, out_area=oa)
                self.cost[key] = cost
                if it and cost > dtime:
                    self.fail_count += 1

                time_in = gettime(self.Table['Puck'][inpuck]['in_date'], self.Table['Puck'][inpuck]['in_time'])
                time_out = gettime(self.Table['Puck'][outpuck]['out_date'], self.Table['Puck'][outpuck]['out_time'])
                self.tensity[key] = cost/(time_out-time_in)
                self.tensity[key] = min(self.tensity[key], 1.0)
                self.avg_tensity += self.tensity[key]
        self.avg_tensity /= self.gust_count

def getCost(Table, flight, allocation, tag):
    pkalloc = {} 
    for g, pks in allocation.items():
        for pk in pks: pkalloc[pk] = g
    cgraph = CostGraph(Table, flight, pkalloc, tag)
    return cgraph.total_cost