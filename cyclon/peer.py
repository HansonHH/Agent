#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

CYCLON Protocol Peer Class

"""
from threading import Thread
import time
from time import gmtime, strftime
from common import *
from db import *
from models import *
import uuid

# Get introducer's ip address (CYCLON Protocol)
INTRODUCER_IP = 'http://' + config.get('CYCLON', 'introducer_ip')
NEIGHBORS = []

# Neighbor object
class Neighbor(object):

    def __init__(self, neighbor_id, ip_address, age):
        self.neighbor_id = neighbor_id
        self.ip_address = ip_address
        self.age = int(age)


class Peer(Thread):
     
    def __init__(self, interval):
        Thread.__init__(self)
        self.STOP = False
        self.interval = interval
        
        if len(NEIGHBORS) == 0:
            introducer = Neighbor(uuid.uuid4(), INTRODUCER_IP, 0)
            NEIGHBORS.append(introducer)
                             
    def run(self):
        while not self.STOP:
            time.sleep(self.interval)
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
            
            self.update_age()
            print 'FIXED_SIZE_CACHE: %s' % FIXED_SIZE_CACHE
            print 'SHUFFLE_LENGTH: %s' % SHUFFLE_LENGTH

    def update_age(self):

        if len(NEIGHBORS) == 0:
            pass
        else:
            for i in range(len(NEIGHBORS)):
                # Update neighbor's age by one                
                neighbor1 = NEIGHBORS[i]
                neighbor2 = Neighbor(NEIGHBORS[i].neighbor_id, NEIGHBORS[i].ip_address, NEIGHBORS[i].age+1)
                NEIGHBORS.remove(neighbor1)
                NEIGHBORS.append(neighbor2)
                #NEIGHBORS[i].age = NEIGHBORS[i].age + 1
                print '-'*50
                print NEIGHBORS[i].neighbor_id
                print NEIGHBORS[i].age
                print NEIGHBORS[i].ip_address
                print '-'*50



    #def push(self):





