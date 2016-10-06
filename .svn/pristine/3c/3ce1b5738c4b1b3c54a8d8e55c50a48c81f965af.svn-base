# -*- coding: utf-8 -*-

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