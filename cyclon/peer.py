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

class Peer(Thread):
     
    def __init__(self, interval):
        Thread.__init__(self)
        self.STOP = False
        self.interval = interval
                             
    def run(self):
        while not self.STOP:
            time.sleep(self.interval)
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
            
            #self.update_age()
            print FIXED_SIZE_CACHE
            print SHUFFLE_LENGTH

    def update_age(self):
        # Get all rows of Image object
        neighbors = read_all_from_DB(AGENT_DB_ENGINE_CONNECTION, Neighbor)

        if len(neighbors) == 0:
            pass
        else:
            for i in range(len(neighbors)):
                # Update neighbor's age by one                
                result = update_in_DB(AGENT_DB_ENGINE_CONNECTION, Neighbor, columns = [Neighbor.neighbor_id], keywords = [neighbors[i].neighbor_id], new_value_dic={"age":neighbors[i].age+1})
                print '-'*50
                print neighbors[i].neighbor_id
                print neighbors[i].age
                print neighbors[i].cloud_address
                print '-'*50



    #def push(self):





