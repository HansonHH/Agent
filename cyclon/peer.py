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

class Peer(Thread):
     
    def __init__(self, interval):
        Thread.__init__(self)
        self.STOP = False
        self.interval = interval
                             
    def run(self):
        while not self.STOP:
            time.sleep(self.interval)
            print 'interval: %d seconds' % self.interval
