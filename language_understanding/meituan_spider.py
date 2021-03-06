# -*- coding: utf-8 -*-

import re
import urllib2
from urllib2 import Request
import urllib
from bs4 import BeautifulSoup
import sys
import json
from CH_phonetic import PinYin

MEITUAN_URL = "http://hotel.meituan.com/search/jiudian"
QUERY_URL = "http://hotel.meituan.com/api/getcounterandpois"

class Deal(object):
    def __init__(self,roomTitle,roomTypeName,breakfast,wifi,price):
        self.roomTitle = roomTitle
        self.roomTypeName = roomTypeName
        self.breakfast = breakfast
        self.wifi = wifi
        self.price = price

    def __unicode__(self):  
        rt = u"%s\t[%s]\t%s\t%s\t¥%s" %(self.roomTitle, self.roomTypeName, self.breakfast, self.wifi, self.price)
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')

class Hotel(object):
    def __init__(self, poiID,hotelName,address,areaID,areaName,districtName,hotelStar,wifi,park,dealList):
        self.poiID = poiID
        self.hotelName = hotelName
        self.address = address
        self.areaID = areaID
        self.areaName = areaName
        self.districtName = districtName
        self.hotelStar = hotelStar
        self.wifi = wifi
        self.park = park
        self.dealList = dealList

    def __unicode__(self):
        rt = u"%s" % (self.hotelName)
        if self.areaName != None and self.areaName.strip() != "":
            rt += u"\t[%s]" % (self.areaName)
        rt += u"\t%s\n" % (self.address)
        #rt = u"%s\t[%s]%s\n" % (self.hotelName, self.areaName, self.address)
        for d in self.dealList:
            #rt += u"%s\t[%s]\t%s\t¥%s\n" %(d.roomTitle, d.roomTypeName, d.breakfast, d.price)
            #rt += u"%s\t[%s]\t%s\n" %(d.roomTitle, d.roomTypeName, d.breakfast)
            rt += u"%s" % (d.roomTitle)
            if d.roomTypeName != None and d.roomTypeName.strip() != "":
                rt += u"\t[%s]" % (d.roomTypeName)
            rt += u"\t%s\n" % (d.breakfast)
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')

class HotelSpider(object):
    """
    the meituan.com spider to query hotel list.
    """
    def __init__(self):
        """ constructiong funcion """
        self.meituan_url_template = "%s/%%s?search=1&mtt=1.hotel%%s2Fsearch%%s2F2.0.0.iq9bgoic#ci=%%s&co=%%s&sort=&w=&page=&attrs="\
            %(MEITUAN_URL)
        self.query_url_template = "%s/%%s?ci=%%s&co=%%s&sort=&w=&attrs="\
            %(QUERY_URL)
        #http://hotel.meituan.com/api/getcounterandpois/haerbin?ci=2016-10-11&co=2016-10-12&sort=&w=&brand=28349&attrs=

    def get_ch_phonetic(self,city):
        print "#####city =",city
        pinyin = PinYin()
        pinyin.load_word()
        city_name = pinyin.hanzipinyin(string=city)
        res = ''.join(city_name)
        print "####city_name=",res
        return res

    def make_query_url(self, city, check_in_date, check_out_date, name_id, area_id, *args, **kwargs):
        city = self.get_ch_phonetic(city)
        query_url = self.query_url_template % (city, check_in_date, check_out_date)
        if name_id != None:
            query_url += "&brand="+name_id
        if area_id != None:
            query_url += "&geoslug=" + area_id
        return query_url

    def make_origin_url(self, city, check_in_date, check_out_date, name_id, area_id, *args, **kwargs):
        city = self.get_ch_phonetic(city)
        origin_url = self.meituan_url_template % (city, '%', '%', check_in_date, check_out_date)
        if name_id != None:
            origin_url += '&brand=' + name_id
        if area_id != None:
            origin_url += '&geoslug=' + area_id
        return origin_url

    def hash_breakfast(self,breakfast):
        if breakfast:
            return u"含早餐"
        return u"不含早餐"

    def hash_wifi(self,wifi):
        if wifi:
            return u"有wifi"
        return u"无wifi"

    def get_hotel_info(self, query):
        """ get ticket infomation"""
        query_url = self.make_query_url(**query)
        origin_url = self.make_origin_url(**query)
        if query_url == None:
            return None
        #TODO logger server
        print >> sys.stderr, "In get_hotel_info,Spider-INFO::Going... to the page %s,to check if there is any affordable dealList" %query_url
        req = Request(query_url)
        req.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        req.add_header('Cookie',"ci=105; abt=1467704796.0%7CBDF; rvct=105; SID=17civeiosqrtod74257sctcqr2; __mta=218010921.1467704798425.1467713884318.1467714726010.4; "\
            "hotel_ci=254; uuid=5b24085c3e2efc995e34.1467704796.0.0.0; "\
            "oc=snNNj2QetM3FK9f_1wtFoBtcZVf7S7pDPcFnMROR9nEvFyyMXs6HdxsUNah4CK6Nt_QODrTLLMVchGCzrqTmoSKOg9bjvqJA9K-WmC4LAZvrPhCX6JJnyuXkQ8WHxSFNvw61Nen4ql66RWaJQ6S05-yAF57CNfBmLY1nOfhS6QA;"\
            " __utma=211559370.1400275573.1467704798.1467704798.1467705209.2; __utmb=211559370.13.9.1467714725150; __utmc=211559370; "\
            "__utmz=211559370.1467704798.1.1.utmcsr=baidu|utmccn=baidu|utmcmd=organic|utmcct=homepage; __utmv=211559370.|1=city=hrb=1")
        req.add_header('X-Requested-With','XMLHttpRequest')
        try:
            response = urllib2.urlopen(req)
            response_html = response.read()
        except Exception,e :
            print >> sys.stderr, e
            return None
        response.close()
        data = json.loads(response_html)
        hotelList = []
        js_data = data['data']
        if not js_data.has_key('dealsData'):
            return {'hotelList': hotelList, 'link': origin_url}
        #return {'hotelList': hotelList, 'link': origin_url}
        dealsData = js_data['dealsData']#房间预订#
        poiDealList = js_data['poiDealList']#酒店号与deal对应关系#
        poiInfo = js_data['poiInfo']#酒店信息#
        for h in poiInfo:
            poiID = str(h['poiID'])
            hotelName = h['name']
            address = h['address']
            areaID = h['areaID']
            areaName = h['areaName']
            districtName = h['districtName']
            park = h['park']
            wifi = h['wifi']
            hotelStar = h['hotelStar']
            dealList = []
            dealIDList = poiDealList[poiID]['dealIDList']
            for id in dealIDList:
                dealData = dealsData[str(id)]
                #print dealData.keys()
                #print dealData
                breakfast = self.hash_breakfast(dealData['breakfast'])
                roomTitle = dealData['title']
                roomTypeName = ""
                if 'roomTypeName' in dealData.keys():
                    roomTypeName = '/'.join(dealData['roomTypeName'])
                price = dealData['value']
                wifi = self.hash_wifi(dealData['wifi'])
                deal = Deal(roomTitle,roomTypeName,breakfast,wifi,price)
                dealList.append(deal)
            hotel = Hotel(poiID,hotelName,address,areaID,areaName,districtName,hotelStar,wifi,park,dealList)
            #print hotel
            hotelList.append(hotel)
        return {'hotelList': hotelList, 'link': origin_url}

if __name__ == '__main__':
    spider = HotelSpider()
    res = spider.get_hotel_info({'city':'北京','check_in_date':'2016-07-10','check_out_date':'2016-07-11'})
    for h in res:
        print h