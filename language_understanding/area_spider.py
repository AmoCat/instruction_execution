#!/usr/bin/env python
#coding:utf-8

import os
import sys
import urllib2
from bs4 import BeautifulSoup
import cPickle as pkl
from CH_phonetic import get_phonetic
import time

MEITUAN_URL = "http://hotel.meituan.com/search/jiudian/%s?search=1&ci=2016-10-19&co=2016-10-20&sort=&w=&page=&attrs="
DATA_DIR = os.path.join(os.path.dirname(__file__),'data')
AREAS_PATH = os.path.join(DATA_DIR,'dump_areas_data')
ORIGIN_AREADATA_PATH = os.path.join(DATA_DIR,'origin_areas_data')
CITIES_PATH = os.path.join(DATA_DIR,'china_cities.txt')

def get_area(cnt, city_name = 'haerbin'):
    if city_name == 'zhongqing':
        city_name = 'chongqing'
    if os.path.exists(os.path.join(AREAS_PATH,city_name)) == True:
        return cnt
    request_url = MEITUAN_URL % (city_name)
    print 'city_name = ',city_name,'cnt = ',cnt
    req = urllib2.Request(request_url)
    req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
    try:
        response = urllib2.urlopen(req)
        response_html = response.read().decode('utf-8')
        soup = BeautifulSoup(response_html,'html.parser')
    except Exception,e:
        print sys.stderr,e
        return cnt

    if soup == None:
        return cnt
    data = dict()
    file_path = os.path.join(ORIGIN_AREADATA_PATH, city_name + ".txt")
    out = open(os.path.join(file_path), 'w')
    for list in  soup.findAll('ul', class_ = "filter-sect-list sub-filter-sect-w__content"):
        areas = list.findAll('li')
        for l in areas:
            #if 'haerbin' in l.a['href']:
            #    out.close()
            #    os.system("rm "+file_path)
            #    return cnt
            #    print l.a['id'],l.string.encode('utf-8')
            data[l.string.encode('utf-8')] = l.a['id']
            out.write(l.string.encode('utf-8')+("/"+l.a['id']+"\n").encode('utf-8'))
    out.close()
    pkl.dump(data, open(os.path.join(AREAS_PATH, city_name),'w'))
    if cnt % 3 == 0:
        time.sleep(60)
    return cnt+1

def spider():
    with open(CITIES_PATH,'r') as cities:
        cnt = 0
        for line in cities:
            name = get_phonetic(line.strip())
            cnt = get_area(cnt, city_name = name)

if  __name__ == '__main__':
    #spider()
    get_area(1)

