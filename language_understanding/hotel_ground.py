# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import re
import os
import traceback
import cPickle as pkl
from CH_phonetic import get_phonetic

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HOTEL_NAME_PATH = os.path.join(DATA_DIR,'hotel_name.txt')
HOME_TYPE_PATH = os.path.join(DATA_DIR,'type.txt')
AREAS_PATH = os.path.join(DATA_DIR,'dump_areas_data')

def hotel_ground(orig, default = None):
    hotel_names = json.load(open(HOTEL_NAME_PATH))
    for k,v in hotel_names.items():
        if k in orig:
            return v
    return default

def type_ground(orig, default = None):
    type = json.load(open(HOME_TYPE_PATH))
    for k,v in type.items():
        if k in orig: return v
    return default

def area_ground(orig, city, default = None):
    city = get_phonetic(city)
    file_path = os.path.join(AREAS_PATH, city)
    area_dict = pkl.load(open(file_path,'r'))
    print "orig=",orig,",",area_dict[orig.encode('utf-8')]
    if area_dict[orig.encode('utf-8')]:
        return orig,area_dict[orig.encode('utf-8')]
    for k,v in area_dict:
        if orig in k:
            return k,v##v[0][0]为对应id
    return default,default
