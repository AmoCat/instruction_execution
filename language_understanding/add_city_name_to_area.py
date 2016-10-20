#!/usr/bin/env python
#coding:utf-8

import os
import sys
from CH_phonetic import get_phonetic
import cPickle as pkl

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AREAS_PATH = os.path.join(DATA_DIR, 'dump_areas_data')
ORIGIN_AREAS_PATH = os.path.join(DATA_DIR, 'origin_areas_data')

def add_cityname(city):
    city_phonetic = get_phonetic(city)
    if city_phonetic == 'zhongqing':
        city_phonetic = 'chongqing'
    dump_areas_path = os.path.join(AREAS_PATH, city_phonetic)
    origin_areas_path = os.path.join(ORIGIN_AREAS_PATH, city_phonetic + ".txt")
    
    data = dict()
    with open(origin_areas_path, 'r') as f:
        list = []
        for line in f:
            list.append(line)

    with open(origin_areas_path, 'w') as f:
        for l in list:
            words = l.strip().split('/', 2)
            f.write(words[0] + '/' +  words[1] + '/' + city + '/' + city_phonetic + '\n')
            data[words[0]] = (words[1], city)
    
    pkl.dump(data, open(dump_areas_path, 'w'))

def add_all_cityname():
    with open(os.path.join(DATA_DIR, 'china_cities.txt'), 'r') as f:
        for line in f:
            add_cityname(line.strip())

if __name__ == '__main__':
    add_all_cityname()
