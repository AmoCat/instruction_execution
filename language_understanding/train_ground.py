#coding:utf-8
from datetime import datetime, timedelta
import json
import re
import os
import traceback

def type_ground(orig, default = None):
    orig = orig.encode('utf-8')
    print "orig=",orig
    type_dic = {'动车':'动车组','高铁':'高速动车','特快':'空调特快','直达':'直达特快'}
    for k,v in type_dic.items():
        if k in orig:
            return v
    t_dic = {'快':'快速'}
    for k,v in t_dic.items():
        if k in orig:
            return v
    return orig


def trainnum_ground(orig, default = None):
    orig = orig.replace('特快','T')
    orig = orig.replace('快','K')
    orig = orig.replace('直达','Z')
    orig = orig.replace('高铁','G')
    orig = orig.replace('动车','D')
    return orig