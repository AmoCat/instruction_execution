#coding:utf8

import urllib
import hashlib
import sys
import urllib2
import json
import time
import cPickle as pkl
import re
import pprint

MY_AK = "3MP2ADZT6RXtdSCKa4l0S2Gqe8ZKsdWY"
API_URL = "http://api.map.baidu.com"
URL_SUFFIX_V1 = "/direction/v1"
URL_SUFFIX_V2 = "/direction/v2"
ERROR_CODE = {"1":"Parameter Error","2":"Permission denied"}

class Taxi(object):
    def __init__(self, t):
        self.day = t['detail'][0]
        self.night = t['detail'][1]
        self.distance = t['distance']
        self.duration = t['duration']
        self.remark = t['remark']
        self.start_km = re.search(u"[0-9.]*公里起步", self.remark).group(0).rstrip(u'公里起步')

    def __unicode__(self):
        res = u"打车费用:\n"
        res += u"%s : %s 元\t(起步价:%s元/%skm,超出部分%s元/km)\n"\
                % (self.day['desc'], self.day['total_price'], \
                   self.day['start_price'], self.start_km, self.day['km_price'])
        res += u"%s : %s 元\t(起步价:%s元/%skm,超出部分%s元/km)\n"\
                %(self.night['desc'], self.night['total_price'], \
                  self.night['start_price'], self.start_km, self.night['km_price'])
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

class Scheme(object):
    def __init__(self, s):
        self.distance = s['distance']
        self.duration = s['duration']
        self.line_price = s['line_price']
        self.line_type = s['plan_trans_type'] #地铁6 ，公交3
        self.bus_price = s['price']
        steps = s['steps']
        #if self.line_type == 3 or self.line_type == 6: #3公交,6地铁,4观光线路
        if self.line_type >= 0 and self.line_type <= 14:
            self.walks = []
            first_bus = None
            for list in steps[0:]:
                if list[0]['type'] == 5:#5为步行
                    self.walks.append(unicode(Step(list[0])))
                if first_bus == None and list[0]['type'] != 5:
                    first_bus = Step(list[0])
            if self.line_type == 3:#公交车，第一个instruction包含了所有公交号
                self.bus_ids = first_bus.get_bus_ids()
                self.instruction = first_bus.get_instruction()
            else:
                self.bus_ids = None
                self.instruction = ""
                for list in steps[0:]:
                    step = Step(list[0])
                    self.instruction += step.get_instruction()
                    self.instruction += "\n" if list[0]['type'] != 5 else ","
                self.instruction += u"至终点"
            self.steps = []
            for list in steps[0:]:
                for step in list:
                    if step['type'] != 5:
                        self.steps.append(Step(step))
        else:
            self.walks = None
            self.steps = None
            self.bus_ids = None

    def __unicode__(self):
        res = u"%s" % (self.instruction)
        res += "\t" if self.bus_ids != None else "\n"
        res += u"耗时：%s\t%s公里" % (self.cal_time(self.duration),self.cal_dis(self.distance))
        if self.bus_price != -1:
            res += u"\t¥%s" % (self.cal_price(self.bus_price))
        #res += u"\n"
        #res = u"%s\t耗时:%s\t票价:¥%s\t距离:%s\n"\
        #        % (self.instruction, self.cal_time(self.duration), self.cal_price(self.bus_price), self.cal_dis(self.distance))
        res += u"\t详情:\n" if self.bus_ids != None else "\n"
        #res += u"以下路线需先" + self.walks[0] + "\n" if self.walks != None else ""
        if self.steps != None and self.bus_ids != None:
            for i in range(len(self.steps)):
                if i < len(self.bus_ids):
                    res += self.bus_ids[i] + u"\t" 
                    res += unicode(self.steps[i])
        res += u"\n"
        #res += self.walks[1] + u"至终点" if self.walks != None and len(self.walks) >= 2 else ""
        #res += "\n"
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

    def cal_dis(self, d):
        return d/1000.0

    def cal_price(self, p):
        return p/200
    
    def cal_time(self, t):
        h = t/3600
        m = (t - h*3600)/60
        t = t % 60
        res = str(t) + u"秒"
        res = str(m) + u"分" + res if m > 0 else res
        res = str(h) + u"时" + res if h > 0 else res
        return res

