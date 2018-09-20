from util import *
import copy

class Graph:
    def __init__(self):
        self.vertex = None
        self.adj = None
        self.type = 0
    def copy(self):
        return copy.deepcopy(self)
    
    def deg(self, k):
        return len(self.adj[k])

    def remove(self, k):
        # if not type(k) is str: k = self.vertex[k]
        if not k in self.adj:
            print('[remove] Warning: no such node', k)
            return
        # remove edge (k,v) from each k's neibore v 
        for v in self.adj[k]:
            self.adj[v].remove(k)
        # remove node k 
        if self.type == 1:
            if k in self.vertex[0]: self.vertex[0].remove(k)
            elif k in self.vertex[1]: self.vertex[1].remove(k)
        else:
            self.vertex.remove(k)
        del self.adj[k]

    def remove_nb(self, k):
        if not k in self.adj:
            print('[remove_nb] Warning: no such node', k)
            return
        for v in self.adj[k].copy(): self.remove(v)
        self.remove(k)

    def size(self, m=None):
        if m is None: return len(self.adj)
        else: return (len(self.vertex[m]))
    def stat(self, k=8):
        avg_deg = 0.0
        i = 0
        print('-'*80)
        if self.type == 0:
            vtx = self.adj
        else:
            vtx = [v for v in self.vertex[0]]
            vtx.extend([v for v in self.vertex[1]])
            
        for v in vtx:
            print('{}: {}'.format(v, self.deg(v)), end=', ')
            if i==k-1: print('')
            avg_deg += self.deg(v)
            i = (i+1)%k
        print('\n\nAverage degree:', avg_deg/self.size())
        print('Size:', self.size())
        print('-'*80)
class GraphT(Graph):
    def __init__(self, puck):
        Graph.__init__(self)
        self.build(puck)
        
    def build(self, puck):
        print('Building time-conflict Graph ...')
        self.vertex = {pk for pk in puck.dict}
        self.adj = {}
        for pi in (self.vertex):
            if not pi in self.adj: self.adj[pi] = set()    
            for pj in (self.vertex):
                if pi == pj: continue 
                if conflict_time(puck[pi], puck[pj]):
                    self.adj[pi].add(pj)

class GraphP(Graph):
    def __init__(self, puck, gate, inv=False):
        Graph.__init__(self)
        self.type = 1
        self.build(puck, gate, inv)

    def build(self, puck, gate, inv):
        if inv:
            print('Building type-nonconflict Graph ...')
        else:
            print('Building type-conflict Graph ...')
        self.vertex = ({pk for pk in puck.dict}, {g for g in gate.dict})
        self.adj = {}
        for p in self.vertex[0]: self.adj[p] = set() 
        for g in self.vertex[1]: self.adj[g] = set() 

        for p in self.vertex[0]:
            for g in self.vertex[1]:
                isconf = conflict_type(puck[p], gate[g])
                if not inv and isconf:
                    self.adj[p].add(g)
                    self.adj[g].add(p)
                if inv and not isconf:
                    self.adj[p].add(g)
                    self.adj[g].add(p)
        if not inv:
            for g1 in self.vertex[1]:
                for g2 in self.vertex[1]:
                    if g1 != g2:
                        if g1 in self.adj:
                            self.adj[g1].add(g2)
                
