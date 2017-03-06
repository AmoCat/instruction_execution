# -*- coding: utf-8 -*-

__all__ = ['FlightCommander']

import urllib2
from datetime import datetime, timedelta
import json
import CRFPP
from .qunar_f_spider import QunarSpider
from .flight_class import Flight
from .ground import date_ground, loc_ground, is_loc_name, time_ground, date_to_time
from .flight_ground import airline_ground, airport_ground, get_loc
from functools import wraps
import os
import re
from ltp_handler import LTP_ne

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
AIRPORT_MAP_PATH = os.path.join(DATA_DIR, 'china_airports.txt')

RESULT_SIZE = 5 #返回航班结果数量

SLOTS = ['start_city', 'arrival_city', 'start_airport', 'arrival_airport', 'start_date', 'arrival_date', 'start_time','cost_relative'
        'arrval_time','airline']

NEEDED_SLOTS = ['start_city', 'arrival_city', 'start_date'] # 必须的slot

QUESTIONS = {'start_city': u'您要从哪里出发呢？',
        'arrival_city': u'您要去哪里呢？',
        'start_date': u'您想要哪一天出发呢？'} # 缺少某个slot时的提问

REPLY_UNSUPPORTED_START_CITY = u'不支持的出发地'
REPLY_UNSUPPORTED_ARRIVAL_CITY = u'不支持的到达地'
REPLY_NOT_FOUND = u'没有找到航班信息'

FILL_DEFAULT_START_CITY = False #是否填充默认的出发地
FILL_DEFAULT_START_DATE = False #是否填充默认的出发日期，默认为明天

STATUS_SUCCESS = 0
STATUS_WAITING = 1
STATUS_INTERUPT = 2

ORIG_SLOT_NAME_PREFIX = '_'

CONTEXT_EXPECTED = 'expected_slot_name'
CONTEXT_SLOTS = 'slots'

#DEBUG = True
DEBUG = False


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODEL_PATH = os.path.join(DATA_DIR, 'flight.model') # crf模型路径
tagger = CRFPP.Tagger('-m %s' % (MODEL_PATH))

def cache(func):
    caches = {}

    @wraps(func)
    def wrap(*args):
        if args not in caches:
            caches[args] = func(*args)
        return caches[args]
    return wrap


def make_link(text, link):
    return u"<a href=\"%s\">%s</a>" % (link, text)

