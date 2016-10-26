#coding:utf8

import urllib
import hashlib
import sys
import urllib2
import json
import time

MY_AK = "3MP2ADZT6RXtdSCKa4l0S2Gqe8ZKsdWY"
API_URL = "http://api.map.baidu.com"

class baiduAPI(object):

    def add_sk(self, origin_url):
        #print "origin_url=" , origin_url
        url = origin_url + "&ak=" + MY_AK
        encodeStr = urllib.quote(url, safe = "/:=&?#+!$,;'@()*[]")
        rawStr = encodeStr + MY_AK
        encodeStr += "&sn="+hashlib.md5(urllib.quote_plus(rawStr)).hexdigest()
        print API_URL + encodeStr
        return API_URL + encodeStr

    def __init__(self):
        self.bus_url_template = "/direction/v1?&mode=%s&origin=%s&destination=%s&region=%s&output=json&timestamp=%s"

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
        print data, data['message']
        return data

    def make_query_url(self, origin, destination, region, mode, *args, **kwargs):
        t = time.time()
        query_url = self.bus_url_template % (mode, origin, destination, region, t)
        print >> sys.stderr,"Before adding ak,the query_url is %s" % (query_url)
        return self.add_sk(query_url)   

    def get_bus_info(self, query):
        url = self.make_query_url(**query)
        data = self.request(url)

if __name__ == "__main__":
    api = baiduAPI()
    query = {"origin":"上地五街","destination":"北京大学","mode":"transit","region":"北京"}
    api.get_bus_info(query)

