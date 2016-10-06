# -*- coding: utf-8 -*-
class Seat(object):
    def __init__(self, price, ticket_left, seats_type):
        self.price = price
        self.ticket_left = ticket_left
        self.seats_type = seats_type

    def __unicode__(self):
        rt = u"%s\t" % (self.seats_type)
        rt += u"%s\t" % (self.price)
        rt += u"%s\t" % (self.ticket_left)
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')

class Train(object):
    def __init__(self, train_number,start_station,arrival_station,from_time, to_time,seats, all_time,price):
        self.train_number = train_number
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
        for s in self.seats:
            rt += u"%s\t" % s.seats_type
            rt += u"%s\t" % s.price
            rt += u"%s\t" % s.ticket_left
        return rt

    def __str__(self):
        return unicode(self).encode('utf-8')