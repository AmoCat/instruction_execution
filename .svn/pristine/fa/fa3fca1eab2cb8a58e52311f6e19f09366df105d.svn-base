#!/usr/bin/python
# -*- coding: UTF-8 -*-

import xml.sax

class LTMLHandler_ne( xml.sax.ContentHandler ):
        def __init__(self):
                self.CurrentData = ""
                self.l_id = []
                self.l_cont = []
                self.l_pos = []
                self.l_ne = []
            
         # 元素开始事件处理
        def startElement(self, tag, attributes):
                self.CurrentData = tag
           	if tag == "xml4nlp":
                        pass 
           	elif tag == "note":
                        pass
                        '''
                        sent = attributes["sent"]
                        print "sent:", sent
                        word = attributes["word"]
                        print "word:", word
                        pos = attributes["pos"]
                        print "pos:", pos
                        ne = attributes["ne"]
                        print "ne:", ne
                        parser = attributes["parser"]
                        print "parser:", parser
                        wsd = attributes["wsd"]
                        print "wsd:", wsd
                        srl = attributes["srl"]
                        print "srl:", srl
                        '''
                elif tag == "doc":
                        pass
                elif tag == "para":
                        pass
                elif tag == "sent":
                        id = attributes["id"]
                        #print "id:", id
                        s_cont = attributes["cont"]
                        #print "cont:", s_cont
                        #self.l_cont.append(s_cont)
                elif tag == "word":
                        w_id = attributes["id"]
                        #print "id:", w_id
                        self.l_id.append(w_id)
                        
                        w_cont = attributes["cont"]
                        #print "cont:", w_cont
                        self.l_cont.append(w_cont)
                        
                        pos= attributes["pos"]
                        #print "pos:", pos
                        self.l_pos.append(pos)

                        ne= attributes["ne"]
                        #print "ne:", ne
                        self.l_ne.append(ne)
                
        def GetResult(self):
                return self.l_cont,self.l_pos,self.l_ne



                    
        








                
               
