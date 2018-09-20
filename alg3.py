#!/usr/bin/python3
# -*- coding: utf-8 -*-

from util import *
import datetime
import copy
import alg2 as Alg2
print('Import alg2 module at', datetime.datetime.now())

def algorithmA(Table, flight, graph, graphPi, allocation):
    return Alg2.algorithmA(Table, flight, graph, graphPi, allocation, tag=3)

def algorithmB(Table, flight, graph, graphPi, allocation):
    return Alg2.algorithmB(Table, flight, graph, graphPi, allocation, tag=3)
