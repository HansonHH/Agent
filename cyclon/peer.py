#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

"""

"""


from threading import Thread
import time
import datetime
from time import gmtime, strftime

class Peer(Thread):
     
    def __init__(self, interval):
        Thread.__init__(self)
        self.STOP = False
        self.interval = interval
                             
    def run(self):
        while not self.STOP:
            time.sleep(self.interval)
            #print 'CYCLON protocol runs every %d seconds, current time: %s' % (self.interval, datetime.datetime.now().time()) 
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
