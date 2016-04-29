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
mc = memcache.Client([MEMCACHED_SERVER_IP], debug=1)

# Get introducer's ip address (CYCLON Protocol)
INTRODUCER_IP = 'http://' + config.get('CYCLON', 'introducer_ip') 
NEIGHBORS = []

# Neighbor object
class Neighbor(object):

    def __init__(self, ip_address, age):
        self.ip_address = ip_address
        self.age = int(age)

class Peer(Thread):
     
    def __init__(self, interval, neighbors):
        Thread.__init__(self)
        self.isJoined = False
        self.STOP = False
        self.interval = interval
        self.neighbors = neighbors
        
        introducer = Neighbor(INTRODUCER_IP, 0)
        self.neighbors.append(introducer)
        # Save neighbor list to memcached (expiration up to 30 days)
        mc.set("neighbors", self.neighbors, 0)

    def run(self):

        if not self.isJoined:
            agent_ip = 'http://' + get_lan_ip() + ':' + config.get('Agent', 'listen_port')
            print 'Peer needs to join the P2P network first...'
            print 'Introducer IP Address: %s' % INTRODUCER_IP 
            print 'Agent IP Address: %s' % agent_ip

            if INTRODUCER_IP != agent_ip:
                print 'Introducer is another agent...'
                self.peer_join(INTRODUCER_IP, agent_ip)
            else:
                print 'Introducer is agent itself...'
                self.isJoined = True
                #self.peer_join(INTRODUCER_IP, agent_ip)

        #for i in range(3):
        while not self.STOP and self.isJoined:
            time.sleep(self.interval)
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
            
            # Update all neighbors' age by one
            self.update_age()
            # Select neighbor with highest age
            #self.pick_up_neighbor_with_highest_age():
    
    # Peer sends a request to its introducer to join the P2P network
    def peer_join(self, introducer_ip, agent_ip):
        print 'Peer is joining the P2P network...'
        headers = {'Content-Type':'application/json; charset=UTF-8'}
        url = introducer_ip + '/v1/agent/cyclon/new_peer_join'
        #url = 'http://127.0.0.1:18090/v1/agent/cyclon/new_peer_join'
        dic = {"new_peer" : {"ip_address" : agent_ip} }
        res = POST_request_to_cloud(url, headers, json.dumps(dic))
        print '~'*60
        print res
        print res.json()
	print type(res.status_code)
	# If introducer's length of neighbors list is less than FIXED_CACHE_SIZE 
	if res.status_code == '201':
            self.neighbors = mc.get("neighbors")
            neighbors_response = res.json()['neighbors']
            print neighbors_response
	    for neighbor in neighbors_response['neighbors']:
                new_neighbor = Neighbor(neighbor['ip_address'], 0)
		self.neighbors.append(new_neighbor)
	    mc.set("neighbors", self.neighbors)
        print len(self.neighbors)
        print '~'*60
        # New peer generates several threads to initiat a shuffle of lenght 1 with nonadjance nodes received from its introducer
        self.isJoined = True
    
    
    # Update peer's all neighbors' age by one
    def update_age(self):

        self.neighbors = mc.get("neighbors")

        if len(self.neighbors) == 0:
            pass
        else:
            print '-'*50
            print 'FIXED_SIZE_CACHE: %s' % FIXED_SIZE_CACHE
            print 'SHUFFLE_LENGTH: %s' % SHUFFLE_LENGTH
            print 'len of neighbors list: %d' % len(self.neighbors)
            for i in range(len(self.neighbors)):
                # Update neighbor's age by one                
                self.neighbors[i].age = self.neighbors[i].age + 1
                print "age: %s" % self.neighbors[i].age
                print "ip_address: %s" % self.neighbors[i].ip_address
                # Save neighbor list to memcached (expiration up to 30 days)
                mc.set("neighbors", self.neighbors, 0)
            print '-'*50

    #def push(self):