class Step(object):
    def __init__(self, step):
        self.type_hash = ["", "火车", "飞机", "公交", "驾车", "步行", "大巴"]
        self.distance = step['distance']
        self.duration = self.cal_time(step['duration'])
        self.type = step['type']
        self.stepOriginLocation = step['stepOriginLocation']
        self.stepDestinationLocation = step['stepDestinationLocation']
        self.path = step['path'] if step.has_key('path') else None
        self.vehicle = Vehicle(step['vehicle']) if step['vehicle'] != None else None
        color = re.compile("<[/]*[a-z]*[\s]*[a-z]*[=\"#]*[a-z0-9]*[\"]*>")
        bus_id_compile = re.compile(u"[地铁]*[0-9a-z]+[号]*[路|线]")
        direction_compile = re.compile(u"(.*)")
        if step.has_key('stepInstruction'):
            self.stepInstruction = re.sub(color,'', step['stepInstruction'])
            self.bus_ids = re.findall(bus_id_compile, step['stepInstruction'])
            self.direction = re.search(direction_compile, step['stepInstruction'])
        else:
            self.stepInstruction = None
            self.bus_ids = None
            self.direction = None

    def __unicode__(self):
        if self.type != 5:
            res = u"耗时:%s\t" % (self.duration)
            if self.vehicle != None:
                res += unicode(self.vehicle)
        elif self.type == 5:
            res = self.stepInstruction
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

    def cal_time(self, time):
        h = time/3600
        m = (time - h*3600)/60
        t = time % 60

        res = str(t) + u"秒"
        res = str(m) + u"分" + res if m > 0 else res
        res = str(h) + u"时" + res if h > 0 else res
        return res

    def cal_dis(self, dis):
        return dis/1000.0

    def get_bus_ids(self):
        return self.bus_ids

    def get_instruction(self):
        return self.stepInstruction

class Vehicle(object):
    def __init__(self, v):
        self.type_hash = [u"普通日行公交", u"地铁、轻轨", u"机场巴士(往)", u"有轨电车", u"机场巴士（返）",
                         u"旅游线路车", u"夜班车", u"机场巴士（机场之间）", u"轮渡", u"其他", u"快车", 
                         u"慢车", u"机场快轨（往）", u"机场快轨（返）", u"机场轨道交通环路"]
        self.start_name = v['start_name']
        self.end_name = v['end_name']
        self.start_time = v['start_time']
        self.end_time = v['end_time']
        self.end_uid = v['end_uid']
        self.name = v['name']
        self.total_price = v['total_price']
        self.stop_num = v['stop_num']
        self.uid = v['uid']
        self.type = self.type_hash[v['type']]
        self.zone_price = v['zone_price']

       
    def __unicode__(self): 
        #res = u"从 %s 上车 - %s 下车 共 %s 站\t" % (self.start_name, self.end_name, self.stop_num)
        res = u"首班车:%s\t末班车:%s\n" % (self.start_time, self.end_time)
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

class Selection(object):
    def __init__(self, s):
        self.origin = s['origin'] if s.has_key('origin') else None
        self.destination = s['destination'] if s.has_key('destination') else None

    def __unicode__(self):
        res = u""
        if self.origin != None:
            for dict in self.origin:
                res += dict['name'] + ':' + dict['address'] + '\n'
        if self.destination != None:
            for dict in self.destination:
                res += dict['name'] + ":" + dict['address'] + '\n'
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

    def get_first_origin(self):
        return None if self.origin == None else self.origin[0]['name'].encode('utf-8')

    def get_first_des(self):
        return None if self.destination == None else self.destination[0]['name'].encode('utf-8')

