#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""

CYCLON Protocol Peer Class

"""

from threading import Thread
import time
from time import gmtime, strftime
#from common import *
from db import *
from models import *
from request import *
from cyclon.config import *
from cyclon.common import *

from threading import Lock
lock = Lock()

# Get introducer's ip address (CYCLON Protocol)
INTRODUCER_IP = 'http://' + config.get('CYCLON', 'introducer_ip') 
AGENT_IP = 'http://' + get_lan_ip() + ':' + config.get('Agent', 'listen_port')
NEIGHBORS = []


# Neighbor object
class Neighbor(object):

    def __init__(self, ip_address, age):
        self.ip_address = ip_address
        self.age = int(age)
    
    def __str__(self):
        return "ip_address: %s, age: %s" % (self.ip_address, self.age)

class Peer(Thread):
     
    def __init__(self, interval, neighbors):
        Thread.__init__(self)
        self.isJoined = False
        self.STOP = False
        self.interval = interval
        self.neighbors = neighbors
        #self.lock = lock
        
        if INTRODUCER_IP != AGENT_IP:
            introducer = Neighbor(INTRODUCER_IP, 0)
            self.neighbors.append(introducer)
            # Save neighbor list to memcached (expiration up to 30 days)
            #mc.set("neighbors", self.neighbors, 0)
            write_to_memory_cache("neighbors", self.neighbors)
        else:
            #mc.set("neighbors", [], 0)
            write_to_memory_cache("neighbors", [])
    
    #def __str__(self):
    #    return "neighbors: %" % (self.neighbors)

    def run(self):

        if not self.isJoined:
            print 'Peer needs to join the P2P network first...'
            print 'Introducer IP Address: %s' % INTRODUCER_IP 
            print 'Agent IP Address: %s' % AGENT_IP

            if INTRODUCER_IP != AGENT_IP:
                print 'Introducer is another agent...'
                self.peer_join(INTRODUCER_IP, AGENT_IP)
            else:
                print 'Introducer is agent itself...'
                #mc.set("neighbors", [], 0)
                self.isJoined = True
                #self.peer_join(INTRODUCER_IP, agent_ip)

        #for i in range(3):
        while not self.STOP and self.isJoined:
            time.sleep(self.interval)
            print 'CYCLON protocol runs every %d seconds, %s' % (self.interval, strftime("%Y-%m-%d %H:%M:%S", gmtime())) 
            
            # Update all neighbors' age by one
            self.update_age()
            #self.lock.acquire()
            #print 'CYCLON Thread Lock Acquire...'
	    self.view_exchange()
            #self.lock.release()
            #print 'CYCLON Thread Lock Release...'
    

    # New peer sends a request to its introducer to join the P2P network
    def peer_join(self, introducer_ip, agent_ip):
        print 'Peer is joining the P2P network...'
        
        headers = {'Content-Type':'application/json; charset=UTF-8'}
        url = introducer_ip + '/v1/agent/cyclon/new_peer_join'
        dic = {"new_peer" : {"ip_address" : agent_ip} }
        
        res = POST_request_to_cloud(url, headers, json.dumps(dic))

	# If introducer's length of neighbors list is less than FIXED_CACHE_SIZE
	if res.status_code == 201:
	    print 'Waiting for responses from introducer\'s neighbors...'
        elif res.status_code == 202:
	    print 'Waiting for random walk endpoint\' response...'

        # New peer generates several threads to initiat a shuffle of lenght 1 with nonadjacent nodes received from its introducer
        self.isJoined = True
    

    # Update peer's all neighbors' age by one
    def update_age(self):

        self.neighbors = read_from_memory_cache("neighbors")

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
                
                # Save neighbor list to memcached (expiration up to 30 days)
                write_to_memory_cache("neighbors", self.neighbors)
            
	    print '-'*50

    # Peer exchanges it view of neighbors with one of its oldest neighbor
    def view_exchange(self):
	
	print 'Peer View Exchange...'

        self.neighbors = read_from_memory_cache("neighbors")
	
	if len(self.neighbors) == 0:
            print 'No neighbor exists, waiting for neighbor to join...'
	    pass
    	else:
            # Pick up a oldest neighbor from neighbors list
	    oldest_neighbor = self.pick_neighbor_with_highest_age(self.neighbors)
            # Create a subset containing SHUFFLE_LENGTH neighbors
            selected_subset, sent_subset = self.select_subnet_randomly(self.neighbors, oldest_neighbor)

            # Send selected subset to the oldest neighbor
            try:
                self.send_to_oldest_neighbor(oldest_neighbor, selected_subset, sent_subset)
            except:
                pass


    # Pick up the oldest neighbor from neighbors list
    def pick_neighbor_with_highest_age(self, neighbors):
        print 'Pick up oldest neighbor...'

	oldest_neighbor = neighbors[0]
        oldest_neighbors = []
	for neighbor in neighbors:
	    if neighbor.age > oldest_neighbor.age:
	        oldest_neighbor = neighbor
        
        for neighbor in neighbors:
            if neighbor.age == oldest_neighbor.age:
                oldest_neighbors.append(oldest_neighbor)
	
	return random.choice(oldest_neighbors)
	

    # Select SHUFFLE_LENGTH - 1 random neighbors
    def select_subnet_randomly(self, neighbors, oldest_neighbor):
        print 'Select Subnet Randomly...'

        temp_list = []
        for neighbor in neighbors:
            if neighbor != oldest_neighbor:
                temp_list.append(neighbor)

        selected_subset = []
        sent_subset = []
        if len(temp_list) != 0:
            for i in range(SHUFFLE_LENGTH-1):
                selected_subset.append(random.choice(temp_list))
                sent_subset.append(random.choice(temp_list))
    
        selected_subset.append(oldest_neighbor)
        # Replace oldest neighbor's entry with a new entry of age 0 and with agent's ip address
        sent_subset.append(Neighbor(AGENT_IP, 0))

        return selected_subset, sent_subset


    def send_to_oldest_neighbor(self, oldest_neighbor, selected_subset, sent_subset):
        print 'Send to oldest neighbor -> ip_address: %s, age: %s' % (oldest_neighbor.ip_address, oldest_neighbor.age)
        
        headers = {'Content-Type': 'application/json'}
        url = oldest_neighbor.ip_address + '/v1/agent/cyclon/receive_view_exchange_request'
        sent_neighbors_data = []
        for neighbor in sent_subset:
            #dic = {"neighbor":{"ip_address":neighbor.ip_address, "age":neighbor.age}}
            dic = {"ip_address":neighbor.ip_address, "age":neighbor.age}
            sent_neighbors_data.append(dic)

        post_data = {"neighbors":sent_neighbors_data}
        res = POST_request_to_cloud(url, headers, json.dumps(post_data))

        response_neighbors = res.json()['neighbors']
    
        neighbors = read_from_memory_cache("neighbors")



        # Remove the oldest neighbor from local memory cahce
        neighbors = remove_from_list(neighbors, oldest_neighbor)
        write_to_memory_cache("neighbors", neighbors)



        # Update local neighbors list in memeory cache    
        update_neighbors_cache(neighbors, response_neighbors, selected_subset)


# Read neighbors list from memory cache
def read_from_memory_cache(key):
    lock.acquire()
    try:
        neighbors = mc.get(key)
    finally:
        lock.release()
        return neighbors

# Write neighbor list to memory cache
def write_to_memory_cache(key, value):
    lock.acquire()
    try:
        mc.set(key, value, 0)
    finally:
        lock.release()

# Remove a item from a list
def remove_from_list(items, target):
    new_items = []
    for item in items:
        if item.ip_address != target.ip_address:
            new_items.append(item)
    return new_items

# Return a list of neighbors' ip addresses
def get_neighbors_ip_list(neighbors):
    neighbors_ip_list = []
    for neighbor in neighbors:
        neighbors_ip_list.append(neighbor.ip_address)
    return neighbors_ip_list

# Check if new peer is already in
def is_in_neighbors(neighbors_ip_list, new_peer_ip_address):
    if new_peer_ip_address in neighbors_ip_list:
        return True
    else:
        return False

# Remove duplicated neighbor
def remove_neighbors_with_same_ip(neighbors):

    new_neighbors = []
    for i in range(len(neighbors)):
        neighbors_ip_list = get_neighbors_ip_list(new_neighbors)
        if neighbors[i].ip_address not in neighbors_ip_list:
            new_neighbors.append(neighbors[i])
    return new_neighbors

# Randomly pick n neighbors
def pick_neighbors_at_random(neighbors, number):

    # Select a cloud at random
    random_neighbors = []
    for i in range(number):
        neighbor =  random.choice(neighbors)
        random_neighbors.append(neighbor)

    return random_neighbors


#update_neighbors_cache(neighbors, response_neighbors, sent_neighbors)
def update_neighbors_cache(neighbors, received_neighbors, selected_neighbors):

    print '!'*150
    # Discard entries pointing to agent, and entries that are already in anget's cache
    filtered_received_neighbors = []
    neighbors_ip_list = get_neighbors_ip_list(neighbors)

    for neighbor in received_neighbors:
        #if neighbor['ip_address'] not in neighbors_ip_list and neighbor['ip_address'] != AGENT_IP:
        #agent_ip = 'http://' + get_lan_ip() + ':' + config.get('Agent', 'listen_port')
        if neighbor['ip_address'] != AGENT_IP:
            neighbor = Neighbor(neighbor['ip_address'], int(neighbor['age']))
            filtered_received_neighbors.append(neighbor)
    
    # Remove redundant neighbors	
    filtered_received_neighbors = remove_neighbors_with_same_ip(filtered_received_neighbors)

    # Update peer's cache to include all remaining entries 
    # Firstly, use empty cache slots (if any)
    if len(neighbors) < FIXED_SIZE_CACHE:
        for i in range(FIXED_SIZE_CACHE-len(neighbors)):
            if len(filtered_received_neighbors) != 0 and len(neighbors) < FIXED_SIZE_CACHE:
                neighbors_ip_list = get_neighbors_ip_list(neighbors)
                random_neighbor = random.choice(filtered_received_neighbors)
                if not is_in_neighbors(neighbors_ip_list, random_neighbor.ip_address):
                    neighbors.append(random_neighbor)
                    filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)
            else:
                break

    print len(neighbors)
    for neighbor in neighbors:
        print '%s, %s' % (neighbor.ip_address, neighbor.age)

    # Secondly, replace entries among the ones originally sent to the other peer
    if len(neighbors) == FIXED_SIZE_CACHE:
        print 'len(neighbors) == FIXED_SIZE_CACHE !!!!!!!!!!!'
        #response_neighbors_cp = response_neighbors
        for i in range(len(filtered_received_neighbors)):

            #if len(neighbors) == FIXED_SIZE_CACHE and not is_in_neighbors(neighbors_ip_list, random_neighbor.ip_address):
            if len(neighbors) == FIXED_SIZE_CACHE:
            
                neighbors_ip_list = get_neighbors_ip_list(neighbors)
                random_neighbor = random.choice(filtered_received_neighbors)
                random_selected_neighbor = random.choice(selected_neighbors)

                if not is_in_neighbors(neighbors_ip_list, random_neighbor.ip_address):
                    print '%'*300
                    print 'random_selected_neighbor: %s' % random_selected_neighbor.ip_address

            	    #random_neighbor = random.choice(filtered_received_neighbors)
            	    filtered_received_neighbors = remove_from_list(filtered_received_neighbors, random_neighbor)

            	    #random_response_neighbor = random.choice(response_neighbors)
            	    selected_neighbors = remove_from_list(selected_neighbors, random_selected_neighbor)

            	    neighbors = remove_from_list(neighbors, random_selected_neighbor)
            	    neighbors.append(random_neighbor)
            else:
                break
    print '!'*150
    
    write_to_memory_cache("neighbors", neighbors)




