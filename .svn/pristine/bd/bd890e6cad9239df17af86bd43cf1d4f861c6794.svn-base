#!/usr/bin/python
# -*- coding: UTF-8 -*-
__all__=['LTP_ne']
import urllib, urllib2
import xml.sax
import time
import sys
from LTMLHandler_ne import*

def LTP_ne(sentence):
    #uri_base = "http://127.0.0.1:12345/ltp"
    uri_base = "http://120.25.81.83:12345/ltp"

    data = {'s': sentence,   'x': 'n',   't': 'ne'}

    request = urllib2.Request(uri_base)
    params = urllib.urlencode(data)
    response = urllib2.urlopen(request, params)
    content = response.read().strip()   
    #print content
    
    Handler = LTMLHandler_ne()
    t = xml.sax.parseString(content,Handler)
    l_cont,l_pos,l_ne = Handler.GetResult()
    #l_cont = []
    #l_cont = l_cont_t[1:]
    """
    seg = ' '.join(l_cont)
    pos = ' '.join(l_pos)
    ner = ' '.join(l_ne)
    """
#print seg + "["+str(len(l_cont))+"]"
#print pos + "["+str(len(l_pos))+"]"
#print ner + "["+str(len(l_ne))+"]"
    #return seg,pos,ner,
    return l_cont,l_pos,l_ne,
    
if __name__ == "__main__":
    t = time.time()
    seg,pos,ner = LTP_ne('为什么我一个事接一个事，这么多事呢？头好痛')
    print seg
    print pos
    print ner
    print time.time()-t
