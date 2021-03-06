# -*- coding: utf-8 -*-

import re
import urllib2
from urllib2 import Request
import urllib
from bs4 import BeautifulSoup
import sys

QUNAR_URL = "http://flight.qunar.com/site/oneway_list.htm"
QUNAR_TOUCH_URL = "http://touch.qunar.com/h5/flight/flightlist"
RESULT_URL = "https://m.flight.qunar.com/ncs/page/flightlist"

class Flight(object):
    def __init__(self, from_place, to_place, from_time, to_time, company1, company2, price):
        self.from_place = from_place
        self.to_place = to_place
        self.from_time = from_time
        self.to_time = to_time
        self.company1 = company1
        self.company2 = company2
        self.price = price

    def __unicode__(self):
        rt = u"%s ~ %s\t" % (self.from_time, self.to_time)
        rt += u"%s - %s\t" % (self.from_place, self.to_place)
        rt += u"（%s）" % (self.company1)
        #rt += "%s\t%s\t\t" % (self.company1, self.company2)
        rt += u"¥%s" % self.price
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')


class QunarSpider(object):
    """
    the qunar.com spider to query flight list
    """
    def __init__(self):
        """ constructiong funcion """
        self.qunar_url_template = "%s?searchDepartureAirport=%%s&searchArrivalAirport=%%s&searchDepartureTime=%%s"\
                %(QUNAR_URL)
        self.touch_url_template = "%s?startCity=%%s&destCity=%%s&startDate=%%s&backDate=&flightType=oneWay&bd_source=flightList3W"\
                %(QUNAR_TOUCH_URL)
        self.result_url = "%s?depCity=%%s&arrCity=%%s&goDate=%%s&sort=&airLine=&from="\
                %(RESULT_URL)

    def make_query_url(self, start_city, arrival_city, start_date, *args, **kwargs):
        query_url = self.qunar_url_template % (start_city, arrival_city, start_date)
        return query_url

    def make_touch_url(self, start_city, arrival_city,start_date, *args, **kwargs):
        touch_url = self.touch_url_template % (start_city, arrival_city, start_date)
        return touch_url

    def make_result_url(self, start_city, arrival_city,start_date, *args, **kwargs):
        result_url = self.result_url % (start_city, arrival_city, start_date)
        return result_url.decode('utf-8')

    def get_query_page(self, query):
        """ get the query url for the ticket infomation page """
        query_url = self.make_query_url(**query)
        req = Request(query_url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        try :
            response =  urllib2.urlopen(req)
            response_html = response.read().decode('utf-8')
            soup = BeautifulSoup(response_html, 'html.parser')
            #f = open('soup.txt','w')
            #print >>f,soup
            query_url = soup.form.input['value']
        except Exception,e:
            # if any exception, return None
            print >> sys.stderr, e
            return None
        response.close()
        query_url = urllib.unquote(query_url)
        return query_url

    def get_font_key_word(self,response_html):
        """ get the font key word to check the price info futher """
        font_pattern = re.compile(r'font-face.*?\'(.*?)\'')
        for line in response_html.split('\n'):
            match = font_pattern.search(line)
            if match:
                return match.group(1)
        # if pattern not found
        return None


    def get_ticket_info(self, query):
        """ get ticket infomation"""
        query_url = self.get_query_page(query)
        touch_url = self.make_touch_url(**query)
        result_url = self.make_result_url(**query)
        if query_url == None:
            return None
        #query_url = "http://touch.qunar.com/h5/flight/flightlist?startCity=北京destCity=&startDate=2016-04-10"
        #TODO logger server
        print >> sys.stderr, "Spider-INFO::Going... to the page %s,to check if there is any affordable ticket" %query_url
        req = Request(query_url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        try:
            response = urllib2.urlopen(req)
            response_html = response.read().decode('utf-8')
        except Exception,e :
            print >> sys.stderr, e
            return None
        response.close()
        '''
        key_word = self.get_font_key_word(response_html)
        if not key_word:
            return None
        #TODO logger server
        print >> sys.stderr, "Spider-INFO::found the price font-pattern: %s" %key_word        
        res = ""
        for i in  soup.findAll(attrs={"class":"price {0}".format(key_word)}):
            price =  int(unicode(i.string).encode('utf-8'))
            if price < AFFORD_PRICE:
                res += str(price)+"RMB   "
        '''
        soup = BeautifulSoup(response_html, 'html.parser')
        flights = []
        for l in soup.findAll('li', class_="list-row item"):
            from_time = l.find('p', class_="from-time").string
            from_place = l.find('p', class_="from-place").string
            to_time = l.find('p', class_="to-time").string
            to_place = l.find('p', class_="to-place").string
            company1 = l.find('span', class_="company1").string
            company2 = l.find('span', class_="company2").string
            price = l.find('p', class_="price-info").find('span').next_sibling.string
            flight = Flight(from_place, to_place, from_time, to_time, company1,company2,price)
            #print "###company1=",flight.company1,"company2=",flight.company2
            flights.append(flight)
        touch_url=touch_url.decode('utf-8')
        #return {'flights': flights, 'link': touch_url}
        return {'flights': flights, 'link': result_url}

if __name__ =="__main__":
    qunar_spider = QunarSpider()
    res = qunar_spider.get_ticket_info({'start_city': '上海', 'arrival_city': '广州', 'start_date': '2016-04-08'})
    for f in res:
        print f
    res = qunar_spider.get_ticket_info({'start_city': '哈尔滨', 'arrival_city': '广州', 'start_date': '2016-05-08'})
    for f in res:
        print f
