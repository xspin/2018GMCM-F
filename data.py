#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd
import copy, time
import matplotlib.pyplot as plt
import numpy as np
import datetime
from util import *


data_file = "./InputData.xlsx"


Hd = {"pk_no": "飞机转场记录号",
          "in_date": "到达\n日期",
          "in_time": "到达\n时刻",
          "in_flight": "到达\n航班",
          "in_type": "到达类型",
          "plane_type": "飞机型号",
          "out_date": "出发\n日期",
          "out_time": "出发\n时刻",
          "out_flight": "出发\n航班", 
          "out_type": "出发类型", 
          "up_airport": "上线\n机场" ,
          "down_airport": "下线\n机场",
          "gust": "旅客\n记录号",
          "#gust": "乘客数",
          "gate": "登机口",
          "hall": "终端厅",
          "area": "区域",
          "body_type": "机体类别"
         }
        
Hdd = copy.deepcopy(Hd)
for k in Hd: Hdd[k] = Hdd[k].replace('\n', '')
#sheet: Pucks, Tickets, Gates  
class Sheet:
    def __init__(self, df):
        self.df = df
        self.dict = {}
        self.__build()

    def __getitem__(self, key):
        return self.dict[key]

    def __build(self):
        temp = {}
        for new_key, old_key in Hd.items():
            temp[old_key] = new_key
        self.df.rename(columns=temp, inplace=True)
        for i, row in self.df.iterrows():
            self.dict[row[0]] = row


class Puck(Sheet):
    pass
    # def __init__(self, df):
    #     Sheet.__init__(self, df)

class Ticket(Sheet):
    pass

class Gate(Sheet):
    pass



def filter_data(df):
    return df[(df[Hd['in_date']].dt.strftime('%d')=='20') | (df[Hd['out_date']].dt.strftime('%d')=='20')].reset_index(drop=True)
    # return df[Hd['in_date']].dt.strftime('%d')


# required dicts:
# in_flight[id]

class Flight:
    star_cnt = 0
    def __init__(self, puck, tag):
        if not tag in ['in', 'out']:
            print("Input error!")
            exit()
        self.puck = puck
        self.name = puck[tag+'_flight']
        self.date = int(puck[tag+'_date'].strftime("%d"))
        if not type(puck[tag+'_time']) is str:
            self.time = (int(puck[tag+'_time'].strftime("%H")), int(puck[tag+'_time'].strftime("%M")))
        else:
            self.time = tuple(map(int, puck[tag+'_time'].split(':')))
        self.type = puck[tag+'_type']
        self.plane_type = puck['plane_type']



def data_process():
    print("Loading data from", data_file)
    Table = pd.read_excel(data_file, sheet_name=None)
    # 去除规定时间外的数据
    print("Removing the data out of the time range ...")
    Table["Pucks"]  = filter_data(Table["Pucks"])
    Table["Tickets"]  = filter_data(Table["Tickets"])

    print('Constructing Tables ...')
    puck = Puck(Table["Pucks"])
    ticket = Ticket(Table["Tickets"])
    gate = Gate(Table["Gates"])
    Table = {}
    Table['Puck'] = puck
    Table['Ticket'] = ticket
    Table['Gate'] = gate

    print('Getting in/out flight dicts ...')
    flight = {}
    for i, row in puck.df.iterrows():
        inkey, outkey = row['in_flight'], row['out_flight']
        if '*' in inkey:
            Flight.star_cnt += 1
            inkey = "**{}**".format(Flight.star_cnt)
        if '*' in outkey:
            Flight.star_cnt += 1
            outkey = "**{}**".format(Flight.star_cnt)

        inflight = 'in' + row['in_date'].strftime('%d') + inkey
        outflight = 'out' + row['out_date'].strftime('%d') + outkey 

        if inflight in flight:
            print('Error: find duplicated in-flight', inflight)
            print(row['in_date'].strftime("%d"), row['out_date'].strftime("%d"))
            pk = flight[inflight].puck
            print(pk['in_date'], pk['out_date'])
        if outflight in flight:
            print('Error: find duplicated out-flight', outflight)
            print(row['in_date'].strftime("%d"), row['out_date'].strftime("%d"))
            pk = flight[outflight].puck
            print(pk['in_date'], pk['out_date'])
        flight[inflight] = Flight(row, 'in')
        flight[outflight] = Flight(row, 'out')
    return Table, flight

def getpalloc(alloc):
    palloc = {}
    for gate, pks in alloc.items():
        for pk in pks: palloc[pk] = gate                  
    return palloc

def savecsv(Table, alloc1, alloc2, alloc3):
    print('saving to csv file, ', datetime.datetime.now())
    pucks = Table['Puck'].df.copy()

    galloc1 = []
    galloc2 = []
    galloc3 = []

    palloc1 = getpalloc(alloc1)
    for _, row in pucks.iterrows():
        if row['pk_no'] in palloc1:
            gate = palloc1[row['pk_no']]
        else: gate = ''
        galloc1.append(gate)

    palloc2 = getpalloc(alloc2)
    for _, row in pucks.iterrows():
        if row['pk_no'] in palloc1:
            gate = palloc2[row['pk_no']]
        else: gate = ''
        galloc2.append(gate)

    palloc3 = getpalloc(alloc3)
    for _, row in pucks.iterrows():
        if row['pk_no'] in palloc1:
            gate = palloc3[row['pk_no']]
        else: gate = ''
        galloc3.append(gate)

    pucks.rename(columns=Hdd, inplace=True)
    pucks['问题一登机口'] = galloc1
    pucks['问题二登机口'] = galloc2
    pucks['问题三登机口'] = galloc3
    pucks.to_csv('output/Output.csv', sep=',', index=False)

print('Import data module at', datetime.datetime.now())
