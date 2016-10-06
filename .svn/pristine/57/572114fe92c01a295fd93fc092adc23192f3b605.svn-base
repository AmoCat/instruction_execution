# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import re
import os
import traceback

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AIRPORT_MAP_PATH = os.path.join(DATA_DIR, 'china_airports.txt')
AIRLINE_PATH = os.path.join(DATA_DIR,'china_airline.txt')

airport_map = json.load(open(AIRPORT_MAP_PATH))
airline_map = json.load(open(AIRLINE_PATH))

def airport_ground(orig, default=None):
    orig = orig.replace("国际机场".decode("utf-8"),"".decode("utf-8"))
    orig = orig.replace("飞机场".decode("utf-8"),"".decode("utf-8"))
    for k,v in airport_map.items():
        if orig in v:
            return v
    return orig

def airline_ground(orig, default = None):
    orig = orig.replace("航空公司".decode("utf-8"),"".decode("utf-8"))
    for k,v in airline_map.items():
        if orig in k or orig == v:
            return v
    return default

def get_loc(orig, default=None):
    for k,v in airport_map.items():
        if orig in v:
            if k == u'北京1':
                k = u'北京'
            if k == u'上海1':
                k = u'上海'
            return k,v
    return default,default