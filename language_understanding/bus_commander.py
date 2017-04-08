#coding:utf-8

__all__ = ['BusCommander']

import urllib2
from datetime import datetime, timedelta
import json
import CRFPP
from .ground import date_ground, loc_ground, is_loc_name
from preprocessor import area_preprocessor
from functools import wraps
from .baidu_API import Scheme, Step, Taxi, Selection, Vehicle, baiduAPI
import os
import re
from ltp_handler import LTP_ne
from CH_phonetic import PinYin

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

RESULT_SIZE = 5

SLOTS = ['from', 'to', 'mode', 'city', 'bus_id']

NEEDED_SLOTS = ['from', 'to', 'city']

QUESTIONS = {'city': u'您在哪个城市呢?','to':u'您要去哪里呢?', 'from':u'您要从哪里出发呢?'} 

REPLY_UNSUPPORTED_CITY = u'不支持的城市'
REPLY_NOT_FOUND = u'没有找到信息'

FILL_DEFAULT_CITY = False
FILL_DEFAULT_FROM  = False 
FILL_DEFAULT_TO = False

STATUS_SUCCESS = 0
STATUS_WAITING = 1
STATUS_INTERUPT = 2

ORIG_SLOT_NAME_PREFIX = '_'

CONTEXT_EXPECTED = 'expected_slot_name'
CONTEXT_SLOTS = 'slots'

DEBUG = True
#DEBUG = False


DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
MODEL_PATH = os.path.join(DATA_DIR, 'bus.model') # crf模型路径
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

class BusCommander(object):
    def __init__(self):
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
            self.recognize(sent, words, postags, nes)
        else:
            expected_slot_name = self.context.get(CONTEXT_EXPECTED)
            print "###self.slots = ",self.slots
            slot = self.recognize_expected_slot(sent, words, postags, nes, expected_slot_name)
            self.slots = self.context.get(CONTEXT_SLOTS, {})
            print "###self.slots = ",self.slots
            self.recognize(sent, words, postags, nes)
            if self.__orig(expected_slot_name) in self.slots.keys():
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
        k,v = self.area_recognize(sent)
        if (k != None) and (v != None):
            self.context['prev'] = (k,v)
        self.fill_default_slots()
        self.infer_city()
        status, reply, context = self.construct_reply()
        return status, reply, context

    def infer_city(self):
        if 'from' in self.slots and 'to' in self.slots:
            f = self.slots['from']
            to = self.slots['to']
            k,v = area_preprocessor(f)
            f_city = [tup[1] for tup in v] if v else []
            k,v = area_preprocessor(to)
            t_city = [tup[1] for tup in v] if v else []
            same = [s for s in f_city if s in t_city]
            if len(same) == 1:
                self.slots['city'] = same[0].decode('utf-8')


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

    def loc_name(self, sent):
        res = is_loc_name(sent,default= None)
        return res

    def area_recognize(self, sent):
        if 'city' in self.slots:
            k, v = area_preprocessor(sent, self.slots['city'])
        else:
            k, v = area_preprocessor(sent)
        if v == None:
            return None, None
        if len(v) == 1:
            #self.slots[self.__orig('area')] = k
            #self.slots['area'] = v[0][0]
            #此处若加入city可能因为单个识别不准而出错
            #if 'city' not in self.slots:
            #    self.slots['city'] = v[0][1].decode('utf-8')
            pass
        else:
            return k.decode('utf-8'), [t[1].decode('utf-8') for t in v]
        return None,None

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
        #print "###construct_regularize_slots",self.slots

    def regularize_slot(self, slot_name, slot_value):
        '''规范化slot'''
        slot_name = self.__reg(slot_name)
        r = slot_value
        if slot_name in ['city']:
            r = self.regularize_loc(slot_value)
        elif slot_name == 'area':
            k,r = self.regularize_area(slot_value)
        elif slot_name in ['from','to']:
            r = self.regularize_area_tag(slot_value)#规范化识别到的area
        return r

    def regularize_area_tag(self, orig):
        r = orig
        return r

    def regularize_area(self, area):
        k,r = area_ground(area)
        return r

    def regularize_loc(self, loc):
        r = loc_ground(loc, default = None)
        return r

    def regularize_hotel(self, hotel):
        r = hotel_ground(hotel, default = None)
        return r

    def regularize_type(self, h_type):
        r = type_ground(h_type, default = None)
        return r

    def regularize_date(self, dt):
        today = datetime.today()
        tomorrow = today + timedelta(days=1)
        d = date_ground(dt, today, default=None)
        r = '%d-%02d-%02d' % (d.year, d.month, d.day)
        return r

    def fill_check_out_time(self,dt):
        if FILL_CHECK_OUT_DATE:
            if 'check_in_date' in self.slots and 'check_out_date' not in self.slots:
                today = datetime.today()
                d = date_ground(dt, today, default=None)
                if d!=None:
                    d = d + timedelta(days=1)
                    r = '%d-%02d-%02d' % (d.year, d.month, d.day)
                    self.slots[self.__reg('check_out_date')] = r

    def fill_default_slots(self):
        if FILL_DEFAULT_CITY and 'city' not in self.slots:
            pass

    def construct_reply(self):
        '''构造回复'''
        #不支持的地点
        if self.__orig('city') in self.slots and 'city' not in self.slots:
            reply = REPLY_UNSUPPORTED_CITY
            context = {}
            if DEBUG:
                context = {CONTEXT_SLOTS: self.slots}
            return STATUS_SUCCESS, reply, context

        # 是否缺少必须的slot
        for needed_slot_name in NEEDED_SLOTS:
            if needed_slot_name not in self.slots:
                reply = self.get_question(needed_slot_name)
                self.context[CONTEXT_EXPECTED] = needed_slot_name
                self.context[CONTEXT_SLOTS] = self.slots
                return STATUS_WAITING, reply.encode('utf-8'), self.context

        # 如果必须的slot都有了
        info = self.get_bus_info(self.slots)
        if info:
            buses = info['bus']#list
            taxi = info['taxi']
            reply = self.make_reply_title(self.slots['from'],self.slots['to'],self.slots['city'])
            if buses:
                reply += u'\n' + ''.join([str(bus) for bus in buses]).decode('utf-8')
            if taxi:
                reply += str(taxi).decode('utf-8')
            reply += "#####"
        else:
            reply = REPLY_NOT_FOUND
        context = {}
        if DEBUG:
            context = {CONTEXT_SLOTS: self.slots}
        return STATUS_SUCCESS, reply.encode('utf-8'), context


    def make_reply_title(self, st, des, city):
        return u"公交线路信息#####以下是我找到%s市从%s到%s的公交线路信息" % (city, st, des)

    def get_bus_info(self, slots):
        region = self.slots['city'].encode('utf-8')
        origin = self.slots['from'].encode('utf-8')
        destination = self.slots['to'].encode('utf-8')
        mode = 'transit'
        api = baiduAPI()
        info = api.get_info({'region': region, 'origin': origin,
            'destination':destination, 'mode':mode})
        return info

    def get_question(self, slot_name):
        return QUESTIONS[slot_name]

    def get_prev_city(self, t):
        res = u','.join(t[1])
        res += u"都有" + t[0] + u','
        return res

