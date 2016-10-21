#!usr/bin/env python
#coding:utf-8

import os
import sys
import cPickle as pkl
from CH_phonetic import get_phonetic

DATA_DIR = os.path.join(os.path.dirname(__file__),'data')
AREA_PATH = os.path.join(DATA_DIR,'dump_areas_data')

def area_preprocessor(sent, city = None, default = None):
    if city == None:
        file_name = os.path.join(AREA_PATH, 'all')
    else:
        file_name = os.path.join(AREA_PATH, get_phonetic(city.strip()))
    try :
        f = open(file_name, 'r')
    except Exception, e:
        print sys.stderr,e
        return default, default
    dict = pkl.load(f)
    for k, v in dict.items():
        if k in sent.encode('utf-8'):
            f.close()
            return k, v
    f.close()
    return default, default
