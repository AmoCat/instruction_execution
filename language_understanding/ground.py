# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
import re
import os
import traceback

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
CITY_LEXICON_PATH = os.path.join(DATA_DIR, 'china_cities.txt')
PROVINCE_MAP_PATH = os.path.join(DATA_DIR, 'province_map.txt')

def hashweekdays(day):
    if day in [u'周一', u'星期一', u'礼拜一']:
        return 1
    if day in [u'周二', u'星期二', u'礼拜二']:
        return 2
    if day in [u'周三', u'星期三', u'礼拜三']:
        return 3
    if day in [u'周四', u'星期四', u'礼拜四']:
        return 4
    if day in [u'周五', u'星期五', u'礼拜五']:
        return 5
    if day in [u'周六', u'星期六', u'礼拜六']:
        return 6
    if day in [u'周日', u'周天' ,u'周末', u'星期天', u'星期日', u'礼拜日', u'礼拜天']:
        return 7

def hashnum(number):
    if re.match(u'一', number):
        return 1
    if re.match(u'二', number):
        return 2
    if re.match(u'两', number):
        return 2
    if re.match(u'三', number):
        return 3
    if re.match(u'四', number):
        return 4
    if re.match(u'五', number):
        return 5
    if re.match(u'六', number):
        return 6
    if re.match(u'七', number):
        return 7
    if re.match(u'八', number):
        return 8
    if re.match(u'九', number):
        return 9
    if re.match(u'十', number):
        return 10
    if re.match(u'十一', number):
        return 11
    if re.match(u'十二', number):
        return 12
    if re.match(u'十三', number):
        return 13
    if re.match(u'十四', number):
        return 14
    if re.match(u'十五', number):
        return 15
    if re.match(u'十六', number):
        return 16
    if re.match(u'十七', number):
        return 17
    if re.match(u'十八', number):
        return 18
    if re.match(u'十九', number):
        return 19
    if re.match(u'二十', number):
        return 20
    if re.match(u'二十一', number):
        return 21
    if re.match(u'二十二', number):
        return 22
    if re.match(u'二十三', number):
        return 23
    if re.match(u'二十四', number):
        return 24
    if re.match(u'二十五', number):
        return 25
    if re.match(u'二十六', number):
        return 26
    if re.match(u'二十七', number):
        return 27
    if re.match(u'二十八', number):
        return 28
    if re.match(u'二十九', number):
        return 29
    if re.match(u'三十', number):
        return 30
    if re.match(u'三十一', number):
        return 31

def time_ground(orig, default=None):
    base_time = 0
    hours = ur"(一|二|两|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|\
            二十|二十一|二十二|二十三|二十四)"
    start_hour = 0
    start_minute = 0
    end_hour = 24
    end_minute = 0
    try:
        if re.search(ur'下午|晚上|今晚|傍晚|明晚', orig):
            base_time = 12
        h = re.search(ur'(' + hours + ur'|(\d+))(点|时)', orig)
        if h:
            hour_num = 0
            if h.group(2):
                hour_num=hashnum(h.group(2))
            else:
                hour_num=int(h.group(3))
            if hour_num<12 and base_time == 12:
                hour_num += base_time
            start_hour = 0 if hour_num-1 < 0 else hour_num-1
            end_hour = 24 if hour_num+1 > 24 else hour_num+1
            return start_hour,start_minute,end_hour,end_minute
        else:
            if base_time == 12:
                if re.search(ur'下午', orig):
                    return 13,0,18,0
                if re.search(ur'晚上|明晚', orig):
                    return 18,0,24,0
                if re.search(ur'傍晚', orig):
                    return 17,0,19,0
            else:
                if re.search(ur'明早|早上|清晨|早晨', orig):
                    return 5,0,10,0
                if re.search(ur'中午|午时|正午|晌午',orig):
                    return 11,0,14,0
                if re.search(ur'上午',orig):
                    print "####return 上午"
                    return 8,0,12,0
    except Exception, e:
        exstr = traceback.format_exc()
        print exstr
        return start_hour,start_minute,end_hour,end_minute
    return start_hour,start_minute,end_hour,end_minute

def date_to_time(orig, default=None):
    try:
        if re.match(ur'今早|今晚|明早|明晚',orig):
            return orig
        d = re.match(ur'(明天|后天|大后天)',orig)
        if d:
            return orig.lstrip(d.group(1))
    except Exception, e:
        exrtr = traceback.format_exc()
        print exrtr
        return default
    return default

