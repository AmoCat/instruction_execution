#coding:utf8

import urllib
import hashlib
import sys
import urllib2
import json
import time
import cPickle as pkl
import re

MY_AK = "3MP2ADZT6RXtdSCKa4l0S2Gqe8ZKsdWY"
API_URL = "http://api.map.baidu.com"
URL_SUFFIX_V1 = "/direction/v1"
URL_SUFFIX_V2 = "/direction/v2"
ERROR_CODE = {"1":"Parameter Error","2":"Permission denied"}


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
        color = re.compile("<[/]*[a-z]*[\s]*[a-z]*[=\"#]*[0-9]*[\"]*>")
        if step.has_key('stepInstruction'):
            self.stepInstruction = re.sub(color,'',step['stepInstruction'])
        else:
            self.stepInstruction = None

    def __unicode__(self):
        if self.type != 5:
            res = u"距离:%s公里\t耗时：%s\t%s\n" % (self.cal_dis(self.distance), self.duration, self.stepInstruction)
            if self.vehicle != None:
                res += unicode(self.vehicle)
        elif self.type == 5:
            res = self.stepInstruction + "\t"
        res += "\n"
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')

    def cal_time(self, time):
        h = time/3600
        m = (time - h*3600)/60
        t = time % 60

        res = str(m) + u"秒"
        res = str(t) + u"分" + res if m > 0 else res
        res = str(h) + u"时" + res if h > 0 else res
        return res

    def cal_dis(self, dis):
        return dis/1000.0

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
        res = u"首班车:%s\t末班车:%s\n" % (self.start_time, self.end_time)
        res += u"%s站 上车 - %s站 下车 共 %s 站" % (self.start_name, self.end_name, self.stop_num)
        return res

    def __str__(self):
        return unicode(self).encode('utf-8')


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
        data = json.loads(response_html)
        return data

    def make_query_url(self, origin, destination, region, mode, *args, **kwargs):
        t = time.time()
        query_url = self.bus_url_template % (mode, origin, destination, region, t)
        print >> sys.stderr,"Before adding ak,the query_url is %s" % (query_url)
        return self.add_sk(query_url)   
    
    def get_bus_info(self, data):
        print >> sys.stderr, "GET_BUS_INFO: status: " + data['message']
        if data['status'] != 0:
            return None
        result = data['result']
        routes = result['routes']
        origin = result['origin']
        destination = result['destination']
        taxi = result['taxi']
        f = open("scheme_format.txt",'w')
        for v in routes:
            schemes = v["scheme"]
            for scheme in schemes:
                "scheme is a dictionary"
                print >> f,json.dumps(scheme, sort_keys = True, indent = 4)
                steps = scheme['steps']
                for v in steps:
                    for step in v:
                        s = Step(step)
                        print s 

    def get_info(self, query):
        url = self.make_query_url(**query)
        data = self.request(url)
        pkl.dump(data, open('bus_info','w'))
        #data = pkl.load(open('bus_info', 'r'))
        if query['mode'] == "transit":
            return self.get_bus_info(data)

if __name__ == "__main__":
    api = baiduAPI()
    query = {"origin":"上地五街","destination":"北京大学","mode":"transit","region":"北京"}
    api.get_info(query)