class GraphTP(Graph):
    def __init__(self, puck, gate, inv=False):
        Graph.__init__(self)
        self.type = 1
        self.build(puck, gate, inv)

    def build(self, puck, gate, inv):
        if inv:
            print('Building time-type-nonconflict Graph ...')
        else:
            print('Building time-type-conflict Graph ...')
            
        self.vertex = ({pk for pk in puck.dict}, {g for g in gate.dict})
        self.adj = {}
        for p in self.vertex[0]: self.adj[p] = set() 
        for g in self.vertex[1]: self.adj[g] = set() 
            
        for pi in (self.vertex[0]):    
            for pj in (self.vertex[0]):
                if pi == pj: continue 
                isconf = conflict_time(puck[pi], puck[pj])
                if not inv and isconf:
                    self.adj[pi].add(pj)
                if inv and not isconf:
                    self.adj[pi].add(pj)

        for p in self.vertex[0]:
            for g in self.vertex[1]:
                isconf = conflict_type(puck[p], gate[g])
                if not inv and isconf:
                    self.adj[p].add(g)
                    self.adj[g].add(p)
                if inv and not isconf:
                    self.adj[p].add(g)
                    self.adj[g].add(p)
        if not inv:
            for g1 in self.vertex[1]:
                for g2 in self.vertex[1]:
                    if g1 != g2:
                        self.adj[g1].add(g2)

def statistic(puck, gate):
    puck_class = {}
    gate_class = {}
    gt_class = {}
    for _, pk in puck.dict.items():
        c = get_puck_type(pk)
        if c in puck_class: puck_class[c] += 1
        else: puck_class[c] = 1
    for _, gt in gate.dict.items():
        c = get_gate_type(gt)
        if c in gate_class: gate_class[c] += 1
        else: gate_class[c] = 1
        for intp in gt['in_type'].replace(', ',''):
            for outtp in gt['in_type'].replace(', ',''):
                c = intp+outtp+gt['body_type']
                if c in gt_class: gt_class[c] += 1
                else: gt_class[c] = 1 
        
    print('Gate classes:')
    s = 0
    for gt_type, val in gate_class.items():
        s += val
        cnt = 0
        a, b = gt_type.split('|')
        for pk_type, v in puck_class.items():
            if pk_type[0] in a and pk_type[1] in b and pk_type[2] in b:
                cnt += v
        print('  {:6s}: {}\t Compatible punks: {}'.format(gt_type, val, cnt))
    print('  Count: {}, Classes: {}'.format(s, len(gate_class)))
    print('-----------')
    s = 0
    for gt_type, val in gt_class.items():
        s += val
        print('  {}: {}'.format(gt_type, val))
    print('  Count: {}, Classes: {}'.format(s, len(gt_class)))
    print('Puck classes:')
    s = 0
    for pk_type, val in puck_class.items():
        s += val
        cnt = 0
        for gttp, v in gate_class.items():
            a, b = gttp.split('|')
            if pk_type[0] in a and pk_type[1] in b and pk_type[2] in b: 
                cnt += v
        print('  {}: {:3d}\t Compatible gates: {}'.format(pk_type, val, cnt))
    print('  Count: {}, Classes: {}'.format(s, len(puck_class)))


def graph_plot(graph, allocation=None):
    print('ploting ...')
    plt.figure(figsize=(12,12))
    R = 50
    pos = {}
    if graph.type == 0:
        for i, v in enumerate(sorted(graph.vertex)):
            t = 2*np.pi*i/graph.size()
            pos[v] = R*np.cos(t), R*np.sin(t) 
            plt.plot(*pos[v], 'ko', ms=2)
            #plt.text(*pos[v],v)
            #for v in graph.vertex:    
        v = 'PK254'
        plt.text(*pos[v],v)
        for u in graph.adj[v]:
            if pos[v] <= pos[u]:
                plt.plot([pos[v][0], pos[u][0]], [pos[v][1], pos[u][1]], 'b', lw=1)
    else:
        vertex = sorted(graph.vertex[0]|graph.vertex[1])
        for i, v in enumerate(vertex):
            t = 2*np.pi*i/graph.size()
            pos[v] = R*np.cos(t), R*np.sin(t) 
            tag = 'ko' if v[0]=='P' else 'r>'
            plt.plot(*pos[v], tag, ms=2)
        for v in graph.vertex[0]:
            for u in graph.adj[v]:
                plt.plot([pos[v][0], pos[u][0]], [pos[v][1], pos[u][1]], 'b', lw=1)
            break
    plt.show()


print('Import graph module at', datetime.datetime.now())