class baiduAPI(object):

    def add_sk(self, origin_url):
        url = origin_url + "&ak=" + MY_AK
        return API_URL + url

    def __init__(self):
        self.bus_url_template = URL_SUFFIX_V1 + "?&mode=%s&origin=%s&destination=%s&region=%s&output=json&timestamp=%s"

    def request(self, url):
        "return json response from the url"
        print >> sys.stderr, "After addig ak,REQUEST-INFO::Going... to the page %s,to get a response" %url
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
            response_html = response.read()
        except Exception, e:
            print >> sys.stderr, e
            return None
        response.close()
        f = open('bus_info.txt', 'w')
        print >> f, response_html
        data = json.loads(response_html)
        return data

    def make_query_url(self, origin, destination, region, mode, *args, **kwargs):
        t = time.time()
        query_url = self.bus_url_template % (mode, origin, destination, region, t)
        print >> sys.stderr,"Before adding ak,the query_url is %s" % (query_url)
        return self.add_sk(query_url)   
    
    def get_bus_info(self, data):
        #print >> sys.stderr, "GET_BUS_INFO: status: " + data['message']
        if data['status'] != 0:
            return None

        result = data['result']
        routes = result['routes']
        origin = result['origin']
        destination = result['destination']
        taxi = result['taxi']
        bus_info_list = {}
        buses = []
        for v in routes:
            schemes = v["scheme"]
            for s in schemes:
                "scheme is a dictionary"
                scheme = Scheme(s)
                buses.append(scheme)
                print scheme
        bus_info_list['bus'] = buses
        print Taxi(taxi)
        bus_info_list['taxi'] = Taxi(taxi)
        return bus_info_list
    
    def get_bus_selection(self, data):
        print >> sys.stderr, "GET_BUS_SELECTION: status: " + data['message']
        if data['status'] != 0:
            return None
        #info = data['info'] 版权信息
        result = data['result']

        selection = Selection(result)
        return selection

    def info_mode_hash(self, mode, data):
        if mode == 'transit':
            return self.get_bus_info(data)
        else:
            return None

    def selection_mode_hash(self, mode, data):
        if mode == 'transit':
            return self.get_bus_selection(data)
        else:
            return None

    def get_info(self, query):
        url = self.make_query_url(**query)
        data = self.request(url)
        #pkl.dump(data, open('beijing_response','w'))
        #data = pkl.load(open('beijing_response', 'r'))
        if data['type'] == 2: #起终点明确，得到查询结果
            return self.info_mode_hash(query['mode'], data)
        elif data['type'] == 1: #起终点模糊，得到选择界面
            sel =  self.selection_mode_hash(query['mode'], data)
            if sel == None:
                print >> sys.stderr, "ERROR INFO: In selection page get \"None\" response.."
                return None
            else:
                first_origin = sel.get_first_origin()
                first_des = sel.get_first_des()
                query['origin'] = first_origin if first_origin != None else query['origin']
                query['destination'] = first_des if first_des != None else query['destination']
                url = self.make_query_url(**query)
                data = self.request(url)
                
                #pp = pprint.PrettyPrinter(indent = 4)
                #pp.pprint(data['result'])

                res = self.info_mode_hash(query['mode'], data)
                if res:
                    return res
                else:
                    return None

if __name__ == "__main__":
    api = baiduAPI()
    #query = {"origin":"哈工大","destination":"凯德广场","mode":"transit","region":"哈尔滨"}
    #query = {"origin":"上地五街","destination":"北京大学","mode":"transit","region":"北京"}
    #query = {"origin":"五道口","destination":"天安门","mode":"transit","region":"哈尔滨"}
    query = {"origin":"哈工大","destination":"哈工大二校区","mode":"transit","region":"哈尔滨"}
    api.get_info(query)

