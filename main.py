
# coding: utf-8
import importlib as imp
import data as Data
import util as Util
import alg1 as Alg1
import alg2 as Alg2
import alg3 as Alg3
import copy
import plot as plot
from data import savecsv, getpalloc
import graph as Graph
import os

# 读取和处理数据
Table, flight = Data.data_process()

#建立各需要的图
# 总冲突图
graph = Graph.GraphTP(Table['Puck'], Table['Gate'])
#graphT = Graph.GraphT(Table['Puck'])
# 航班与登机口间的冲突图
graphP = Graph.GraphP(Table['Puck'], Table['Gate'])
# 航班与登机口兼容性冲突图
graphPi = Graph.GraphP(Table['Puck'], Table['Gate'], inv=True)
# 统计图中的信息
Graph.statistic(Table['Puck'], Table['Gate'])

# 问题一步骤A
alloc1A, remain1A = Alg1.algorithm1A(Table, graph, graphPi)
Util.check_allocation(Table, alloc1A, remain1A)
# 问题一步骤B
alloc1B, remain1B = Alg1.algorithm1B(Table, graph, graphPi, alloc1A, remain1A)
# 问题一步骤c
alloc1 = Alg1.algorithm1C(Table, graph, graphPi, alloc1B)
#Util.check_allocation(Table, alloc1C)

# 问题二算法
alloc2A = Alg2.algorithmA(Table, flight, graph, graphPi, alloc1)
alloc2 = Alg2.algorithmB(Table, flight, graph, graphPi, alloc2A)

# 问题三算法
alloc3A = Alg3.algorithmA(Table, flight, graph, graphPi, alloc2)
alloc3 = Alg3.algorithmB(Table, flight, graph, graphPi, alloc3A)

# 题一算法结果画图
if not os.path.isdir('output'): os.mkdir('output')
puckalloc1 = getpalloc(alloc1)
plot.plot_alg1(Table, alloc1, puckalloc1)

# 对于题二三算法结果，建立令有中转时间和紧张度等数据的图
cgraph = Util.CostGraph(Table, flight, getpalloc(alloc2))
plot.plot_alg23(Table, cgraph, 2)

cgraph = Util.CostGraph(Table, flight, getpalloc(alloc3))
plot.plot_alg23(Table, cgraph, 3)

# 分配结果导出csv文件
# alloc1C, alloc2, alloc3 分别是三个题的分配结果
Data.savecsv(Table, alloc1, alloc2, alloc3)