class FlightCommander(object):
    def __init__(self):
        #self.tagger = CRFPP.Tagger('-m /Users/Oliver/Documents/IR/笨笨/project/crf.model')
        self.slots = {}
        self.slot_probs = {}
        self.context = {}

    def __orig(self, slot_name):
        '''给定一个slot_name，返回它表示原始数据的keyname'''
        if self.__is_orig(slot_name):
            return slot_name
        return ORIG_SLOT_NAME_PREFIX + slot_name

    def __reg(self, slot_name):
        '''给定一个slot_name，返回它表示规范化后的数据的keyname'''
        if self.__is_orig(slot_name):
            return slot_name[len(ORIG_SLOT_NAME_PREFIX):]
        return slot_name

    def __is_orig(self, slot_name):
        return slot_name.startswith(ORIG_SLOT_NAME_PREFIX)

    def __is_reg(self, slot_name):
        return not self.__is_orig(slot_name)

    '''
    def ltp_process(self, sent):
        url_get_base = "http://ltpapi.voicecloud.cn/analysis/?"
        api_key = 'C2A1p2a08gAyNDgDqktGavGSgQ5ppGxsVONU5G3r'
        format = 'json'
        pattern = 'ner'
        result = urllib2.urlopen("%sapi_key=%s&text=%s&format=%s&pattern=%s" % (url_get_base,api_key,sent.encode('utf-8'),format,pattern))
        content = result.read().strip()
        result = json.loads(content)[0][0]
        words = [r['cont'] for r in result]
        postags = [r['pos'] for r in result]
        nes  = [r['ne'] for r in result]
        return words, postags, nes
    '''

    def ltp_process(self,sent):
        words,pos,nes = LTP_ne(sent.encode('utf-8'))
        return words,pos,nes

    def __is_status_waiting(self):
        r = CONTEXT_EXPECTED in self.context.keys()
        return r

    def get_reply(self, sent, context):
        words, postags, nes = self.ltp_process(sent)
        status, reply, context = self.get_reply_with_lexical(sent, words, postags, nes, context)
        return status, reply, context

    def get_reply_with_lexical(self, sent, words, postags, nes, context):
        '''接口，取得回复。words是unicode'''
        self.context = context
        if not self.__is_status_waiting():
            #print "###not waiting..."
            self.recognize(sent, words, postags, nes)
            #print "###recognize over..."
        else:
            expected_slot_name = self.context.get(CONTEXT_EXPECTED)
            print "###self.slots = ",self.slots
            slot = self.recognize_expected_slot(sent, words, postags, nes, expected_slot_name)
            self.slots = self.context.get(CONTEXT_SLOTS, {})
            print "###self.slots = ",self.slots
            self.recognize(sent, words, postags, nes)
            if self.__reg(expected_slot_name) in self.slots.keys():
                print "###self.__orig(expected_slot_name) in self.slots.keys()"
                pass
            elif slot != None:
                print "###slot != None,slot= ",slot
                self.slots.update(slot)
            else:
                return STATUS_INTERUPT,'',{}
            # 如果没有获得需要的slot，则中断多轮会话
            print "###self.slots = ",self.slots

        self.construct_regularize_slots()
        if self.__orig('start_date') in self.slots.keys():
            if self.slots[self.__orig('start_date')] == u'昨天':
                reply = u'亲爱的,昨天的飞机早就飞走了呀~'
                return STATUS_SUCCESS,reply,'{}'
        self.fill_default_slots()
        status, reply, context = self.construct_reply()
        if 'start_city' in self.slots.keys() and 'arrival_city' in self.slots.keys():
            if self.slots['start_city'] == self.slots['arrival_city']:
                reply = u'出发地和到达地不能相同'
                return STATUS_SUCCESS, reply, '{}'
        return status, reply, context

    def add_slot(self, slot_name, slot_value, prob):
        if slot_name not in self.slots:
            self.slots[slot_name] = slot_value
            self.slot_probs[slot_name] = prob
        elif slot_name in self.slot_probs.keys():
            if prob > self.slot_probs[slot_name]:
                self.slots[slot_name] = slot_value
                self.slot_probs[slot_name] = prob
        elif slot_name in self.slots:
            '''waiting状态重新输入了目的地或出发地'''
            self.slots[slot_name] = slot_value
            self.slot_probs[slot_name] = prob

    def recognize_expected_slot(self, sent, words, postags, nes, expected_slot_name):
        '''单个词CRF不能识别，在此处先根据标准化来判断是否为所需回答'''
        if expected_slot_name not in SLOTS:
            return None
        regularized_slot_value = self.regularize_slot(expected_slot_name,sent)
        if regularized_slot_value != None:
            return {self.__orig(expected_slot_name):sent}
        return None

    def loc_name(self,sent):
        res = is_loc_name(sent,default= None)
        return res

    def recognize(self, sent, words, postags, nes):
        '''识别slot'''
        if self.loc_name(sent):
            return
        tagger.clear()
        size = len(words)
        for i in range(size):
            cont = ' '.join([words[i], postags[i], nes[i]])
            tagger.add(cont.encode('utf-8'))
        tagger.parse()

        word = ''
        cur_slot_name = ''
        prob = 0
        for i in range(size):
            tag = tagger.y2(i)
            #print "#########"+tag, tagger.prob(i)
            if tag.startswith('B-'):
                if word:
                    self.add_slot(self.__orig(cur_slot_name), word, prob)
                    print "###cur_slot_name = ",cur_slot_name
                    #slots[self.__orig(cur_slot_name)] = word
                    word, cur_slot_name = '', ''
                    prob = 0
                word += words[i]
                cur_slot_name = tagger.y2(i)[2:]
                prob = tagger.prob(i)
            elif tag.startswith('I-'):
                word += words[i]
            elif tag == 'O':
                if word:
                    self.add_slot(self.__orig(cur_slot_name), word, prob)
                    #slots[self.__orig(cur_slot_name)] = word
                    word, cur_slot_name = '', ''
                    prob = 0
        if word:
            #slots[self.__orig(cur_slot_name)] = word
            self.add_slot(self.__orig(cur_slot_name), word, prob)
            print "###cur_slot_name = ",cur_slot_name

    def construct_regularize_slots(self):
        '''把slots中未规范化的slot规范化'''
        #print "###",self.slots
        for k, v in self.slots.items():
            #print "### k = ",k,"v = ",v
            if self.__is_reg(k): ## 如果不是待规范的slot_name，则跳过
                continue
            if self.__reg(k) in self.slots: ## slots里面已经存在规范化过的了
                continue
            regularized_slot_value = self.regularize_slot(k, v)
            if regularized_slot_value != None:
                self.slots[self.__reg(k)] = regularized_slot_value
                if k in ['_start_airport','_arrival_airport']:
                    self.add_city(k, regularized_slot_value)
                if k in ['_start_time','_arrival_time']:
                    self.add_date(k, regularized_slot_value)
                if k in ['_start_date','_arrival_date']:
                    self.add_time(k, v)
        #print "###construct_regularize_slots",self.slots

    def add_time(self, k, date):
        t = date_to_time(date)
        slot_name = None
        if k == '_start_date':
            slot_name = 'start_time'
        if k == 'arrival_date':
            slot_name = 'arrival_time'
        if t and slot_name not in self.slots.keys():
            s = self.regularize_time(t)
            self.slots[slot_name] = s
        elif t == None and slot_name not in self.slots.keys():
            s = self.regularize_time(date)
            self.slots[slot_name] = s

    def add_date(self, k, time):
        slot_name = None
        if k == "_start_time":
            slot_name = "_start_date"
        elif k == "_arrival_time":
            slot_name = "_arrival_date"
        d = re.search(ur"明早|明晚|今早|今晚",time)
        if d:
            self.slots[slot_name] = "明天"

    def add_city(self, k, regularized_slot_value):
        airport_map = json.load(open(AIRPORT_MAP_PATH))
        #print "### k in ['_start_airport','_arrival_airport'],k =",k
        city = None
        for key in airport_map.keys():
            #print"### key = ",key,"airport_map[key]=",airport_map[key],"regularized_slot_value",regularized_slot_value
            if regularized_slot_value in airport_map[key]:
                city = key
                if city == u'北京1':
                    city = u'北京'
                if city == u'上海1':
                    city = u'上海'
            if k == '_start_airport':
                self.slots['start_city'] = city
            elif k == '_arrival_airport':
                #print "###k == _arrival_airport"
                self.slots['arrival_city'] = city

    def regularize_slot(self, slot_name, slot_value):
        '''规范化slot'''
        slot_name = self.__reg(slot_name)
        r = slot_value
        if slot_name in ['start_city', 'arrival_city']:
            r = self.regularize_loc(slot_value)
            if r == None:
                r,airport = get_loc(slot_value)
                if r and (slot_name == 'start_city'):
                    self.slots['start_airport'] = airport
                if r and (slot_name == 'arrival_city'):
                    self.slots['arrival_airport'] = airport
        elif slot_name in ['start_date', 'arrival_date']:
            r = self.regularize_date(slot_value)
        elif slot_name in ['start_time', 'arrival_time']:
            r = self.regularize_time(slot_value)
        elif slot_name in ['start_airport', 'arrival_airport']:
            r = self.regularize_airport(slot_value)
        elif slot_name is 'cost_relative':
            r = slot_value
        elif slot_name == 'airline':
            r = regularize_airline(slot_value)
        return r

    def regularize_airline(self, airline):
        r = airline_ground(self, airline)
        return r

    def regularize_loc(self, loc):
        r = loc_ground(loc, default=None)
        return r
    def regularize_airport(self, airport):
        #print "###regularize_airport"
        r = airport_ground(airport, default=None)
        return r

    def regularize_time(self, tm):
        #print "###regularize_time"
        sh,sm,eh,em = time_ground(tm, default = None)
        r = '%02d:%02d~%02d:%02d'%(sh,sm,eh,em)
        return r

    def regularize_date(self, dt):
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        d = date_ground(dt, today, default=None)
        r = '%d-%02d-%02d' % (d.year, d.month, d.day) if d else None
        return r

    def fill_default_slots(self):
        if FILL_DEFAULT_START_CITY and 'start_city' not in self.slots:
            pass
        if FILL_DEFAULT_START_DATE and 'start_date' not in self.slots:
            tomorrow = datetime.now() + timedelta(days=1)
            self.slots.update({'start_date': '%d-%02d-%02d' % (tomorrow.year, tomorrow.month, tomorrow.day)})

    def construct_reply(self):
        '''构造回复'''
        #不支持的地点
        if self.__orig('start_city') in self.slots and 'start_city' not in self.slots:
            reply = REPLY_UNSUPPORTED_START_CITY
            context = {}
            if DEBUG:
                context = {CONTEXT_SLOTS: self.slots}
            return STATUS_SUCCESS, reply, context
        elif self.__orig('arrival_city') in self.slots and 'arrival_city' not in self.slots:
            reply = REPLY_UNSUPPORTED_ARRIVAL_CITY
            context = {}
            if DEBUG:
                context = {CONTEXT_SLOTS: self.slots}
            return STATUS_SUCCESS, reply.encode('utf-8'), context

        # 是否缺少必须的slot
        for needed_slot_name in NEEDED_SLOTS:
            if needed_slot_name not in self.slots:
                reply = self.get_question(needed_slot_name)
                self.context[CONTEXT_EXPECTED] = needed_slot_name
                self.context[CONTEXT_SLOTS] = self.slots
                return STATUS_WAITING, reply.encode('utf-8'), self.context

        # 如果必须的slot都有了
        info = self.get_ticket_info(self.slots)
        if info:
            flights = info['flights']
            link = info['link']
            flights.sort(key=lambda x: int(x.price))
            reply = self.make_reply_title(self.slots['start_date'],
                    self.slots['start_city'],
                    self.slots['arrival_city'], 0)
            if len(flights) == 0:
                reply = self.make_reply_title(self.slots['start_date'],
                    self.slots['start_city'],
                    self.slots['arrival_city'], 1) + u"#####" + link
                context = {}
                if DEBUG:
                    context = {CONTEXT_SLOTS: self.slots}
                return STATUS_SUCCESS, reply.encode('utf-8'), context
            if 'arrival_airport' in self.slots:
                airport = self.slots['arrival_airport']
                for f in flights[0:]:
                    #print "###f = ",f,"airport=",airport
                    if airport not in f.to_place:
                        flights.remove(f)
            if 'start_airport' in self.slots:
                airport = self.slots['start_airport']
                for f in flights[0:]:
                    if airport not in f.from_place:
                        flights.remove(f)
            if 'start_time' in self.slots or 'arrival_time' in self.slots:
                time = re.match(ur'(.+)~(.+)',self.slots['start_time'])
                lt = time.group(1)
                rt = time.group(2)
                if 'start_time' in self.slots:
                    reply += u',起飞时间为%s~%s：'%(lt,rt)
                    for f in flights[0:]:
                        st = self.hash_time(f.from_time)
                        if self.hash_time(lt) > st:
                            flights.remove(f)
                            continue
                        if self.hash_time(rt) < st:
                            flights.remove(f)
                            continue
                if 'arrival_time' in self.slots:
                    reply += u',到达时间为%s~%s：'%(lt,rt)
                    for f in flights[0:]:
                        at = self.hash_time(f.to_time)
                        if self.hash_time(lt) > at:
                            flights.remove(f)
                            continue
                        if self.hash_time(rt) < at:
                            flights.remove(f)
                            continue
            if 'alrline' in self.slots:
                f = self.slots['airline']
                for f in flights[0:]:
                    if f.company1 != f:
                        flights.remove(f)
            if 'cost_relative' in self.slots:
                if len(flights) > 1:
                    for f in flights[1:]:
                        flights.remove(f)
            if len(flights) != 0:
                #print "###len(flights) != 0"
                reply += '\n'+'\n'.join([str(f) for f in flights[:RESULT_SIZE]]).decode('utf-8')
                reply += '\n'
                #print "#####reply=",reply
                #reply += (u'\n更多航班信息请进入：%s' % link).encode('utf-8')
                #reply += u'更多航班信息请点' + make_link(u'这里', link)
                reply += u'更多航班信息请点击该消息#####' + link
            else:
                #reply +=u'\n您的限制条件太多啦！没有符合条件的航班信息\n查看当日航班请点' + make_link(u'这里', link)
                reply +=u'\n没有符合条件的航班信息\n查看当日航班请点该消息#####' + link
        else:
            reply = REPLY_NOT_FOUND
        context = {}
        if DEBUG:
            context = {CONTEXT_SLOTS: self.slots}
        return STATUS_SUCCESS, reply.encode('utf-8'), context

    def hash_time(self, str):
        l = str.split(':')
        h = int(l[0])
        m = int(l[1])
        return h*60+m


    def make_reply_title(self, start_date, start_city, arrival_city, type):
        year, month, day = start_date.split('-')
        month = month.lstrip('0')
        day = day.lstrip('0')
        res = u"机票信息#####"
        if type == 0:
            return res + u"以下是我找到的%s月%s日从%s到%s的机票" % (month, day, start_city, arrival_city)
        else:
            return res + u"帮您查到了%s月%s日从%s到%s的机票，请点击该消息查看" % (month, day, start_city, arrival_city)

    def get_ticket_info(self, slots):
        start_city = slots['start_city'].encode('utf-8')
        arrival_city = slots['arrival_city'].encode('utf-8')
        start_date = slots['start_date'].encode('utf-8')
        spider = QunarSpider()
        #flights = spider.get_ticket_info(start_city, arrival_city, start_date)
        info = spider.get_ticket_info({'start_city': start_city, 'arrival_city': arrival_city,
            'start_date':start_date})
        return info

    def get_question(self, slot_name):
        return QUESTIONS[slot_name]

