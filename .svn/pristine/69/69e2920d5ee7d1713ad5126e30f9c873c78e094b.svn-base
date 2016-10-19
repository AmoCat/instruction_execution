# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import re
import os
import traceback

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
HOTEL_NAME_PATH = os.path.join(DATA_DIR,'hotel_name.txt')
HOME_TYPE_PATH = os.path.join(DATA_DIR,'type.txt')

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
