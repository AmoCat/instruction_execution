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
    if (not os.path.exists(origin_areas_path)) or (not os.path.exists(dump_areas_path)):
        return
    
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

def create_dict_of_all_city():
    with open(os.path.join(DATA_DIR, 'china_cities.txt'), 'r') as f:
        all = {}
        for line in f:
            phonetic = get_phonetic(line.strip())
            if phonetic == 'zhongqing':
                phonetic = 'chongqing'
            path = os.path.join(AREAS_PATH, phonetic)
            if not os.path.exists(path):
                continue
            f = open(path, 'r')
            dictionary = pkl.load(f)
            all.update(dictionary)
            f.close()
        print all['五道口'][1]
        pkl.dump(all, open(os.path.join(AREAS_PATH, 'all'), 'w'))

def test():
    path = os.path.join(AREAS_PATH, 'all')
    dict = pkl.load(open(path, 'r'))
    dict['哈工大'] = ('1haoxian_hagongda', '哈尔滨')
    dict['中央大街'] = ('zhongyangdajie', '哈尔滨')
    #del dict['大学']
    pkl.dump(dict, open(path, 'w'))
    print dict['哈工大'][1]

if __name__ == '__main__':
    #add_all_cityname()
    #create_dict_of_all_city()
    test()
