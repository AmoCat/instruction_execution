# -*- coding: utf-8 -*-

import re
import urllib2
from urllib2 import Request
import urllib
from urllib import urlencode
from bs4 import BeautifulSoup
import sys
import json

QUERY_URL = "http://train.qunar.com/dict/open/s2s.do"
QUNAR_URL = "http://train.qunar.com/stationToStation.htm"
QUNAR_TOUCH_URL = "http://touch.qunar.com/h5/train/trainList"
#http://train.qunar.com/dict/open/s2s.do?dptStation=北京&arrStation=上海&date=2016-06-01&type=normal&user=neibu&source=site&start=1&num=500&sort=3
#http://train.qunar.com/dict/open/s2s.do?callback=jQuery17203771695054035038_1464694247431&dptStation=%E5%8C%97%E4%BA%AC&arrStation=%E4%B8%8A%E6%B5%B7&date=2016-06-01&type=normal&user=neibu&source=site&start=1&num=500&sort=3&_=1464694247635
class Seat(object):
    def __init__(self, price, ticket_left, seat_type):
        self.price = price
        self.ticket_left = ticket_left
        self.seat_type = seat_type

    def __unicode__(self):
        rt = u"%s\t" % (self.seat_type)
        rt += u"¥%s\t" % (self.price)
        rt += u"%s\t" % (self.ticket_left)
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')

class Train(object):
    def __init__(self, train_number,start_station,arrival_station,from_time, to_time,seats, all_time,price,train_type):
        self.train_number = train_number
        self.from_time = from_time
        self.to_time = to_time
        self.start_station = start_station
        self.arrival_station = arrival_station
        self.price = price
        self.all_time = all_time
        self.seats = seats
        self.train_type = train_type

    def __unicode__(self):
        rt = u"%s\t" % (self.train_number)
        rt += u"%s ~ %s\t" % (self.from_time, self.to_time)
        rt += u"%s - %s\t" % (self.start_station, self.arrival_station)
        rt += u"%s\t" % self.all_time
        for s in self.seats:
            rt += u"%s\t" % s.seat_type
            rt += u"¥%s\t" % s.price
            rt += u"%s\t" % s.ticket_left
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')

class QunarSpider(object):
    """
    the qunar.com spider to query flight list
    """
    def __init__(self):
        """ constructiong funcion """
        self.qunar_url_template = "%s?fromStation=%%s&toStation=%%s&date=%%s&stsSearch="\
                %(QUNAR_URL)
        self.ticket_url_template = "%s?dptStation=%%s&arrStation=%%s&date=%%s&type=normal&user=neibu&source=site&start=1&num=500&sort=3"\
                %(QUERY_URL)
        self.touch_url_template = "%s?startStation=%%s&endStation=%%s&searchType=stasta&bd_source=train3W&date=%%s"\
                %(QUNAR_TOUCH_URL)

    def make_query_url(self, start_city, arrival_city, start_date, *args, **kwargs):
        query_url = self.ticket_url_template % (start_city, arrival_city, start_date)
        return query_url

    def make_origin_url(self, start_city, arrival_city,start_date, *args, **kwargs):
        origin_url = self.qunar_url_template % (start_city, arrival_city, start_date)
        return origin_url

    def make_touch_url(self, start_city, arrival_city,start_date, *args, **kwargs):
        touch_url = self.touch_url_template % (start_city, arrival_city, start_date)
        return touch_url
    
    def get_url(self,start_city, arrival_city, start_date, *args, **kwargs):
        fromStation_l = {}
        fromStation_l['fromStation']=start_city
        fromStation = urlencode(fromStation_l)
        toStation_l = {}
        toStation_l['toStation']=arrival_city
        toStation = urlencode(toStation_l)
        res = QUNAR_URL + '?' + fromStation + '&'+ toStation + '&date=' + start_date + '&stsSearch='
        return res

    def get_params(self,start_city, arrival_city, start_date, *args, **kwargs):
        res = {}
        res['fromStation']=start_city
        res['toStation']=arrival_city
        res['date']= start_date
        res['strsSearch'] = ''
        return res

    def get_ticket_info(self, query):
        """ get ticket infomation"""
        query_url = self.make_query_url(**query)
        """
        origin_url = self.make_origin_url(**query)
        origin_url = origin_url.replace('&',"%26")
        """
        origin_url = self.get_url(**query)
        touch_url = self.make_touch_url(**query)
        """
        params = self.get_params(**query)
        origin_url = urlencode(params)
        origin_url = QUNAR_URL+'?'+origin_url
        #origin_url = origin_url.replace('&',"%26")
        """        
        print "###origin_url = ",origin_url
        if query_url == None:
            return None
        #TODO logger server
        print >> sys.stderr, "In get_ticket_info,Spider-INFO::Going... to the page %s,to check if there is any affordable ticket" %query_url
        req = Request(query_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
        #req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko')
        try:
            response = urllib2.urlopen(req)
            response_html = response.read()
        except Exception,e :
            print >> sys.stderr, e
            return None
        response.close()
        json_data = json.loads(response_html)
        train_li =  json_data['data']['s2sBeanList']
        trains = []
        for t in train_li:
            train_number = t['trainNo']
            from_time = t['dptTime']
            to_time = t['arrTime']
            start_station = t['startStationName']
            arrival_station = t['arrStationName']
            train_type = t['extraBeanMap']['trainType']
            all_time = t['extraBeanMap']['interval']
            seats = []
            s = t['seats']
            for k,v in s.items():
                seats_type = k
                count = v['count']
                price = v['price']
                if count == 0:
                    count = u"无票"
                elif count == -1:
                    count = u"停售"
                else:
                    count = str(count)+u"张"
                seat_info = Seat(price,count,seats_type)
                seats.append(seat_info)
            train = Train(train_number,start_station,arrival_station,from_time,to_time,seats,all_time,price,train_type)
            trains.append(train)
        return {'trains': trains, 'link': touch_url}

if __name__ =="__main__":
    qunar_spider = QunarSpider()
    res = qunar_spider.get_ticket_info({'start_city': '上海', 'arrival_city': '广州', 'start_date': '2016-06-10'})
    for t in res:
        print t