def date_format(orig, default = None):
    print "##date orig =",orig
    res = re.search(ur'([0-9]{2})(-|\.)([0-9]{1,2})(-|\.)([0-9]{1,2})',orig)
    if res:
        return 2000+int(res.group(1)),int(res.group(3)),int(res.group(5))
    res = re.search(ur'([0-9]{4})(-|\.)([0-9]{1,2})(-|\.)([0-9]{1,2})',orig)
    if res:
        return int(res.group(1)),int(res.group(3)),int(res.group(5))
    res = re.search(ur'([0-9]{1,2})(-|\.)([0-9]{1,2})',orig)
    if res:
        return default,int(res.group(1)),int(res.group(3)) 
    return default,default,default

def date_ground(orig, base_date, default=None):
    week_days = ur"(周一|星期一|礼拜一|周二|星期二|礼拜二|周三|星期三|礼拜三|周四|星期四|礼拜四|周五|星期五|礼拜五|周六|星期六|礼拜六|周日|周天|周末|星期天|星期日|礼拜天|礼拜日)"
    numbers = ur"(一|二|两|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十|二十一|二十二|二十三|二十四|二十五|二十六|二十七|二十八|二十九|三十|三十一)"
    year,month,day = date_format(orig, default=None)
    if month and day:
        if year:
            return datetime(year, month, day)
        else:
            return datetime(base_date.year, month, day)

    try:
        if re.match(ur'今天|今早|今晚', orig):
            return base_date
        if re.match(ur'昨天', orig):
            return base_date + timedelta(days=-1)
        if re.match(ur'明天|明日|明早|明晚', orig):
            return base_date + timedelta(days=1)
        if re.match(ur'后天', orig):
            return base_date + timedelta(days=2)
        if re.match(ur'大后天', orig):
            return base_date + timedelta(days=3)

        m = re.match(ur'(这|本)?'+week_days, orig)
        if m:
            wkd = hashweekdays(m.group(2)) - 1 # monday is 0
            delta = wkd - base_date.weekday()
            return base_date + timedelta(days = delta)

        m = re.match(ur'下'+week_days, orig)
        if m:
            wkd = hashweekdays(m.group(1)) - 1 # monday is 0
            delta = wkd - base_date.weekday() + 7
            return base_date + timedelta(days = delta)

        m = re.match(ur'(' + numbers + ur'|(\d+))(号|日)', orig)
        if m:
            if m.group(2):
                d = hashnum(m.group(2))
            else:
                d = int(m.group(3))
            return datetime(year=base_date.year, month=base_date.month, day=d)

        m = re.match(ur'(' + numbers + ur'|(\d+))' + ur'天(之|以)?后', orig)
        if m:
            if m.group(2):
                delta = hashnum(m.group(2))
            else:
                delta = int(m.group(3))
            return base_date + timedelta(days = delta)

        m = re.match(ur'(' + numbers+ur'|(\d+))月'+ ur'(' + numbers+ur'|(\d+))(号|日)*', orig)
        if m:
            if m.group(2):
                mon = hashnum(m.group(2))
            else:
                mon = int(m.group(3))

            if m.group(5):
                d = hashnum(m.group(5))
            else:
                d = int(m.group(6))
            return datetime(year=base_date.year, month=mon, day=d)

        m = re.match(ur'下(个)?月' + ur'(' + numbers+ur'|(\d+))(号|日)*', orig)
        if m:
            if m.group(3):
                d = hashnum(m.group(3))
            else:
                d = int(m.group(4))

            next_month = (base_date.month % 12) + 1
            dy = 1 if base_date.month == 12 else 0
            return datetime(year=base_date.year+dy, month=next_month, day=d)


        m = re.match(ur'五一', orig)
        if m:
            return datetime(year=base_date.year, month=5, day=1)

    except:
        return default

    return default



province_map = json.load(open(PROVINCE_MAP_PATH))
china_cities = open(CITY_LEXICON_PATH).read().decode('utf-8').strip().split('\n')

def loc_ground(orig, default=None):
    for city in china_cities:
        if city in orig:
            return city

    for province in province_map:
        if province in orig:
            return province_map[province]

    return default

def is_loc_name(orig, default=None):
    for city in china_cities:
        if city == orig:
            return city

    return default
