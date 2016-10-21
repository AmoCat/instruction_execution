#!usr/bin/env python
#coding:utf-8

import os
import sys

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AREAS_PATH = os.path.join(DATA_DIR, 'dump_areas_data')
ORIGIN_AREAS_PATH = os.path.join(DATA_DIR, 'origin_areas_data')

def add_city_name(city, filename = './beijing.txt'):
    file_path = os.path.join(ORIGIN_AREAS_PATH,city.)
