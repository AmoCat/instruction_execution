# -*- coding: utf-8 -*-

import re
import urllib2
from urllib2 import Request
import urllib
from bs4 import BeautifulSoup
import sys
from .train_class import Train
from .flight_class import Flight

#QUNAR_URL = "http://train.qunar.com/stationToStation.htm"
QUNAR_URL = "http://touch.qunar.com/h5/train/trainList"
#QUNAR_URL = "http://train.qunar.com/dict/open/s2s.dmZ?callback=jQuery17206062052847276143_1463902394917&dptStation=%E4%B8%8A%E6%B5%B7&arrStation=%E5%B9%BF%E5%B7%9E&date=2016-05-21&type=normal&user=neibu&source=site&start=1&num=500&sort=3&_=146390239537mZ"

class Train(object):
    def __init__(self, train_number,start_station,arrival_station,from_time, to_time,seats, all_time,price,ticket_left):
        self.train_number = train_number
        self.ticket_left = ticket_left
        self.from_time = from_time
        self.to_time = to_time
        self.start_station = start_station
        self.arrival_station = arrival_station
        self.price = price
        self.all_time = all_time
        self.seats = seats

    def __unicode__(self):
        rt = u"%s\t" % (self.train_number)
        rt += u"%s ~ %s\t" % (self.from_time, self.to_time)
        rt += u"%s - %s\t" % (self.start_station, self.arrival_station)
        rt += u"%s\t" % self.all_time
        rt += u"%s\t" % self.seats
        rt += u"%s" % self.price
        rt += u"%s" % self.ticket_left
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')


class QunarSpider(object):
    """
    the qunar.com spider to query flight list
    """
    def __init__(self):
        """ constructiong funcion """
        self.qunar_url_template = "%s?startStation=%%s&endStation=%%s&searchType=stasta&date=%%s&sort=7"\
                %(QUNAR_URL)
        #http://touch.qunar.com/h5/train/trainList?startStation=%E5%8C%97%E4%BA%AC&endStation=%E4%B8%8A%E6%B5%B7&searchType=stasta&date=2016-05-30&sort=7
        #self.qunar_url_template = "http://train.qunar.com/dict/open/s2s.do?callback=jQuery17206062052847276143_1463902394917"\
        #        "&dptStation=%%s&arrStation=%%s&date=%%s"

    def make_query_url(self, start_city, arrival_city, start_date, *args, **kwargs):
        query_url = self.qunar_url_template % (start_city, arrival_city, start_date)
        return query_url

    def get_query_page(self, query):
        """ get the query url for the ticket infomation page """
        query_url = self.make_query_url(**query)
        req = Request(query_url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        try :
            response =  urllib2.urlopen(req)
            response_html = response.read().decode('utf-8')
            print response_html
            soup = BeautifulSoup(response_html, 'html.parser')
            #f = open('soup.txt','w')
            #print >> f, soup
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
        query_url = self.make_query_url(**query)
        #query_url = urllib.unquote(query_url)
        print "##query_url=",query_url
        if query_url == None:
            return None
        #query_url = "http://train.qunar.com/stationToStation.htm?fromStation=%E5%8C%97%E4%BA%AC&toStation=%E4%B8%8A%E6%B5%B7&date=2016-05-17&stsSearch="
        #TODO logger server
        #query_url = "http://train.qunar.com/dict/open/s2s.do?callback=jQuery17206062052847276143_1463902394917&dptStation=%E4%B8%8A%E6%B5%B7&arrStation=%E5%B9%BF%E5%B7%9E&date=2016-05-21&type=normal&user=neibu&source=site&start=1&num=500&sort=3&_=1463902395374"

        print >> sys.stderr, "In get_ticket_info,Spider-INFO::Going... to the page %s,to check if there is any affordable ticket" %query_url
        req = Request(query_url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        try:
            response = urllib2.urlopen(req)
            response_html = response.read().decode('utf-8')
            #print response_html
        except Exception,e :
            print >> sys.stderr, e
            return None
        response.close()

        #key_word = self.get_font_key_word(response_html)
        #if not key_word:
        #    return None
        #TODO logger server
        #print >> sys.stderr, "In get_ticket_info,Spider-INFO::found the price font-pattern: %s" %key_word
        soup = BeautifulSoup(response_html, 'html.parser')
        f = open('soup.txt','w')
        print >> f,soup
        '''
        res = ""
        for i in  soup.findAll(attrs={"class":"price {0}".format(key_word)}):
            price =  int(unicode(i.string).encode('utf-8'))
            if price < AFFORD_PRICE:
                res += str(price)+"RMB   "
        '''
        trains = []
        for l in soup.findAll('li', class_="qn_arrow_grey r"):
            ticket_info = l.find('p', class_="clearfix trainName").get_text().strip().split()
            train_number = ticket_info[0]
            #ticket_left = ticket_info[1]
            from_time = l.find('p', class_="dInfo").find('span', class_="important").string
            to_time = l.find('p', class_="aInfo").find('span', class_="qn_grey").string
            start_station = l.find('p', class_="dInfo").find('span', class_="station").string
            arrival_station = l.find('p', class_="aInfo").find('span', class_="qn_grey station").string
            all_time = l.find('p', class_="allTime").find('span', class_="time").string
            ticket_left = l.find('p', class_="clearfix trainName").find('span', class_="qn_fr qn_grey").string
            if l.find('p', class_="allTime").find('span',class_="qn_grey des"):
                seats = "已售空"
                price = str(0)
            else:
                price = l.find('p', class_="dInfo").find('span', class_="qn_fr qn_orange important").string
                seats = l.find('p', class_="aInfo").find('span', class_="qn_fr").string
            train = Train(train_number,start_station,arrival_station,from_time,to_time,seats,all_time,price,ticket_left)
            trains.append(train)
            #for train in trains:
            #    print train
        return {'trains': trains, 'link': query_url}

if __name__ =="__main__":
    qunar_spider = QunarSpider()
    res = qunar_spider.get_ticket_info({'start_city': '上海', 'arrival_city': '广州', 'start_date': '2016-05-29'})
    for t in res:
        print t
    res = qunar_spider.get_ticket_info({'start_city': '哈尔滨', 'arrival_city': '广州', 'start_date': '2016-05-30'})
    for t in res:
        print t
