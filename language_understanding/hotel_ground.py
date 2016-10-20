# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import re
import os
import traceback
import cPickle as pkl

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
	file_path = os.join(AREAS_PATH, city)
	area_dict = pkl.load(file_path)
	if area_dict[orig]:
		return orig,area_dict[orig]
	for k,v in area_dict:
		if orig in k:
			return k,v
	return default,default