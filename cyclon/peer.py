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
from request import *

import memcache
mc = memcache.Client(['127.0.0.1:11211'], debug=1)

# Get introducer's ip address (CYCLON Protocol)
INTRODUCER_IP = 'http://' + config.get('CYCLON', 'introducer_ip') + ':' + config.get('Agent', 'listen_port')

# Neighbor object
class Neighbor(object):

    #def __init__(self, neighbor_id, ip_address, age):
    def __init__(self, ip_address, age):
        #self.neighbor_id = neighbor_id
        self.ip_address = ip_address
        self.age = int(age)

class Peer(Thread):
     
    def __init__(self, interval, neighbors):
        Thread.__init__(self)
        self.isJoined = False
        self.STOP = False
        self.interval = interval
        self.neighbors = neighbors
        
        if len(NEIGHBORS) == 0:
            #introducer = Neighbor(uuid.uuid4(), INTRODUCER_IP, 0)
            introducer = Neighbor(INTRODUCER_IP, 0)
            self.neighbors.append(introducer)
            # Save neighbor list to memcached (expiration up to 30 days)
            mc.set("neighbors", self.neighbors, 0)


    def run(self):

        if not self.isJoined:
            print 'Peer needs to join the P2P network first...'
            agent_ip = 'http://' + get_lan_ip() + ':' + config.get('Agent', 'listen_port')
            print INTRODUCER_IP 
            print agent_ip

            if INTRODUCER_IP != agent_ip:
                print 'Introducer is another agent...'
                self.peer_join(INTRODUCER_IP, agent_ip)
            else:
                print 'Introducer is agent itself...'
                #self.peer_join(INTRODUCER_IP, agent_ip)

        #for i in range(3):
        while not self.STOP:
            time.sleep(self.interval)
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
            
            # Update all neighbors' age by one
            self.update_age()
            # Select neighbor with highest age
            #self.pick_up_neighbor_with_highest_age():
    
    # Peer sends a request to its introducer to join the P2P network
    def peer_join(self, introducer_ip, agent_ip):
        print 'Peer Join!!!'
        headers = {'Content-Type':'application/json; charset=UTF-8'}
        url = introducer_ip + '/v1/agent/cyclon/new_peer_join'
        #url = 'http://127.0.0.1:18090/v1/agent/cyclon/new_peer_join'
        dic = {"new_peer" : {"ip_address" : agent_ip} }
        print url
        print dic
        print json.dumps(dic)
        res = POST_request_to_cloud(url, headers, json.dumps(dic))
        print res
        self.isJoined = True
    
    
    # Update peer's all neighbors' age by one
    def update_age(self):

        self.neighbors = mc.get("neighbors")

        if len(self.neighbors) == 0:
            pass
        else:
            for i in range(len(self.neighbors)):
                # Update neighbor's age by one                
                self.neighbors[i].age = self.neighbors[i].age + 1
            
                print '-'*50
                print 'FIXED_SIZE_CACHE: %s' % FIXED_SIZE_CACHE
                print 'SHUFFLE_LENGTH: %s' % SHUFFLE_LENGTH
                print 'len of neighbors list: %d' % len(self.neighbors)
                #print "neighbor_id: %s" % self.neighbors[i].neighbor_id
                print "age: %s" % self.neighbors[i].age
                print "ip_address: %s" % self.neighbors[i].ip_address
                print '-'*50

                # Save neighbor list to memcached (expiration up to 30 days)
                mc.set("neighbors", self.neighbors, 0)


    #def push(self):





